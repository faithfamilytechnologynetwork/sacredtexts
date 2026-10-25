# Phase 3 — iteration 2 rebuttal

**Reviews**: codex `REQUEST_CHANGES` (1 blocking) · claude `APPROVE` (all 5 iter-1 findings verified
fixed in code; 3 minor + housekeeping). The blocking item and claude's first minor are two sides of
the same gap; both fixed. Suite after folding: **446 passed, 1 pre-existing skip** (was 443; +3 tests).

---

## codex (BLOCKING) + claude #1 — the `--questions`↔answers digest binding was silently skippable
**Agreed; fixed on both sides.** The iter-1 binding only compared `question_set_digest` *when both
sides happened to carry one*, so it could be skipped:
- **manifest side (codex):** a questions manifest with a `corpus_hash` but **no**
  `question_set_digest` was accepted, binding the index on an unverified corpus hash.
- **answers side (claude #1):** answers with no/mixed `question_set_digest` gave `answers_digest =
  None`, short-circuiting the check so an arbitrary `--questions` corpus_hash was trusted.

Fix: under `--equivalence-index` the binding is now mandatory on both sides.
- CLI: the answers must carry **exactly one non-empty** `question_set_digest`, else `BadParameter`
  (`re-collect to a coherent set`).
- `_run_corpus_hash`: given an `answers_digest`, the manifest **must** carry a `question_set_digest`
  and it must equal it (a missing one is `BadParameter: cannot confirm --questions describes these
  answers`). New tests: `test_judge_cli_questions_manifest_without_digest_fails_fast` (codex),
  `test_judge_cli_answers_without_digest_fails_fast` (claude #1).

## claude #2 (minor) — `estimate(index_digest=…)` untested, yet it's the path the CLI hits first
**Agreed; fixed.** The CLI runs `estimate` before `judge`, so the user-visible mixed-index error
surfaces from `estimate`, while the iter-1 test exercised `judge()` directly. Added
`test_estimate_mixed_index_fails_fast` asserting `estimate` raises on a resume whose `index_digest`
differs from the pinned sidecar.

## claude #3 (minor) — a very large index row can exceed `_STATE_CHAR_LIMIT`, failing that cell forever
**Acknowledged; declined for phase-3 scope, recorded as a follow-up.** `judgment_state` already
fails fast (`exceeds the context budget`) rather than sending an oversized state to the API, so there
is no safety issue — the concern is recoverability (that cell stays pending on every retry). claude
notes it is "not reachable with the fixture or #32's current shape". Capping the number of alternates
sent would silently truncate the equivalence evidence (a semantic change), so it belongs in a
considered follow-up, not an in-phase patch. Recorded in the thread's follow-ups.

## claude #4 (housekeeping) — uncommitted phase + untracked fixtures
**Will action at the phase boundary** (the project's pattern: the builder commits phase code; porch
commits only `status.yaml`), with `pipelines/tests/testdata/equivalence_index.sample.jsonl{,.manifest.json}`
`git add`-ed **explicitly** (never `git add -A`) so the committed suite finds `INDEX_FIXTURE`.
