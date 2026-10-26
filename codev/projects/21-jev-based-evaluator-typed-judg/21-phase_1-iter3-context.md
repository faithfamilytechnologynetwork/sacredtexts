### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Prior findings addressed, but resume still accepted malformed or mixed-build sidecar rows (`_load_existing` validated only `rubric_id`, never each existing row's `judge_model_resolved` against the manifest), violating the no-mixed-build invariant.
- claude: APPROVE — All iteration-1 findings from both reviewers genuinely fixed and verified (403 passing, working CLI path, Karr authorship intact, committed evidence untouched). Five non-blocking items: judge-summary/judge fail-open on a missing path; `_load_manifest` not requiring a non-empty resolved build; the `--yes` budget gate untested; `_single_question_set_digest` tolerating a present/absent mix; the thread stale at "399 passed".

### Builder Response to Iteration 2
# Spec 21 — Phase 1 (Jev judge pass + CLI) iteration 2 rebuttal

Two reviews: **codex REQUEST_CHANGES** (one blocking finding) and **claude APPROVE** (five
non-blocking items). Both converge on the same area — the "no mixed-build files" invariant for a
hand-edited or half-written sidecar. All points accepted and fixed. Full suite now **410 passed, 1
pre-existing skip** (was 403; +7 tests).

## Accepted and fixed

**codex (blocking) — resume trusted existing rows' build.** `_load_existing` guarded only
`rubric_id`; it never checked each existing row's `judge_model_resolved` against the manifest's
pinned build, so a sidecar whose manifest pins build X could carry a row from build Y and resume
would accept it and append more. Fixed: `_load_existing(path, *, pinned_build)` now (a) requires
every row to carry a non-empty `judge_model_resolved`, and (b) fails fast if it differs from the
manifest's pinned build. Both `estimate` and `judge` pass `manifest["judge_model_resolved"]` in.
New tests `test_existing_row_build_mismatch_on_resume_fails_fast` and
`test_existing_row_without_build_on_resume_fails_fast`.

**claude #4 (sibling, latent) — manifest missing the resolved build.** A hand-edited manifest with
no `judge_model_resolved` left `established[0] is None`, so the next response would silently re-pin
the build — the same hole, on the manifest side. `_load_manifest` now fails fast when the manifest
has no non-empty `judge_model_resolved`. New test `test_manifest_without_build_fails_fast`.

**claude #1 — `judge-summary` on a missing path reported zeros, exit 0.** Fixed in the CLI command
(not `summarize`, whose absent-file-is-zero behaviour `judge` itself relies on): `judge-summary` now
raises `sidecar not found` before summarizing. Test `test_cli_judge_summary_missing_sidecar_is_a_clean_error`.

**claude #2 — `judge` on a missing answers file raised a raw `FileNotFoundError`.** Now guarded with
the `typer.BadParameter("input path not found: … — run collect first")` pattern every other command
uses. Test `test_cli_judge_missing_answers_file_is_a_clean_error`.

**claude #3 — the `--yes` budget gate had no automated test.** New CLI test
`test_cli_judge_without_yes_refuses_to_spend` (`CliRunner`): without `--yes`, exit 2, `jev.judge`
never called, no sidecar written. Done now (claude asked for it before Phase 4).

**claude #5 — `_single_question_set_digest` tolerated a present/absent mix.** Now all-or-none: a mix
fails fast. Latent (not reachable from `collect` output). Test
`test_mixed_question_set_digest_presence_fails_fast`.

**claude #6 — thread not updated for iteration 2.** `codev/state/aspir-21_thread.md` updated with the
iter-1/iter-2 loop, the live-smoke numbers (refusal_p 0.97, build `typesafe/jev-1.14-20261014`,
$0.000027), the git-divergence resolution, and the 410-passed count.

## Disagreements
None. codex's finding and claude's #4 are two faces of one real invariant gap; the rest are genuine
fail-open/consistency/coverage fixes.

### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code (iter-2 fixes are in commit 1e391d2).
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting.
3. Do not re-raise concerns that have been explained as false positives with valid justification.
4. This is iteration 3 (porch max_iterations). codex's one iteration-2 blocker (mixed-build resume guard) is now fixed and tested; verify against `pipelines/sacredbench/jev.py::_load_existing` / `_load_manifest` and `pipelines/tests/test_jev.py`.
