# bugfix-147 thread — Talmud native arms: Vilna naming, retrieve + cite at daf+amud

## 2026-11-03 investigate

- Reproduced from the committed question files: every native Talmud prompt names "the William Davidson
  Aramaic edition of the Babylonian Talmud" (EN) / "מהדורת ויליאם דייווידסון הארמית" (HE); retrieve asks
  for `Megillah 23b:3` (Sefaria segment); cite expects `Megillah 23b:3` with a `Megillah 23b:3`-style example.
- Root cause: `items/for-test/review/build_questions.py` — `_EDITION_DISPLAY` + the `he` templates in
  `judaism()`, and `rows_for` asking/expecting the Sefaria segment citation for the Talmud.
- The pool takes ONE passage per amud (the `break` in `judaism()`), so "one retrieve row per amud" holds by
  construction today; I still mark a second same-amud row `unasked`, like #140.
- **Scoring check (issue item 3): a segment-less `Megillah 23b` expected does NOT go through #112 cleanly.**
  Re-scoring the 960 committed native Talmud cite cells at the bare daf+amud (example segment dropped too)
  moves 64 cells correct→incorrect:
  - `canonical_citation_text` rewrites Hebrew daf notation (`מגילה כ״ג ב:א`) only when the expected ends in
    `:segment` (`_DAF_CITATION`), so every Hebrew-notation answer loses its credit;
  - the raw number-shape matcher reads `Bekhorot 4a:2` as `bekhorot 4` beside `bekhorot 4a` — a hedge.
  Fix: a bare daf+amud of a segment-indexed tractate is scored by #112's daf+amud stage alone (Hebrew
  notation rewritten, any volunteered segment dropped, example-echo rule), `segment_match` None. Prototype
  over the committed cells: 0 movers of 913 scored (47 refused). Adding colon rivals (as `_score_at_ang`
  does) moved 1 cell (a quoted `Numbers 3:45` verse), so no rival rule: #112 never had one for Talmud.
- Open question sent to architect: the issue says "the drawn passage stays the row's source.citation, as
  #140 did", but #140 set source.citation to the expected pankti. Going with the explicit wording (drawn
  passage stays); a one-line flip if they want #140's actual behaviour.

## 2026-11-03 fix

- Architect (00:04Z): follow #140's ACTUAL behaviour — retrieve `source.citation` = the segment the
  expected text is (`Megillah 23b:1`), drawn passage kept in `row["drawn"]`. Daf+amud scorer approved:
  containment-free like `_score_at_ang`, `segment_match` null, 0 movers, documented beside GGS.
- `citations._score_at_daf`: canonical text (Hebrew daf notation now rewritten for a bare daf expected
  too: `_DAF_CITATION` accepts no segment), segments dropped, a dangling `23b:` colon dropped, verdict =
  the expected is the single extracted candidate. No raw-matcher OR (it reads `23b:3` as `23`), no
  colon rivals (would mark wrong a committed right answer naming the verse its passage quotes).
  Oracle: 0 outcome movers over all 960 committed native cite cells; 106 n_candidates-only changes pinned.
- `build_questions.py`: Vilna naming; `rows_for` English cite rows now keep the passage's own citation
  (byte-identical for every existing caller); native Talmud cite via `cited_as=talmud_amud`; retrieve
  rows re-asked at the amud opening, one per (sample, condition, amud), `drawn` kept for verify donors.
- Rebuild: only the 4 native Talmud question files change (every other file byte-identical, incl. the
  English Talmud and the Masoretic files whose "no" donors are Aramaic Talmud). Row counts unchanged:
  the pool holds one passage per amud, so no row became unasked.
- `join_run --test` still groups: like Sikh after #140, the `:1` retrieve citation counts as a passage,
  so the 3-passage smoke covers 2 Talmud passages (8 rows), all rows of each.
- Review point: Vilna amudim open mid-sentence, so some expecteds are short (`כנגדו נמי לא בעי`, 4
  words; range 4–78). Retrieval is containment-scored, so a longer reply that includes them is credited.

## 2026-11-04 amend (architect, 00:25Z)

- Short openings: 7 of 30 amudim open with under 10 words, a clause carried over from the previous
  amud (`Megillah 23b:1` is 4). The retrieve expected is now `talmud_opening`: segments :1, :2, …
  space-joined until ≥10 words. Prompt unchanged; `source.citation` stays `<amud>:1`. No natural
  field for the segment span in the row schema, so it is not recorded (recoverable from the raw file:
  the shortest run of segments from :1 reaching 10 words, which the test re-derives).
- Rebuild: only the two population files move (the familiarity Berakhot 2a:1 is 17 words); 7 retrieve
  rows per arm change expected text; lengths now 10–78 words.

## 2026-11-04 review rounds (architect 00:41Z, 00:44Z, 00:54Z, 00:56Z; CMAP round 3)

- 00:41Z P2s: spelled-out Hebrew (`מסכת`, `דף`/`daf`, `עמוד א/ב`, a comma after the tractate) and
  `Megillah, 23b` read in `_daf_text`. Reading them opened a false-credit hedge (an unlabeled second daf),
  so 00:44Z option B: an unlabeled Hebrew daf marked by `דף` or `ע״א/ע״ב` is its own candidate unless it
  restates a named daf. 2 sonnet movers registered (correct→incorrect, hedges in Hebrew reasoning).
- 00:54Z consult findings: (1) the disclaimed-echo rule from `_score_at_ang` adopted (`Gittin 40a or
  Megillah 23b` is a hedge); (2) refusal claim reworded everywhere: 219 and 196 retrieve refusals per arm,
  only 35 and 10 on copyright/licence, most on the segment divisions and orthography of a specific digital
  edition (recounted from the run: all Talmud); (3) line/Mishnah/segment qualifiers ignored, and the
  rebuild test asserts `_is_bare_daf` on every native cite expected.
- CMAP round 3 (e2b152a): gemini APPROVE, claude APPROVE, codex REQUEST_CHANGES. P2: a decimal daf with a
  Hebrew amud (`מגילה 23 ע״ב`, `דף 23 עמוד ב`) scored incorrect; now read (named, unlabeled rival,
  restatement). P3: commit 5b2531d uses a `[bugfix-147]` prefix; left as is (rewriting needs a force-push).
- 00:56Z (the project's Talmud scholar, via the architect): the print convention, a period after the daf
  is amud alef and a colon amud bet, when no digit follows (`מגילה כג:` = 23b; `כג:3` stays a segment
  form, so no amud). Tractate-labelled Hebrew numerals only: a decimal `Megillah 23.` and a bare `כד.`
  with no tractate are not read (too easily a sentence end). `כג, א` / `כג ב` already read.
- Oracle after all of these: 5 movers, registered by identity. 2 sonnet hedges as above; haiku 84b1fbf0
  correct→refused (a decline naming Rosh HaShanah 11a "ולא במסכת מגילה 23b", non-adjacent, plus the
  example form quoted in a note, so the example is a rival); fable 628ae424 `גיטין מ.:י"ג` and f02605da
  `בבא קמא קיא:` incorrect→correct (print convention). n_candidates-only: 127.
- Question files rebuild byte-identical (scorer + comments only this round).
