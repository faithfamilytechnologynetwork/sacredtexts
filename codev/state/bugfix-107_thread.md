# bugfix-107 thread — paper_figures.py needs the #102 --run-dir scoping

## Investigate (2026-11-02)

- Branch was cut before PR #106 merged; merged origin/main (5f42337) so `items/for-test/paper_join.py` is available. Architect asked for exactly that.
- **Repro** (scratch script, tmp `runs/` with an "archive" `haiku/base` and a `rerun-2026-11-03/haiku/base`, `RUNS`/`OUT` monkeypatched so nothing in `runs/paper/` is touched): `paper_figures.main()` takes no arguments, `_collect` read the archive answer row, and `write_early` read the archive `summary.json` (incorrect=1, not the rerun's 7). The rerun root is unreachable, and `python3 paper_figures.py --run-dir X` would silently ignore the flag and overwrite `runs/paper/*` from the archive.
- **Root cause**: `RUNS = REPO / "runs"` hard-coded (L24); `_collect` reads `RUNS / model / "base"` + `rglob("answers.jsonl")` (L108–111); `write_early` globs `RUNS.glob("*/base/**/summary.json")` (L558); no CLI. Answers are scored from the question embedded in each row, but the partial-star denominator (`_expected`/`_expected_kind`) counts the *current* population files — so answers from another question generation would be scored and starred against the wrong denominator with no error. That's where the coverage guard belongs.
- Today the archive is fully covered (30688/30688 answer rows match current questions), so the bug is latent until the rerun's question set lands — consistent with the issue ("must land before any paper figure is regenerated").
- Panel (`models/openrouter.yaml`) == models on disk today.

**Fix shape** (<100 LOC): typer `main(--run-dir required, --allow-partial)`, `resolve_run_dir` + `check_coverage` before writing anything, `_collect`/`write_early` read via `model_files(run_dir, …)`; with `--allow-partial` the unjoined rows are left out of the joined tables and the note goes in the `.tex`/`early-outcomes.md` headers. A run-dir model not on the panel fails fast (would otherwise be dropped from every table silently). Docs: `runs/README.md`, `runs/analysis-template.md`. Test: `items/for-test/test_paper_figures.py`. Not regenerating `runs/paper/*`.

## Fix (2026-11-02)

- Commit "Fix #107": `paper_figures.py` typer CLI (required `--run-dir`, `--allow-partial`), `resolve_run_dir` + `check_coverage` before any write, `_collect`/`write_early` read via `model_files`, non-panel model fails fast, `.tex`/`early-outcomes.md` headers name the source run (+ the partial note). The scoring body lost one indent level (per-model loop folded into `model_files`) — `git diff -w` is +50/−34.
- `items/for-test/test_paper_figures.py`: 5 tests; all 5 fail on the pre-fix script (verified by swapping the old file in with `OUT` monkeypatched), all pass with the fix.
- Real-data check: fixed script `--run-dir runs` vs old script (both into scratch) → all 7 outputs byte-identical except the new provenance comment. Committed `runs/paper/*` NOT regenerated (it's older than the current answers for the still-collecting models — fable/astra/sol/qwen3/gpt-oss/opus-Enc rows would move; that's the architect's call on rerun day).
- Gate: the runs/ doc edits pull in the viewer lane, which failed only on a missing `apps/viewer/node_modules` in the fresh worktree; `pnpm install --frozen-lockfile` → viewer 225, items 25, pipelines 882 passed.

## PR (2026-11-02)

- PR #109. First CMAP dispatch did nothing ("Multiple projects found" — main now carries many `codev/projects/*`); re-ran with `--issue 107`.
- CMAP: gemini APPROVE (HIGH), codex APPROVE (HIGH), claude APPROVE (HIGH). Claude nits: folded the stale `_collect` return annotation (I'd carried it through the line I edited) and made the headline test's task column order-independent. Not folded: a panel guard in `write_early` (needs a `summary.json` with no `answers.jsonl`, which collect never writes) and the pre-existing dead `seen` dict (out of BUGFIX scope).
