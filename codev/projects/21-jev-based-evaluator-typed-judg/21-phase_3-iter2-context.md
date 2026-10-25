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


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
