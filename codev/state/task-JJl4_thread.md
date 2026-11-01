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

## Review iteration 1 (architect approve-after-nits, 2026-11-01)
Four fixes:
1. convert.py: made a MISSING `narrator` key raise like null does (`.get("narrator")`, no
   default). Added `convert_hadith_sunnah_en` to test_schema_convert imports + the fail-fast
   parametrize (both top-level shapes), and a new parametrized test
   `test_hadith_en_malformed_english_fails` (english-not-dict / narrator-null / narrator-missing
   / text-missing / text-null). Real data audit: narrator is always a non-null str in all six
   books, so the stricter get is safe.
2. source.yaml header (lines 1-13) rewritten: nine Arabic hadith collections, the six canonical
   (Kutub al-Sittah) ALSO in English; converter list incl. hadith_sunnah_en; English provenance.
3. Per-book English `license_detail` reworked + "freely available online" reframed as
   AVAILABILITY not a licence. **PREMISE CORRECTION**: sunnah.com does NOT publish per-collection
   translator credits (stated policy: "various translators"); scraped metadata carries only the
   classical compiler. So translators are recorded as the *matched Dar-us-Salam edition*
   (Bukhari=Muhsin Khan, Tirmidhi=Abu Khaliyl, Nasa'i & Ibn Majah=Nasiruddin al-Khattab),
   Muslim & Abu Dawud left unattributed — NOT as sunnah.com-stated. Flagged to architect.
4. Converter docstring: English citations are a STRICT SUBSET of the Arabic (3 missing — one each
   in Bukhari/Muslim/Tirmidhi; verified by comparing converted citation sets), skips at most one
   per book. No English-only hadith.
- Architect follow-up on #3: keep matched names, record the basis. Final phrasing per book:
  "sunnah.com credits no per-collection translator; text matches the Darussalam edition (tr. X)";
  Muslim/Abu Dawud: "sunnah.com credits no translator". Each notes "freely available online" is
  availability, not a licence.
- Local: convert OK (230 docs / 30 targets); pipelines pytest **726 passed** (+7 new tests).
- MERGE ORDER: architect first said #74 before #79, then superseded — owner's merge word GIVEN,
  **#79 merges FIRST**, builder merges it on green CI; #74 (air-74) re-pins after (33→30 etc.).
