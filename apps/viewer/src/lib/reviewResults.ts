// The results page's numbers (issue #157): how the matcher's shown verdict agrees with the reviewer's
// labels, counted from the same gold rows the download writes and by the same rules as
// `review-compare --version committed` (`review_compare._version_report`): `cant_judge` and
// defect-flagged rows are not in `n`; groups are sorted by code point. The shape is that report's
// without the per-text `arms`, and fixtures/review_results.json pins both sides to the same numbers.

import { compareCodePoints, type GoldRow } from "./goldSet";

export interface Tally {
  agree: number;
  n: number;
  /** Percent to one decimal; null when n is 0. */
  pct: number | null;
}

export interface Disagreement {
  cell_id: string;
  /** The reviewer's outcome. */
  human: string;
  reviewer_id: string;
  task: string;
  text: string;
  /** The matcher's shown outcome (review-compare's name for a version's outcome). */
  version: string;
}

export interface AgreementReport {
  /** Labelled cells, judged or not. */
  rows: number;
  excluded: { both: number; cant_judge: number; defect: number; total: number };
  overall: Tally;
  by_task: Record<string, Tally>;
  by_text: Record<string, Tally>;
  by_grader_path: Record<string, Tally>;
  disagreements: Disagreement[];
}

/** Python's `round(100 * agree / n, 1)`: the double's exact decimal value, rounded half to even. */
export function roundPct(agree: number, n: number): number | null {
  if (n === 0) return null;
  const exact = ((100 * agree) / n).toFixed(100); // the double's exact decimal digits, to 100 places
  const dot = exact.indexOf(".");
  const tenths = Number(exact.slice(0, dot + 2).replace(".", ""));
  const rest = exact.slice(dot + 2);
  const half = "5".padEnd(rest.length, "0");
  return (rest > half || (rest === half && tenths % 2 === 1) ? tenths + 1 : tenths) / 10;
}

function tally(agrees: boolean[]): Tally {
  const agree = agrees.filter(Boolean).length;
  return { agree, n: agrees.length, pct: roundPct(agree, agrees.length) };
}

function breakdown(keys: string[], agrees: boolean[]): Record<string, Tally> {
  const groups = new Map<string, boolean[]>();
  keys.forEach((key, i) => groups.set(key, [...(groups.get(key) ?? []), agrees[i]!]));
  return Object.fromEntries([...groups.keys()].sort(compareCodePoints).map((key) => [key, tally(groups.get(key)!)]));
}

export function agreementReport(rows: readonly GoldRow[]): AgreementReport {
  const judged = rows.filter((r) => r.label.outcome !== "cant_judge" && !r.label.defect);
  const agrees = judged.map((r) => r.shown.outcome === r.label.outcome);
  const cantJudge = rows.filter((r) => r.label.outcome === "cant_judge");
  return {
    rows: rows.length,
    excluded: {
      both: cantJudge.filter((r) => r.label.defect).length,
      cant_judge: cantJudge.length,
      defect: rows.filter((r) => r.label.defect).length,
      total: rows.length - judged.length,
    },
    overall: tally(agrees),
    by_task: breakdown(judged.map((r) => r.task), agrees),
    by_text: breakdown(judged.map((r) => r.text), agrees),
    by_grader_path: breakdown(judged.map((r) => r.shown.grader_path), agrees),
    disagreements: judged
      .filter((_, i) => !agrees[i])
      .map((r) => ({ cell_id: r.cell_id, human: r.label.outcome, reviewer_id: r.reviewer_id, task: r.task, text: r.text, version: r.shown.outcome })),
  };
}

/** `agree / n (pct)`, as review-compare prints it. */
export function formatTally(t: Tally): string {
  return `${t.agree} / ${t.n} (${t.pct === null ? "—" : `${t.pct.toFixed(1)}%`})`;
}
