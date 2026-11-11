import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { goldRows } from "./goldSet";
import { parseSample } from "./reviewSample";
import { agreementReport, formatTally, roundPct } from "./reviewResults";
import { goldFixtureLabels, REVIEWER } from "../test/reviewHarness";

const read = (name: string) => readFileSync(resolve(process.cwd(), "../../fixtures", name), "utf8");

describe("agreementReport", () => {
  it("counts the fixture labels exactly as review-compare --version committed does (the shared fixture)", () => {
    const sample = parseSample(JSON.parse(read("review_sample.json")));
    const report = agreementReport(goldRows(sample, goldFixtureLabels(), REVIEWER.id));
    const fixture = JSON.parse(read("review_results.json"));
    expect(report).toEqual(fixture);
    // toEqual ignores key order, but the page renders the groups in it: review-compare's sorted order.
    for (const group of ["by_task", "by_text", "by_grader_path"] as const) {
      expect(Object.keys(report[group]), group).toEqual(Object.keys(fixture[group]));
    }
  });

  it("is empty with no labels", () => {
    expect(agreementReport([])).toMatchObject({ rows: 0, overall: { agree: 0, n: 0, pct: null }, disagreements: [] });
  });
});

describe("roundPct", () => {
  it("rounds as Python's round(100 * agree / n, 1) does, ties to even on the double's exact value", () => {
    // Python: round(6.25, 1) == 6.2, round(18.75, 1) == 18.8, round(100 / 2000, 1) == 0.1 (0.05 is a hair above).
    const cases: Array<[number, number, number | null]> = [
      [6, 8, 75], [2, 3, 66.7], [1, 16, 6.2], [3, 16, 18.8], [1, 2000, 0.1], [3, 2000, 0.1], [8, 8, 100], [0, 5, 0], [0, 0, null],
    ];
    for (const [agree, n, pct] of cases) expect(roundPct(agree, n), `${agree}/${n}`).toBe(pct);
  });

  it("formats a tally as review-compare prints it", () => {
    expect(formatTally({ agree: 6, n: 8, pct: 75 })).toBe("6 / 8 (75.0%)");
    expect(formatTally({ agree: 0, n: 0, pct: null })).toBe("0 / 0 (—)");
  });
});
