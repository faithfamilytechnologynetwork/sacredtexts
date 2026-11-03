// How an answered cell failed, finer than correct / incorrect / refused / missing.
//
// The four outcomes stay the headline: this label never changes `correct`. It is a
// deterministic reading of the metrics and the two texts, task by task:
//
//   retrieve_quote / complete_unit (incorrect)
//     other_script   the answer is not in the reference's script (often English prose)
//     omission       the answer is a shorter span contained in the reference
//     near_copy      token overlap ≥ 0.85: the scorer did not fold a close copy. Split by
//                    the token edit distance between the base-letter texts (issue #96):
//       diacritic_only   0 — the same text once vowel signs, accents and pointing go
//       edition_variant  1–2 tokens — movable nu, plene/defective, one changed word
//       near_copy        more than 2
//     paraphrase     token overlap in [0.4, 0.85): a rewrite, not a near copy
//     wrong_passage  everything else (a different span, or too little overlap to call)
//   retrieve_quote / complete_unit (correct, contained, not exact)
//     addition       the reference is delivered and the answer continues well past it
//                    (containment still scores this correct; the label only surfaces it)
//   cite_passage (incorrect)
//     hedge          more than one formally shaped citation
//     wrong_locus    exactly one citation, and it is not the reference
//     no_citation    no formally shaped citation
//   verify_source (incorrect)
//     wrong_verdict  a committed Yes/No that is not the expected one
//
// Refused and missing cells get no kind. A script mismatch is not evidence of another edition.

export type FailureKind =
  | "paraphrase"
  | "wrong_passage"
  | "other_script"
  | "diacritic_only"
  | "edition_variant"
  | "near_copy"
  | "omission"
  | "addition"
  | "wrong_locus"
  | "hedge"
  | "no_citation"
  | "wrong_verdict";

export const FAILURE_KINDS: readonly FailureKind[] = [
  "paraphrase",
  "wrong_passage",
  "other_script",
  "diacritic_only",
  "edition_variant",
  "near_copy",
  "omission",
  "addition",
  "wrong_locus",
  "hedge",
  "no_citation",
  "wrong_verdict",
];

/** A minor kind stays on the passage that was asked for. A major kind replaces it. */
const MINOR: ReadonlySet<FailureKind> = new Set([
  "paraphrase", "omission", "addition", "diacritic_only", "edition_variant", "near_copy",
]);

export function failureSeverity(kind: FailureKind | null): "minor" | "major" | null {
  if (!kind) return null;
  return MINOR.has(kind) ? "minor" : "major";
}

/** Short label for the explorer badge and filter. */
export const FAILURE_KIND_LABEL: Record<FailureKind, string> = {
  paraphrase: "paraphrase",
  wrong_passage: "wrong passage",
  other_script: "other script",
  diacritic_only: "diacritic only",
  edition_variant: "edition variant",
  near_copy: "near copy",
  omission: "omission",
  addition: "addition",
  wrong_locus: "wrong locus",
  hedge: "hedge",
  no_citation: "no citation",
  wrong_verdict: "wrong verdict",
};

/** High token-F1 misses in the committed runs are paraphrases, not contained quotes. */
const PARAPHRASE_F1 = 0.4;
const NEAR_COPY_F1 = 0.85;
/** Extra tokens past the reference before a contained answer is called an addition. */
const ADDITION_EXTRA_TOKENS = 8;
/** Inside the near-copy gate, at most this many base-letter token edits is an edition variant. */
const EDITION_VARIANT_TOKENS = 2;

export interface FailureInput {
  task: string;
  correct: boolean;
  refused: boolean;
  missing: boolean;
  answer: string;
  expected: string;
  tokenF1: number | null;
  /** The overlap with vowel signs and accents removed; preferred over tokenF1 when present. */
  tokenF1Base?: number | null;
  normalized: number | null;
  containsReference: number | null;
  nCandidates: number | null;
}

