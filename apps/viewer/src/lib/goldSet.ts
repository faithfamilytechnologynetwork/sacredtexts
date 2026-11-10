// The gold-set download (Spec 154): a reviewer's labels as JSONL, one row per labelled cell, read
// by `review-compare`. Each row carries everything needed to re-score its cell (task, prompt,
// expected, answer, source), the verdict the matcher showed (`shown`) and the human `label`, so it
// doesn't depend on any one matcher version.
//
// The bytes are canonical and match `review_compare.dumps_gold_rows` exactly (pinned by the shared
// fixtures/review_gold_set.jsonl): rows sorted by cell id, one compact JSON object per line, keys
// sorted by code point at every level, non-ASCII unescaped. The builder reads no clock (each row's
// `labelled_at` is its label's own stamp), so two downloads of unchanged labels are byte-identical.

import type { CellLabel } from "./review";
import type { ReviewSample, SampleCell } from "./reviewSample";

export const GOLD_FORMAT = 1;

/** One gold-set row (`review_compare.GOLD_KEYS`). */
export interface GoldRow {
  format: typeof GOLD_FORMAT;
  sample_id: string;
  cell_id: string;
  run: string;
  model_id: string;
  question_id: string;
  scores_path: string;
  task: string;
  text: string;
  prompt: string;
  expected: Record<string, unknown>;
  answer: string;
  source: Record<string, unknown>;
  shown: { outcome: string; metrics: Record<string, unknown>; grader_path: string };
  label: { outcome: string; defect: boolean; notes: string };
  rubric_version: string;
  reviewer_id: string;
  labelled_at: string;
}

/** Labels that can't be written as a gold set. */
export class GoldSetError extends Error {
  override name = "GoldSetError";
}

/** Order strings by Unicode code point, as Python's `sorted` does (JS `<` compares UTF-16 units). */
export function compareCodePoints(a: string, b: string): number {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    const x = a.codePointAt(i)!;
    const y = b.codePointAt(i)!;
    if (x !== y) return x - y;
    if (x > 0xffff) i++; // the same astral character: skip its low surrogate
  }
  return a.length - b.length;
}

/** JSON with object keys sorted by code point at every level (Python's `sort_keys=True`). */
function canonicalJson(value: unknown): string {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new GoldSetError(`cannot write the number ${value} to a gold set`);
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    const keys = Object.keys(record).sort(compareCodePoints);
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(record[k])}`).join(",")}}`;
  }
  throw new GoldSetError(`cannot write a ${typeof value} to a gold set`);
}

function goldRow(sampleId: string, cell: SampleCell, label: CellLabel, outcome: string, reviewerId: string): GoldRow {
  return {
    format: GOLD_FORMAT,
    sample_id: sampleId,
    cell_id: cell.cell_id,
    run: cell.run,
    model_id: cell.model_id,
    question_id: cell.question_id,
    scores_path: cell.scores_path,
    task: cell.task,
    text: cell.text,
    prompt: cell.prompt,
    expected: cell.expected,
    answer: cell.answer,
    source: cell.source,
    shown: { outcome: cell.outcome, metrics: cell.metrics, grader_path: cell.grader_path },
    label: { outcome, defect: label.defect, notes: label.notes },
    rubric_version: label.rubric_version,
    reviewer_id: reviewerId,
    labelled_at: label.labelled_at,
  };
}

/**
 * The gold rows for a reviewer's labels on a sample, sorted by cell id. Every label with an outcome
 * becomes a row, whether or not its text is still among the chosen ones. A label without an outcome
 * is not a judgement yet and is left out. A label for a cell the sample doesn't hold, or one missing
 * its rubric version or time, throws: the file would not be one `review-compare` accepts.
 */
export function goldRows(
  sample: ReviewSample,
  labels: Readonly<Record<string, CellLabel>>,
  reviewerId: string,
): GoldRow[] {
  if (reviewerId === "") throw new GoldSetError("a gold set needs the reviewer's account id");
  const cells = new Map(sample.cells.map((c) => [c.cell_id, c]));
  const rows: GoldRow[] = [];
  for (const [cellId, label] of Object.entries(labels)) {
    if (label.outcome === null) continue;
    const cell = cells.get(cellId);
    if (!cell) throw new GoldSetError(`a label names cell ${cellId}, which is not in sample ${sample.sample_id}`);
    if (label.rubric_version === "" || label.labelled_at === "") {
      throw new GoldSetError(`the label on ${cellId} has lost its rubric version or time; edit it to restamp it`);
    }
    rows.push(goldRow(sample.sample_id, cell, label, label.outcome, reviewerId));
  }
  return rows.sort((a, b) => compareCodePoints(a.cell_id, b.cell_id));
}

/** The gold-set file's text: one canonical JSON row per line, each ending in a newline. */
export function buildGoldSet(
  sample: ReviewSample,
  labels: Readonly<Record<string, CellLabel>>,
  reviewerId: string,
): string {
  return goldRows(sample, labels, reviewerId)
    .map((row) => `${canonicalJson(row)}\n`)
    .join("");
}

/** The download's file name: the sample id, never a clock or a cell id. */
export function goldSetFileName(sampleId: string): string {
  return `gold-${sampleId}.jsonl`;
}
