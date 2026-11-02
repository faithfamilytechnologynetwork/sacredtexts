// Dev-only run-serving logic for the viewer, extracted from vite.config.ts so it is
// importable and unit-testable against a temp dir (the old inline `serveRuns` closure
// had a hardcoded root and could not be tested). node-only — lives OUTSIDE src/ so a
// stray client import cannot pull fs/path into the browser bundle.
//
// It exposes:
//   listRuns(runsDir)      — the run index: [{id, mtimeMs, generatedAt?}] for each subdir
//                            with a readable summary.json, newest first BY RECENCY (not
//                            mtime alone — see listRuns / recency.ts, Issue #7).
//   resolveRunFile(dir,rel)— confined single-file resolution (realpath + symlink reject).
//   createRunsHandler(dir) — a Connect middleware mounting both at /runs (dev server).
//
// Confinement is canonical-path based (fs.realpathSync), not a lexical startsWith, so a
// symlink under runs/ that escapes the root is rejected; URL decoding is wrapped so a
// malformed-percent-encoding request returns 400 rather than throwing.

import fs from "node:fs";
import path from "node:path";
import type { IncomingMessage, ServerResponse } from "node:http";
// Pure, browser-safe recency helper from src/ — safe to import here (node → src is fine; the
// banned direction is src → this node-only module, which pulls fs into the browser bundle).
import { runRecencyMs } from "../src/lib/recency";

export interface RunIndexEntry {
  id: string;
  mtimeMs: number;
  /** `summary.generated_at`, if the run's summary.json carries a string one — surfaced so
   * the client can order by it (recency, Issue #7) without fetching every summary. */
  generatedAt?: string;
}

/** `generated_at` from a run's summary.json if present as a string, else undefined. Never
 * throws: a missing/unreadable/malformed summary yields undefined (recency then falls back). */
function consider(out: RunIndexEntry[], dir: string, id: string): void {
  const summary = path.join(dir, "summary.json");
  try {
    const ls = fs.lstatSync(summary);
    if (ls.isSymbolicLink() || !ls.isFile()) return;
    fs.accessSync(summary, fs.constants.R_OK);
    out.push({ id, mtimeMs: fs.statSync(dir).mtimeMs, generatedAt: readGeneratedAt(summary) });
  } catch {
    /* missing / unreadable summary.json — skip */
  }
}

function readGeneratedAt(summaryPath: string): string | undefined {
  try {
    const parsed = JSON.parse(fs.readFileSync(summaryPath, "utf8")) as unknown;
    const g = (parsed as { generated_at?: unknown })?.generated_at;
    return typeof g === "string" ? g : undefined;
  } catch {
    return undefined;
  }
}

/** Virtual run that rolls every nested summary under runs/model/base into one
 * leaderboard. Model folders have no summary of their own, so without this the current
 * collects never appear in the run index. */
export const PANEL_RUN_ID = "panel";

const SKIP_TOP = new Set(["paper", "archive", PANEL_RUN_ID]);

interface CountBucket {
  n: number;
  correct: number;
  incorrect: number;
  refused: number;
  f1: number;
  f1w: number;
  f1b: number;
  f1bw: number;
  exact: number;
  exactw: number;
  norm: number;
  normw: number;
  contains: number;
  containsw: number;
}

function emptyBucket(): CountBucket {
  return {
    n: 0, correct: 0, incorrect: 0, refused: 0,
    f1: 0, f1w: 0, f1b: 0, f1bw: 0,
    exact: 0, exactw: 0, norm: 0, normw: 0, contains: 0, containsw: 0,
  };
}