function normalize(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokenList(s: string): string[] {
  const n = normalize(s);
  return n ? n.split(" ") : [];
}

/** Deleted before the base-letter comparison, as the scorer deletes them: Arabic tatweel, the
 * Qur'anic annotation block, and the zero-width joiners inside Indic conjuncts. */
const BASE_DROP = /[\u0640\u06D6-\u06ED\u200C\u200D]/gu;

/** Tokens with every combining mark removed, alef-wasla read as alef and final sigma as sigma —
 * the pipeline's base_tokens (failure_kind.py), byte for byte. */
function baseTokens(s: string): string[] {
  const bare = s
    .normalize("NFKD")
    .replace(/\u0671/g, "\u0627")
    .replace(BASE_DROP, "")
    .replace(/\p{M}/gu, "");
  return tokenList(bare).map((t) => t.replace(/\u03C2/g, "\u03C3"));
}

/** Levenshtein distance over tokens (insert, delete, substitute one word). */
function tokenDistance(a: string[], b: string[]): number {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur.push(Math.min(prev[j]! + 1, cur[j - 1]! + 1, prev[j - 1]! + (a[i - 1] === b[j - 1] ? 0 : 1)));
    }
    prev = cur;
  }
  return prev[b.length]!;
}

function nearCopyKind(answer: string, expected: string): FailureKind {
  const d = tokenDistance(baseTokens(answer), baseTokens(expected));
  if (d === 0) return "diacritic_only";
  if (d <= EDITION_VARIANT_TOKENS) return "edition_variant";
  return "near_copy";
}

type Script = "hebrew" | "arabic" | "greek" | "latin";

function primaryScript(s: string): Script | null {
  let hebrew = 0;
  let arabic = 0;
  let greek = 0;
  let latin = 0;
  for (const ch of s) {
    const c = ch.codePointAt(0)!;
    if (c >= 0x0590 && c <= 0x05ff) hebrew++;
    else if (
      (c >= 0x0600 && c <= 0x06ff) ||
      (c >= 0x0750 && c <= 0x077f) ||
      (c >= 0x08a0 && c <= 0x08ff) ||
      (c >= 0xfb50 && c <= 0xfdff) ||
      (c >= 0xfe70 && c <= 0xfeff)
    )
      arabic++;
    // Greek and Coptic + Greek Extended. grc is a supported canonical language, so a Greek
    // prompt answered in English must read as other_script, not wrong_passage.
    else if ((c >= 0x0370 && c <= 0x03ff) || (c >= 0x1f00 && c <= 0x1fff)) greek++;
    else if ((c >= 65 && c <= 90) || (c >= 97 && c <= 122)) latin++;
  }
  const best = Math.max(hebrew, arabic, greek, latin);
  if (best < 4) return null;
  if (hebrew === best) return "hebrew";
  if (arabic === best) return "arabic";
  if (greek === best) return "greek";
  return "latin";
}

/** The answer's normalised text is a shorter, word-bounded span of the reference. */
function isOmission(answer: string, expected: string): boolean {
  const a = normalize(answer);
  const e = normalize(expected);
  const aTokens = a ? a.split(" ") : [];
  const eTokens = e ? e.split(" ") : [];
  if (aTokens.length < 2 || aTokens.length >= eTokens.length) return false;
  if (aTokens.length > eTokens.length * 0.85) return false;
  const padded = ` ${e} `;
  return padded.includes(` ${a} `);
}

function textRetrievalKind(input: FailureInput): FailureKind | null {
  if (input.correct) {
    if (input.containsReference !== 1 || input.normalized === 1) return null;
    const extra = tokenList(input.answer).length - tokenList(input.expected).length;
    return extra >= ADDITION_EXTRA_TOKENS ? "addition" : null;
  }
  const expectedScript = primaryScript(input.expected);
  const answerScript = primaryScript(input.answer);
  if (expectedScript && answerScript && expectedScript !== answerScript) return "other_script";
  if (isOmission(input.answer, input.expected)) return "omission";
  const f1 = input.tokenF1Base ?? input.tokenF1 ?? 0;
  if (f1 >= NEAR_COPY_F1) return nearCopyKind(input.answer, input.expected);
  if (f1 >= PARAPHRASE_F1) return "paraphrase";
  return "wrong_passage";
}

/** A failure kind for this cell, or null when the four-way outcome is the whole story. */
export function classifyFailure(input: FailureInput): FailureKind | null {
  if (input.missing || input.refused) return null;
  if (input.task === "retrieve_quote" || input.task === "complete_unit") return textRetrievalKind(input);
  if (!input.correct && input.task === "cite_passage") {
    if ((input.nCandidates ?? 0) > 1) return "hedge";
    if (input.nCandidates === 1) return "wrong_locus";
    return "no_citation";
  }
  if (!input.correct && input.task === "verify_source") return "wrong_verdict";
  return null;
}
