# bugfix-96 thread — near-verbatim tier for incorrect text-retrieval cells

## Investigate (2026-11-02)

**Reproduced** against the committed 2026-11-02 run (`runs/*/base/**/scores.jsonl` + answers):
8,929 incorrect text-retrieval cells; 1,388 at token_f1 ≥ 0.7; 721 at ≥ 0.9 — the issue's numbers
exactly. The issue's rule (F1 ≥ 0.9 OR base-letter word-bounded containment) tags **757** cells
(36 via base containment alone). Per-tradition share at F1≥0.7 matches the issue (islam/english 68%).

**Root cause**: the text-retrieval branch of `score_answer` (`pipelines/sacredbench/score.py`)
emits only exact/normalized/token_f1/token_f1_base/contains_reference + a binary
correct/incorrect outcome. Nothing tiers an incorrect cell, so `_outcome_cell` / `summary_markdown`
cannot report it and the viewer explorer has no field to badge/filter on.

**Existing work found**: `failure_kind.near_copy` (F1 ≥ 0.85, viewer + `failure_kind.py`) is a
mutually-exclusive *failure-kind label* computed downstream, after other_script/omission. The issue's
`near_miss` is a different thing: a pipeline-emitted, outcome-orthogonal tier in `scores.jsonl` +
summaries. Implementing as the issue specifies; not touching `near_copy`.

**Design**:
- `metrics.near_miss` on every retrieve_quote/complete_unit row, appended after `outcome`;
  1 iff outcome == incorrect AND (emitted token_f1 ≥ 0.9 OR base_letters(expected) word-bounded in
  base_letters(answer)). correct/refused cells carry 0. `normalize()` untouched; headline untouched.
- Summary: text-retrieval task cells (per model × task, per model × text × task) gain
  `near_miss` count + `near_miss_share` (= near_miss / incorrect) next to `incorrect`.
  summary.md shows it in the task cells and as a per-text column.
- Viewer: `near_miss` on QuestionResult; "near miss" badge; result filter option.
- Committed **archive** scores.jsonl (byte-identity re-score tests) rebaselined with an oracle:
  dropping `near_miss` reproduces the committed bytes. Live `runs/<model>/base/` evidence is NOT
  re-scored here (collection still running on main → conflict risk); `join_run.py` re-scores on its
  next pass.

## Fix (2026-11-02)

- **#97, pre-existing**: 9 failures in test_collect.py / test_phase2_tools.py (`_DaemonPool._initializer`
  on Python 3.14) fail on origin/main too. Architect: not mine, don't patch `_DaemonPool`; merge
  origin/main once #97 lands for a clean gate.
- Implemented per the investigate design. Full pipelines suite from repo root: 872 passed, 9 failed —
  exactly the #97 set, nothing else. Viewer: 222/222, `tsc --noEmit` clean.
- Regression test `pipelines/tests/test_near_miss.py`: 7/7 FAIL against base `score.py`, 7/7 pass with fix.
- Archive rebaseline (byte-guarded only): first-run / original / tutorial `scores.jsonl`, each written
  only after the projection oracle held (regenerated minus `near_miss` == committed bytes). Tagged
  near misses: first-run 16, original 28, tutorial 8. No headline moved. exp-* archives and live
  `runs/<model>/base/` NOT re-scored (no byte guard; live collection still committing on main).