function num(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

function round4(x: number): number {
  return Math.round(x * 10000) / 10000;
}

function addCell(bucket: CountBucket, cell: Record<string, unknown>): void {
  const correct = num(cell.correct);
  const incorrect = num(cell.incorrect);
  const answered = correct + incorrect;
  bucket.n += num(cell.n);
  bucket.correct += correct;
  bucket.incorrect += incorrect;
  bucket.refused += num(cell.refused);
  if (answered <= 0) return;
  if (typeof cell.token_f1 === "number") {
    bucket.f1 += cell.token_f1 * answered;
    bucket.f1w += answered;
  }
  if (typeof cell.token_f1_base === "number") {
    bucket.f1b += cell.token_f1_base * answered;
    bucket.f1bw += answered;
  }
  if (typeof cell.exact === "number") {
    bucket.exact += cell.exact * answered;
    bucket.exactw += answered;
  }
  if (typeof cell.normalized === "number") {
    bucket.norm += cell.normalized * answered;
    bucket.normw += answered;
  }
  if (typeof cell.contains_reference === "number") {
    bucket.contains += cell.contains_reference * answered;
    bucket.containsw += answered;
  }
}

function finishCell(bucket: CountBucket): Record<string, unknown> {
  const answered = bucket.correct + bucket.incorrect;
  const cell: Record<string, unknown> = {
    n: bucket.n,
    accuracy: answered > 0 ? round4(bucket.correct / answered) : null,
    coverage: bucket.n > 0 ? round4(answered / bucket.n) : null,
    correct: bucket.correct,
    incorrect: bucket.incorrect,
    refused: bucket.refused,
    refused_rate: bucket.n > 0 ? round4(bucket.refused / bucket.n) : null,
  };
  if (bucket.f1w > 0) cell.token_f1 = round4(bucket.f1 / bucket.f1w);
  if (bucket.f1bw > 0) cell.token_f1_base = round4(bucket.f1b / bucket.f1bw);
  if (bucket.exactw > 0) cell.exact = round4(bucket.exact / bucket.exactw);
  if (bucket.normw > 0) cell.normalized = round4(bucket.norm / bucket.normw);
  if (bucket.containsw > 0) cell.contains_reference = round4(bucket.contains / bucket.containsw);
  return cell;
}

function mergeCells(
  into: Record<string, CountBucket>,
  cells: Record<string, unknown>,
): void {
  for (const [task, raw] of Object.entries(cells)) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) continue;
    const bucket = into[task] ?? emptyBucket();
    addCell(bucket, raw as Record<string, unknown>);
    into[task] = bucket;
  }
}

/** Nested summary.json files under one model directory (not a summary sitting on the
 * directory itself). Symlinks are skipped. */
export function nestedSummaries(modelDir: string): string[] {
  const out: string[] = [];
  const walk = (dir: string, depth: number) => {
    if (depth > 8) return;
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.isSymbolicLink()) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p, depth + 1);
      else if (e.isFile() && e.name === "summary.json" && depth > 0) out.push(p);
    }
  };
  walk(modelDir, 0);
  return out;
}

function promptKind(summaryPath: string): string | null {
  const parts = summaryPath.split(path.sep);
  if (parts.includes("prompt-native")) return "Native prompt";
  if (parts.includes("prompt-english")) return "English prompt";
  if (parts.includes("english")) return "English text";
  return null;
}

/** Same split as sacredbench.claims.negative_kind. A verify-no is an alphabet check
 * when the donor is another script, and a canon check in the two hard pairs. */
export function negativeKind(language: string | undefined, asked: string | undefined, trueTradition: string | undefined): string {
  if (language === "pa" || language === "pi" || language === "sa" || language === "grc") return "Different script";
  if (asked === "Book of Mormon" && trueTradition === "Encyclicals") return "Book of Mormon shown an encyclical";
  if (asked === "Encyclicals") return "Encyclical shown the Book of Mormon";
  if (asked === "Judaism") return "Talmud shown the Bible";
  if (asked === "Islam") return "Qur'an shown a hadith";
  if (asked === "Christianity" && language === "en") return "NRSV shown the Book of Mormon";
  return "Other same-script negative";
}

