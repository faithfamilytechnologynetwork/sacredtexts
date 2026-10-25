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
  (`token_f1`→`tokenF1`, `contains_reference`→`containsReference`, `n_candidates`→`nCandidates`,
  `missing: false`) and calls `classifyFailure`.

Every branch of the classifier has a case; add one when a branch is added. All strings are
synthetic — no restricted-corpus text (NABRE, TLG) ever appears in a committed fixture.
