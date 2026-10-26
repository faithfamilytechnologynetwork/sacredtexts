### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Equivalence lookup works, but index identity is not reliably bound to the loaded index or validated per sidecar row.
- claude: REQUEST_CHANGES — Equivalence consumer is well-built and well-tested (off-by-default, manifest/corpus_hash/digest fail-fasts, mixed-index resume all correct), but index wordings open an unguarded restricted-text path to the third-party judge, and the requested-wording exclusion is exact-string fragile.

### Builder Response to Iteration 1
# Phase 3 — iteration 1 rebuttal

**Reviews**: codex `REQUEST_CHANGES` (2 blocking) · claude `REQUEST_CHANGES` (1 blocking + 3 in-phase
+ housekeeping). Strongly convergent. All substantive findings actioned. Suite after folding:
**443 passed, 1 pre-existing skip** via `.codev/checks/test.sh` (was 437; +6 net tests). Real-CLI
dry-run (no spend) still loads the index, binds corpus_hash + question_set_digest, and stops at the
`--yes` gate.

---

## claude #1 (BLOCKING, baked constraint) — restricted text could reach the judge via index wordings
**Agreed; fixed.** `state["indexed_other_wordings"]` carries full `text` from index rows to the
Decisions API, and the loader applied no restricted check — relying on #32's producer to have
filtered is exactly the dependence the baked constraint ("guard independent of the commit-time audit
gate") rejects, and #32 isn't merged.

Fix: `load_equivalence_index(..., restricted_keys=frozenset())` now checks every wording's
`(work, version, language)` against `restricted_keys` and **fails fast** (`RESTRICTED target … broken
index`) — a producer that emits a restricted wording is a broken index, not a cell to skip. The CLI
passes the `restricted` set it already computes (`aud.restricted_keys(sources)`). New test
`test_load_equivalence_index_restricted_wording_fails_fast`.

## codex #1 / claude #4 (BLOCKING / footgun) — `judge(index=, index_digest=)` independently settable
**Agreed; fixed.** A caller could pair an index with a wrong/absent digest (my own mixed-index test
did exactly that). `judge` now **derives** `index_digest` from `index.digest`; a supplied digest that
disagrees raises; an `index_digest` without an index raises (equivalence is off — nothing to pin). The
CLI already passed `index.digest`, so it is unaffected. New tests
`test_judge_rejects_index_digest_that_disagrees_with_index`,
`test_judge_index_digest_without_index_fails_fast`; the mixed-index test was rewritten to use **two
genuinely different indexes** (different digests, same `corpus_hash`) and let `judge` derive the digest.

## codex #2 / claude resume — per-row `index_digest` not validated on resume
**Agreed; fixed.** The manifest check alone let a row with a missing/conflicting `index_digest` pass
under a matching manifest. `_load_existing` gains `pinned_index_digest` (a `_UNCHECKED` sentinel vs
the real value `None`, since a no-index sidecar legitimately pins `None`); `judge`/`estimate` pass the
run's `index_digest`, so every existing row's digest is bound to the sidecar's pinned identity. The
`load_provenance` path leaves it unchecked (provenance doesn't care about index state). New test
`test_judge_resume_rejects_row_with_conflicting_index_digest`.

## claude #2 (in-phase) — requested-wording exclusion by exact text is brittle
**Agreed; fixed.** `EquivalenceIndex.wordings()` excluded the requested wording by exact `text`
equality — fragile exactly in the Arabic/Hebrew orthographic-variance regime this diagnoses (a
one-diacritic drift between the index's text and `expected.text` would leave the requested wording in
`indexed_other_wordings` and invite a false `other_indexed_wording`). It now excludes by **`version`**
(the question's own edition, threaded from `question.source.version` through `_alternates`/`run_cell`),
with the exact-text compare kept only as a backstop. New test
`test_wordings_excludes_by_version_not_exact_text`.

## claude #3 (in-phase) — `--questions` binding to this run unverified
**Agreed; fixed.** `_run_corpus_hash` read only `corpus_hash`; a mis-pointed `--questions` (a different
run's file) would silently supply the wrong hash. It now also reads `question_set_digest` and requires
it to equal the answers' digest (computed in the CLI from the answer rows), so `--questions` must
describe *these* answers. New test `test_judge_cli_mispointed_questions_fails_fast`.

## claude #5 (housekeeping) — uncommitted phase + untracked fixtures
**Will action at the phase boundary.** Per the phase-1/2 pattern in this project (the builder commits
phase code; porch commits only `status.yaml`), phase-3 is committed when the phase completes, with the
two fixture files `git add`-ed **explicitly** (never `git add -A`). Noted so the committed suite finds
the fixtures.


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Phase 3 is largely complete, but the questions-to-answers binding still permits an unverifiable manifest.
- claude: APPROVE — Phase 3's equivalence-index consumer is complete and correct; all five iteration-1 findings verified fixed in code with tests, suite green at 443 passed.

### Builder Response to Iteration 2
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


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
