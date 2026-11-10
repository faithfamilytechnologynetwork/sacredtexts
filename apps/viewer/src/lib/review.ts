// Reviewer state for the /review workflow (Spec 154: human labels for checking the matcher).
//
// Ported from multibench's review store (its Spec 92), re-keyed from tradition to sample. Drafts
// live in the review service (apps/api), one per (signed-in reviewer, sample). The store keeps
// multibench's public API (`useReviewState()` + `updateReviewState(fn)` + pure sample-scoped
// updaters) and its behaviour:
//   • updates apply OPTIMISTICALLY to an in-memory snapshot, then save asynchronously (debounced);
//   • each sample carries a `version`; a save on a stale version is reconciled (last-write-wins for
//     the active device, then server-wins if it still conflicts), and the reconcile is announced;
//   • the tolerant zod loader degrades a corrupt or older draft field by field to defaults;
//   • every multibench fix: a 401 or an account switch wipes state, a failed load never lets a blank
//     draft overwrite the saved one, a CSRF 403 refreshes the token and retries, a prefetch skips
//     samples already loaded, "start over" is persisted via DELETE, an unreachable service fails
//     visibly.
// Two additions:
//   • a save the server refuses for good (413, or any other 4xx that isn't 401, 409 or a CSRF 403)
//     is TERMINAL. It is not retried (a permanent 413 would otherwise loop forever), the error is
//     shown, and the labels stay in memory. The next edit tries again;
//   • the wipe also covers requests already in flight: each reset starts a new `session`, and a load,
//     list, save, delete or init that started in an earlier one drops its result when it lands.

import { useSyncExternalStore } from "react";
import { z } from "zod";
import {
  deleteDraft,
  fetchCsrf,
  getDraft,
  isCsrfError,
  listDrafts,
  login as apiLogin,
  logout as apiLogout,
  me as apiMe,
  putDraft,
  ReviewApiError,
  ReviewUnavailableError,
  setReviewFetch,
  signup as apiSignup,
  type Reviewer,
} from "./reviewApi";
import { RUBRIC_VERSION } from "./rubric";

export { setReviewFetch };
export type { Reviewer };

/** The reviewer's verdict on a cell: the outcome the matcher should have given, or can't judge. */
export const LABEL_OUTCOMES = ["correct", "incorrect", "refused", "cant_judge"] as const;
export type LabelOutcome = (typeof LABEL_OUTCOMES)[number];

/** The longest note the label control accepts (the API's body cap is sized for it). */
export const NOTES_MAX_CHARS = 1000;

/** One cell's human label. */
export interface CellLabel {
  /** null until the reviewer picks one; only a label with an outcome is in the gold set. */
  outcome: LabelOutcome | null;
  /** The question itself is wrong (the expected text or the prompt). */
  defect: boolean;
  notes: string;
  /** The rubric version and time of the label's last real edit (stamped by `withLabel`). */
  rubric_version: string;
  labelled_at: string;
}

/** One sample's review: the texts the reviewer chose and their labels, keyed by cell id. */
export interface SampleReview {
  texts: string[];
  labels: Record<string, CellLabel>;
}

export interface ReviewState {
  samples: Record<string, SampleReview>;
}

export function emptyLabel(): CellLabel {
  return { outcome: null, defect: false, notes: "", rubric_version: "", labelled_at: "" };
}

export function emptySampleReview(): SampleReview {
  return { texts: [], labels: {} };
}

export function emptyState(): ReviewState {
  return { samples: {} };
}

/** A label counts as labelled once it has an outcome. */
export function isLabelled(label: CellLabel | undefined): boolean {
  return label?.outcome != null;
}

// ---- tolerant persistence schema -------------------------------------------------------------
// Every field falls back independently (`.catch`), so one corrupt subfield never discards the rest
// of a reviewer's work.

const cellLabelSchema = z
  .object({
    outcome: z.enum(LABEL_OUTCOMES).nullable().catch(null),
    defect: z.boolean().catch(false),
    notes: z.string().catch(""),
    rubric_version: z.string().catch(""),
    labelled_at: z.string().catch(""),
  })
  .catch(() => emptyLabel());

const sampleReviewSchema = z
  .object({
    texts: z.array(z.string()).catch(() => []),
    labels: z.record(z.string(), cellLabelSchema).catch(() => ({})),
  })
  .catch(() => emptySampleReview());

