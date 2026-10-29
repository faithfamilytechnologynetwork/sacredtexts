# Phase 1 (implement) — Rebuttal to iteration-2 consults

Both REQUEST_CHANGES (HIGH). claude found a **blocking correctness defect** that triggered a
design pivot (architect-endorsed 2026-10-29); codex found two precise containment/pinning bugs.
All accepted. Every claim was re-verified against the code and corpus before changing anything.

## claude — BLOCKING: `dagger→alef` makes the diacritic load-bearing (design pivot)

claude proved the `dagger→ا` fold un-credits the **defective-spelling (رسم ناقص)** class: Imla'i
writes the long ā as a full alef for the plene class (`الكتاب`, `سبحان`) but **omits** it for
`هذا`/`ذلك`/`الرحمن`/`لكن` — a **lexical**, not positional, split, so no position predicate fixes
it. Measured: 2,276 of 2,648 dagger-bearing corpus words stopped matching a dagger-omitting answer,
and **two verbatim-correct committed tutorial cells** (`haiku/retrieve_quote-07ca676a80ab`,
`-5c645a8301ad`) flipped `normalized=1,correct=1 → 0/0/0`. That is the spec's own harm inverted.

**Fix (claude's direction, architect-endorsed, strictly dominant):** the long-ā alef is made
**OPTIONAL** and ALL orthographic flexibility moves into the containment predicate; `normalize()`
and the equality submetrics (`exact`/`normalized`/`token_f1`) are **unchanged**. Specifically:
- `fold_arabic_orthography` now does only the SYMMETRIC letter folds (ء→ا, and a **bare**
  alef-maqsura ى→ي — a ى carrying a dagger is left alone, else the digraph's ā would collide
  `ءَاتَىٰنَا` "He gave us" with `ءَاتَيْنَا` "we gave").
- new `fold_aware_contains` = `bounded_contains OR` a fold match built from the reference with an
  OPTIONAL `ا?` at each dagger/`ىٰ` position, symmetric folds, and whitespace-flex between Arabic
  letters, word-bounded. Being `OR bounded_contains` makes it a strict **superset**, so
  `normalized=1 ⇒ contains=1` holds and the fold only ADDS credit.

Validated: the 2 tutorial cells preserved (normalize unchanged); plene (`الكتاب`), defective
(`هذا`/`الرحمن`), digraph (`أتاكم`), word-final (`على`), hamza-seat, and the يَـٰبُنَىَّ↔يَا بُنَيَّ
word boundary all credited; experiment still converges; negatives (`therapist`, `Jude 1:3`↛`1:30`,
`١ ٣`≠`١٣`, sub-word `هدي`) rejected; strict-superset asserted (no cell lost). Spec + plan +
`score.py` docstring updated to record why the equality-fold was abandoned, with `هذا`/`الرحمن` as
the motivating counterexample (architect directive). **Plan/witness blast radius shrank**: only
`contains_reference`/`correct`/`outcome` move; all similarity submetrics (Arabic included) are
frozen, which simplifies the witness and the #48 rebase.

**Merge-only diagnostic (claude):** the Phase-1 corpus diagnostic enumerated only *merges* and so
could not see this *loss* class. Under the pivoted design the loss class is gone by construction
(the dagger is deleted, not promoted; `normalize()` is untouched), and the strict-superset property
of `fold_aware_contains` is the guard that there are no credit losses. The diagnostic remains, now
over the symmetric-fold residue.

**Minor (claude):** the misleading `ذَٰلِكَ` vs `ذالك` test is gone (replaced by the real
defective-spelling assertion `score_normalize("ذَٰلِكَ")=="ذلك"` and the preserved `normalize()`
match). Edits are now committed (this rebuttal ships with them).

## codex — two containment/pinning bugs (fixed, and carried into the pivot)

1. **Arabic-Indic digits treated as Arabic in the ws-flex** (`١ ٣` matched `١٣`). FIXED: the
   whitespace-flex is gated on Arabic **letters** (category L), which excludes digits (Nd), so
   numeric separators are preserved. Negatives added (`الآية ١ ٣`↛`١٣`, `سورة ١:٣`↛`١٣`). Carried
   into `_fold_containment_pattern` in the pivoted design.
2. **Allow-list froze only bucket keys, not members.** FIXED: `_ACCEPTED_DISTINCT_WORD_MERGES` now
   pins each bucket's **strict-skeleton SET**, and the test asserts per-bucket skeleton membership —
   so a new distinct word entering an existing bucket (which would not change the key set) fails.

## Net

Suite **575 passed / 2 skipped**; all four committed-run regression guards unchanged and passing
(`normalize()` byte-identical, `ANCHOR_DIGEST` stable). The blocking defect is resolved by a
simpler, safer, strictly-dominant design that the architect endorsed; the two codex bugs are fixed
and folded into it.
