### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Core calculations are sound, but fail-fast evidence validation is incomplete.
- claude: REQUEST_CHANGES — Census, outcomes and the edition counterfactual all work correctly on the real run (denominator 32, 3 genuine other_edition tags), but the scores↔summary check runs in only one direction — an empty scores.jsonl still yields a full card — and the requested-edition exclusion has no non-vacuous test.

### Builder Response to Iteration 1
# Phase 2 — Rebuttal to implement iteration-1 reviews

Both **REQUEST_CHANGES / HIGH**, both verified on the real run (denominator 32, 3 genuine
`other_edition` tags), and the findings converge. **All accepted and fixed.** Suite now
**415 passed / 1 skipped** (+8 tests). Fix commit authored by me (review-response engineering;
the carry-over credit is on the Phase-2 feature commit).

## Must-fix (both reviewers)

1. **`scores.jsonl` ↔ `summary.json` verified in only one direction; `_overall` copied** (codex #1,
   claude #1 — claude probed it: an emptied `scores.jsonl` still produced a full card). *Fixed.*
   `_verify_against_summary` now (a) requires the scores' `(model, task)` set to **equal** the
   summary's, and (b) recomputes each model's `_overall` from the summed per-task scores counts and
   raises on disagreement. `_outcomes` now **derives** `overall` counts from the verified per-task
   scores (accuracy/coverage from the count-verified summary), so the card's overall can never
   contradict its own `by_task`. New tests: an empty `scores.jsonl`, a dropped task, and a corrupted
   `_overall` all raise `FacctError`.

2. **Join not one-to-one** (codex #2). *Fixed.* `_index_unique` indexes both sides, failing on a
   missing or **duplicate** `(question_id, model_id)`; `build_facct` then requires the two key sets to
   be **equal** (every score has an answer and every answer has a score). New tests: duplicate answer
   row and an unmatched answer row both raise.

3. **Requested-edition exclusion was untested (vacuous)** (claude #2). *Fixed.* Added a fixture cell
   whose answer carries only its **requested** edition's wording (KJV-requested `Test 6:6`, answer =
   the KJV wording, scored incorrect). It is in the denominator but **not** tagged; deleting the
   `passage.version == requested_version` guard now breaks `test_requested_edition_only_answer_not_tagged`.

## Minors adopted

- **`other_edition` label not in the JSON** (codex #3, claude). *Fixed.* Each tagged cell now carries
  `"tag": "other_edition"`, so the machine-readable card states the classification (Phase 3 prints it).
- **`s["task"]` could raise `KeyError` not `FacctError`** (claude). *Fixed.* `_outcome_counts` raises
  `FacctError` on a score row missing `task`; a test covers it.
- **No evidence-immutability test in this phase** (claude). *Fixed.* A test sha256s the four input
  files before and after `build_facct` + `write_facct_json` and asserts they are unchanged.
- **`per_model[model_id]` no-op seeding** (claude). *Fixed.* Replaced the bare-expression seed with an
  explicit dict assignment.

## Noted (no code change here)

- **`zero_question_languages` includes `grc` reachable only via a restricted target (TLG)** (claude).
  Defensible; recorded as a Phase-3 prose item — the card's wording will say the language is zero
  because its source is held back, not because of a coverage gap.
- **Whole-corpus conversion on every build** (claude). Fine at this scale (~0.5s); a lazy build is a
  future optimization, not a correctness issue.

## Net

Both must-fix integrity gaps are closed with revert-detecting tests, the counterfactual carries its
explicit tag, and the card's numbers are now provably consistent across `scores.jsonl`,
`summary.json`, and the card's own `by_task`/`overall`.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
