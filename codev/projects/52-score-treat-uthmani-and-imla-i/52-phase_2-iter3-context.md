# Phase 2 — iter 3 context (what changed since iter 2)

iter 2: **claude APPROVE**; **codex REQUEST_CHANGES** on one item (the Arabic-cell partition-count
pin). All folded:

1. **Arabic-cell partition pin added (codex's sole iter-2 item).** New
   `test_arabic_cell_partition_pinned` in `test_orthography_rebaseline.py`. "Arabic cell" is defined
   precisely — letters-only via `_is_arabic_letter` (category L in the Arabic blocks; excludes
   Arabic-Indic digits and Arabic punctuation, resolving the predicate-ambiguity codex flagged).
   Pins arabic-expected and arabic-either counts per run: tutorial (132,132), original (420,459),
   first-run (0,2), exp-ar (28,28), exp-en (28,29). Complements the exact mover-identity sets (guards
   corpus/question-set domain drift even when no cell moves).

2. **Summary self-consistency extended (claude comment 2).** `test_summary_agrees_with_scores` now
   also recomputes and asserts each model's `_overall` roll-up, not just the per-task leaves.

3. **Docs (claude comments 1, 3).** Review known-limitations now records: the conservative
   `ىٰ`-digraph-vs-bare-maqsura behavior (reference digraph → `ا?` only; 0 committed cells; flagged
   for #39, not widened); and that the plan's partition-count deliverable landed as BOTH the exact
   mover-sets and the explicit partition pin.

Nothing else changed: `normalize()` and the equality submetrics remain byte-stable; the 58-cell
rebaseline, regenerated `jev_agreement` (containment 0.9325→0.9825, judge-only 27→7, det-only 0),
and the surgical splices are as verified in iter 2. Suite: pipelines 634 pass / 2 skip; viewer 187;
audit OK. Rebuttals: `52-phase_2-iter2-rebuttals.md`.
