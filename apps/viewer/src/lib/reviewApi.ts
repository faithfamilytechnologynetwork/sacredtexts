// Client for the review service (apps/api), ported from multibench's reviewApi. The review UI and
// the API share one origin (Spec 154: one Hono service serves both), so requests use same-origin
// paths and credentials. Mutations echo the CSRF token in the X-CSRF-Token header; the token comes
// from the login/signup bodies and GET /api/auth/csrf, as in multibench. `fetch` is injectable so
// tests drive a fake API without a live server.
//
// Two failure classes are told apart here, because the pages must show different things:
//   • ReviewUnavailableError: a non-JSON answer from a non-5xx response. There is no review API at
//     this origin, as on the static Cloudflare Pages build, which answers /api/* with its
//     index.html. That is "review service unavailable", never "signed out".
//   • ReviewApiError: the review API answered with an error status (its JSON `error` is the
//     message), or a 413 from it or any proxy in front of it.
//
// The API's submission routes have no caller here: the reviewer's output is the gold-set download.

import { parseSample, type ReviewSample } from "./reviewSample";

export type FetchImpl = typeof fetch;
let fetchImpl: FetchImpl = (...args) => fetch(...args);
/** Test seam: swap the fetch used by every call. */
export function setReviewFetch(impl: FetchImpl): void {
  fetchImpl = impl;
}

let csrfToken: string | null = null;

/**
 * The byte cap on a draft save, mirroring `REVIEW_BODY_MAX_BYTES` in apps/api/src/routes/review.ts
 * (a test pins the two equal). `putDraft` measures its body against it before sending.
 */
export const REVIEW_BODY_MAX_BYTES = 8 * 1024 * 1024;
export const TOO_LARGE_MESSAGE = "this change is too large to save";
export const UNAVAILABLE_MESSAGE = "review service unavailable";

export class ReviewApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ReviewApiError";
  }
}

export class ReviewUnavailableError extends Error {
  constructor() {
    super(UNAVAILABLE_MESSAGE);
    this.name = "ReviewUnavailableError";
  }
}

/** A 403 from the API's double-submit check (`{error: "csrf"}`): a fresh token can fix it. */
export function isCsrfError(e: unknown): boolean {
  return e instanceof ReviewApiError && e.status === 403 && e.message === "csrf";
}

function isJsonResponse(res: Response): boolean {
  const essence = (res.headers.get("content-type") ?? "").split(";")[0]?.trim().toLowerCase();
  return essence === "application/json";
}

async function readJson(res: Response): Promise<any> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

async function call(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const method = init.method ?? "GET";
  if (init.body !== undefined) headers.set("Content-Type", "application/json");
  if (method !== "GET" && method !== "HEAD" && csrfToken) headers.set("X-CSRF-Token", csrfToken);
  const res = await fetchImpl(path, { ...init, headers, credentials: "same-origin" });
  // The API's own 413 is plain text (hono's bodyLimit), and so is a proxy's: judge it by status.
  if (res.status === 413) throw new ReviewApiError(413, TOO_LARGE_MESSAGE);
  if (res.status >= 500) {
    const json = isJsonResponse(res) ? await readJson(res) : null;
    throw new ReviewApiError(res.status, json?.error ?? "review service error");
  }
  if (!isJsonResponse(res)) throw new ReviewUnavailableError();
  return res;
}

export interface Reviewer {
  id: string;
  email: string;
  name: string;
  background?: string | null;
}

/** Fetch (and cache) a CSRF token so subsequent mutations can echo it. */
export async function fetchCsrf(): Promise<void> {
  const res = await call("/api/auth/csrf");
  if (res.ok) csrfToken = (await readJson(res))?.csrfToken ?? null;
}

/** The signed-in reviewer, or null if there is no valid session. Throws when the service fails. */
export async function me(): Promise<Reviewer | null> {
  const res = await call("/api/auth/me");
  if (res.status === 200) return (await readJson(res))?.reviewer ?? null;
  return null; // 401 / not signed in
}