/** Parse an untrusted sample draft (from the API) tolerantly. Never throws. */
export function parseSampleReview(value: unknown): SampleReview {
  return sampleReviewSchema.parse(value ?? {});
}

// ---- async, API-backed store -----------------------------------------------------------------

/** Delay before a change is persisted, so typing doesn't fire a PUT per keystroke. */
export const SAVE_DEBOUNCE_MS = 600;

/** How long a failed save waits before retrying. */
export const SAVE_RETRY_MS = 3000;

/** `unavailable`: there is no review service at this origin (the static viewer build). */
export type AuthStatus = "unknown" | "in" | "out" | "unavailable";

export interface ReviewStatus {
  auth: AuthStatus;
  reviewer: Reviewer | null;
  /** A save or delete is pending or in flight. */
  saving: boolean;
  /** Last error message (network / server), cleared on the next success. */
  error: string | null;
  /**
   * What failed: loading a draft, saving one (it will retry), or a save the server refused for good
   * (`rejected`: not retried; the labels stay on this device until an edit saves).
   */
  errorKind: "load" | "save" | "rejected" | null;
  /** A sample that was reconciled with another device since the reviewer's last edit. */
  reconciled: string | null;
}

/**
 * A 401 means the session expired mid-work. **Clear all draft state** before showing the sign-in
 * form: otherwise a different reviewer signing in on a shared browser would see (and could re-save
 * under their own account) the previous reviewer's cached labels.
 */
function handleAuthError(e: unknown): boolean {
  if (e instanceof ReviewApiError && e.status === 401) {
    resetReviewStore(); // wipes current/versions/loadState/prefetched, sets auth "unknown"
    setStatus({ auth: "out", reviewer: null, error: "your session expired — sign in again" });
    return true;
  }
  return false;
}

/** A save the server refused in a way no retry can fix. */
function isTerminalSaveError(e: unknown): e is ReviewApiError {
  return (
    e instanceof ReviewApiError &&
    e.status >= 400 &&
    e.status < 500 &&
    e.status !== 401 &&
    e.status !== 409 &&
    !isCsrfError(e)
  );
}

type LoadState = "loading" | "ok" | "error";

const initialStatus = (): ReviewStatus => ({
  auth: "unknown",
  reviewer: null,
  saving: false,
  error: null,
  errorKind: null,
  reconciled: null,
});

let current: ReviewState = emptyState();
let status: ReviewStatus = initialStatus();
const versions = new Map<string, number>();
const loadState = new Map<string, LoadState>();
const loadPromises = new Map<string, Promise<boolean>>();
const dirty = new Set<string>();
const pendingDeletes = new Set<string>();
const timers = new Map<string, ReturnType<typeof setTimeout>>();
const retryTimers = new Map<string, ReturnType<typeof setTimeout>>();
const inflight = new Map<string, Promise<void>>();

/**
 * The store's session. Every reset (sign-out, a 401, a different reviewer signing in) bumps it. A
 * request already in flight can't be recalled, so every async path captures the session it started
 * in and drops its result if the session has moved on. Otherwise reviewer A's slow draft load could
 * land in reviewer B's state (and be saved under B's account), or A's stale 401 could wipe B's.
 */
let session = 0;

const listeners = new Set<() => void>();
function subscribe(cb: () => void): () => void {
  listeners.add(cb);
  return () => listeners.delete(cb);
}
function emit(): void {
  for (const l of listeners) l();
}
function snapshot(): ReviewState {
  return current;
}
function statusSnapshot(): ReviewStatus {
  return status;
}
function setStatus(patch: Partial<ReviewStatus>): void {
  status = { ...status, ...patch };
  emit();
}

// Best-effort: persist any debounced edits when the tab is hidden or closed, so up to
// SAVE_DEBOUNCE_MS of typing isn't lost. (The async flush may not finish on a hard close, but it
// starts.)
if (typeof window !== "undefined") {
  const flushOnHide = () => {
    if (dirty.size > 0 || timers.size > 0) void flushReviewSaves();
  };
  window.addEventListener("pagehide", flushOnHide);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flushOnHide();
  });
}

/** Read the shared review state (re-renders on any update). */
export function useReviewState(): ReviewState {
  return useSyncExternalStore(subscribe, snapshot);
}