function addNegatives(runsDir: string, summaryPath: string, into: Record<string, CountBucket>): void {
  const questions = readJsonl(questionsForSummary(runsDir, summaryPath));
  const byId = new Map<string, Record<string, unknown>>();
  for (const q of questions) if (typeof q.id === "string") byId.set(q.id, q);
  const scores = path.join(path.dirname(summaryPath), "scores.jsonl");
  let text: string;
  try {
    if (fs.lstatSync(scores).isSymbolicLink() || !fs.lstatSync(scores).isFile()) return;
    text = fs.readFileSync(scores, "utf8");
  } catch {
    return;
  }
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    let row: { question_id?: unknown; task?: unknown; metrics?: { outcome?: unknown; expected?: unknown } };
    try {
      row = JSON.parse(line) as typeof row;
    } catch {
      continue;
    }
    if (row.task !== "verify_source" || row.metrics?.expected !== "no" || typeof row.question_id !== "string") continue;
    const q = byId.get(row.question_id);
    const src = (q?.source ?? {}) as Record<string, unknown>;
    const asked = Array.isArray(src.tradition) ? String(src.tradition[0] ?? "") : typeof src.tradition === "string" ? src.tradition : undefined;
    const expected = (q?.expected ?? {}) as Record<string, unknown>;
    const kind = negativeKind(
      typeof src.language === "string" ? src.language : undefined,
      asked,
      typeof expected.true_tradition === "string" ? expected.true_tradition : undefined,
    );
    const bucket = into[kind] ?? emptyBucket();
    bucket.n += 1;
    const outcome = row.metrics?.outcome;
    if (outcome === "correct") bucket.correct += 1;
    else if (outcome === "incorrect") bucket.incorrect += 1;
    else if (outcome === "refused") bucket.refused += 1;
    into[kind] = bucket;
  }
}

function addVerify(summaryPath: string, into: Record<string, Record<"yes" | "no", CountBucket>>): void {
  const scores = path.join(path.dirname(summaryPath), "scores.jsonl");
  let text: string;
  try {
    if (fs.lstatSync(scores).isSymbolicLink() || !fs.lstatSync(scores).isFile()) return;
    text = fs.readFileSync(scores, "utf8");
  } catch {
    return;
  }
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    let row: { model_id?: unknown; task?: unknown; metrics?: { outcome?: unknown; expected?: unknown } };
    try {
      row = JSON.parse(line) as typeof row;
    } catch {
      continue;
    }
    if (row.task !== "verify_source" || typeof row.model_id !== "string") continue;
    const expected = row.metrics?.expected;
    if (expected !== "yes" && expected !== "no") continue;
    const outcome = row.metrics?.outcome;
    const bucket = (into[row.model_id] ??= { yes: emptyBucket(), no: emptyBucket() })[expected];
    bucket.n += 1;
    if (outcome === "correct") bucket.correct += 1;
    else if (outcome === "incorrect") bucket.incorrect += 1;
    else if (outcome === "refused") bucket.refused += 1;
  }
}

function questionsForSummary(runsDir: string, summaryPath: string): string | null {
  const rel = path.relative(runsDir, summaryPath);
  const parts = rel.split(path.sep);
  const base = parts.indexOf("base");
  if (base < 0 || base === parts.length - 1) return null;
  const rest = parts.slice(base + 1, -1);
  const q = path.resolve(runsDir, "..", "items", "for-test", ...rest, "questions.jsonl");
  try {
    if (fs.lstatSync(q).isFile() && !fs.lstatSync(q).isSymbolicLink()) return q;
  } catch {
    return null;
  }
  return null;
}

interface PanelBuild {
  files: string[];
  summary: Record<string, unknown>;
  mtimeMs: number;
}

/** Merge every nested per-file summary under model directories into one summary the
 * viewer already knows how to render: models, by_tradition, usage. Rates are recomputed
 * from summed counts. */
