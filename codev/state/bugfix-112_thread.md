# bugfix-112 thread — cite_passage citation-equivalence layer

## Investigate (2026-11-02)

**Reproduced** with a throwaway prototype (scratchpad, not committed) over every `cite_passage` cell:
rerun `runs/rerun-2026-11-03` (main checkout, uncommitted, read-only; 8,039 cells) and the committed
archive `runs/<model>/base/` (7,364 cells). Counts are flips *beyond* #111's digit fold.

| Class | rerun | archive |
|---|---|---|
| Notation: native book/label + Hebrew numerals + amud letters + surah names | **319** (Greek 85, Masoretic 202, Talmud-exact 22, Qur'an surah 8, Dhammapada 2) | **298** (incl. the gemini-flash `ਅੰਗ ੭੩੪:੮`) |
| Granularity: Talmud daf+amud | **265** (en 102, prompt-en 80, prompt-native 83) | **285** |
| Granularity: GGS Ang page | **82** (prompt-en 45, prompt-native 37) | **70** |
| correct → incorrect | 0 | 0 |

**Root cause** — `pipelines/sacredbench/score.py` `_COLON_CITE`/`_NUM_CITE` prefix is
`[A-Za-z0-9]…`, so a Greek/Hebrew/Gurmukhi book word is never part of the span: `Πράξεις 24:1`
extracts as bare `24:1`, which can't equal `acts 24 1`. Hebrew letter-numerals (`כח:מג`) have no `\d`
so nothing is extracted (n=0). `normalize()` turns gershayim/geresh into spaces (`כ״ח` → `כ ח`), so
numeral parsing must happen on the raw text, before `normalize()`. Talmud/GGS: the expected carries
Sefaria's segment / line index, so `21a:5` ≠ `21a:2` by design.

**Sikh discrepancy vs the issue:** the issue says "only 1–2 cells match at page level"; I measure
85 page matches out of 732 single-citation Sikh answers (82 newly credited) against a chance
baseline of ~14 (answer vs a random question's page), so the signal is real.
Flagged to the architect.

**Genuinely-wrong Hebrew-numeral cells stay wrong** (negatives): e.g. `ויקרא ה׳:י״ט` for Leviticus
14:19, `מלכים א' כא:יח` for 1 Kings 22:39, `נדרים נ״ב א` for Nedarim 52b:2 (amud a ≠ b).

**Design (prototype-validated):** canonicalise the RAW answer (NFKD + `strip_script_marks` +
casefold + digit fold + drop Greek keraia), then rewrite native book/tractate/label aliases to the
expected's English name (longest-first, word-bounded), then Hebrew numerals anchored on a canonical
book (`exodus כח:מג` → `exodus 28:43`; Talmud `<tractate> HN [ע"]א|ב [:seg]` → `21a:5`), then
(Arabic only) surah names → number. Re-use the existing matcher on the rewritten answer. Talmud/GGS
coarsen both expected and answer spans (drop `:seg`) for the headline; `segment_match` = the
full-granularity verdict. Headline `correct = legacy OR equivalence` ⇒ credit-only by construction.

**Known gaps (left alone):** the traditional `.`/`:` amud notation (`גיטין מ.:י"ג`, `בבא קמא קיא:`), ~2 cells;
Greek abbreviations (`Γαλ.`, `Ῥωμαν.`); prose answers ("chapter 10 verse 36").

**Coordination:** #111 (bugfix-111) has not landed. I build the alias data, the canonicaliser module, and its
tests first, and wire it into `_single_citation_correct` only after #111 merges.

## Fix (2026-11-02/03)

**Decisions from the architect (data):** (1) granularity default CONFIRMED (Talmud daf+amud, GGS
Ang, `segment_match` sub-field), kept as one switch `citations.HEADLINE_DROPS_SEGMENT`. (2) #118
(prompt example echo) added to this PR as a separate commit. (3) `original-2026-10-21` byte-for-byte
guard: option A — keep committed scores, pin the 21 moved rows by identity (FAccT card frozen, #74).
(4) #118 refinement: drop the echo only when another citation exists; an echo-only answer stays
`wrong_locus` (removed a 319/419-cell `wrong_locus → no_citation` shift).

**Data location:** `pipelines/sacredbench/citation_aliases.yaml` (package data next to the code, not
`texts/raw/<tradition>/`): the Greek NT and Masoretic sets are tradition "Christianity", which has
no raw dir, and a package-relative path keeps scoring independent of the repo layout.

**Shape quirk found:** `_shape_rx` routes Talmud citations (`23b:3`) to `_NUM_CITE`, since its colon
test is `\d\s*:\s*\d` and the amud letter breaks it, so legacy Talmud candidates are daf-without-amud
(`megillah 23`). That's harmless to correctness (the final `bounded_contains` decides), but it means
the #118 example has to be turned into candidates with the SAME extractor (`_citation_candidates(example,
expected)`), not compared as raw text.

**Pre-existing, not fixed (follow-up):** the boundary match credits `1 John 3:16` for an expected
`John 3:16` (the candidate span contains `john 3 16`); the alias layer inherits this for
`Α΄ Ἰωάννου`. `John` IS an expected book (Greek set), but no credited cell in the rerun or archive
has a numbered sibling (`1 John …`) in its answer (checked), so no number here depends on it.

**Numbers** (after #111; rerun = `runs/rerun-2026-11-03`, archive = committed `runs/<model>/base`):
- #112 notation: rerun 319, archive 298 (= 203 label-only + 86 Hebrew numerals/amud + 9 surah names)
- #112 granularity: rerun 347 (Talmud 265, GGS 82), archive 355 (Talmud 285, GGS 70)
- #118: rerun 56 credited (sonnet 40, haiku 12, luna 4) + 15 hedge→wrong_locus; archive 69 + 13
- original-2026-10-21: 2 credited (Talmud daf), 19 gain `segment_match` only; #118 moves none
- cite_passage accuracy, rerun (old→new): christianity .598→.811, judaism .064→.270, sikhism
  .004→.108, islam .872→.893, buddhism .699→.708, hinduism .911→.917; coverage unchanged.

## PR phase — CMAP round 1 (PR #122)

gemini APPROVE, claude APPROVE, codex REQUEST_CHANGES. Codex: (1) "Dhammapada 74 or Dhammapada 184"
(example offered as an alternative) is credited; (2) "John 1:1 or 1 John 8:41" with example
"John 8:41" drops `1 John 8:41` as an echo. (2) is real: the echo was a `search` inside the
candidate span, so a numbered-book namesake matched. Fixed with a `(?<!\d )` lookbehind on the echo
pattern + test. (1) is kept as the architect specified: the generator always takes the example from
a *different* entry, so naming it can never raise the hit rate the anti-hedge guards; 0 of the credited
cells (69 archive, 56 rerun) offer it as an alternative (all disclaim it: "न कि 10:36", "in the form
34:46"). Pinned by a test and noted in score.py SCOPE. Claude's notes folded: `segment_match` now
uses the canonicalized example; the `example_citation` parameter renamed `example` (it shadowed the
function); the daf/Ang extractor switch (`_NUM_CITE` can't see a non-daf colon rival) is in SCOPE.
Follow-ups (not here): carry the exemplar in the question row instead of re-parsing the prompt;
surface `segment_match` in the viewer/analysis.

## PR phase — codex round 2

Codex still REQUEST_CHANGES. (a) New concrete case: `Ang 1297:15 or John 1:1` vs `Ang 1297:28` was
credited, because dropping to the Ang switched the extractor to `_NUM_CITE`, which can't see the
colon rival. For GGS that was weaker than the old matcher (its `_COLON_CITE` counted it), so
`score_citation` now keeps the colon candidates of the full citation's shape as rivals when the
shape changes. It moves 0 of 16,633 committed + rerun cells. Talmud is untouched: its extractor was
already `_NUM_CITE` pre-#112 (shape quirk), and counting colon spans there would un-credit a
same-passage Mishnah cross-reference (`bekhorot 4a:3` + `bekhorot 1:1`). (b) Codex repeats the
"example offered as an alternative" point. That is a policy call against the architect's #118
direction, so it is escalated, not changed.

## PR approved (architect integration review) + four pre-merge fixes

Architect kept the "example offered as an alternative" choice (codex point declined: never the
answer, 0/125 credited cells, pinned). Pre-merge fixes: (1) the echo lookbehind also skips word /
Roman book ordinals (`First|Second|Third|I|II|III`), so `John 1:1 or First John 3:16` with example
`John 3:16` stays a hedge; 8 of 9 ordinal cases fail without it, no oracle moved. (2) Documented
that the example is a same-work entry by construction, which is why the Ang rivals path never
consults it. (3) `summary.json` gains `headline_drops_segment` (beside `evaluators`) and a per
model x text `segment_match` aggregate `{correct, segment_match}` over correct Talmud/GGS cells, so
the stricter count is reachable without per-cell JSON. (4) arch.md §score.py carries the #112/#118
rules. Merged #121 and #123 (conflict in `test_original_run_regression.py`: #117's refused-outcome
rewrite of row 457 and my 21 cite rows don't overlap; both registries now apply).
Follow-ups the architect filed: viewer display of `segment_match`; key granularity on `source.work`
rather than the label string.
