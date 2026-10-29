# PR body draft (Spec 52) — fill the moved-numbers after the Phase-2 rebaseline

**Title:** `[Spec 52] Score Uthmani and Imla'i Arabic orthographies as equivalent (prereq for #39)`

---

## What & why

A model that reproduces a Qur'anic verse correctly but in a different orthography than the QUL
Uthmani corpus is no longer penalised. The 2026-10-29 Arabic-prompt experiment showed Arabic-
scaffolded prompts switch models to standard Imla'i output, costing ~8–11 measured accuracy points
that were entirely a scorer artifact — this is the declared prerequisite for #39 (the Arabic-
instruction subset). Requested by Nancy in the working group.

## How

All orthographic flexibility lives in the containment predicate `fold_aware_contains`, a strict
**superset** of the old `bounded_contains`:
- symmetric letter folds (standalone hamza ء→ا, bare alef-maqsura ى→ي) are canonical in
  `score_normalize`;
- the long ā (dagger-alif ـٰ / the ىٰ digraph) is matched as an **optional** alef, because Imla'i
  writes it plene for some words (الكتاب) and omits it for the defective-spelling class (هذا,
  الرحمن) — a lexical, not positional, distinction that a context-free fold gets wrong;
- whitespace-flexed between Arabic letters (Uthmani one-word ↔ Imla'i two-word), word-bounded,
  and direction-independent.

`normalize()` and the similarity submetrics (`exact`/`normalized`/`token_f1`) are **unchanged**, so
generation's question-set digest and the copyright audit are untouched and only `contains_reference`
/ `correct` / `outcome` move. The change is a **sanctioned, oracle-witnessed rebaseline**:
non-Arabic and all similarity projections are frozen against pre-change SHAs, and every moved Arabic
cell is pre-registered and hand-verified.

## Rebaseline (moved numbers)

_Filled after Phase 2 — per-run accuracy/coverage deltas for tutorial / original /
exp-arabic-prompts, and the pre-registered flip set. Surfaced to the architect before merge._

## Known limitation

10 rare distinct-word minimal pairs share a skeleton after a necessary fold (see the review doc and
`test_arabic_orthography_fold.py`); accepted, pinned as a drift-detecting allow-list, and harmless
at verse-length references.

## Coordination

Built after #48 (refusal decline-cues) per the architect's merge order; rebased onto it and the
orthography witness re-run over the post-#48 baseline.

## Tests

Full suite green (pipelines pytest + viewer vitest); copyright audit passes; committed-run guards
and `ANCHOR_DIGEST` as expected (similarity frozen, only containment/headline moved).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
