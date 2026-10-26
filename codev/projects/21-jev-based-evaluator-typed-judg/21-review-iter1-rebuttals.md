# PR #47 review — iteration 1 rebuttal

**Reviews**: codex `REQUEST_CHANGES` (4 provenance/fail-fast gaps + stale doc) · claude `REQUEST_CHANGES`
(the dropped manual disagreement review + minors) · architect integration review (consolidated the two,
added two blockers of its own). **All folded** as validation-path-only changes — tip `c4e8b92`. The
committed sidecar/agreement files are byte-unchanged (no re-judge, no new live spend; project total
still ≈ $0.0118). Full suite **565 passed, 1 pre-existing skip**; audit green; `git diff` over `runs/`
empty (same 4 added files, unmodified).

## Blocking — all Addressed

1. **Equivalence-index digest trusted, not verified** (codex) → **Addressed**. `load_equivalence_index`
   recomputes `sha256(file_bytes)[:16]` over the JSONL it loads and fails on mismatch with the manifest.
   Test: `test_load_equivalence_index_tampered_file_same_row_count_fails_fast` (edit a wording in place,
   row_count unchanged → rejected).
2. **`score --judgments` didn't bind judgments to the scored answers** (architect) → **Addressed**.
   `load_provenance(..., answer_keys=…)` now requires every judged `(question_id, model_id,
   answer_digest)` to be among the answers being scored; `score.py` passes those keys. The old
   "accepts `a0` for answer `x`" fixture was inverted → `test_judgments_from_different_answers_rejected`.
3. **`_single_question_set_digest` accepted a digest-less answers file** (architect) → **Addressed**. It
   now raises when no non-empty digest is present (matching `collect`/`score`). Test:
   `test_judge_requires_a_question_set_digest`.
4. **`interpret()` under-validated the typed choice** (codex) → **Addressed**. All `_KINDS` labels must
   be present, every `kind_probabilities` value and `kind_confidence` a probability in [0,1], and
   `usage` cost/tokens non-negative. Tests: `test_interpret_rejects_incomplete_or_out_of_range_choice`,
   `test_interpret_rejects_negative_usage`.

## Minor — all Addressed (in this PR)

5. **`jev_agreement` re-declared `JUDGED_TASKS`** → **Addressed**: imported from `jev` (single source).
   Also made the join strict (codex consult #3): every judgment needs a matching answer + `answer_digest`;
   duplicate `(qid, model_id)` fails. Tests added.
6. **Retry predicate precedence** (jev.py) → **Addressed**: parenthesized the `and` inside the `or`.
7. **Stale test count in the review** → **Addressed**: now 565.
8. **`graders.py` "kind" unconditional** → **Addressed**: one-line note that it is index-conditional and
   the deferred merge pass must treat it as optional.
9. **`TYPICAL_COST_USD`** nudged 2.7e-5 → 3e-5 so the pre-flight estimate is conservative (claude).

## claude's main finding — Addressed

The **manual disagreement review** (all 35 cells, 3 categories) that the template rewrite had dropped is
**restored** to the review as a `## Validation on the committed tutorial run` section, with the agreement
table, raw per-class distributions, and the three disagreement classes.

## Follow-ups (filed as issues, architect-directed; not in this PR)

- **#48 (F1)** — refusal-classifier false positives on web-search hedges (the 11 cells), adjudication
  against `outcomes.py`; ties into #41.
- **#49 (F2)** — deferred per-row merge-into-`scores.jsonl` (kind index-conditional), running-spend
  circuit breaker, self-describing agreement report (`judge_model_resolved`/`rubric_id` header +
  `n_indexed_other_wordings`).

No disputes — every point was legitimate and actioned. Not merged; holding for the human `pr` gate.