export function buildPanel(runsDir: string): PanelBuild | null {
  let root: string;
  try {
    root = fs.realpathSync(runsDir);
  } catch {
    return null;
  }
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    return null;
  }
  const files: string[] = [];
  for (const e of entries) {
    if (e.isSymbolicLink() || !e.isDirectory() || SKIP_TOP.has(e.name)) continue;
    const dir = path.join(root, e.name);
    if (fs.existsSync(path.join(dir, "summary.json"))) continue;
    files.push(...nestedSummaries(dir));
  }
  if (files.length === 0) return null;

  const models: Record<string, Record<string, CountBucket>> = {};
  const byTradition: Record<string, Record<string, Record<string, CountBucket>>> = {};
  const byPrompt: Record<string, Record<string, Record<string, CountBucket>>> = {};
  const verify: Record<string, Record<"yes" | "no", CountBucket>> = {};
  const negatives: Record<string, CountBucket> = {};
  const usage: Record<string, { calls: number; in: number; out: number }> = {};
  let generatedAt: string | undefined;
  let newestMtime = 0;
  const evaluators = new Set<string>();

  for (const file of files) {
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(fs.readFileSync(file, "utf8")) as Record<string, unknown>;
      newestMtime = Math.max(newestMtime, fs.statSync(path.dirname(file)).mtimeMs);
    } catch {
      continue;
    }
    if (typeof parsed.generated_at === "string" && (!generatedAt || parsed.generated_at > generatedAt)) {
      generatedAt = parsed.generated_at;
    }
    if (Array.isArray(parsed.evaluators)) {
      for (const ev of parsed.evaluators) if (typeof ev === "string") evaluators.add(ev);
    }
    const modelBlock = parsed.models;
    if (modelBlock && typeof modelBlock === "object") {
      for (const [id, cells] of Object.entries(modelBlock as Record<string, unknown>)) {
        if (!cells || typeof cells !== "object") continue;
        models[id] = models[id] ?? {};
        mergeCells(models[id], cells as Record<string, unknown>);
      }
    }
    const tradBlock = parsed.by_tradition;
    if (tradBlock && typeof tradBlock === "object") {
      for (const [id, trads] of Object.entries(tradBlock as Record<string, unknown>)) {
        if (!trads || typeof trads !== "object") continue;
        byTradition[id] = byTradition[id] ?? {};
        for (const [trad, cells] of Object.entries(trads as Record<string, unknown>)) {
          if (!cells || typeof cells !== "object") continue;
          byTradition[id][trad] = byTradition[id][trad] ?? {};
          mergeCells(byTradition[id][trad], cells as Record<string, unknown>);
        }
      }
    }
    const prompt = promptKind(file);
    if (prompt && modelBlock && typeof modelBlock === "object") {
      for (const [id, cells] of Object.entries(modelBlock as Record<string, unknown>)) {
        if (!cells || typeof cells !== "object") continue;
        byPrompt[id] = byPrompt[id] ?? {};
        byPrompt[id][prompt] = byPrompt[id][prompt] ?? {};
        mergeCells(byPrompt[id][prompt], cells as Record<string, unknown>);
      }
    }
    addVerify(file, verify);
    addNegatives(runsDir, file, negatives);
    const per = (parsed.usage as { per_model?: Record<string, { calls?: number; in?: number; out?: number }> } | undefined)?.per_model;
    if (per && typeof per === "object") {
      for (const [id, row] of Object.entries(per)) {
        const acc = usage[id] ?? { calls: 0, in: 0, out: 0 };
        acc.calls += num(row?.calls);
        acc.in += num(row?.in);
        acc.out += num(row?.out);
        usage[id] = acc;
      }
    }
  }

  const finishMap = (src: Record<string, CountBucket>) => {
    const out: Record<string, unknown> = {};
    for (const [k, b] of Object.entries(src)) out[k] = finishCell(b);
    return out;
  };
  const modelsOut: Record<string, unknown> = {};
  for (const [id, cells] of Object.entries(models)) modelsOut[id] = finishMap(cells);
  const tradOut: Record<string, unknown> = {};
  for (const [id, trads] of Object.entries(byTradition)) {
    const per: Record<string, unknown> = {};
    for (const [trad, cells] of Object.entries(trads)) per[trad] = finishMap(cells);
    tradOut[id] = per;
  }
  const promptOut: Record<string, unknown> = {};
  for (const [id, kinds] of Object.entries(byPrompt)) {
    const per: Record<string, unknown> = {};
    for (const [kind, cells] of Object.entries(kinds)) per[kind] = finishMap(cells);
    promptOut[id] = per;
  }
  const verifyOut: Record<string, unknown> = {};
  for (const [id, sides] of Object.entries(verify)) {
    const per: Record<string, unknown> = {};
    for (const side of ["yes", "no"] as const) {
      if (sides[side]) per[side] = finishCell(sides[side]);
    }
    if (Object.keys(per).length > 0) verifyOut[id] = per;
  }
  const total = { calls: 0, in: 0, out: 0 };
  for (const row of Object.values(usage)) {
    total.calls += row.calls;
    total.in += row.in;
    total.out += row.out;
  }
  const summary: Record<string, unknown> = {
    models: modelsOut,
    by_tradition: tradOut,
    by_prompt: promptOut,
    verify: verifyOut,
    verify_negative: finishMap(negatives),
    usage: { per_model: usage, total },
    evaluators: [...evaluators],
    generated_at: generatedAt,
    files: files.length,
  };
  return { files, summary, mtimeMs: newestMtime };
}

