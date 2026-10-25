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
