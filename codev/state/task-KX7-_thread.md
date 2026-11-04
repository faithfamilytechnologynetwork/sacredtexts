# task-KX7-: refresh the #150 / #149 mover registries after run commit 562f3f6e

**Task.** 562f3f6e re-collected the native Talmud arms of runs/facct-2026-11-03 (#147: new question
ids, files re-ordered) and re-scored the run under #149/#150. Main CI went red on the two
row-indexed oracles, `test_completion_head.py::test_committed_cells_move_only_as_registered` and
`test_talmud_fold.py::test_committed_cells_move_only_as_registered`. Their registries,
`completion_head_movers.tsv` and `talmud_fold_movers.tsv`, were keyed to the pre-recollect rows.

**Generator.** Neither PR (#151, #152) commits a generator. Both say the registry is what the oracle
finds, so I re-ran each oracle's derivation verbatim in a scratchpad script, with every assert kept.
The rows are written exactly as derived, sorted by (folder, row). The header text is unchanged except
for the counts and one form in the Talmud list (`שלוש/שלש` is no longer among the movers; `ב״ד/בית דין`
now is). No row was hand-edited.

**Counts (before → after).**

| registry | facct-2026-11-03 | runs/<model>/base | archive/ | total |
|---|---:|---:|---:|---:|
| completion_head_movers | 177 → 178 | 205 → 205 | 21 → 21 | 403 → 404 |
| talmud_fold_movers | 42 → 41 | 43 → 43 | 0 → 0 | 85 → 84 |

Per text, only Talmud Bavli · William Davidson Edition - Aramaic (`he`) changes:
- completion head: facct 26 → 27, all runs 53 → 54. The other 151 facct movers in 23 texts keep the
  same (folder, row, qid) keys.
- Talmud fold: facct 42 → 41, all runs 85 → 84 (52 complete_unit, 32 retrieve_quote).
- Every non-facct key is unchanged, because 562f3f6e touched only facct-2026-11-03 and runs/paper.

**Movers are real.** The oracle asserts each mover goes incorrect → correct, changing only
contains_reference, correct and outcome. I also checked each one against the committed verdict.
All 488 match, with 0 mismatches. A facct mover is committed as correct, since that run was
re-scored under #149/#150. A mover in any other run is still committed as incorrect, since those
runs were not re-scored.

I then read the word-level diff of every new facct mover:
- **Completion head, 27 new movers.** Each answer holds the ten-word head verbatim and lacks the
  full continuation.
- **Talmud fold, all 84 movers.** Every difference is a guide form: הימנו/ממנו, אע״פ, נכרי for גוי
  or עובד כוכבים, a leading ו, וחייבין, את היציע, בר״ה, רשב״ג, ר׳ or א״ר for רבי, ר״ל, ב״ד, י׳ for
  עשרה, or האסורים.
- Three rows looked odd in the window diff, and I read them raw. gemini-flash r39 has
  `בר"ה בטלה …` verbatim further on, kimi's answer has a leading ו (`ורחל`), and astra r64 has
  `מתני'` before the passage.

**Scope note.** Two pinned counts in the test files restate the registries, so they had to move with
them. `test_completion_head.py::test_registered_mover_counts` went from facct 177 to 178, and the last
line of the Talmud oracle went from 42 to 41. That makes four files plus this thread, not the two TSVs
the brief named. No scoring code was touched.

**Verification.** This worktree's runs/ holds exactly the 597 tracked scores.jsonl, so the oracles
see what CI sees. `uv --project pipelines run pytest pipelines` gave 1504 passed, 35 skipped, 0
failed. Before the two count edits, the only failures were the two pinned counts; both set-equality
oracles already passed.
