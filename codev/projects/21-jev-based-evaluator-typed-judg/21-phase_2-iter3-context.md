### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Core registration and opt-in provenance work is sound, but provenance can be falsely stamped and documentation contradicts the sidecar-only contract.
- claude: APPROVE — Phase 2 deliverables are complete and correct — non-inline/verdict-less `jev` registration, explicit `--judgments` provenance validated before any write, fixed `test_graders.py` fixture, recipe extended; only doc-accuracy and dedup nits remain.

### Builder Response to Iteration 1
# Phase 2 — iteration 1 rebuttal

**Reviews**: codex `REQUEST_CHANGES` (2 blocking) · claude `APPROVE` (5 non-blocking).
Both converge on the same two substantive points (provenance can be falsely stamped; the "merge
into scores.jsonl" wording contradicts the sidecar-only contract). Both actioned. Suite after
folding: **425 passed, 1 pre-existing skip** via `.codev/checks/test.sh` (was 423; +2 net tests).

---

## codex #1 (BLOCKING) — `load_provenance` accepts an empty/absent sidecar → false provenance
**Agreed; fixed.** The original `load_provenance` validated only `<path>.manifest.json`, so
`score --judgments <empty-or-missing-sidecar>` would stamp a judge build into `summary["judge"]`
although zero verdicts exist — provenance would lie. (My own iter-1 fixtures wrote empty sidecars,
which wrongly normalised this case; those fixtures now write a real row.)

Fix (`jev.py:load_provenance`): after the manifest checks, the sidecar file must **exist** and carry
**at least one** judgment, and **every row must agree with the manifest's resolved build and
question-set digest**. This reuses `_load_existing(path, pinned_build=resolved, pinned_qsd=...)` — the
same row guard the resume path uses — so a build-mismatched, set-mismatched, or build-less row fails
fast (this also satisfies codex's "row identity agrees with the manifest" and reduces the duplication
claude #3 flagged). An empty sidecar now raises `no judgments recorded`; a missing sidecar raises
`the judgments file is missing`.

New tests: `test_judgments_empty_sidecar_fails_fast`, `test_judgments_row_build_mismatch_fails_fast`
(both in `test_score.py`). Real-CLI smoke confirms the empty-sidecar fail-fast and that a real-row
sidecar still stamps provenance at exit 0.

## codex #2 / claude #1 (BLOCKING / non-blocking) — docs claim a merge into `scores.jsonl`
**Agreed; fixed.** Part 2 is sidecar-authoritative per the spec; no per-row merge into `scores.jsonl`
is built here (a merge is a deferred follow-up). Corrected everywhere the stale "merges its
`metric_keys` into each row" / "merged into scores.jsonl" wording appeared:
- `graders.py` module docstring — now: the pass "writes its typed verdicts to a **sidecar** … in this
  part the sidecar is authoritative and nothing is merged into `scores.jsonl` (a per-row merge is a
  documented follow-up)".
- `graders.py` `jev` registration comment — "its own pass (jev.py) WRITES to a sidecar".
- `graders.py` `resolve_evaluators` error message (pre-existing Spec-15 text) — now: "its verdicts are
  written to a sidecar by its own resumable pass (`judge`), never into scores.jsonl". The
  `separate-pass` token the CLI/unit tests match on is retained.
- `CODE_WALKTHROUGH.md:243` retained clause — same reword; the worked-example paragraph already said
  the pass "never touches `scores.jsonl`".

## claude #2 (non-blocking) — CODE_WALKTHROUGH line pointers drifted
**Agreed; fixed.** This phase's additions to `graders.py` moved the cited symbols. Updated the
pointers to the exact current lines: `GRADERS` 49→54, `Grader` 33→38, `resolve_evaluators` 86→93,
`submetrics_for` 111→119, `Grader.default` 37→42. (`test_code_walkthrough.py` only range-checks, so it
would not have caught the drift — the pointers are now exact regardless.)

## claude #3 (non-blocking) — `load_provenance` duplicates `_load_manifest`
**Partially actioned; remainder declined with reason.** The row-validation duplication is removed:
`load_provenance` now delegates row checks to `_load_existing` (shared with the resume path). The
remaining manifest-field checks are kept **deliberately not** delegated to `_load_manifest`, because
`_load_manifest` binds on `index_digest` (a resume-path concern) and provenance must stay decoupled
from index state — a Phase-3 sidecar judged *with* an index must still be usable for `score
--judgments` provenance. The two validators are small and their messages are intentionally
provenance-specific.

## claude #4 (non-blocking, explicitly out of scope) — provenance binds on question-set digest only
**Acknowledged; not changed (within phase-2 contract).** A sidecar from a *different collect run over
the same question set* still validates, because the plan scoped phase-2 provenance to manifest fields
(build + rubric + qsd). The row-level `answer_digest` cross-check against the specific answers is a
sensible follow-up both reviewers agree is out of phase-2 scope; recorded in the thread as a follow-up.
(Note: the new row-identity check does bind rows to the build + qsd, closing the empty/mixed-build
hole; the remaining gap is only "same question set, different collect run".)

## claude #5 (non-blocking) — test nits
**Partially actioned.** Moved the mid-file `from sacredbench.jev import …` in `test_score.py` to the
top import block (the E402-style nit). Kept the `"cost" not in json.dumps(summary).lower()` assertion:
it deliberately mirrors the established `test_tutorial_run.py:66` guard and states the acceptance
criterion directly ("no cost field in the summary"); added a comment clarifying the sidecar row's own
`usage.cost` never reaches the summary.


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Phase 2 is largely correct, but provenance validation still accepts a skeletal row containing no actual typed verdict, allowing false judge provenance.
- claude: APPROVE — Both iteration-1 blockers are genuinely fixed in code and tests; phase-2 deliverables are complete, the seam is coherent, and the summary addition is viewer-safe — only test-hygiene and error-wrapping nits remain.

### Builder Response to Iteration 2
# Phase 2 — iteration 2 rebuttal

**Reviews**: codex `REQUEST_CHANGES` (1 blocking) · claude `APPROVE` (confirms both iter-1 blockers
genuinely fixed; 4 minor nits). Suite after folding: **427 passed, 1 pre-existing skip** via
`.codev/checks/test.sh` (was 425; +2 tests).

---

## codex (BLOCKING) — provenance still accepts a *skeletal* row (no actual verdict)
**Agreed; fixed.** My iter-1 fix routed row validation through `_load_existing`, which only checks
`rubric_id` / resolved build / question-set digest. codex is right: a row carrying **only** those
three fields keys as `(None, None, None)` — non-empty — so `summary["judge"]` would still be stamped
for a sidecar that holds no real judgment.

Fix: `_load_existing` gains an opt-in `require_verdict` flag (the resume path leaves it `False` — its
own writes are always complete). When set (only by `load_provenance`), each row must additionally pass
`_validate_verdict_row`: non-empty `question_id` / `model_id` / `answer_digest`, numeric
`refusal_p` / `matches_requested_p` in [0,1], and either a `kind` label or the
`equivalence: "not_evaluated"` sentinel — exactly codex's required set. A skeletal or verdict-less row
now fails fast (`not a complete judgment` / `refusal_p is not a probability`).

New regression tests: `test_judgments_skeletal_row_fails_fast` (codex's exact case — only the three
identity/pin fields) and `test_judgments_row_missing_verdict_fields_fails_fast` (full identity but no
probabilities). Real-CLI smoke: a skeletal-row sidecar now errors `row missing question_id; not a
complete judgment`; a real-row sidecar still stamps provenance at exit 0.

## claude (APPROVE) — minor nits
1. **`test_separate_pass_metric_merge_path` was vacuous.** *Fixed.* Renamed to
   `test_separate_pass_keys_match_the_sidecar_contract` and driven from `GRADERS["jev"].metric_keys`,
   so a drift between the registration and the sidecar schema now fails the test.
2. **Bare `json.loads` on the manifest.** *Fixed.* `load_provenance` and `_load_manifest` now wrap the
   manifest parse in `JevError` (`{mpath}: not JSON (...)`), matching how `_load_existing`/`summarize`
   already wrap row JSON errors — the fail-fast path is uniform.
3. **`metric_keys` declares `kind`, which a no-index row writes as `equivalence: "not_evaluated"`.**
   *Acknowledged, no change.* Nothing consumes a non-inline grader's keys today; recorded as a note
   for the deferred per-row merge pass (thread follow-up).
4. **CLI error surface (`--judgments` JevError vs `--evaluator` BadParameter).** *No change — not a
   traceback.* `cli.main()` catches `JevError` and prints `error: <msg>` at exit 2 (verified: the
   skeletal-row smoke above prints a clean one-line error, no traceback). This matches how the other
   `ScoreError` raises in the same command already surface; claude also recommended leaving it.

claude also independently verified the new `summary["judge"]` key is viewer-safe
(`apps/viewer/src/lib/localResults.ts` whitelists summary keys and drops unknowns) and that committed
run evidence is untouched.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