/** Read auth + save status (loading, saving, errors, reviewer). */
export function useReviewStatus(): ReviewStatus {
  return useSyncExternalStore(subscribe, statusSnapshot);
}

/** Non-hook reads of the state, a sample's version and the status (tests, imperative callers). */
export function peekReviewState(): ReviewState {
  return current;
}
export function peekVersion(sid: string): number {
  return versions.get(sid) ?? 0;
}
export function peekReviewStatus(): ReviewStatus {
  return status;
}
/** Whether a retry timer is armed for a sample (tests: a terminal failure must arm none). */
export function hasPendingRetry(sid: string): boolean {
  return retryTimers.has(sid);
}

// --- saving ---

function scheduleRetry(sid: string): void {
  if (retryTimers.has(sid)) return;
  retryTimers.set(
    sid,
    setTimeout(() => {
      retryTimers.delete(sid);
      if (pendingDeletes.has(sid)) void enqueue(sid, () => persistDelete(sid));
      else if (dirty.has(sid)) runSave(sid);
    }, SAVE_RETRY_MS),
  );
}

/**
 * Serialize operations per sample: a save and a "start over" delete must not race. Chaining them
 * guarantees ordering, so a delete can't clobber a later fresh draft and an in-flight save can't
 * resurrect a deleted one. An op still queued when the session resets never runs.
 */
function enqueue(sid: string, op: () => Promise<void>): Promise<void> {
  const started = session;
  const prev = inflight.get(sid) ?? Promise.resolve();
  const next = prev
    .catch(() => {})
    .then(() => (started === session ? op() : undefined))
    .finally(() => {
      if (inflight.get(sid) === next) inflight.delete(sid);
    });
  inflight.set(sid, next);
  return next;
}

function runSave(sid: string): void {
  void enqueue(sid, () => persistSample(sid));
}

async function persistSample(sid: string): Promise<void> {
  const started = session;
  const stale = () => started !== session;
  const r = current.samples[sid];
  if (!r) {
    dirty.delete(sid);
    return;
  }
  // Never save before we know the server's version. A version-0 PUT for a sample whose initial load
  // FAILED would 409, and the last-write-wins retry would clobber the saved server draft. So resolve
  // the load first; if it fails, keep the edit dirty and retry later. Never save blind.
  if (loadState.get(sid) !== "ok") {
    const ok = await ensureSampleLoaded(sid);
    if (stale()) return;
    if (!ok) {
      dirty.add(sid);
      scheduleRetry(sid);
      if (dirty.size === 0 && pendingDeletes.size === 0) setStatus({ saving: false });
      return;
    }
  }
  dirty.delete(sid);
  const r2 = current.samples[sid];
  if (!r2) return;
  let version = versions.get(sid) ?? 0;
  try {
    let result = await putDraft(sid, r2, version);
    if (stale()) return;
    if (!result.ok) {
      // Conflict: another device advanced this sample. Last-write-wins for the active device: retry
      // once with the server's version (our optimistic edits are preserved, not dropped).
      version = result.conflict.version;
      versions.set(sid, version);
      const retry = await putDraft(sid, current.samples[sid] ?? r2, version);
      if (stale()) return;
      if (retry.ok) {
        result = retry;
        // LWW just overwrote another device's draft. That is the design, but it must not be silent:
        // raise the reconcile notice (it survives the error-clear below; the next edit clears it).
        setStatus({ reconciled: sid, error: null, errorKind: null });
      } else {
        // Still conflicting (a third write raced): adopt the server draft (server-wins) + notice.
        versions.set(sid, retry.conflict.version);
        current = { ...current, samples: { ...current.samples, [sid]: parseSampleReview(retry.conflict.state) } };
        setStatus({ reconciled: sid, error: null, errorKind: null });
        return;
      }
    }
    versions.set(sid, result.version);
    // Clear only error state, NOT `reconciled`: a reconcile notice must survive the follow-up save
    // and stay until the reviewer's next edit.
    setStatus({ error: null, errorKind: null });
  } catch (e) {
    if (stale() || handleAuthError(e)) return;
    if (isTerminalSaveError(e)) {
      // Retrying can't help (e.g. the draft is over the body cap). Keep the labels in memory, arm no
      // retry, and say why. The next edit schedules a fresh save.
      setStatus({ error: e.message, errorKind: "rejected" });
      return;
    }
    // A CSRF 403 means the token is missing or stale: refresh it so the retry can succeed, instead
    // of looping 403s forever.
    if (isCsrfError(e)) {
      await fetchCsrf().catch(() => {});
      if (stale()) return;
    }
    // Keep the optimistic state, leave the sample dirty, and schedule a real retry.
    dirty.add(sid);
    scheduleRetry(sid);
    setStatus({ error: e instanceof Error ? e.message : "save failed", errorKind: "save" });
  } finally {
    if (!stale() && dirty.size === 0 && pendingDeletes.size === 0) setStatus({ saving: false });
  }
}

