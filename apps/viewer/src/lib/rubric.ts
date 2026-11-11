// The reviewer rubric (Spec 154, "Reviewer rubric (shown per task)"). It is guidance shown beside
// each cell, not a scorer. Every label records the version it was made under (`withLabel` stamps
// it on a real edit), so bump RUBRIC_VERSION whenever the guidance below changes meaning.

import type { SampleTask } from "./reviewSample";

export const RUBRIC_VERSION = "1";

/** One outcome's guidance: the outcome name as the reviewer sees it, then what qualifies. */
export interface RubricRule {
  outcome: "Correct" | "Incorrect" | "Refused";
  text: string;
}

export interface TaskRubric {
  rules: RubricRule[];
  /** Tolerances that apply to every rule of the task (shown once, under the rules). */
  tolerances?: string[];
}

const QUOTE_TOLERANCES = [
  "vowel marks, cantillation and diacritics",
  "punctuation and spacing",
  "verse numbers",
  "the edition's script convention (e.g. Uthmani vs Imla'i)",
];

const QUOTE_REFUSED =
  "the answer declines and presents no original-language passage. It may offer a summary, " +
  "translation or pointer instead. If it declines and then delivers the text anyway, judge the " +
  "delivered text.";

export const RUBRIC: Record<SampleTask, TaskRubric> = {
  retrieve_quote: {
    rules: [
      {
        outcome: "Correct",
        text:
          "the answer presents a passage as its answer, and the full expected passage appears in it " +
          "unbroken. Hedges like \"from memory\" don't matter. The wording must match, ignoring the " +
          "tolerances below. Any amount of text around the passage is fine.",
      },
      {
        outcome: "Incorrect",
        text: "a different passage, a translation or paraphrase, or words missing or changed inside it.",
      },
      { outcome: "Refused", text: QUOTE_REFUSED },
    ],
    tolerances: QUOTE_TOLERANCES,
  },
  complete_unit: {
    rules: [
      {
        outcome: "Correct",
        text:
          "the continuation given contains the expected continuation's first ten words, or all of it " +
          "if it is shorter. It may stop after those or run on. The wording must match, ignoring the " +
          "tolerances below.",
      },
      {
        outcome: "Incorrect",
        text: "a different continuation, a translation or paraphrase, or words missing or changed inside it.",
      },
      { outcome: "Refused", text: QUOTE_REFUSED },
    ],
    tolerances: QUOTE_TOLERANCES,
  },
  cite_passage: {
    rules: [
      {
        outcome: "Correct",
        text:
          "exactly one location is offered and it is the expected one, at the precision asked: " +
          "chapter:verse, Talmud daf+amud, GGS Ang. Any numerals or notation count. The same location " +
          "in two notations is one location, and a disclaimed echo of the prompt's form example " +
          "doesn't count.",
      },
      { outcome: "Incorrect", text: "two or more different locations, a wrong one, or none." },
      { outcome: "Refused", text: "the answer declines." },
    ],
  },
  verify_source: {
    rules: [
      {
        outcome: "Correct",
        text: "the Yes or No the answer opens with matches the expected answer.",
      },
      { outcome: "Incorrect", text: "the answer opens with the other one." },
      { outcome: "Refused", text: "the answer doesn't open with Yes or No." },
    ],
  },
};

/** Shown under every task's rules. */
export const CANT_JUDGE_GUIDANCE = "Use can't judge when you can't tell, and add notes.";
