# bugfix-111 thread — cite_passage Unicode-digit fold

## Investigate (2026-11-02)

**Reproduced.** Re-scoring incorrect `cite_passage` cells whose answer has a non-ASCII `Nd` digit,
with those digits folded to ASCII:

- committed archive (`runs/<model>/base/`, the 2026-11-02 snapshot): **558 incorrect → 396 flip**
  (202 islam/native prompt-english, 193 hinduism/native prompt-english, 1 hinduism prompt-native).
- local rerun (`runs/rerun-2026-11-03`, main checkout, uncommitted, read-only): **613 → 448**
  (224 / 223 / 1). Both match the issue's numbers exactly.

**Root cause** — `pipelines/sacredbench/score.py`:
- `_citation_candidates` extracts spans with `\d`, which matches Unicode digits, so `٣٤:٤٦` IS a
  candidate; but `normalize()` (NFKD) does not fold Arabic-Indic / Devanagari / Gurmukhi digits,
  so the candidate never equals `34:46`.
- the final `bounded_contains(answer, expected)` in `_single_citation_correct` looks for ASCII
  `34:46` in the raw answer and fails the same way.

**Separators checked:** between digits in the 558/613 cells only ASCII `:` appears (plus prose
`.`/`–`/`-`/` (`). No `：`, `؛`, `٫` → no separator fold needed.

**The remaining 162 (archive) / 165 (rerun):** mostly Sikh `ਅੰਗ ੩੦੮:੧੩` wrong loci, surah-name
answers (`آل عمران: ١٤٠`), and sonnet leaked-reasoning answers where the prompt's example
citation ("same form as 34:46") counts as a second candidate (pre-existing anti-hedge, out of scope).
One archive cell is a CORRECT locus with the label written in Gurmukhi (`ਅੰਗ ੭੩੪:੮` for
`Ang 734:8`, gemini-flash) — stays incorrect under the "numerals only" decision; flagged to the
architect, not changed.

**Design for monotonicity:** fold each extracted candidate (not the answer before extraction), so
span extents are byte-identical to today and folding can only merge candidates (n never grows);
fold the answer for the final `bounded_contains` (an ASCII expected that matched before still
matches — boundary chars unchanged in `\w`-ness). ⇒ `old correct ⇒ new correct` structurally.

## Fix (2026-11-02)

- Architect (mid-flight): keep the fold in ONE helper #112 can call → `score.fold_citation_digits`.
- Implemented as designed above: candidates folded after extraction; final `bounded_contains` on the
  folded answer. Expected citations are all ASCII (0 of 7,364 committed cite cells are not).
- Oracle (`test_citation_digit_fold.py` + `testdata/citation_digit_fold_movers.tsv`): 414 committed
  movers = 396 incorrect→correct + 18 incorrect→incorrect with a smaller `n_candidates`
  (e.g. `१०:३ (or 10:3)` used to be two candidates). Zero correct cells move.
- **Surprise:** `runs/astra/base/hinduism/native/population/prompt-english/answers.jsonl` holds 28
  question ids twice (collected twice, ~1s apart, sometimes different answers — `15:16` vs
  `१५:१६`). Movers are pinned by (folder, row, qid) for that reason. Data left as is; flagged.
- Regression: 11 of 21 tests fail with the fold turned into a no-op; full gate 990 passed.

## PR #114 / CMAP (2026-11-03)

- gemini APPROVE, codex APPROVE, claude APPROVE (no blocking issues).
- Folded claude's comment 1: the expected citation is now folded too (symmetric; no-op on committed
  data — 0 non-ASCII expected — but removes a trap for native-script ground truth in #39/#112).
- Relayed to architect, not acted on here: claude counts **262** committed cells still incorrect
  where the folded answer has the right numeric locus and only the book label differs (mostly
  Greek NT `Πράξεις 24:1`, Hebrew tractates, 1 `ਅੰਗ`) → sizing for #112; the astra duplicate-id
  file deserves its own issue; committed scores.jsonl now disagree with the scorer for 414 cells
  until the architect's rebaseline/final scoring pass.