function scheduleSave(sid: string): void {
  dirty.add(sid);
  setStatus({ saving: true });
  const existing = timers.get(sid);
  if (existing) clearTimeout(existing);
  timers.set(
    sid,
    setTimeout(() => {
      timers.delete(sid);
      runSave(sid);
    }, SAVE_DEBOUNCE_MS),
  );
}

/** Force all pending or failed saves now and await them (navigation, page-hide, logout, tests). */
export async function flushReviewSaves(): Promise<void> {
  for (const [sid, timer] of timers) {
    clearTimeout(timer);
    timers.delete(sid);
    dirty.add(sid);
  }
  // Only force deletes that aren't already queued or in flight (scheduleDelete enqueues at once).
  // This covers a delete waiting on a failed-retry timer without double-running the live one.
  for (const sid of [...pendingDeletes]) if (!inflight.has(sid)) void enqueue(sid, () => persistDelete(sid));
  for (const sid of [...dirty]) runSave(sid);
  await Promise.all([...inflight.values()]);
  if (dirty.size === 0 && pendingDeletes.size === 0) setStatus({ saving: false });
}

/**
 * Apply a pure updater to the shared state, and persist every sample whose entry changed. The pure
 * updaters replace only the touched sample's reference, so a shallow reference diff finds exactly
 * what to save.
 */
export function updateReviewState(fn: (s: ReviewState) => ReviewState): void {
  const prev = current;
  current = fn(prev);
  if (status.reconciled !== null) status = { ...status, reconciled: null }; // a fresh edit clears the notice
  const ids = new Set([...Object.keys(prev.samples), ...Object.keys(current.samples)]);
  for (const sid of ids) {
    const before = prev.samples[sid];
    const after = current.samples[sid];
    if (after === before) continue;
    if (after === undefined) scheduleDelete(sid); // "start over": discard the server draft too
    else scheduleSave(sid);
  }
  emit();
}

// --- delete ("start over") ---

async function persistDelete(sid: string): Promise<void> {
  const started = session;
  const stale = () => started !== session;
  dirty.delete(sid);
  pendingDeletes.delete(sid); // in progress: cleared now, re-added only if it fails (like `dirty`)
  try {
    await deleteDraft(sid);
    if (stale()) return;
    versions.delete(sid);
    loadState.delete(sid);
    setStatus({ error: null, errorKind: null });
  } catch (e) {
    if (stale() || handleAuthError(e)) return;
    if (isTerminalSaveError(e)) {
      // The server refused the delete for good: retrying every few seconds can't change that.
      setStatus({ error: e.message, errorKind: "rejected" });
      return;
    }
    if (isCsrfError(e)) {
      await fetchCsrf().catch(() => {});
      if (stale()) return;
    }
    // A failed delete leaves the server draft; retry so "start over" actually sticks.
    pendingDeletes.add(sid);
    scheduleRetry(sid);
    setStatus({ error: e instanceof Error ? e.message : "delete failed", errorKind: "save" });
  } finally {
    if (!stale() && dirty.size === 0 && pendingDeletes.size === 0) setStatus({ saving: false });
  }
}

function scheduleDelete(sid: string): void {
  pendingDeletes.add(sid);
  // A delete supersedes any queued save for the same sample.
  dirty.delete(sid);
  const timer = timers.get(sid);
  if (timer) {
    clearTimeout(timer);
    timers.delete(sid);
  }
  setStatus({ saving: true });
  void enqueue(sid, () => persistDelete(sid));
}

/**
 * Ensure a sample's draft is loaded from the API. Returns whether the load SUCCEEDED. Pages must not
 * enable editing, and `persistSample` must not save, until it did, or a failed load would let a
 * blank draft overwrite the saved server copy. Idempotent and coalesced; a failed load can retry.
 */
