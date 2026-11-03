# bugfix-128 thread — verify_source: Talmudic Aramaic אִין ("yes") read as Hebrew "no"

## 2026-11-02 — investigate

**Reproduced.** `score.parse_yes_no("אין", "he") == "no"`. `_YES_NO_BY_LANG["he"]` and `["arc"]` both list
`אין` under no (#76/#95), and `_strip_marks` drops the hiriq that separates Aramaic אִין (yes) from
Hebrew אֵין, so the leading-stance reader inverts every Aramaic "yes".

**Premise mismatch with the issue.** The issue keys the fix on `arc` cells and keeps `he` cells as
"no". But the Talmud (William Davidson Aramaic) cells carry `source.language: "he"` (Sefaria's
Hebrew-script tag — `texts/raw/Judaism/source.yaml`), not `arc`. `arc` is only 16 Masoretic cells
per arm (the Aramaic portions). An arc-only fix moves zero cells; the issue's unit case
"אין on he → no" contradicts its own 66:1 oracle (those 66 cells ARE `he`).

**Evidence (every verify_source answer under runs/, incl. archive + untracked rerun/facct):**
- Every stand-alone leading אין is on a Talmud Aramaic `ask_english` cell (prompt: "Answer in the
  language of the William Davidson Aramaic edition"). None on ask_native (Hebrew prompt "ענה כן או לא").
- Masoretic (he + arc), every other corpus, runs/archive: **0** cells open with אין.
- rerun-2026-11-03: 66 expected-yes (incorrect) + 1 expected-no (beam `אִין` to Jeremiah 50:23, a
  wrong yes, currently correct).
- git-tracked committed runs: 73 expected-yes + 1 expected-no (same shape, same beam cell).
- facct-2026-11-03 / -pre113 (untracked): 66 expected-yes each.

**Candidate A** (move אין from he/arc "no" to arc "yes"; non-Latin ⇒ read on every cell via #95):
diffed over all runs, moves exactly those cells and nothing else. Mirrors Syriac ܐܝܢ, already "yes"
on every cell.

**Wrinkle:** `test_cross_language_verdict_rebaseline.py::test_only_registered_cells_move_and_only_out_of_refused`
only lets a tracked cell move out of `refused`; the 74 committed movers go incorrect↔correct, so
that scan must accept #128's identity-pinned registry.

Asked the architect to choose A (every cell) vs B (edition-keyed, keeps Masoretic he → no, needs
source fields plumbed into score_answer). Holding before implementing.

## 2026-11-03 — fix (architect chose A)

- `score.py`: `אין` moved from the `he`/`arc` no-lists to the `arc` yes-list; non-Latin ⇒ read on
  every cell (#95), so the Talmud `he` cells read it as yes. Stand-alone rule unchanged
  (`אין לי גישה` → None). `test_score.py`'s `("אין","he","no")` case is now `("אִין","he","yes")`.
- `tests/test_talmudic_aramaic_yes.py`: unit cases + identity registry (committed 73→correct,
  1→incorrect = beam qid 122e8950a7783ac3; rerun 66→correct, 1→incorrect = beam qid e884c1bbd9dd5e5e)
  + a rerun scan: the cells whose stored verdict is `no` and now isn't are exactly the registered set.
  (A plain "outcome unchanged" scan over the rerun is impossible: it was scored before #115.)
- `test_cross_language_verdict_rebaseline.py`: the #95 scan over git-tracked scores now accepts
  #128's registered cells, which must move between correct and incorrect.
- Without the fix: 25 failures; with it: green (rerun witness symlinked in temporarily, removed).
- Not registered: `runs/facct-2026-11-03` and `-pre113` (untracked; 66 Talmud cells → correct each).
  The paper numbers come from a re-score under the final contract.
- arch.md #95 clause updated with the premise correction.
