# Phase 2 — iter 2 context (what changed since iter 1)

Both iter-1 consults were REQUEST_CHANGES (HIGH) and agreed the core design is correct and
non-circular (58 movers all `incorrect→correct`, SIM frozen recomputed from `b93e881`, splices
byte-identical, both lanes green). All flagged items are folded — please verify the fixes:

1. **`jev_agreement.{json,md}` regenerated (was the blocking item for both reviewers).**
   `runs/tutorial-2026-10-11/jev_agreement.{json,md}` is regenerated from the committed
   `judgments.jsonl` against the folded `scores.jsonl` (free, deterministic). Containment agreement
   0.9325 → **0.9825** (both 239 → 259, judge-only 27 → 7, deterministic-only 0 throughout). The
   README note was rewritten from "historical / read refusal from summary.json" to the current,
   consistent framing and now surfaces the corroboration. Verify the file agrees with its source
   scores and the README no longer disclaims the wrong (refusal) column.

2. **Witness pins EXACT cell identities, not counts.** `test_orthography_rebaseline.py` now pins the
   exact `(model_id, question_id)` orthographic-mover set per run (tutorial 20, original 15,
   first-run ∅, exp-ar 14, exp-en 9), re-derived via `fold_aware_contains ∧ ¬bounded_contains` and
   asserted as exact set equality. Added `test_summary_agrees_with_scores` (recompute from
   `scores.jsonl`) guarding the surgical splices — notably `original`'s summary, which had no pin.
   Suite 625 → 629.

3. **Directionality claim narrowed (claim fix, not code).** The `fold_aware_contains` docstring no
   longer over-claims full direction-independence: the plene answer form is load-bearing (14
   committed cells match only via it), but a reference *itself* written in mixed Imla'i (no daggers
   to carry the per-position optionality) is not fully matched. This never arises on the committed
   corpora (references are always the corpus/Uthmani orthography). Documented in the docstring and
   the review's known-limitations beside the Q14:34 `ءَا↔آ` residual.

Full suite: pipelines 629 pass / 2 skip; viewer 187 pass; copyright audit OK. `normalize()` and the
equality submetrics remain byte-stable; only `contains_reference`/`correct`/`outcome` move.

Rebuttals: `52-phase_2-iter1-rebuttals.md`. Review doc: `codev/reviews/52-score-treat-uthmani-and-imla-i.md`.