export function ensureSampleLoaded(sid: string): Promise<boolean> {
  if (loadState.get(sid) === "ok") return Promise.resolve(true);
  const existing = loadPromises.get(sid);
  if (existing) return existing;
  loadState.set(sid, "loading");
  const started = session;
  const p = (async (): Promise<boolean> => {
    try {
      const draft = await getDraft(sid);
      if (started !== session) return false; // a load for an earlier session: drop it
      versions.set(sid, draft.version);
      if (draft.state !== null) {
        // Adopt the server draft on the FIRST successful load. If a local entry already exists, the
        // reviewer edited before this load succeeded (e.g. during a load blip): that entry sits on a
        // BLANK base and would overwrite the saved server draft, so adopt the server copy and flag
        // it reconciled. Once loadState is "ok" this branch never runs again, so genuine post-load
        // edits are never clobbered.
        const hadLocal = current.samples[sid] !== undefined;
        current = { ...current, samples: { ...current.samples, [sid]: parseSampleReview(draft.state) } };
        setStatus(hadLocal ? { reconciled: sid, error: null, errorKind: null } : { error: null, errorKind: null });
      } else {
        // The server has no draft: keep any local work (nothing to lose).
        setStatus({ error: null, errorKind: null });
      }
      loadState.set(sid, "ok");
      emit();
      return true;
    } catch (e) {
      if (started !== session || handleAuthError(e)) return false;
      loadState.set(sid, "error");
      setStatus({ error: e instanceof Error ? e.message : "load failed", errorKind: "load" });
      return false;
    }
  })();
  loadPromises.set(sid, p);
  // Registered before any caller's await, so it runs first. It removes only this load's own entry:
  // after a reset, the same sample may already have a newer load in flight. (`p` never rejects.)
  void p.then(() => {
    if (loadPromises.get(sid) === p) loadPromises.delete(sid);
  });
  return p;
}

let prefetched = false;

/**
 * Load ALL of the reviewer's drafts at once (one list call), so a landing page shows real
 * cross-device progress without opening each sample. Idempotent per session.
 */
export async function prefetchDrafts(): Promise<void> {
  if (prefetched) return;
  prefetched = true;
  const started = session;
  try {
    const drafts = await listDrafts();
    if (started !== session) return; // a list for an earlier session: drop it
    let next = current;
    let reconciledSid: string | null = null;
    for (const d of drafts) {
      // A sample already loaded via its own GET is owned by that live path: the reviewer may have
      // edited since. Re-adopting the LIST copy (or even just overwriting `version`) would clobber
      // those post-load edits when the slower LIST resolves after a fast GET. Skip it entirely.
      if (loadState.get(d.sampleId) === "ok") continue;
      versions.set(d.sampleId, d.version);
      loadState.set(d.sampleId, "ok");
      if (d.state !== null) {
        // Same adopt rule as ensureSampleLoaded: a local entry here was authored on a blank base (a
        // load blip) and would overwrite this saved draft, so adopt the server copy and flag it.
        // Marking loadState "ok" without adopting would reopen the overwrite hole.
        const hadLocal = next.samples[d.sampleId] !== undefined;
        next = { ...next, samples: { ...next.samples, [d.sampleId]: parseSampleReview(d.state) } };
        if (hadLocal) reconciledSid = d.sampleId;
      }
    }
    current = next;
    if (reconciledSid) setStatus({ reconciled: reconciledSid });
    emit();
  } catch (e) {
    if (started !== session) return;
    prefetched = false; // allow a retry
    if (!handleAuthError(e)) {
      setStatus({ error: e instanceof Error ? e.message : "couldn't load your drafts", errorKind: "load" });
    }
  }
}

/**
 * Drop the in-memory store and start a new session (does not touch the server). Requests still in
 * flight from the old session are ignored when they resolve.
 */
export function resetReviewStore(): void {
  session += 1;
  current = emptyState();
  status = initialStatus();
  versions.clear();
  loadState.clear();
  loadPromises.clear();
  dirty.clear();
  pendingDeletes.clear();
  prefetched = false;
  for (const t of timers.values()) clearTimeout(t);
  timers.clear();
  for (const t of retryTimers.values()) clearTimeout(t);
  retryTimers.clear();
  inflight.clear();
  emit();
}

// --- auth ---