export interface GapItem {
  id: string;
  task: string;
  tradition: string;
  citation: string;
}

export interface GapFile {
  model: string;
  file: string;
  questions: number;
  saved: number;
  /** Question-file rows with no answer. Present only when the file has no summary, so a
   * finished --head run is not listed as a failure. */
  missing: GapItem[];
  /** Saved rows whose answer text is empty. */
  empty: GapItem[];
}

/** Unsaved questions on an unfinished file, and saved answers that are empty. */
export function collectGaps(runsDir: string): GapFile[] {
  let root: string;
  try {
    root = fs.realpathSync(runsDir);
  } catch {
    return [];
  }
  const out: GapFile[] = [];
  const walk = (dir: string) => {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.isSymbolicLink()) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (dir === root && SKIP_TOP.has(e.name)) continue;
        walk(p);
      }
    }
    const answersPath = path.join(dir, "answers.jsonl");
    let answersStat: fs.Stats;
    try {
      answersStat = fs.lstatSync(answersPath);
    } catch {
      return;
    }
    if (answersStat.isSymbolicLink() || !answersStat.isFile()) return;
    const rel = path.relative(root, dir);
    const model = rel.split(path.sep)[0];
    if (!model || SKIP_TOP.has(model)) return;
    const questionsPath = questionsForSummary(runsDir, path.join(dir, "summary.json"));
    const roster = readJsonl(questionsPath);
    const answers = readJsonl(answersPath);
    const savedIds = new Set(answers.map((r) => String(r.question_id ?? "")));
    let summaryExists = false;
    try {
      const st = fs.lstatSync(path.join(dir, "summary.json"));
      summaryExists = st.isFile() && !st.isSymbolicLink();
    } catch {
      summaryExists = false;
    }
    const missing: GapItem[] = [];
    if (!summaryExists) {
      for (const q of roster) {
        const id = String(q.id ?? "");
        if (!id || savedIds.has(id)) continue;
        missing.push(itemOf(q, id));
        if (missing.length >= 40) break;
      }
    }
    const empty: GapItem[] = [];
    for (const row of answers) {
      const text = typeof row.answer === "string" ? row.answer.trim() : "";
      if (text) continue;
      const id = String(row.question_id ?? "");
      const q = roster.find((r) => String(r.id ?? "") === id) ?? row;
      empty.push(itemOf(q, id));
      if (empty.length >= 40) break;
    }
    if (missing.length === 0 && empty.length === 0) return;
    out.push({
      model,
      file: rel,
      questions: roster.length,
      saved: answers.length,
      missing,
      empty,
    });
  };
  walk(root);
  out.sort((a, b) => (a.model < b.model ? -1 : a.model > b.model ? 1 : a.file < b.file ? -1 : 1));
  return out;
}

