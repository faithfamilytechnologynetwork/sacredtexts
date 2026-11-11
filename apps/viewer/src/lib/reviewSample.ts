// The review sample (Spec 154): the committed, seeded draw of scored cells that reviewers label.
// `pipelines/sacredbench/review_sample.py` writes it and `GET /api/sample` serves its bytes. This
// module parses it strictly (a bad file fails loudly; it never degrades), derives a reviewer's
// pass from the texts they chose, counts progress, and adapts a cell to the explorer's
// QuestionResult so the review pages render cells exactly as the error explorer does.

import type { CellLabel } from "./review";
import { joinResults, type QuestionResult, type ScoreMetrics } from "./localResults";

/** The sample format this viewer reads (`review_sample.FORMAT`). */
export const SAMPLE_FORMAT = 1;
export const SAMPLE_TASKS = ["retrieve_quote", "complete_unit", "cite_passage", "verify_source"] as const;
export type SampleTask = (typeof SAMPLE_TASKS)[number];
/** The matcher's outcomes (`review_sample.OUTCOMES`). */
export const MATCHER_OUTCOMES = ["correct", "incorrect", "refused"] as const;
export type MatcherOutcome = (typeof MATCHER_OUTCOMES)[number];

export interface SampleText {
  /** The edition folder, e.g. `islam/native`. */
  id: string;
  /** The human label, e.g. "The Qur'an — Uthmani (QUL)". */
  label: string;
  /** How many of the sample's cells come from this text. */
  drawn: number;
}

export interface SampleStratum {
  outcome: MatcherOutcome;
  task: SampleTask;
  text: string;
  population: number;
  drawn: number;
}

/** The question's provenance, verbatim from the run. The fields the review pages read are typed. */
export interface CellSource {
  tradition: string[];
  language: string;
  citation: string;
  [k: string]: unknown;
}

export interface SampleCell {
  /** `<run>:<model_id>:<question_id>`. */
  cell_id: string;
  run: string;
  model_id: string;
  question_id: string;
  /** Repo-relative path of the cell's `scores.jsonl`. */
  scores_path: string;
  task: SampleTask;
  text: string;
  prompt: string;
  /** The question's expected dict, verbatim. */
  expected: Record<string, unknown>;
  answer: string;
  source: CellSource;
  /** The matcher's recorded metrics, verbatim (`outcome` plus submetrics). */
  metrics: Record<string, unknown>;
  /** The matcher's verdict. */
  outcome: MatcherOutcome;
  /** Which grader gave the verdict (`exact` / `normalized` / `contained` / `none` / `citation` / `verdict`). */
  grader_path: string;
}

export interface ReviewSample {
  format: typeof SAMPLE_FORMAT;
  sample_id: string;
  source_run: string;
  seed: string;
  per_stratum: number;
  /** Sorted by id. */
  texts: SampleText[];
  strata: SampleStratum[];
  /** In sample order: the order every pass walks. */
  cells: SampleCell[];
}

/** A sample that isn't in the format this viewer reads. */
export class SampleFormatError extends Error {
  override name = "SampleFormatError";
}

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === "object" && v !== null && !Array.isArray(v);

function fail(message: string): never {
  throw new SampleFormatError(`review sample: ${message}`);
}

function requireString(obj: Record<string, unknown>, key: string, where: string): string {
  const v = obj[key];
  if (typeof v !== "string") fail(`${where}: '${key}' must be a string`);
  return v;
}

function requireCount(obj: Record<string, unknown>, key: string, where: string): number {
  const v = obj[key];
  if (typeof v !== "number" || !Number.isInteger(v) || v < 0) fail(`${where}: '${key}' must be a count`);
  return v;
}

function requireRecord(obj: Record<string, unknown>, key: string, where: string): Record<string, unknown> {
  const v = obj[key];
  if (!isRecord(v)) fail(`${where}: '${key}' must be an object`);
  return v;
}

function requireOneOf<T extends string>(obj: Record<string, unknown>, key: string, allowed: readonly T[], where: string): T {
  const v = obj[key];
  if (typeof v !== "string" || !(allowed as readonly string[]).includes(v)) {
    fail(`${where}: unknown ${key} ${JSON.stringify(v)}`);
  }
  return v as T;
}

function requireList(obj: Record<string, unknown>, key: string): Record<string, unknown>[] {
  const v = obj[key];
  if (!Array.isArray(v) || !v.every(isRecord)) fail(`'${key}' must be a list of objects`);
  return v;
}