async function authPost(path: string, body: unknown): Promise<Reviewer> {
  const res = await call(path, { method: "POST", body: JSON.stringify(body) });
  const json = await readJson(res);
  if (!res.ok) throw new ReviewApiError(res.status, json?.error ?? `request failed (${res.status})`);
  csrfToken = json?.csrfToken ?? csrfToken;
  return json.reviewer;
}

export function login(email: string, password: string): Promise<Reviewer> {
  return authPost("/api/auth/login", { email, password });
}

export function signup(input: {
  email: string;
  password: string;
  name: string;
  background?: string;
  inviteCode: string;
}): Promise<Reviewer> {
  return authPost("/api/auth/signup", input);
}

/**
 * Sign out. A refusal throws: a stale CSRF token's 403 (`isCsrfError`, which a fresh token fixes) or
 * any other non-2xx. The server session and its cookie are still live after a refusal, so the caller
 * must never treat it as signed out.
 */
export async function logout(): Promise<void> {
  const res = await call("/api/auth/logout", { method: "POST" });
  if (!res.ok) throw new ReviewApiError(res.status, (await readJson(res))?.error ?? "sign-out failed");
  csrfToken = null;
}

/** The active review sample, strictly parsed (a bad file throws a SampleFormatError). */
export async function getSample(): Promise<ReviewSample> {
  const res = await call("/api/sample");
  if (res.status === 401) throw new ReviewApiError(401, "unauthorized");
  const json = await readJson(res);
  if (!res.ok) throw new ReviewApiError(res.status, json?.error ?? "sample load failed");
  return parseSample(json);
}

export interface DraftEnvelope {
  /** The stored SampleReview shape (opaque here; the store's tolerant zod parses it). */
  state: unknown;
  version: number;
}

/** All of the reviewer's drafts (for cross-device progress without opening each sample). */
export async function listDrafts(): Promise<Array<{ sampleId: string } & DraftEnvelope>> {
  const res = await call("/api/review");
  if (res.status === 401) throw new ReviewApiError(401, "unauthorized");
  const json = await readJson(res);
  if (!res.ok) throw new ReviewApiError(res.status, json?.error ?? "list failed");
  return (json?.drafts ?? []).map((d: any) => ({
    sampleId: d.sampleId,
    state: d.state ?? null,
    version: d.version ?? 0,
  }));
}

/** Discard a sample's draft ("start over"). Idempotent. */
export async function deleteDraft(sampleId: string): Promise<void> {
  const res = await call(`/api/review/${encodeURIComponent(sampleId)}`, { method: "DELETE" });
  if (res.status === 401) throw new ReviewApiError(401, "unauthorized");
  if (!res.ok) throw new ReviewApiError(res.status, (await readJson(res))?.error ?? "delete failed");
}

/** Load a sample's draft. Absent → {state: null, version: 0}. */
export async function getDraft(sampleId: string): Promise<DraftEnvelope> {
  const res = await call(`/api/review/${encodeURIComponent(sampleId)}`);
  if (res.status === 401) throw new ReviewApiError(401, "unauthorized");
  const json = await readJson(res);
  if (!res.ok) throw new ReviewApiError(res.status, json?.error ?? "load failed");
  return { state: json?.state ?? null, version: json?.version ?? 0 };
}

export type PutDraftResult = { ok: true; version: number } | { ok: false; conflict: DraftEnvelope };

/**
 * Save a sample's draft with optimistic concurrency. A 409 returns the current server draft. A body
 * over the API's byte cap is refused here, before sending, with the same 413 error the API returns.
 */
export async function putDraft(sampleId: string, state: unknown, version: number): Promise<PutDraftResult> {
  const body = JSON.stringify({ state, version });
  if (new TextEncoder().encode(body).length > REVIEW_BODY_MAX_BYTES) {
    throw new ReviewApiError(413, TOO_LARGE_MESSAGE);
  }
  const res = await call(`/api/review/${encodeURIComponent(sampleId)}`, { method: "PUT", body });
  const json = await readJson(res);
  if (res.status === 409) {
    return { ok: false, conflict: { state: json?.state ?? null, version: json?.version ?? 0 } };
  }
  if (!res.ok) throw new ReviewApiError(res.status, json?.error ?? "save failed");
  return { ok: true, version: json.version };
}
