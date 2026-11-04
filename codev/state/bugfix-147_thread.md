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
