# bugfix-95 thread — verify_source cross-language yes/no verdicts (#95)

## Investigate (2026-11-02)

**Root cause.** `pipelines/sacredbench/score.py` `_native_verdict` looks up native tokens with
`_YES_NO_BY_LANG.get(language)` only, so a verdict in another language's script (Punjabi ਨਹੀਂ on a
Pali cell, Hebrew לא on a Punjabi cell, Syriac ܠܐ on a Hebrew cell) is never read → `parsed=None` →
`refused`. #76 gated by language to keep the Latin Pali `na`/`āma` from flipping English answers;
that motivation only applies to Latin-script tokens.

**Reproduced** over the committed run (`runs/<model>/base/**`): 510 refused verify_source cells in
`scores.jsonl` (matches the issue). Current code still returns `None` on all 510.

**The issue's 71/49/22 is a prefix count, not the stand-alone rule it prescribes.** Its per-token
tallies match a "leading token starts with any yes/no word" scan exactly. Under the rule the issue
specifies (all non-Latin native tokens on every cell, stand-alone kept, Pali Latin gated, + Syriac):
- **44** of the 510 committed-refused flip: **42 → correct, 2 → incorrect** (the 2 are Syriac ܠܐ
  on `he` cells, expected yes). Breakdown: ਨਹੀਂ 21 (pi 13, sa 8), नहि/नहीं 7 (pi), לא 7, لا 4,
  ܠܐ 3, न 2.
- The other 27 of the issue's 71 are not cross-language and stay refused under the rule:
  17 gemma `नास्ति।`/`नान।` on `sa` cells (a different word, not stand-alone न), 4 haiku
  `לא ניתן לאמת…`-style negation-particle refusals on `he` cells (exactly the #76 must-stay-refused
  case), 1 haiku `नहीं कह सकता`, 5 argon `ਹਾਂ ਜੀ` on `pa` cells (same-language, honorific ਜੀ follows).
- A further **20** flips sit in `runs/gpt-oss-20b/base/buddhism/native/population/prompt-english/`
  answers, which has no `scores.jsonl` yet (12 correct, 8 incorrect).
- `runs/archive/**`: 0 flips. No cell with a non-None parse changes (moves out of `refused` only).

Fix scope: ~20 LOC in score.py + tests. Fits BUGFIX.

## Architect decisions (2026-11-03 00:57Z)

- Plan approved as written: rule as specified, rule-derived set pinned by identity in the oracle,
  **no rewrite of committed `runs/*/scores.jsonl`** (the rerun is rescored under the final contract).
  The 44 supersedes the issue's 71 (architect will correct the issue).
- Added in this PR: Punjabi `ਹਾਂ ਜੀ` (polite yes; `ਜੀ` is part of the token, so stand-alone still
  applies after it) and Sanskrit `नास्ति` (no). Skip `नान` and the `לא ניתן לאמת`-style refusals.
- The 9 `_DaemonPool._initializer` failures (test_collect.py / test_phase2_tools.py, Python 3.14)
  are **#97, pre-existing** on origin/main, not ours; merge origin/main once #97 lands.

## Fix

- `score.py`: `_ANY_CELL_YES`/`_ANY_CELL_NO` = every non-Latin word from `_YES_NO_BY_LANG` plus
  Syriac `ܐܝܢ`/`ܠܐ`, read on every cell after the cell's own words. Latin-script words (Pali
  `na`/`āma`) are detected by Unicode name and stay gated to their cell. `ਹਾਂ ਜੀ` → `pa` yes,
  `नास्ति` → `sa` no.
- Final flip set (pre-#95 HEAD parser vs #95, over every committed answer): **85 cells**, 60 → correct,
  25 → incorrect. 65 are in committed scores (all `refused` there): 48 → correct, 17 → incorrect
  (44 cross-language, 5 `ਹਾਂ ਜੀ`, 16 `नास्ति` — 15 of those are gemma's "no" to an expected yes).
  20 are in the unscored `gpt-oss-20b/.../buddhism/.../prompt-english`. Archive: 0. No cell with a
  verdict changes.
- Oracle `pipelines/tests/test_cross_language_verdict_rebaseline.py`: pins the 85 by identity; re-
  derives every committed verify_source score and allows a difference only for a registered cell
  that is committed `refused` (so it holds before and after the rescore).
- Regression proof: against the HEAD `score.py` (scratch copy on PYTHONPATH), 37 new assertions fail;
  all pass with the fix.
- Full suite: 912 passed, 2 skipped, 9 failed — exactly the #97 `_DaemonPool._initializer` set (test_collect.py ×6, test_phase2_tools.py ×3), **#97, pre-existing**.

## PR (2026-11-03)

- PR #100 opened (Fixes #95). porch `fix` → `porch done` is blocked by the tests check, which fails
  ONLY on the 9 #97 tests (**#97, pre-existing**; fix is PR #99, still open). Holding at `fix`:
  once #99 lands, merge origin/main, re-run `porch done bugfix-95`, then record `--pr 100`.

## Architect review fold (2026-11-03 01:10Z)

- #99 landed; merged origin/main (2d20cb2). Gate now green on Python 3.11: 924 passed, 2 skipped.
- PR #100 approved pending 3 items, all done: oracle scan widened to `runs/**/scores.jsonl` (archive
  0-flip claim now machine-witnessed); per-folder skip instead of all-or-nothing, and a scores file
  with no sibling answers.jsonl is passed over (a scored row with no answer fails with a message);
  `_native_verdict` docstring notes the Arabic label stays per-cell. `runs/` untouched.
- Architect owns regenerating `runs/paper/*` from the rerun under the final contract (#94+#95+#96).

## CMAP (pr phase)

- gemini **APPROVE**, codex **COMMENT** (non-blocking: two follow-up commits used `[bugfix-95]`
  instead of `[Bugfix #95]`; left as-is rather than rewrite pushed history), claude **APPROVE**
  (independently re-scored 7,777 committed verify cells incl. 413 archive: exactly 65 move, 48/17, 0
  into refused).
- Folded claude's cheap nits: disjointness test compares the mark-stripped forms actually matched;
  `_is_latin` documents the no-letter case; a missing registered cell fails with a message; arch.md
  line rewrapped.
- **For the rerun (not fixed here; contract change):** `_strip_marks` collapses `हाँ`→`ह`,
  `ਹਾਂ`→`ਹ`, so a leading stand-alone `है।`/`ਹੈ।` ("is") now reads yes on every cell (before: on
  `sa`/`pa` cells only). Fires on 0 of 7,777 committed cells; worth a glance at the rerun's
  refusal delta.