function itemOf(row: Record<string, unknown>, id: string): GapItem {
  const src = (row.source ?? (row.question as { source?: Record<string, unknown> } | undefined)?.source ?? {}) as Record<string, unknown>;
  const trad = Array.isArray(src.tradition) ? String(src.tradition[0] ?? "") : String(src.tradition ?? "");
  return {
    id,
    task: String(row.task ?? ""),
    tradition: trad,
    citation: String(src.citation ?? ""),
  };
}

function readJsonl(file: string | null): Record<string, unknown>[] {
  if (!file) return [];
  let text: string;
  try {
    if (fs.lstatSync(file).isSymbolicLink() || !fs.lstatSync(file).isFile()) return [];
    text = fs.readFileSync(file, "utf8");
  } catch {
    return [];
  }
  const rows: Record<string, unknown>[] = [];
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    try {
      const parsed = JSON.parse(line) as unknown;
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) rows.push(parsed as Record<string, unknown>);
    } catch {
      /* a broken line is skipped; the gap is the missing id */
    }
  }
  return rows;
}

function panelQuestions(runsDir: string, files: string[]): string {
  const seen = new Set<string>();
  const lines: string[] = [];
  for (const file of files) {
    const q = questionsForSummary(runsDir, file);
    if (!q || seen.has(q)) continue;
    seen.add(q);
    let text = "";
    try {
      text = fs.readFileSync(q, "utf8");
    } catch {
      continue;
    }
    for (const line of text.split("\n")) {
      if (line.trim()) lines.push(line);
    }
  }
  return lines.length ? `${lines.join("\n")}\n` : "";
}

function panelJsonl(files: string[], name: string): string {
  const chunks: string[] = [];
  for (const file of files) {
    const sibling = path.join(path.dirname(file), name);
    try {
      if (fs.lstatSync(sibling).isSymbolicLink() || !fs.lstatSync(sibling).isFile()) continue;
      const text = fs.readFileSync(sibling, "utf8").trim();
      if (text) chunks.push(text);
    } catch {
      /* a summary without its sibling is still a scored file */
    }
  }
  return chunks.length ? `${chunks.join("\n")}\n` : "";
}

/** Immediate subdirectories of `runsDir` that contain a readable `summary.json`, newest
 * first. Ordering is by recency (`summary.generated_at` → run-id date → dir mtime, Issue #7;
 * id asc as a stable tiebreak), NOT mtime alone, which collapses in a fresh clone. A
 * nonexistent root returns []. */
export function listRuns(runsDir: string): RunIndexEntry[] {
  let root: string;
  try {
    root = fs.realpathSync(runsDir);
  } catch {
    return []; // runs/ does not exist yet — the empty state, not an error.
  }
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    return [];
  }
  const out: RunIndexEntry[] = [];
  for (const e of entries) {
    // Do not serve symlinked entries at all (the binding requirement rejects symlink
    // traversal, not only escaping ones); a symlinked run dir is intentionally skipped.
    if (e.isSymbolicLink() || !e.isDirectory()) continue;
    const dir = path.join(root, e.name);
    // Dated evidence lives one level down. A folder named archive with no
    // summary of its own contributes each child that has one, id archive/<name>.
    if (e.name === "archive") {
      let nested: fs.Dirent[];
      try {
        nested = fs.readdirSync(dir, { withFileTypes: true });
      } catch {
        continue;
      }
      for (const child of nested) {
        if (child.isSymbolicLink() || !child.isDirectory()) continue;
        consider(out, path.join(dir, child.name), `archive/${child.name}`);
      }
      continue;
    }
    consider(out, dir, e.name);
  }
  out.sort(
    (a, b) =>
      runRecencyMs({ generatedAt: b.generatedAt, runId: b.id, mtimeMs: b.mtimeMs }) -
        runRecencyMs({ generatedAt: a.generatedAt, runId: a.id, mtimeMs: a.mtimeMs }) ||
      (a.id < b.id ? -1 : a.id > b.id ? 1 : 0),
  );
  const panel = buildPanel(runsDir);
  if (panel && !out.some((r) => r.id === PANEL_RUN_ID)) {
    out.push({
      id: PANEL_RUN_ID,
      mtimeMs: panel.mtimeMs,
      generatedAt: typeof panel.summary.generated_at === "string" ? panel.summary.generated_at : undefined,
    });
    out.sort(
      (a, b) =>
        runRecencyMs({ generatedAt: b.generatedAt, runId: b.id, mtimeMs: b.mtimeMs }) -
          runRecencyMs({ generatedAt: a.generatedAt, runId: a.id, mtimeMs: a.mtimeMs }) ||
        (a.id < b.id ? -1 : a.id > b.id ? 1 : 0),
    );
  }
  return out;
}

