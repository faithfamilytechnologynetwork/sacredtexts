# task-JJl4 — finish & ship English-hadith corpus PR

## Task
Finish/ship the English-hadith corpus PR on `corpus/hadith-english-six` (architect WIP commit
14d6fc4 on top of main 493f700). Six canonical books only (bukhari/muslim/abudawud/tirmidhi/
nasai/ibnmajah); converter `hadith_sunnah_en`; translations ⇒ outside the original-language pool
(pool stays 20 texts). Do NOT add Malik/Ahmad/Darimi English (air-74 owns removing those).
Do NOT touch runs/.

## Steps
1. Re-pin `ANCHOR_CORPUS_HASH` de2c8679cbde3cf5 → e588c0892cf922ce in
   pipelines/tests/test_original_run_regression.py; extend dated comment (2026-11-01 sunnah.com
   English six; digest unchanged 93b71460742a8ecd). Verify via independent `generate`.
2. `convert` → full pipelines suite + viewer lane per .codev/checks/test.sh — all green.
3. PR to main, Problem/Root cause/Fix/Testing body; report PR# to architect. No merge.

## Progress
- Checked out corpus/hadith-english-six. Architect WIP commit adds convert_hadith_sunnah_en,
  source.yaml English targets for the six books, test_catalogue/test_schema_convert updates,
  and the six English payloads. Anchor re-pin is the remaining WIP item.
- DONE: re-pinned ANCHOR_CORPUS_HASH de2c8679cbde3cf5 → e588c0892cf922ce + extended dated
  comment. Ran `convert` (230 docs / 30 targets, six English books present).
- VERIFIED independently: `generate texts/standardized --per-text 28 --seed 20261010
  --negatives-share 0.5` → corpus_hash=e588c0892cf922ce (matches new anchor),
  question_set_digest=93b71460742a8ecd (unchanged, 10 translations excluded from pool).
- Test gate: pipelines pytest **719 passed** (8m13s, incl. copyright audit). Viewer vitest
  first FAILED only because this worktree had no apps/viewer/node_modules (`vitest: command not
  found`) — ran `pnpm -C apps/viewer install`, then vitest **190 passed** (19 files). GOTCHA for
  future builders touching texts/ or runs/ here: the dispatcher routes to the viewer lane too,
  so the worktree needs `pnpm -C apps/viewer install` before the gate is green.
- Committed anchor re-pin (f82425f) on top of architect's WIP commit (14d6fc4). Pushed.
- Opened **PR #79** → main. NOT merged (architect's call). Reported to architect.
