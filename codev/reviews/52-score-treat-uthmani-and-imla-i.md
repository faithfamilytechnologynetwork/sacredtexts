# Review: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

**Spec**: [codev/specs/52-score-treat-uthmani-and-imla-i.md](../specs/52-score-treat-uthmani-and-imla-i.md) ·
**Plan**: [codev/plans/52-score-treat-uthmani-and-imla-i.md](../plans/52-score-treat-uthmani-and-imla-i.md)

> Draft started during the Phase-2 hold (#48 merges first). Phase-1 sections are final; the
> moved-numbers table and Phase-2/3 notes are filled when the rebaseline runs.

## What shipped

A model that reproduces a Qur'anic verse correctly but in a different orthography than the QUL
Uthmani corpus (the common case when prompted in Arabic — #39) is now credited. The equivalence is
implemented **entirely in the containment predicate** (`fold_aware_contains`), as a strict superset
of the previous `bounded_contains`: `normalize()` and the similarity submetrics
(`exact`/`normalized`/`token_f1`) are byte-for-byte unchanged, so the only scores that move are
`contains_reference`, the headline `correct`, and `outcome`.

The fold: symmetric letter folds (standalone hamza ء→ا, bare alef-maqsura ى→ي) are canonical in
`score_normalize`; the long ā (dagger-alif ـٰ and the ىٰ digraph) is matched as an **optional** alef
(`ا?`) with whitespace-flex between Arabic letters, word-bounded, and direction-independent (the
reference pattern is matched against the answer in both its dagger-deleted and plene forms).

## Lessons learned

- **The hard part was NOT a character fold — it was that the long ā is lexically optional.** Standard
  Imla'i writes the long ā as a full alef for the plene class (الكتاب, سبحان) but OMITS it for the
  defective-spelling (رسم ناقص) class (هذا, ذلك, الرحمن, لكن). A context-free `dagger→ا` fold
  therefore *un-credits* the defective class — it would mark `هذا`/`الرحمن` wrong, the inverse of
  the spec's purpose, and in prototyping it flipped two verbatim-correct committed tutorial cells to
  incorrect. Optionality cannot live in a canonical string, so it had to live in the containment
  regex. **Lesson: an orthographic "equivalence" that is present-on-one-side / absent-on-the-other
  is not a fold; it is an optional match.**
- **A strict-superset containment is the safe way to change a scoring headline.** Defining the new
  predicate as `bounded_contains OR fold_match` makes `normalized=1 ⇒ contains=1` true by
  construction, guarantees the change only ADDS credit, and shrinks the rebaseline to one submetric
  family — which also made the witness and the #48 rebase far simpler.
- **Put a fold in the scoring-comparison path, not the shared `normalize()`.** `generate.py` and
  `editions.py` share `normalize()`; folding there would have moved the committed question-set
  `ANCHOR_DIGEST` and touched the copyright-audit path. Keeping it out of `normalize()` left
  generation and the audit untouched.
- **Context-free Arabic folds are provably insufficient** and some necessary folds merge rare
  distinct-word minimal pairs (the 10-bucket residue below). The honest gate is no *wrong credit*,
  enforced by hand-verifying every moved cell at scoring granularity, with the vocab residue pinned
  as a drift-detecting allow-list — not a literal zero-collision rule.
- **Cross-builder thread reuse paid off**: aspir-48's thread surfaced the summary.json/summary.md
  "splice scar" (naive regeneration nulls the panel; the renderer emits extra columns that break the
  committed-summary guards) before I hit it.

## Accepted collision residue (known limitation, architect-approved 2026-10-29)

10 QUL word-buckets where a necessary fold merges genuinely distinct words sharing a consonantal
skeleton; pinned in `test_arabic_orthography_fold.py`:
- hamza (ء→ا): سواء/سوء, جزاء/جزء, وراء/ورءا, ملأ/ملء, شىء/شيـٔا, برىء/بريـٔا
- maqsura (ى→ي): نبى/نبّئ, قرى/قرئ, أمرى/امرئ
- optional-long-ā branch: رَأَىٰ/رَءَا

Benign at verse-length references; the no-wrong-credit gate catches any that would mis-credit a
committed answer.

## Consult trail (Phase 1)

Spec: 1 iteration (codex + claude, both REQUEST_CHANGES → folded). Plan: 2 iterations. Implement
phase_1: 3 iterations — iter2 caught the blocking dagger defect (→ the containment-only pivot,
architect-endorsed); iter3 caught direction-independence, a dead-fold-branch whitespace bug for
newline-bearing hadith references, and the diagnostic's blind spot (now sweeps both answer forms).

## Moved numbers (filled in Phase 2)

_To be completed after the rebaseline over the post-#48 baseline — per-run, per-task accuracy and
coverage deltas, the pre-registered flip set, and the hand-verification method._

## Flaky tests

None observed.
