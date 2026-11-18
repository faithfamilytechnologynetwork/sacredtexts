import { describe, it, expect } from "vitest";
import { parseSample } from "./reviewSample";
import { progressDashboard } from "./reviewProgress";
import { multiScriptSample } from "../test/reviewHarness";

const SAMPLE = parseSample(multiScriptSample());
const ISLAM = ["fixture-run:model-b:df788ade727db3cf", "fixture-run:model-a:12e45dddc647beb6"];
const HINDU = "fixture-run:model-a:f713b30ff8deb19b";
const TALMUD = "fixture-run:model-a:he0001";
const at = "2026-11-18T09:30:00.000Z";
const reviewer = (name: string, texts: string[], labelledCellIds: string[]) => ({ name, texts, labelledCellIds, submissions: 0, updatedAt: at });

describe("progressDashboard", () => {
  const dashboard = progressDashboard(SAMPLE, [
    reviewer("Amira", ["islam/native"], [ISLAM[0]!, HINDU, ISLAM[1]!]),
    reviewer("Ben", ["islam/native", "judaism/native"], [ISLAM[0]!, TALMUD, "other-run:m:q"]),
    reviewer("Cy", [], []),
  ]);

  it("counts each reviewer's labels per text they chose or labelled in, out of the text's cells in the sample", () => {
    expect(dashboard.reviewers).toEqual([
      {
        name: "Amira",
        texts: [
          { text: "hinduism/english", label: "Bhagavad Gita — Annie Besant (1922)", labelled: 1, inPass: 5, chosen: false },
          { text: "islam/native", label: "The Qur'an — Uthmani (QUL)", labelled: 2, inPass: 5, chosen: true },
        ],
        labelled: 3,
        updatedAt: at,
      },
      {
        name: "Ben",
        texts: [
          { text: "islam/native", label: "The Qur'an — Uthmani (QUL)", labelled: 1, inPass: 5, chosen: true },
          { text: "judaism/native", label: "Talmud Bavli — Aramaic", labelled: 1, inPass: 2, chosen: true },
        ],
        labelled: 2, // a cell outside the sample is not counted
        updatedAt: at,
      },
      { name: "Cy", texts: [], labelled: 0, updatedAt: at },
    ]);
  });

  it("counts a cell labelled by several reviewers once in the per-text rollup, for every text in the sample", () => {
    expect(dashboard.coverage.texts.map((t) => [t.text, t.labelled, t.inPass])).toEqual([
      ["hinduism/english", 1, 5],
      ["islam/native", 2, 5],
      ["judaism/native", 1, 2],
      ["sikhism/native", 0, 1],
    ]);
    expect(dashboard.coverage.overall).toEqual({ labelled: 4, inPass: 13 });
  });

  it("is all zeros with no reviewers", () => {
    const empty = progressDashboard(SAMPLE, []);
    expect(empty.reviewers).toEqual([]);
    expect(empty.coverage.overall).toEqual({ labelled: 0, inPass: 13 });
  });
});
