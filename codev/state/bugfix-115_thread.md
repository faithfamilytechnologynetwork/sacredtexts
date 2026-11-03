# bugfix-115 thread — verify_source native verdict tokens

## Investigate (2026-11-02)

Reproduced over `runs/rerun-2026-11-03` (main checkout, untracked; scored at 7567318, zero drift vs current code):
455 refused verify_source cells; grouped by leading token of `_leading_window`.

Root cause (`pipelines/sacredbench/score.py`, `_native_verdict` and its tables):
- `आम्` (Sanskrit yes, 105 cells, all `sa`) and `הן` / `הין` (13, all `he`) are missing from the yes lists.
- `Nahi` / `Nahiṁ` / `Nahīṃ` (9 cells, not 10: the issue double-counted `Nahiṁ`) are missing from the Latin no lists.
  The cells are `pi` (8) and `sa` (1), **not** `en`. The issue assumed prompt-english cells carry `language == en`,
  but `source.language` is the text's language. So the #95 Latin gate (own-cell only) already covers every
  observed cell, and no cross-cell exception for Latin words is needed. Decision: keep them gated.
- `नो` (2): both cells are `नो हेतं` (Pali "no hetaṃ", meaning "not so"). `_strip_marks` turns `नो` into `न`, which is
  already listed. They fail `_stands_alone` because `हेतं` follows, so adding bare `नो` moves nothing. The fix needs
  the two-word token `नो हेतं` (precedent: `ਹਾਂ ਜੀ`).
- `उत्तर:` / `उत्तरम्:` (5, sonnet, `sa` cells): `_NATIVE_LABEL_PREFIX` is Arabic-only and per-cell. The label regex
  runs on the mark-stripped window, so it has to be built from `_strip_marks(word)`. The 2 `उत्तरम्: आम्‌` cells
  also need `_stands_alone` to skip a ZWNJ (U+200C, category Cf) after the token.
- Gotcha: `_strip_marks` drops Devanagari vowel signs too (`हाँ` becomes `ह`, `नहीं` becomes `नह`), so a token's
  stripped form is what really matches.

Candidate fix measured with a monkeypatched oracle (scratch, not committed):
- rerun: 134 moves, 133 refused→correct and 1 refused→incorrect (gemma `**Nahi**` on an expected-yes cell).
- committed `runs/` (archive included): 23 moves, 21 refused→correct and 2 refused→incorrect. Archive 0 moves.
  Nothing moves into refused, and nothing goes correct→incorrect.
- Applying the labels on every cell (Arabic included) moves nothing beyond the tokens.
- The #95 scan in `test_cross_language_verdict_rebaseline.py` will see the 23 committed moves (and 134 rerun moves
  when the rerun is present) and has to accept the #115 registry.

Out of scope, seen in the sweep: `بلى` (4, Arabic emphatic yes), `התשובה:` label (1), `בלי` (2), `Nohi`/`Na hi`/`Natthi`.
Pre-existing risk: since `हाँ` strips to `ह`, a leading `है।` would read as yes. Not touched here.

## Fix (2026-11-02)

- `score.py`: added `הן` (he/arc), `הין` (arc), `आम्`/`आम`, `नो`, `नो हेतं` and Latin `nahi`/`nahiṃ` (sa, pi; still
  gated to their own cells). Labels are now one regex built from `_strip_marks(label)` and stripped on every cell,
  with `उत्तर`/`उत्तरम्` added. `_stands_alone` skips Cf (ZWNJ) as well as marks.
- Contract nuance: `test_score.py::test_native_label_and_marks_do_not_touch_other_cells` (AIR #75) asserted the
  Arabic label is read only on ar cells. The issue asks for labels on every cell, and since #95 the bare `لا،` is
  already read on a he cell, so I renamed and flipped the test to `test_native_label_is_read_on_every_cell`.
  The oracle shows no cell moves from this part. arch.md § score.py now notes it.
- New `test_native_verdict_tokens_rebaseline.py`: unit positives and negatives per token, plus a registry pinned by
  identity (23 committed cells, 134 rerun cells). The #95 scan in `test_cross_language_verdict_rebaseline.py`
  now accepts the union of #95 and #115 registered cells. Mutation check: with the #115 registry emptied, the scan
  fails on the first committed mover.
- Verified: the new tests fail on HEAD's score.py (53 fail) and pass with the fix. Full suite passes both with
  the rerun jsonl copied into the worktree (1034 passed) and without it. Gotcha: pathlib `**` does not follow a
  symlinked `runs/rerun-…` (3.11), so a symlink silently skips the scan, and a copy was needed.

## PR (2026-11-02)

- PR #121. Merged origin/main twice (#110, #111); the #111 merge had an arch.md conflict, resolved keeping both notes.
- Snag: `runs/rerun-2026-11-03` is live. `join_run.py` for gpt-oss-20b and qwen3-32b is still collecting, and new cells
  move under #115, so the #95 scan failed in the main checkout. Architect decision: don't wait on live collections.
  The #95 "nothing else moves" scan now reads only **git-tracked** `runs/**/scores.jsonl` (`_tracked_score_files`).
  The rerun registry pins only the 14 models whose collection is complete; it is a witness, skip-if-absent.
  The regenerated registry was identical (134 cells, none from gpt-oss/qwen).
- CMAP round 1: codex APPROVE; gemini skipped (agy produced no output).
