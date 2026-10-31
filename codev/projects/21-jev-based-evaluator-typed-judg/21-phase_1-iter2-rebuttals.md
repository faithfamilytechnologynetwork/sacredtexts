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

**claude #1 — `judge-summary` on a missing path reported zeros, exit 0.** Fail-open against the
project's fail-fast rule. Fixed in the CLI command (not `summarize`, whose absent-file-is-zero
behaviour `judge` itself relies on): `judge-summary` now raises `input-not-found` before summarizing.
New test `test_cli_judge_summary_missing_sidecar_is_a_clean_error`.

**claude #2 — `judge` on a missing answers file raised a raw `FileNotFoundError`.** Now guarded with
the same `typer.BadParameter("input path not found: … — run collect first")` pattern every other
command in `cli.py` uses. New test `test_cli_judge_missing_answers_file_is_a_clean_error`.

**claude #3 — the `--yes` budget gate had no automated test.** It is the single enforcement point for
"no unseen live pass" and the $8 cap, and Phase 4 runs through it. New CLI test
`test_cli_judge_without_yes_refuses_to_spend` (`CliRunner`): without `--yes`, the command exits 2,
`jev.judge` is never called, and no sidecar is written. Done now (claude asked for it before Phase 4).

**claude #5 — `_single_question_set_digest` tolerated a present/absent mix.** It silently adopted the
one digest found when some rows carried it and others didn't. Now all-or-none: a mix fails fast. Not
reachable from `collect` output (tutorial rows all carry the digest), so this is latent hardening.
New test `test_mixed_question_set_digest_presence_fails_fast`.

**claude #6 — thread not updated for iteration 2.** `codev/state/aspir-21_thread.md` still said "399
passed" and recorded only the zero-call pre-flight. Updated with the iter-1/iter-2 loop, the live
smoke numbers (refusal_p 0.97, build `typesafe/jev-1.14-20261014`, $0.000027), the git-divergence
resolution, and the 410-passed count — the durable post-merge surface Phase 4 will cite.

## Disagreements

None. codex's finding and claude's #4 are two faces of one real invariant gap; the rest are genuine
fail-open/consistency/coverage fixes.

## Note

jev.py's origin is the contributor's PR #30, carried under that authorship on the feat commit (`a7d33b2`). This
iteration's review-driven hardening is committed under my authorship, consistent with the iter-1
review/rebuttal commit (`a9769c7`). No `Co-Authored-By`/`Generated-with` trailers (global CLAUDE.md +
architect brief); the earlier commits that wrongly carried one will be cleaned message-only before the
PR.
