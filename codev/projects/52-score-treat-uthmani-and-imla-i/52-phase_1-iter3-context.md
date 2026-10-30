### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Core fold logic is sound, but the containment helper is unsafe outside Arabic and the corpus collision diagnostic does not fulfill the phase plan.
- claude: REQUEST_CHANGES — The position-aware fold is correct and corpus-verified, but the whitespace-insensitive containment helper loses word-boundedness (Jude 1:3 matches 1:30) and so can't be wired in Phase 2, and the corpus diagnostic is blind to the 7 distinct-word merges it was meant to list.

### Builder Response to Iteration 1
# Phase 1 (implement) — Rebuttal to iteration-1 consults

Both reviewers returned **REQUEST_CHANGES** (HIGH) and confirmed the fold logic is correct and
corpus-verified (claude independently counted 211 medial / 400 word-final / 15 bare-medial maqsura
cases and 0 non-adjacent daggers, validating the boundary detector). Two defects + minors; all
accepted and fixed.

## Issue 1 — `arabic_ws_insensitive_contains` was script-blind and unbounded (both reviewers)

The helper deleted ALL whitespace, so it equated Latin `"the rapist"`/`"therapist"` and matched
`Jude 1:3` inside `1:30` and `هدي` inside `المهديون` — breaking the word-boundedness
`bounded_contains` guarantees, which Phase 2 makes the single shared containment contract. FIXED
with claude's strictly-dominating approach, Arabic-gated:

- **Arabic reference** → anchored pattern `(?<!\w) + \s*.join(chars of fold-normalised ref) + (?!\w)`
  — optional whitespace between characters so one-word Uthmani ↔ two-word Imla'i matches in either
  direction, while the anchors keep it bounded.
- **Non-Arabic reference** → plain word-bounded containment, unchanged (so the Latin contract and
  the non-Arabic projection freeze hold).

Added the missing negatives: `Jude 1:3`↛`1:30`, `هدي`↛`المهديون`, `the rapist`↛`therapist`, plus a
positive cross-boundary Arabic match and a non-Arabic bounded match.

## Issue 2 — the corpus diagnostic was blind to the collisions it was meant to list (both)

My `skeleton()` neutralised the fold's own alphabet (ء→ا, ى→ي), so `len(skels)==1` could not see
the one collision class the fold introduces; claude enumerated 7 genuine distinct-word merges that
passed silently, and 4 are from the **hamza ء→ا** rule the spec limitation hadn't named. FIXED:

- The diagnostic now uses a **strict skeleton** that folds only the zero-risk orthography
  (dagger/digraph→alef, wasl, marks, NFKD seats/madda) and **keeps ء and ى distinct** — so it can
  see the real collisions. The full corpus residue is **9 buckets** (claude's 7 plus `شىء/شيـٔا`
  and `برىء/بريـٔا`), now a **pre-registered, hand-annotated allow-list** (`_ACCEPTED_DISTINCT_WORD_
  MERGES`): the test asserts the residue equals it exactly, so a NEW collision (or a vanished one)
  fails and forces re-review. Every non-residue bucket is asserted to be a pure same-word
  Uthmani↔plene reunion.
- The one-sided `< 150` bound is now **two-sided** (`40 < n < 120`) so a no-op fold (0 merges) fails.
- The `score.py` limitation comment now names BOTH the maqsura and hamza classes and lists the 9;
  the spec's known-limitation paragraph is extended the same way (architect directive to document
  the residue — now covering the hamza class claude surfaced). It feeds the Phase-3 architect packet.

## Minors (COMMENT) — both fixed

- **`score_normalize` duplicated `normalize`'s body.** Parameterised a single private
  `_normalize(text, *, fold)`; both public functions delegate, so they cannot drift. The
  byte-for-byte committed-run guards confirm `normalize()` behaviour is unchanged.
- **`_folds_equal` vacuous symmetry** — simplified to one comparison, with a comment that
  direction-independence has teeth only for the containment predicate (which the helper tests cover).

## Net

Suite now **578 passed / 2 skipped**; all four committed-run regression guards unchanged and
passing (default path byte-identical). The two wiring-relevant defects that would have surfaced in
Phase 2 (unbounded containment; undocumented hamza collisions) are closed now, and the distinct-word
residue is a frozen allow-list the rest of the project builds on.


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Fold logic is sound, but containment still creates Arabic-numeral false positives and the collision allow-list does not fully freeze bucket membership.
- claude: REQUEST_CHANGES — Fold logic, residue allow-list, and unwired discipline all verify, but the dagger→alef rule makes the U+0670 diacritic load-bearing (2,276 of 2,648 corpus word-forms) and un-credits two verbatim-correct committed tutorial cells, and the merge-only corpus diagnostic cannot see that class.

### Builder Response to Iteration 2
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


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
