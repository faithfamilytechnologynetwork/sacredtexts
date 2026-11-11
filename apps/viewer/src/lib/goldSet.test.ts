import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { buildGoldSet, compareCodePoints, goldRows, goldSetFileName, GoldSetError } from "./goldSet";
import { emptyLabel, type CellLabel } from "./review";
import { parseSample, type ReviewSample } from "./reviewSample";

const read = (rel: string) => readFileSync(resolve(process.cwd(), rel), "utf8");
const sample = parseSample(JSON.parse(read("../../fixtures/review_sample.json")));
const goldText = read("../../fixtures/review_gold_set.jsonl");
const goldLines: any[] = goldText.trimEnd().split("\n").map((l) => JSON.parse(l));
const REVIEWER = goldLines[0].reviewer_id as string;

/** The labels the fixture records, as the store holds them. */
function fixtureLabels(): Record<string, CellLabel> {
  const labels: Record<string, CellLabel> = {};
  for (const row of goldLines) {
    labels[row.cell_id] = {
      outcome: row.label.outcome,
      defect: row.label.defect,
      notes: row.label.notes,
      rubric_version: row.rubric_version,
      labelled_at: row.labelled_at,
    };
  }
  return labels;
}

// review_compare.GOLD_KEYS: the row carries the reviewer's account id and nothing else about them.
const GOLD_KEYS = [
  "answer", "cell_id", "expected", "format", "label", "labelled_at", "model_id", "prompt", "question_id",
  "reviewer_id", "rubric_version", "run", "sample_id", "scores_path", "shown", "source", "task", "text",
];

describe("buildGoldSet", () => {
  it("reproduces the shared fixture byte for byte (the Python writer's bytes)", () => {
    expect(goldLines.every((row) => row.reviewer_id === REVIEWER)).toBe(true);
    expect(buildGoldSet(sample, fixtureLabels(), REVIEWER)).toBe(goldText);
  });

  it("is deterministic: unchanged labels give identical bytes, whatever order they were made in", () => {
    const labels = fixtureLabels();
    const reversed = Object.fromEntries(Object.entries(labels).reverse());
    const first = buildGoldSet(sample, labels, REVIEWER);
    expect(buildGoldSet(sample, labels, REVIEWER)).toBe(first);
    expect(buildGoldSet(sample, reversed, REVIEWER)).toBe(first);
  });

  it("each row has exactly the gold-set fields: an account id, no email or name", () => {
    for (const row of goldRows(sample, fixtureLabels(), REVIEWER)) {
      expect(Object.keys(row).sort()).toEqual(GOLD_KEYS);
      expect(Object.keys(row.label).sort()).toEqual(["defect", "notes", "outcome"]);
      expect(Object.keys(row.shown).sort()).toEqual(["grader_path", "metrics", "outcome"]);
    }
  });

  it("a label without an outcome is left out; nothing labelled is an empty file", () => {
    const labels = fixtureLabels();
    const [firstId] = Object.keys(labels);
    labels[firstId!] = { ...labels[firstId!]!, outcome: null };
    const rows = goldRows(sample, labels, REVIEWER);
    expect(rows).toHaveLength(goldLines.length - 1);
    expect(rows.some((r) => r.cell_id === firstId)).toBe(false);
    expect(buildGoldSet(sample, {}, REVIEWER)).toBe("");
    expect(buildGoldSet(sample, { [firstId!]: { ...emptyLabel(), notes: "unsure" } }, REVIEWER)).toBe("");
  });

  it("fails loudly on a label for a cell the sample doesn't hold", () => {
    const labels = { ...fixtureLabels(), "other-run:m:q": { ...emptyLabel(), outcome: "correct" as const, rubric_version: "1", labelled_at: "2026-11-10T12:00:00.000Z" } };
    expect(() => buildGoldSet(sample, labels, REVIEWER)).toThrow(GoldSetError);
    expect(() => buildGoldSet(sample, labels, REVIEWER)).toThrow(/not in sample review_sample/);
  });

  it("fails loudly on a label that lost its rubric version or time, and without a reviewer id", () => {
    const labels = fixtureLabels();
    const [firstId] = Object.keys(labels);
    const lostStamp = { ...labels, [firstId!]: { ...labels[firstId!]!, labelled_at: "" } };
    expect(() => buildGoldSet(sample, lostStamp, REVIEWER)).toThrow(/edit it to restamp it/);
    expect(() => buildGoldSet(sample, labels, "")).toThrow(/account id/);
  });

  it("sorts keys by code point at every level, as Python's sort_keys does", () => {
    // JS objects iterate integer-like keys first ("9" before "10" before "a"); Python sorts them as
    // strings ("10" < "9" < "a"). The gold set must follow Python.
    const cell = { ...sample.cells[0]!, metrics: { a: 1, "9": 2, "10": 3.5 } };
    const odd: ReviewSample = { ...sample, cells: [cell] };
    const label = { ...emptyLabel(), outcome: "correct" as const, rubric_version: "1", labelled_at: "2026-11-10T12:00:00.000Z" };
    const line = buildGoldSet(odd, { [cell.cell_id]: label }, REVIEWER);
    expect(line).toContain('"metrics":{"10":3.5,"9":2,"a":1}');
    expect(line.endsWith("}\n")).toBe(true);
    expect(line.split("\n")).toHaveLength(2);
  });

  it("writes non-ASCII text unescaped", () => {
    const line = buildGoldSet(sample, fixtureLabels(), REVIEWER);
    expect(line).toContain("القرآن");
    expect(line).not.toMatch(/\\u0[6-9a-f]/i);
  });
});

describe("compareCodePoints", () => {
  it("orders by code point, not by UTF-16 unit", () => {
    // U+1F600 is stored as the surrogates D83D DE00, which compare below U+FFFD as UTF-16 units.
    expect("\u{1F600}" < "�").toBe(true);
    expect(compareCodePoints("\u{1F600}", "�")).toBeGreaterThan(0);
    expect(compareCodePoints("ab", "abc")).toBeLessThan(0);
    expect(compareCodePoints("x\u{1F600}a", "x\u{1F600}b")).toBeLessThan(0);
    expect(compareCodePoints("same", "same")).toBe(0);
  });
});

describe("goldSetFileName", () => {
  it("names the file by the sample id", () => {
    expect(goldSetFileName("facct-2026-11-03-k10")).toBe("gold-facct-2026-11-03-k10.jsonl");
  });
});
