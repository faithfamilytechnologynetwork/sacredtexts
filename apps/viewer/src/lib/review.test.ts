import { describe, it, expect } from "vitest";
import {
  emptyLabel,
  emptySampleReview,
  emptyState,
  isLabelled,
  parseSampleReview,
  withLabel,
  withTexts,
  withoutSample,
  type ReviewState,
} from "./review";
import { RUBRIC_VERSION } from "./rubric";

const T1 = new Date("2026-11-10T12:00:00.000Z");
const T2 = new Date("2026-11-11T09:30:00.000Z");

describe("parseSampleReview (tolerant persistence)", () => {
  it("null and non-object payloads degrade to an empty review", () => {
    expect(parseSampleReview(null)).toEqual(emptySampleReview());
    expect(parseSampleReview("a string")).toEqual(emptySampleReview());
    expect(parseSampleReview([1, 2])).toEqual(emptySampleReview());
  });

  it("round-trips a real review", () => {
    let s = withTexts(emptyState(), "S", ["islam/native", "sikhism/native"]);
    s = withLabel(s, "S", "run:m:q1", { outcome: "incorrect", notes: "ليس هذا", defect: true }, T1);
    s = withLabel(s, "S", "run:m:q2", { outcome: "cant_judge" }, T2);
    const review = s.samples.S!;
    expect(parseSampleReview(JSON.parse(JSON.stringify(review)))).toEqual(review);
  });

  it("a corrupt field falls back alone; the rest of the work survives", () => {
    const raw = {
      texts: ["islam/native"],
      labels: {
        a: { outcome: "bogus", defect: true, notes: "keep me", rubric_version: "1", labelled_at: "2026-11-10T12:00:00.000Z" },
        b: { outcome: "correct", defect: "yes", notes: 42, rubric_version: 1, labelled_at: null },
        c: "not a label",
      },
    };
    const parsed = parseSampleReview(raw);
    expect(parsed.texts).toEqual(["islam/native"]);
    expect(parsed.labels.a).toEqual({
      outcome: null,
      defect: true,
      notes: "keep me",
      rubric_version: "1",
      labelled_at: "2026-11-10T12:00:00.000Z",
    });
    expect(parsed.labels.b).toEqual({ outcome: "correct", defect: false, notes: "", rubric_version: "", labelled_at: "" });
    expect(parsed.labels.c).toEqual(emptyLabel());
  });

  it("a corrupt texts list or labels map falls back without touching the other", () => {
    expect(parseSampleReview({ texts: "islam/native", labels: { a: { outcome: "refused" } } })).toEqual({
      texts: [],
      labels: { a: { outcome: "refused", defect: false, notes: "", rubric_version: "", labelled_at: "" } },
    });
    expect(parseSampleReview({ texts: ["x"], labels: [] })).toEqual({ texts: ["x"], labels: {} });
  });
});

describe("withLabel", () => {
  it("creates the sample and the label on first touch, stamped with the rubric and the time", () => {
    const s = withLabel(emptyState(), "S", "c1", { outcome: "correct" }, T1);
    expect(s.samples.S?.texts).toEqual([]);
    expect(s.samples.S?.labels.c1).toEqual({
      outcome: "correct",
      defect: false,
      notes: "",
      rubric_version: RUBRIC_VERSION,
      labelled_at: "2026-11-10T12:00:00.000Z",
    });
  });

  it("a real change to outcome, defect or notes restamps the label", () => {
    const s1 = withLabel(emptyState(), "S", "c1", { outcome: "correct" }, T1);
    for (const patch of [{ outcome: "refused" as const }, { defect: true }, { notes: "why" }]) {
      const s2 = withLabel(s1, "S", "c1", patch, T2);
      expect(s2.samples.S?.labels.c1?.labelled_at).toBe("2026-11-11T09:30:00.000Z");
    }
  });

  it("a no-op edit keeps the old stamp and returns the same state (no save)", () => {
    const s1 = withLabel(emptyState(), "S", "c1", { outcome: "incorrect", notes: "n" }, T1);
    const s2 = withLabel(s1, "S", "c1", { outcome: "incorrect", notes: "n", defect: false }, T2);
    expect(s2).toBe(s1);
    expect(s2.samples.S?.labels.c1?.labelled_at).toBe("2026-11-10T12:00:00.000Z");
  });

  it("an old label isn't restamped with a newer rubric unless it really changes", () => {
    // A label made under rubric "0" (an older rubric) keeps "0" through a no-op edit.
    const old: ReviewState = {
      samples: {
        S: {
          texts: [],
          labels: {
            c1: { outcome: "correct", defect: false, notes: "", rubric_version: "0", labelled_at: "2026-01-01T00:00:00.000Z" },
          },
        },
      },
    };
    expect(withLabel(old, "S", "c1", { outcome: "correct" }, T2)).toBe(old);
    const edited = withLabel(old, "S", "c1", { notes: "re-checked" }, T2);
    expect(edited.samples.S?.labels.c1?.rubric_version).toBe(RUBRIC_VERSION);
    expect(edited.samples.S?.labels.c1?.labelled_at).toBe("2026-11-11T09:30:00.000Z");
  });

  it("an empty patch on an unlabelled cell creates nothing", () => {
    const s = emptyState();
    expect(withLabel(s, "S", "c1", { notes: "" }, T1)).toBe(s);
  });

  it("clearing the outcome is a real change", () => {
    const s1 = withLabel(emptyState(), "S", "c1", { outcome: "correct" }, T1);
    const s2 = withLabel(s1, "S", "c1", { outcome: null }, T2);
    expect(s2.samples.S?.labels.c1?.outcome).toBeNull();
    expect(isLabelled(s2.samples.S?.labels.c1)).toBe(false);
  });

  it("touches only the edited sample's reference (what the store saves)", () => {
    const s1 = withTexts(withTexts(emptyState(), "A", ["x"]), "B", ["y"]);
    const s2 = withLabel(s1, "A", "c1", { outcome: "correct" }, T1);
    expect(s2.samples.B).toBe(s1.samples.B);
    expect(s2.samples.A).not.toBe(s1.samples.A);
  });
});

describe("withTexts and withoutSample", () => {
  it("withTexts sets the choice, keeps the labels, and is a no-op when unchanged", () => {
    let s = withLabel(emptyState(), "S", "c1", { outcome: "correct" }, T1);
    s = withTexts(s, "S", ["islam/native"]);
    expect(s.samples.S?.labels.c1?.outcome).toBe("correct");
    expect(withTexts(s, "S", ["islam/native"])).toBe(s);
    const added = withTexts(s, "S", ["islam/native", "judaism/native"]);
    expect(added.samples.S?.texts).toEqual(["islam/native", "judaism/native"]);
    expect(added.samples.S?.labels).toBe(s.samples.S?.labels);
  });

  it("withTexts with an empty choice on an untouched sample still records it", () => {
    expect(withTexts(emptyState(), "S", []).samples.S).toEqual({ texts: [], labels: {} });
  });

  it("withoutSample drops exactly that sample", () => {
    let s = withTexts(emptyState(), "a", ["x"]);
    s = withTexts(s, "b", ["y"]);
    s = withoutSample(s, "a");
    expect(s.samples.a).toBeUndefined();
    expect(s.samples.b?.texts).toEqual(["y"]);
  });
});

describe("isLabelled", () => {
  it("is true only once the label has an outcome", () => {
    expect(isLabelled(undefined)).toBe(false);
    expect(isLabelled({ ...emptyLabel(), notes: "thinking" })).toBe(false);
    expect(isLabelled({ ...emptyLabel(), outcome: "cant_judge" })).toBe(true);
  });
});