/** Resolve a (already-decoded) relative path within `runsDir` to a confined regular file,
 * or null. Rejects parent traversal AND any path component that is a symlink (so a symlink
 * is never followed, in-root or escaping), then confirms containment and that the target
 * is a regular file. */
export function resolveRunFile(runsDir: string, rel: string): string | null {
  let root: string;
  try {
    root = fs.realpathSync(runsDir); // root itself is canonical (no symlink components)
  } catch {
    return null;
  }
  const parts = rel.split(/[/\\]+/).filter((p) => p.length > 0 && p !== ".");
  let cur = root;
  for (const part of parts) {
    if (part === "..") return null; // no parent traversal
    cur = path.join(cur, part);
    try {
      if (fs.lstatSync(cur).isSymbolicLink()) return null; // reject any symlink component
    } catch {
      return null; // component does not exist
    }
  }
  if (cur !== root && !cur.startsWith(root + path.sep)) return null; // containment backstop
  try {
    if (!fs.statSync(cur).isFile()) return null;
  } catch {
    return null;
  }
  return cur;
}

type ReqLike = Pick<IncomingMessage, "url">;
type ResLike = Pick<ServerResponse, "statusCode" | "setHeader" | "end">;

/** A Connect middleware for the dev server. Mounted at `/runs`, Connect STRIPS the mount
 * prefix, so a collection request arrives as `req.url === "/"` or `"/_index"` and a file
 * request as `"/<id>/summary.json"`. */
export function createRunsHandler(runsDir: string) {
  return (req: ReqLike, res: ResLike): void => {
    const rawPath = (req.url ?? "").split("?")[0] ?? "";
    let decoded: string;
    try {
      decoded = decodeURIComponent(rawPath);
    } catch {
      res.statusCode = 400;
      res.end("bad request");
      return;
    }

    // Collection request → the run index as JSON.
    if (decoded === "/_gaps") {
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify(collectGaps(runsDir)));
      return;
    }
    if (decoded === "" || decoded === "/" || decoded === "/_index") {
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify(listRuns(runsDir)));
      return;
    }

    // Single-file request, confined.
    const rel = decoded.replace(/^\/+/, "");
    if (rel.startsWith(`${PANEL_RUN_ID}/`)) {
      const panel = buildPanel(runsDir);
      if (!panel) {
        res.statusCode = 404;
        res.end("not found");
        return;
      }
      const name = rel.slice(PANEL_RUN_ID.length + 1);
      if (name === "summary.json") {
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify(panel.summary));
        return;
      }
      if (name === "scores.jsonl" || name === "answers.jsonl") {
        res.setHeader("Content-Type", "text/plain");
        res.end(panelJsonl(panel.files, name));
        return;
      }
      if (name === "questions.jsonl") {
        res.setHeader("Content-Type", "text/plain");
        res.end(panelQuestions(runsDir, panel.files));
        return;
      }
      res.statusCode = 404;
      res.end("not found");
      return;
    }
    const file = resolveRunFile(runsDir, rel);
    if (!file) {
      res.statusCode = 404;
      res.end("not found");
      return;
    }
    let body: Buffer;
    try {
      body = fs.readFileSync(file);
    } catch {
      res.statusCode = 500; // confined + a regular file, but reading still failed
      res.end("read error");
      return;
    }
    res.setHeader("Content-Type", file.endsWith(".json") ? "application/json" : "text/plain");
    res.end(body);
  };
}
