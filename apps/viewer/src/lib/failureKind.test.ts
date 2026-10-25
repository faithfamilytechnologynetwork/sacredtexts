import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { classifyFailure, failureSeverity, type FailureInput, type FailureKind } from "./failureKind";

// The shared parity fixture: the SAME cases pytest asserts against
// (pipelines/tests/test_failure_kind.py), so classifyFailure and classify_failure cannot drift.
interface SharedCase {
  name: string;
  task: string;
  correct: boolean;
  refused: boolean;
  answer: string;
  expected: string;
  token_f1: number | null;
  normalized: number | null;
  contains_reference: number | null;
  n_candidates: number | null;
  expected_kind: FailureKind | null;
  expected_severity: "minor" | "major" | null;
}

// vitest runs with cwd = apps/viewer (see deploy.test.ts reading "package.json"); the shared
// fixture lives at the repo root, two levels up.
const fixturePath = resolve(process.cwd(), "../../fixtures/failure_kind_cases.json");
const sharedCases: SharedCase[] = JSON.parse(readFileSync(fixturePath, "utf8")).cases;

function fromSharedCase(c: SharedCase): FailureInput {
  return {
    task: c.task,
    correct: c.correct,
    refused: c.refused,
    missing: false,
    answer: c.answer,
    expected: c.expected,
    tokenF1: c.token_f1,
    normalized: c.normalized,
    containsReference: c.contains_reference,
    nCandidates: c.n_candidates,
  };
}

describe("classifyFailure shared fixture parity", () => {
  it.each(sharedCases.map((c) => [c.name, c] as const))("%s", (_name, c) => {
    const kind = classifyFailure(fromSharedCase(c));
    expect(kind).toBe(c.expected_kind);
    expect(failureSeverity(kind)).toBe(c.expected_severity);
  });
});

function row(partial: Partial<FailureInput>): FailureInput {
  return {
    task: "retrieve_quote",
    correct: false,
    refused: false,
    missing: false,
    answer: "a completely different sentence here",
    expected: "the reference verse text itself",
    tokenF1: 0,
    normalized: 0,
    containsReference: 0,
    nCandidates: null,
    ...partial,
  };
}

describe("classifyFailure", () => {
  it("leaves refused, missing, and plain-correct cells unlabeled", () => {
    expect(classifyFailure(row({ refused: true }))).toBeNull();
    expect(classifyFailure(row({ missing: true }))).toBeNull();
    expect(classifyFailure(row({ correct: true, normalized: 1, containsReference: 1 }))).toBeNull();
  });

  it("splits a text-retrieval miss into paraphrase, omission, wrong witness, or wrong passage", () => {
    expect(classifyFailure(row({ tokenF1: 0.62 }))).toBe("paraphrase");
    expect(classifyFailure(row({ tokenF1: 0.1 }))).toBe("wrong_passage");
    expect(
      classifyFailure(
        row({
          answer: "the reference",
          expected: "the reference verse text itself and more words",
          tokenF1: 0.5,
        }),
      ),
    ).toBe("omission");
    expect(
      classifyFailure(
        row({
          answer: "In the beginning God created the heaven",
          expected: "בְּרֵאשִׁית בָּרָא אֱלֹהִים",
          tokenF1: 0,
        }),
      ),
    ).toBe("other_script");
  });

  it("flags a correct contained quote that runs well past the reference as addition", () => {
    const expected = "one two three four";
    const answer = `${expected} five six seven eight nine ten eleven twelve`;
    expect(
      classifyFailure(
        row({ correct: true, answer, expected, containsReference: 1, normalized: 0, tokenF1: 0.5 }),
      ),
    ).toBe("addition");
    expect(
      classifyFailure(
        row({ correct: true, answer: expected, expected, containsReference: 1, normalized: 0 }),
      ),
    ).toBeNull();
  });

  it("splits a bad citation into hedge, wrong locus, or no citation, and a bad yes/no into wrong verdict", () => {
    expect(classifyFailure(row({ task: "cite_passage", nCandidates: 2 }))).toBe("hedge");
    expect(classifyFailure(row({ task: "cite_passage", nCandidates: 1 }))).toBe("wrong_locus");
    expect(classifyFailure(row({ task: "cite_passage", nCandidates: 0 }))).toBe("no_citation");
    expect(classifyFailure(row({ task: "verify_source" }))).toBe("wrong_verdict");
  });
});
