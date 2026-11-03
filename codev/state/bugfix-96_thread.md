# bugfix-96 thread — failure kinds on the paper's path (issue #96)

## Investigate (2026-11-02)
Reproduced the issue's numbers on the 2026-11-02 run (8,929 incorrect text-retrieval cells; 1,388 at
token_f1 ≥ 0.7; 721 at ≥ 0.9). Root cause: text-retrieval scoring is binary and nothing on the
`score` → summary path says *how* an incorrect cell failed.

## Fix v1 — superseded
Implemented the issue's original plan (a `metrics.near_miss` field + archive `scores.jsonl`
rebaseline), committed locally (0215f79), never pushed. **Architect redirect (01:01Z):** do not add a
parallel field; the taxonomy already exists in `failure_kind.py` / `failureKind.ts`. Reverted
(4aebcef) — kept in history. Issue body updated to the revised scope.

## Fix v2 — revised scope
- `score_file` classifies every cell with `failure_kind.classify_failure` (passing `token_f1_base`, as
  `report_run` does) and reports `minor`/`major` (a split of `incorrect`; every incorrect cell has
  exactly one kind — fails loud otherwise) + a `kinds` map per model × task, model × text, and their
  `_overall`; summary.md: minor/major in cells, a per-task kinds table, per-text columns.
  `scores.jsonl` is byte-identical → no committed-evidence rebaseline.
- near_copy split **inside** the existing F1 ≥ 0.85 gate (a strict refinement; no other kind moves):
  diacritic_only (base-letter token edit distance 0), edition_variant (1–2), near_copy (rest).
  On the 2026-11-02 run: 989 → 174 / 558 / 257.
- Base letters: `failure_kind.base_tokens` (NFKD, drop all combining marks, alef-wasla→alef, drop
  tatweel / Qur'anic annotation block / ZWJ-ZWNJ, final sigma→sigma) instead of importing
  `score.base_letters`, so the TS mirror is exact. Agrees with `score.base_letters` on all 989 real
  near-copy cells and on Arabic/Hebrew/Greek/Pali/Devanagari/Gurmukhi/Latin probes.
- `splits.py` collapses the family back to near_copy (its floor sweep is about the paraphrase floor).
- Viewer: kinds already drive the badge + "how it failed" filter, so the new kinds appear there.
  The explorer now also passes `token_f1_base` (as the summary does), so its badge equals the
  summary counts — before, TS used strict F1 only.
- Parity fixture +7 cases (each new branch + boundaries + base-F1 preference), green in both suites.

## Tests
- Regression: `test_summary_failure_kinds.py` + new fixture cases — 10 fail on base code, all pass.
- **#97, pre-existing**: 9 failures in test_collect.py / test_phase2_tools.py (`_DaemonPool._initializer`
  on Python 3.14) fail on origin/main too; architect: don't patch, merge main once #97 lands.
- 01:09Z architect: #99 (fix for #97) on main → merged origin/main (fa7cccc). Gate `bash .codev/checks/test.sh`
  on Python 3.11: pipelines 889 passed / 2 skipped, viewer 233/233 — fully green, no #97 failures left.
- Priority (owner): #96 must be in the same final scoring pass as #94/#95 before the rerun is scored.
- CMAP on PR #105: gemini APPROVE, codex APPROVE, claude APPROVE (all HIGH). Folded Claude's nits:
  base_tokens↔score.base_letters agreement test (7 scripts), analysis_markdown minor-kind prose.
  Kept the by-text `ov['minor']` read unguarded on purpose: summary_markdown only renders a fresh
  score_file summary, which always carries it — a missing key should fail loud.
