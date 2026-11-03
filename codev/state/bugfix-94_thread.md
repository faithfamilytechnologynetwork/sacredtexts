# bugfix-94 — Latin transliteration diacritics penalised (Allāh vs Allah)

## Investigate (2026-11-02)

**Reproduced exactly.** Over the committed 2026-11-02 run (`runs/<model>/base/**`), the current
scorer reproduces all 29,470 committed score rows (positional pairing). 183 `incorrect`
text-retrieval cells flip to correct when Latin combining marks are folded on both sides:
151 islam/english, 15 hinduism/english, 9 buddhism prompt-english, 8 buddhism prompt-native.
Per model: terra 29, fable 27, opus 23, argon 22, beam 20, gemini-flash 16, kimi 15, luna 11,
sonnet 11, deepseek-v4-pro 7, haiku 1, sol 1.

**Root cause.** `score._normalize` deliberately keeps Latin diacritics on the letter
(`_recompose_latin_marks`, issue #50), so `normalize("Allāh") != normalize("Allah")`. Both
headline paths inherit that: `normalized` is plain `normalize()` equality, and
`fold_aware_contains` returns early for a non-Arabic reference (its Spec 52 fold is Arabic-only),
so it falls back to `bounded_contains` over `normalize()`.

**What the diffs are.** Islam: `allāh→allah` (254 token diffs), `muḥammad`, `iḥrām`, `luqmān`,
`islām`. Hinduism (Besant's Gita): `pârtha`, `yogî`, `madhusûdana`, `kuntî`, `bhârata`.
Pali: niggahita convention `ṃ↔ṁ`, plus metrical / edition vowel-length variants (`suddhī↔suddhi`,
`jagatippadeso↔jagatīppadeso`, `nappasahati↔nappasahatī`, `tathāttānaṃ↔tathattānaṃ`) and one
retroflex dot (`khaṇatha↔khanatha`). These are in the issue's pre-registered set, so they are in
scope. I'll flag the vowel-length part in the PR for the architect anyway.

**Archive is untouched.** No archived run (`runs/archive/*`) moves under the fold, in
`normalized` or in containment. So the byte-for-byte re-score guards (first-run, original,
tutorial) and the Spec 52 similarity SHAs stay green without any rebaseline.

**Data quirk, not ours.** The three astra hinduism answer files hold every question twice
(identical rows). Pairing by position works; keying by `question_id` silently drops rows.
The oracle test pairs by position.

**Pre-existing failures.** Architect: 9 failures in test_collect.py / test_phase2_tools.py
(`_DaemonPool._initializer` on Python 3.14) are #97, pre-existing on main. Not mine; don't patch.

**Fix plan (<300 LOC).** A scoring-only Latin-mark fold (`fold_latin_marks` over `normalize()`
output, the `_is_latin_mark` set), used by (a) the `normalized` equality that `strict` grades
and (b) `fold_aware_contains` as an extra OR after the `bounded_contains` floor. Shared
`normalize()`, `token_f1`, `cite_passage`, Indic and Arabic/Hebrew behaviour are unchanged.
Oracle test: re-derive every committed text-retrieval cell; the movers equal the 183 pinned
cells, every mover goes incorrect→correct, nothing else moves.

## Architect redirect (2026-11-03 01:00Z): exclude Pali

The fold applies only when `source.language == "en"`. In romanized Pali the macron is the
orthography (dhamma ≠ dhammā, same status as a Devanagari vowel sign), so #50's headline rule
stands and `test_normalize_nonlatin.py` is unchanged. Noted on issue #94.

## Fix

- `score.fold_latin_marks` (NFD, drop the `_is_latin_mark` set) over `normalize()` output.
- `score_answer`: on an `en` cell, `normalized` compares the folded forms and
  `fold_aware_contains(..., fold_latin=True)` adds one more OR after the `bounded_contains` floor.
  Every other call-site (classify_refusal, facct, probes) keeps the default (no Latin fold).
- `items/for-test/analyze_run.py` now passes `language` to `score_answer`, like `score_file`
  and `paper_figures.py`; without it the analysis would keep the old contract on English cells.
- arch.md § score.py and the arch-critical scoring fact note the English-only fold.

**167 movers, not 166.** Against the committed (pre-#94) scores: 166 incorrect→correct
(151 islam/en, 15 hinduism/en) plus 1 refused→correct: opus hinduism/en `61d0882ddf899d86`,
a hedged delivery of Gita 9:13 ("I can't verify… reads approximately: …O Pârtha…") against a
reference that prints `Partha` without the circumflex. The issue's 183 counted only incorrect
cells. Credit-only either way. Over all 29,470 committed rows, nothing else moves.

**Oracle** (`pipelines/tests/test_latin_diacritic_fold.py` + `testdata/latin_fold_movers.tsv`):
re-scores every committed English text-retrieval row. A registered cell must be `correct` under
#94 and, if its committed row is still pre-#94, differ only in normalized/contains/correct/outcome
from the registered pre-#94 outcome. Every other row must match its committed scores exactly. It
keeps passing when folders get re-scored under the new contract. It fails when unregistered cells
move, or when registered cells disappear. With the fold switched off, the scenario tests and the
oracle fail (3 failed); with it, all 8 pass.

**Full suite:** 873 passed, 2 skipped, 9 failed. All 9 are `_DaemonPool._initializer` on
Python 3.14 (test_collect.py / test_phase2_tools.py): #97, pre-existing on main, not this fix.