function parseCell(raw: Record<string, unknown>, textIds: Set<string>): SampleCell {
  const where = `cell ${JSON.stringify(raw.cell_id)}`;
  const cell_id = requireString(raw, "cell_id", where);
  const run = requireString(raw, "run", where);
  const model_id = requireString(raw, "model_id", where);
  const question_id = requireString(raw, "question_id", where);
  if (cell_id !== `${run}:${model_id}:${question_id}`) fail(`${where}: cell_id is not <run>:<model_id>:<question_id>`);
  const text = requireString(raw, "text", where);
  if (!textIds.has(text)) fail(`${where}: names unknown text ${JSON.stringify(text)}`);
  const source = requireRecord(raw, "source", where);
  const tradition = source.tradition;
  if (!Array.isArray(tradition) || !tradition.every((t) => typeof t === "string")) {
    fail(`${where}: 'source.tradition' must be a list of strings`);
  }
  requireString(source, "language", `${where} source`);
  requireString(source, "citation", `${where} source`);
  return {
    cell_id,
    run,
    model_id,
    question_id,
    scores_path: requireString(raw, "scores_path", where),
    task: requireOneOf(raw, "task", SAMPLE_TASKS, where),
    text,
    prompt: requireString(raw, "prompt", where),
    expected: requireRecord(raw, "expected", where),
    answer: requireString(raw, "answer", where),
    source: source as CellSource,
    metrics: requireRecord(raw, "metrics", where),
    outcome: requireOneOf(raw, "outcome", MATCHER_OUTCOMES, where),
    grader_path: requireString(raw, "grader_path", where),
  };
}

/**
 * Parse a sample strictly. Every check `review_sample.load_sample` makes is made here too, plus the
 * types of the fields the review pages read. Anything else throws a `SampleFormatError`.
 */
export function parseSample(value: unknown): ReviewSample {
  if (!isRecord(value)) fail("a sample is a JSON object");
  if (value.format !== SAMPLE_FORMAT) fail(`unsupported format ${JSON.stringify(value.format)}`);
  const sample_id = requireString(value, "sample_id", "sample");
  if (sample_id === "") fail("'sample_id' is empty");

  const texts = requireList(value, "texts").map((t, i) => ({
    id: requireString(t, "id", `text ${i}`),
    label: requireString(t, "label", `text ${i}`),
    drawn: requireCount(t, "drawn", `text ${i}`),
  }));
  const textIds = new Set(texts.map((t) => t.id));
  if (textIds.size !== texts.length) fail("duplicate text id");

  const strata = requireList(value, "strata").map((s, i) => ({
    outcome: requireOneOf(s, "outcome", MATCHER_OUTCOMES, `stratum ${i}`),
    task: requireOneOf(s, "task", SAMPLE_TASKS, `stratum ${i}`),
    text: requireString(s, "text", `stratum ${i}`),
    population: requireCount(s, "population", `stratum ${i}`),
    drawn: requireCount(s, "drawn", `stratum ${i}`),
  }));

  const seen = new Set<string>();
  const cells = requireList(value, "cells").map((raw) => {
    const cell = parseCell(raw, textIds);
    if (seen.has(cell.cell_id)) fail(`duplicate cell ${cell.cell_id}`);
    seen.add(cell.cell_id);
    return cell;
  });

  return {
    format: SAMPLE_FORMAT,
    sample_id,
    source_run: requireString(value, "source_run", "sample"),
    seed: requireString(value, "seed", "sample"),
    per_stratum: requireCount(value, "per_stratum", "sample"),
    texts,
    strata,
    cells,
  };
}

/** A reviewer's pass: the sample's cells from the chosen texts, in sample order. */
export function passCells(sample: ReviewSample, texts: readonly string[]): SampleCell[] {
  const chosen = new Set(texts);
  return sample.cells.filter((c) => chosen.has(c.text));
}

export interface ProgressCount {
  /** Cells in the pass that carry a human outcome. */
  labelled: number;
  /** Cells in the pass. */
  inPass: number;
}

export interface TextProgress extends ProgressCount {
  text: string;
  label: string;
}

export interface PassProgress {
  /** One entry per chosen text, in the sample's text order. */
  texts: TextProgress[];
  overall: ProgressCount;
}

/** Labelled / in pass, per chosen text and overall. A label counts once it has an outcome. */
export function progressByText(
  sample: ReviewSample,
  texts: readonly string[],
  labels: Readonly<Record<string, CellLabel>>,
): PassProgress {
  const counts = new Map<string, ProgressCount>();
  for (const t of sample.texts) if (texts.includes(t.id)) counts.set(t.id, { labelled: 0, inPass: 0 });
  for (const cell of sample.cells) {
    const count = counts.get(cell.text);
    if (!count) continue;
    count.inPass += 1;
    if (labels[cell.cell_id]?.outcome != null) count.labelled += 1;
  }
  const perText = sample.texts
    .filter((t) => counts.has(t.id))
    .map((t) => ({ text: t.id, label: t.label, ...counts.get(t.id)! }));
  return {
    texts: perText,
    overall: {
      labelled: perText.reduce((n, t) => n + t.labelled, 0),
      inPass: perText.reduce((n, t) => n + t.inPass, 0),
    },
  };
}

/**
 * A cell as the explorer's QuestionResult: the same join the explorer runs over a run's scores and
 * answers, so the review pages show the same expected text, metrics and failure kind.
 */
export function toQuestionResult(cell: SampleCell): QuestionResult {
  const [result] = joinResults(
    [{ question_id: cell.question_id, model_id: cell.model_id, task: cell.task, metrics: cell.metrics as unknown as ScoreMetrics }],
    [
      {
        question_id: cell.question_id,
        model_id: cell.model_id,
        task: cell.task,
        answer: cell.answer,
        question: { prompt: cell.prompt, expected: cell.expected, source: cell.source },
      },
    ],
  );
  return result!;
}
