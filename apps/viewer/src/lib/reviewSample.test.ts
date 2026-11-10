import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { emptyLabel, type CellLabel } from "./review";
import { parseSample, passCells, progressByText, SampleFormatError, toQuestionResult } from "./reviewSample";

const readJson = (rel: string) => JSON.parse(readFileSync(resolve(process.cwd(), rel), "utf8"));
const fixture = () => readJson("../../fixtures/review_sample.json");
const sample = parseSample(fixture());

const ISLAM = "islam/native";
const GITA = "hinduism/english";
const labelled = (outcome: CellLabel["outcome"]): CellLabel => ({ ...emptyLabel(), outcome });

describe("parseSample", () => {
  it("reads the shared fixture", () => {
    expect(sample.sample_id).toBe("review_sample");
    expect(sample.texts.map((t) => t.id)).toEqual([GITA, ISLAM]);
    expect(sample.cells).toHaveLength(10);
    const first = sample.cells[0]!;
    expect(first.cell_id).toBe("fixture-run:model-b:df788ade727db3cf");
    expect(first.source.language).toBe("ar");
    expect(first.metrics.outcome).toBe("correct");
  });

  it("reads the committed FAccT sample, and every cell's verdict survives the explorer's join", () => {
    const facct = parseSample(readJson("../../review/samples/facct-2026-11-03-k10.json"));
    expect(facct.sample_id).toBe("facct-2026-11-03-k10");
    expect(facct.texts).toHaveLength(13);
    expect(facct.cells).toHaveLength(1423);
    for (const cell of facct.cells) {
      const r = toQuestionResult(cell);
      expect(r.correct).toBe(cell.outcome === "correct");
      expect(r.refused).toBe(cell.outcome === "refused");
    }
  });

  const broken: Array<[string, (s: any) => void, RegExp]> = [
    ["an unknown format", (s) => (s.format = 2), /unsupported format 2/],
    ["a missing sample id", (s) => delete s.sample_id, /'sample_id' must be a string/],
    ["texts that aren't a list", (s) => (s.texts = {}), /'texts' must be a list of objects/],
    ["a duplicate text", (s) => s.texts.push({ ...s.texts[0] }), /duplicate text id/],
    ["a cell naming an unknown text", (s) => (s.cells[0].text = "nope"), /names unknown text "nope"/],
    ["an unknown task", (s) => (s.cells[0].task = "summarise"), /unknown task "summarise"/],
    ["an unknown matcher outcome", (s) => (s.cells[0].outcome = "maybe"), /unknown outcome "maybe"/],
    ["a duplicate cell", (s) => s.cells.push({ ...s.cells[0] }), /duplicate cell/],
    ["a cell id that isn't run:model:question", (s) => (s.cells[0].cell_id = "x"), /cell_id is not/],
    ["a non-string answer", (s) => (s.cells[0].answer = null), /'answer' must be a string/],
    ["metrics that aren't an object", (s) => (s.cells[0].metrics = []), /'metrics' must be an object/],
    ["a tradition that isn't a list", (s) => (s.cells[0].source.tradition = "Islam"), /'source.tradition'/],
    ["a missing language", (s) => delete s.cells[0].source.language, /'language' must be a string/],
    ["a negative stratum count", (s) => (s.strata[0].drawn = -1), /'drawn' must be a count/],
  ];
  it.each(broken)("fails loudly on %s", (_name, corrupt, message) => {
    const raw = fixture();
    corrupt(raw);
    expect(() => parseSample(raw)).toThrow(SampleFormatError);
    expect(() => parseSample(raw)).toThrow(message);
  });

  it("fails loudly on a non-object", () => {
    expect(() => parseSample(null)).toThrow(SampleFormatError);
    expect(() => parseSample([])).toThrow(/a sample is a JSON object/);
  });
});

describe("passCells", () => {
  it("is the sample's cells from the chosen texts, in sample order", () => {
    const pass = passCells(sample, [ISLAM]);
    expect(pass.map((c) => c.cell_id)).toEqual(sample.cells.filter((c) => c.text === ISLAM).map((c) => c.cell_id));
    expect(pass.every((c) => c.text === ISLAM)).toBe(true);
    expect(pass).toHaveLength(5);
  });

  it("adding a text adds its cells, still in sample order, whatever order the texts were chosen in", () => {
    const both = passCells(sample, [ISLAM, GITA]);
    expect(both.map((c) => c.cell_id)).toEqual(sample.cells.map((c) => c.cell_id));
    expect(passCells(sample, [GITA, ISLAM])).toEqual(both);
  });

  it("no chosen texts is an empty pass; an unknown text adds nothing", () => {
    expect(passCells(sample, [])).toEqual([]);
    expect(passCells(sample, ["nope"])).toEqual([]);
  });
});

describe("progressByText", () => {
  it("counts labelled / in pass per chosen text, in the sample's text order, and overall", () => {
    const islam = passCells(sample, [ISLAM]);
    const gita = passCells(sample, [GITA]);
    const labels: Record<string, CellLabel> = {
      [islam[0]!.cell_id]: labelled("correct"),
      [islam[1]!.cell_id]: labelled("cant_judge"),
      [islam[2]!.cell_id]: { ...emptyLabel(), notes: "no outcome yet" }, // not labelled
      [gita[0]!.cell_id]: labelled("incorrect"),
    };
    expect(progressByText(sample, [ISLAM, GITA], labels)).toEqual({
      texts: [
        { text: GITA, label: "Bhagavad Gita — Annie Besant (1922)", labelled: 1, inPass: 5 },
        { text: ISLAM, label: "The Qur'an — Uthmani (QUL)", labelled: 2, inPass: 5 },
      ],
      overall: { labelled: 3, inPass: 10 },
    });
  });

  it("a label on a text outside the pass isn't counted", () => {
    const gita = passCells(sample, [GITA]);
    const progress = progressByText(sample, [ISLAM], { [gita[0]!.cell_id]: labelled("correct") });
    expect(progress.texts).toHaveLength(1);
    expect(progress.overall).toEqual({ labelled: 0, inPass: 5 });
  });

  it("no chosen texts is no progress", () => {
    expect(progressByText(sample, [], {})).toEqual({ texts: [], overall: { labelled: 0, inPass: 0 } });
  });
});

describe("toQuestionResult", () => {
  it("renders a cell as the explorer does", () => {
    const cell = sample.cells.find((c) => c.task === "retrieve_quote" && c.outcome === "incorrect")!;
    const r = toQuestionResult(cell);
    expect(r).toMatchObject({
      question_id: cell.question_id,
      model_id: cell.model_id,
      task: "retrieve_quote",
      correct: false,
      missing: false,
      refused: false,
      prompt: cell.prompt,
      answer: cell.answer,
      expected: cell.expected.text,
      tradition: cell.source.tradition,
      exact: 0,
      normalized: 0,
      token_f1: cell.metrics.token_f1,
    });
    expect(r.failure).not.toBeNull();
  });

  it("shows a cite cell's expected citation and a verify cell's expected answer", () => {
    const cite = sample.cells.find((c) => c.task === "cite_passage")!;
    expect(toQuestionResult(cite).expected).toBe(cite.expected.citation);
    const refused = sample.cells.find((c) => c.outcome === "refused")!;
    const r = toQuestionResult(refused);
    expect(r.expected).toBe(refused.expected.answer);
    expect(r.refused).toBe(true);
    expect(r.exact).toBeNull();
  });
});
