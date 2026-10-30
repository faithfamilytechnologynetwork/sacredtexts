# Phase 2 impl consult — iter 2 rebuttals

**claude: APPROVE (HIGH)** — "all three iter-1 blocking items verifiably folded; the 58-cell
rebaseline is minimal, non-circular, and independently corroborated with no wrong credit." Three
non-blocking COMMENTs, all folded below.

**codex: REQUEST_CHANGES (HIGH)** — one item: the Arabic-cell partition-count pin (a Phase-2
deliverable) was missing. Folded.

## codex: pin the Arabic-cell partition count — FIXED
Added `test_arabic_cell_partition_pinned`. "Arabic cell" is defined precisely (letters-only via
`_is_arabic_letter`: category L in the Arabic blocks — excludes Arabic-Indic digits and Arabic
punctuation, resolving codex's predicate-ambiguity note). Pins both arabic-expected and
arabic-either counts per run: tutorial (132, 132), original (420, 459), first-run (0, 2),
exp-ar (28, 28), exp-en (28, 29). Complements the exact mover-sets: this guards a corpus change
that alters the fold's domain even if no cell moves.

## claude comment 1: ىٰ-digraph vs bare maqsura undocumented — FIXED
Documented in the review known-limitations: a reference `ىٰ` digraph compiles to `ا?` only, so it
does not match an answer's bare maqsura/ya (`علىٰ` vs `على`). Conservative, 0 committed cells, not
widened now; flagged for #39.

## claude comment 2: summary self-consistency only guarded models[task] leaves — PARTLY FIXED
Extended `test_summary_agrees_with_scores` to also recompute and assert each model's `_overall`
roll-up. `by_tradition`/`by_text` leaves remain derived structurally by the surgical splice (copied
from a fresh `score_file` aggregation) and are correct today (independently verified by claude); a
full recompute guard for them is a reasonable future hardening but non-blocking and out of this
spec's scope.

## claude comment 3: plan's partition-count landed as mover-sets — FIXED (both now present)
Noted in the review doc; and the partition count is now explicitly pinned too (see codex item), so
it no longer reads as skipped.

Suite after fixes: pipelines 634 pass / 2 skip (witness 21); viewer 187; audit OK.
