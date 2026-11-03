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
