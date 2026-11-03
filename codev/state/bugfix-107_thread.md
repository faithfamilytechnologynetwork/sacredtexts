# bugfix-107 thread — paper_figures.py needs the #102 --run-dir scoping

## Investigate (2026-11-02)

- Branch was cut before PR #106 merged; merged origin/main (5f42337) so `items/for-test/paper_join.py` is available. Architect asked for exactly that.
- **Repro** (scratch script, tmp `runs/` with an "archive" `haiku/base` and a `rerun-2026-11-03/haiku/base`, `RUNS`/`OUT` monkeypatched so nothing in `runs/paper/` is touched): `paper_figures.main()` takes no arguments, `_collect` read the archive answer row, and `write_early` read the archive `summary.json` (incorrect=1, not the rerun's 7). The rerun root is unreachable, and `python3 paper_figures.py --run-dir X` would silently ignore the flag and overwrite `runs/paper/*` from the archive.
- **Root cause**: `RUNS = REPO / "runs"` hard-coded (L24); `_collect` reads `RUNS / model / "base"` + `rglob("answers.jsonl")` (L108–111); `write_early` globs `RUNS.glob("*/base/**/summary.json")` (L558); no CLI. Answers are scored from the question embedded in each row, but the partial-star denominator (`_expected`/`_expected_kind`) counts the *current* population files — so answers from another question generation would be scored and starred against the wrong denominator with no error. That's where the coverage guard belongs.
- Today the archive is fully covered (30688/30688 answer rows match current questions), so the bug is latent until the rerun's question set lands — consistent with the issue ("must land before any paper figure is regenerated").
- Panel (`models/openrouter.yaml`) == models on disk today.

**Fix shape** (<100 LOC): typer `main(--run-dir required, --allow-partial)`, `resolve_run_dir` + `check_coverage` before writing anything, `_collect`/`write_early` read via `model_files(run_dir, …)`; with `--allow-partial` the unjoined rows are left out of the joined tables and the note goes in the `.tex`/`early-outcomes.md` headers. A run-dir model not on the panel fails fast (would otherwise be dropped from every table silently). Docs: `runs/README.md`, `runs/analysis-template.md`. Test: `items/for-test/test_paper_figures.py`. Not regenerating `runs/paper/*`.
