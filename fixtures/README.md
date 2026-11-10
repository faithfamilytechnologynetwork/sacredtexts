# Cross-language shared fixtures

Fixtures asserted by more than one app's test suite. A fixture lives here precisely because
two implementations in different languages must agree, and a shared file is the only thing that
makes the agreement a test rather than a hope.

## `failure_kind_cases.json`

The failure-kind taxonomy is implemented twice — `pipelines/sacredbench/failure_kind.py`
(`classify_failure`) and `apps/viewer/src/lib/failureKind.ts` (`classifyFailure`). They must
return the same kind for the same `(task, correct, refused, answer, expected, metrics)` input, or
the viewer's badge disagrees with the paper's counts. This fixture is the single source both test
suites load:

- `pipelines/tests/test_failure_kind.py` splats each case's fields straight into
  `classify_failure(**…)`.
- `apps/viewer/src/lib/failureKind.test.ts` maps the snake_case fields to the TS camelCase input
  (`token_f1`→`tokenF1`, optional `token_f1_base`→`tokenF1Base`, `contains_reference`→`containsReference`, `n_candidates`→`nCandidates`,
  `missing: false`) and calls `classifyFailure`.

Every branch of the classifier has a case; add one when a branch is added. All strings are
synthetic — no restricted-corpus text (NABRE, TLG) ever appears in a committed fixture.

## `review_sample.json` + `review_gold_set.jsonl`

The review gold set (Spec 154) has two writers — the viewer's review page (the gold-set
download, Spec 154 phase 5) and `pipelines/sacredbench/review_compare.py` (`gold_row` +
`dumps_gold_rows`) — and is read by `review-compare`. They must write the same bytes for the same sample and labels, or
a downloaded gold set and the Python comparison disagree on what was labelled.

- `review_sample.json` is a sample in the `review-sample` format: 8 cells, one per task in
  `islam/native` (Arabic, right-to-left) and `hinduism/english`. Its prompts, expected texts and
  sources are real FAccT questions; the answers and run (`fixture-run`, models `model-a` /
  `model-b`) are made up. Two `shown` verdicts stand for an older matcher, so the current scorer
  moves one cell to `fixed` and one to `broken` (see `pipelines/tests/test_review_compare.py`).
- `review_gold_set.jsonl` is that sample labelled by one reviewer. It includes a `cant_judge`
  row and a defect-flagged row.

`pipelines/tests/test_review_compare.py` rebuilds the gold set from the sample and the labels
and compares bytes, and pins the comparison numbers on it.
