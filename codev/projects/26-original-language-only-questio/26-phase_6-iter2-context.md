# Phase 6 iter-2 context — what changed since iter-1

Both iter-1 reviewers returned REQUEST_CHANGES. All findings accepted and fixed in commit
`d068d6f`. Full rebuttal: `26-phase_6-iter1-rebuttals.md`. Summary for this re-review:

1. **Generation-invariance anchor restored (codex #2, claude #1/#2).** New
   `pipelines/tests/test_original_run_regression.py` with two guards:
   - `test_rescoring_committed_original_run_reproduces_scores` — re-scores
     `runs/original-2026-10-21/answers.jsonl` byte-for-byte vs committed `scores.jsonl` (always runs).
   - `test_regenerating_original_run_reproduces_digest` — regenerates from the committed manifest's
     own `inputs`/`seed`/`per_text`/`negatives_share` via the real `cli.generate` path and pins digest
     `ca5b5d5372f81603` + corpus hash (skips if `texts/standardized/` absent).
   The `test_first_run_regression.py` docstring now points at this concrete guard. Suite: **364 passed**
   (+2).

2. **False headline claims corrected (codex #1).** KJV is 100% for the two frontier models only
   (`gpt-oss-20b` 16%); opus is **86–100%** (not 93–100%) across English texts. Fixed in
   `runs/original-2026-10-21/README.md` and `TUTORIAL.md`.

3. **TUTORIAL four-contestant framing reconciled (claude #3).** §2 scopes the four-contestant /
   search-on-off language to the reader's own tutorial panel and notes the shipped reference run is
   three models, search-off (three rows, no search comparison); §8 leaderboard/standings updated to
   match.

4. **README audit quote fixed (claude #4).** Now quotes `audit runs/original-2026-10-21` →
   `1 path(s)` (the previous `2 path(s)` was the two-arg `audit runs/… texts/standardized`).

5. **verify_source refused = 0/357 (claude note).** Acknowledged as a known evidence gap (the
   negation-evasion refusal path is covered by unit tests in `test_score.py`; no live cell triggered
   it); to be carried into the review doc.

No changes to the run artifacts themselves (`answers.jsonl` / `scores.jsonl` / `summary.*` / manifest)
— re-score remains byte-for-byte, audit origin-clean. Only the README prose, TUTORIAL prose, and tests
changed.
