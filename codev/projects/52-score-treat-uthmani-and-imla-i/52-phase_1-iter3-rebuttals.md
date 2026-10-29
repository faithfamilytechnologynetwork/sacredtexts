# Phase 1 (implement) — Rebuttal to iteration-3 consults

Both REQUEST_CHANGES (HIGH); both confirmed the pivoted containment-only design is correct and
corpus-validated (claude: superset is structural, defective-spelling fix real, digraph guard holds
— maqsura→dagger gap histogram `{0: 2242}`; direction-independence now data-backed). The remaining
items — one real blocking bug, one diagnostic-coverage gap, direction-independence, and the
duplication root cause — are all fixed.

## codex — direction-independence (accepted)

`fold_aware_contains` only made the long-ā optional when the **reference** had a dagger, so an
Imla'i reference vs Uthmani answer failed — against the spec's "both directions" / future-Imla'i-
corpus assumption. FIXED: the reference pattern is now matched against the answer in BOTH its
default (dagger-deleted `score_normalize`) and **plene** (`_answer_plene_form`, dagger→alef) forms,
so the equivalence is symmetric. Kept the **per-position** `ا?` (a uniform plene/defective fold
cannot handle a mixed verse like `هَٰذَا ٱلْكِتَٰبَ` — defective `هذا` + plene `الكتاب` in one
reference). Added reverse-direction + mixed-verse tests.

## claude — blocking whitespace bug + diagnostic coverage + duplication

1. **BLOCKING: `_fold_containment_pattern` omitted `normalize()`'s whitespace collapse.** A `\n`/`\t`
   in a reference compiled to a required literal newline the (space-collapsed) answer can never
   contain, killing the fold branch for the **23 newline-bearing Arabic `retrieve_quote`
   references** in `original-2026-10-21` (hadith chains; 0-cell delta today but #39 is hadith-heavy
   and Phase 2 would freeze an inert capability). FIXED: the builder now folds any whitespace
   (`ch.isspace()`) to a single space, mirroring `_WS_RE`. Added a multi-line-reference test
   (verified `ٱلْكِتَٰبِ\nسُبْحَٰنَ` now matches).
2. **Diagnostic blind to the credit-granting branches.** The sweep covered only `score_normalize`
   equality, not the `ا?`/plene branch. FIXED: it now sweeps BOTH answer canonicalisations
   (`score_normalize` and `_answer_plene_form`) and pins the union residue — **10 buckets** (the 9
   symmetric-fold buckets plus the plene-only `راا` = `رَأَىٰ`/`رَءَا`). `_ACCEPTED_DISTINCT_WORD_MERGES`,
   the `score.py` known-limitation comment, and the spec's limitation paragraph all now name the
   optional-ā class. (claude's "5 skeleton-pairs" was a coarser cross-word count; the sweep over the
   actual canonicalisations `fold_aware_contains` tries yields the one extra bucket, `راا`.)
3. **Duplication (root cause of #1).** `_answer_plene_form` was a third hand-copy of the pipeline.
   FIXED: parameterised `_normalize(text, *, fold=False, plene=False)`; `normalize`, `score_normalize`,
   and `_answer_plene_form` all delegate, so they cannot drift. Extended the Latin/Hebrew invariance
   test to `_answer_plene_form` (incl. soft-hyphen and curly quotes). The pattern builder remains a
   regex emitter (cannot share a string pipeline) but now matches `normalize()`'s passes including the
   whitespace collapse.

## Net

Suite **577 passed / 2 skipped**; the four committed-run guards and `ANCHOR_DIGEST` pass unmodified
(`normalize()` byte-identical). The capability is now direction-independent, correct for multi-line
references, de-duplicated, and its full distinct-word residue (10 buckets, both branches) is a
pre-registered allow-list for Phase-2 hand-verification.