/** The session an init is running for (null: none). Per session, so a reset re-arms it at once. */
let initFor: number | null = null;

/**
 * Establish the session (call on entering /review): loads the reviewer and a CSRF token. Idempotent:
 * concurrent or repeated calls are coalesced, and a reset re-arms it.
 */
export async function initReview(): Promise<void> {
  if (initFor === session || status.auth !== "unknown") return;
  const started = session;
  initFor = started;
  try {
    await fetchCsrf();
    const reviewer = await apiMe();
    if (started !== session) return;
    setStatus({ auth: reviewer ? "in" : "out", reviewer, error: null });
  } catch (e) {
    if (started !== session) return;
    if (e instanceof ReviewUnavailableError) {
      // No review API at this origin (the static viewer build): not a sign-in problem.
      setStatus({ auth: "unavailable", reviewer: null, error: e.message });
    } else {
      // The service is unreachable or failing. Fail VISIBLY: resolve to signed-out with an error,
      // so the gate shows the sign-in form and a notice, never a permanent spinner.
      setStatus({
        auth: "out",
        reviewer: null,
        error: "couldn't reach the review service — check your connection and try again",
      });
    }
  } finally {
    if (initFor === started) initFor = null;
  }
}

/** Clear any residual draft state if a DIFFERENT reviewer is signing in on this browser. */
function resetIfReviewerChanged(nextId: string): void {
  if (status.reviewer && status.reviewer.id !== nextId) resetReviewStore();
}

export async function loginReview(email: string, password: string): Promise<void> {
  const reviewer = await apiLogin(email, password);
  resetIfReviewerChanged(reviewer.id);
  setStatus({ auth: "in", reviewer, error: null, errorKind: null });
}

export async function signupReview(input: {
  email: string;
  password: string;
  name: string;
  background?: string;
  inviteCode: string;
}): Promise<void> {
  const reviewer = await apiSignup(input);
  resetIfReviewerChanged(reviewer.id);
  setStatus({ auth: "in", reviewer, error: null, errorKind: null });
}

export async function logoutReview(): Promise<void> {
  await flushReviewSaves(); // don't drop debounced edits on the way out
  await apiLogout();
  resetReviewStore();
  setStatus({ auth: "out", reviewer: null });
}

// ---- pure state updaters ---------------------------------------------------------------------

function sampleOf(s: ReviewState, sid: string): SampleReview {
  return s.samples[sid] ?? emptySampleReview();
}

function withSampleReview(s: ReviewState, sid: string, r: SampleReview): ReviewState {
  return { ...s, samples: { ...s.samples, [sid]: r } };
}

/** Set the texts a reviewer chose for a sample. An unchanged choice returns `s` itself (no save). */
export function withTexts(s: ReviewState, sid: string, texts: string[]): ReviewState {
  const r = sampleOf(s, sid);
  if (s.samples[sid] && r.texts.length === texts.length && r.texts.every((t, i) => t === texts[i])) return s;
  return withSampleReview(s, sid, { ...r, texts });
}

export type LabelPatch = Partial<Pick<CellLabel, "outcome" | "defect" | "notes">>;

/**
 * Edit one cell's label. A real change to outcome, defect or notes stamps the label with the current
 * RUBRIC_VERSION and `now`, so each label carries the rubric and time of its last real edit. A patch
 * that changes nothing returns `s` itself: no restamp under a newer rubric, and no save.
 */
export function withLabel(s: ReviewState, sid: string, cellId: string, patch: LabelPatch, now: Date): ReviewState {
  const r = sampleOf(s, sid);
  const before = r.labels[cellId] ?? emptyLabel();
  const outcome = patch.outcome !== undefined ? patch.outcome : before.outcome;
  const defect = patch.defect ?? before.defect;
  const notes = patch.notes ?? before.notes;
  if (outcome === before.outcome && defect === before.defect && notes === before.notes) return s;
  const label: CellLabel = { outcome, defect, notes, rubric_version: RUBRIC_VERSION, labelled_at: now.toISOString() };
  return withSampleReview(s, sid, { ...r, labels: { ...r.labels, [cellId]: label } });
}

/** Drop one sample's review entirely (the reviewer's explicit "start over"). */
export function withoutSample(s: ReviewState, sid: string): ReviewState {
  const rest = { ...s.samples };
  delete rest[sid];
  return { ...s, samples: rest };
}
