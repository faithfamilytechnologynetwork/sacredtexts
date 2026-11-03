# bugfix-102 thread — analysis scripts silently drop unmatched question ids (#102)

## Investigate (2026-11-02)
- **Reproduced.** `claim_tests.py` and `facct_findings.py` index `items/for-test/**/population/**/questions.jsonl`
  by `id` and join run rows by `question_id` with `.get()` + `continue`. Against main's question sets every
  committed row joins (30,688/30,688 answers). Against PR #98's regenerated sets (extracted from
  `origin/builder/bugfix-90` into scratch) only **8,976/30,688 answers (29.2%)** and 8,598/29,470 scores join.
  `claim_tests.main()` still exits 0 and writes "From 29470 scored cells across 16 models".
- **Root cause.** The join sites are `claim_tests.py` L71–73 (`meta = questions.get(...)`; `if not meta: continue`)
  and `facct_findings.py` `_instrument` L131–133. Nothing compares matched vs total, and `n_cells` is counted
  before the join. Both scripts glob `runs/*/base/**`, i.e. the committed archive is the only thing they can read;
  a #92 landing-zone rerun (`runs/<name>/<model>/base/**`) is unreachable, and there is no way to scope.
- Other `.get(...)+continue` sites in `facct_findings.py` (`_load`, `_digits`, `_canon`) join scores→answers
  *within one run*, so #98 does not move them; out of scope.
- `analyze_run.py` scores from the question embedded in each answer row (no id join) — unaffected.
  `paper_figures.py` reads `runs/*/base/**/summary.json` (no id join) but also has no `--run-dir` — follow-up, not this fix.
- **Architect instructions (01:08Z):** `--run-dir` is REQUIRED (no default) and takes the run root
  (`runs/rerun-2026-11-03`, globbing `<run-dir>/<model>/base/**`), so the archive is never globbed by accident.
  Merged origin/main @ 0b79afe (#99) as instructed.
- **Fix scope (<300 LOC):** a small shared helper in `items/for-test/` (resolve required `--run-dir`, population
  question index, per-model answer-row coverage, abort unless `--allow-partial`), wired into both scripts with
  Typer CLIs; header names the run dir and the partial count; test in `items/for-test/`.

## Fix (2026-11-02)
- `items/for-test/paper_join.py` (new): `resolve_run_dir` (required; must be a dir holding `<model>/base/**/answers.jsonl`),
  `model_files`, `population_questions`, `check_coverage` (per-model matched/total answer rows → `SystemExit` with the
  table unless `--allow-partial`), `partial_note`. Both scripts now take Typer `--run-dir` (required) + `--allow-partial`.
- `claim_tests.py` counts `n_cells` after the join and names the run dir in the header.
- **Verified on the real path:** archive vs #98's question files → both scripts abort with "8976 of 30688", per model
  (qwen3-32b 400/908, the rest ~572/~1,938–2,160). Archive vs today's question files → pre-fix and post-fix output
  byte-identical except the header (run dir named) and the 3 `_digits` sample lines (files are now read in sorted
  order, not filesystem order — deterministic now). `takeaway.pdf` byte-identical.
- Committed `runs/paper/*.md` predate the latest collections (27,264 vs 29,470 cells today); not regenerated here.
- Follow-up candidate (not this fix): `paper_figures.py` also globs `runs/*/base/**` with no `--run-dir`.
