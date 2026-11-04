# task-wndi: refresh Gurmukhi verse-counter mover row indices

**Task.** Commit 229a7ff (runs/facct-2026-11-03 rebaseline: Sikh retrieve rows replaced per #140,
Sikh cite rows per #135) reordered the Sikh `answers.jsonl` files. That left the #134 oracle
`test_gurmukhi_verse_counter.py::test_committed_cells_move_only_as_registered` pointing at stale
row indices for the five facct-2026-11-03 movers.

**What changed.** Only `pipelines/tests/testdata/gurmukhi_verse_counter_movers.tsv`, five row
indices. The folders and question ids are unchanged, and so is the set of moving cells:

| folder (facct-2026-11-03/…/sikhism/native/population/) | qid | old | new |
|---|---|---|---|
| astra/base/…/prompt-english | 715857cce322744d | 65 | 32 |
| fable/base/…/prompt-english | fedccb9fed113993 | 106 | 53 |
| fable/base/…/prompt-native | 8d44031c082424c0 | 64 | 33 |
| fable/base/…/prompt-native | 318e714fc6590b9b | 107 | 54 |
| opus/base/…/prompt-native | 318e714fc6590b9b | 109 | 54 |

I looked up each new index directly by question id in the tracked answers files. Each is still
the only row with that qid, and its task is still `complete_unit`. The two earlier per-model
movers (opus 108, sol 63) did not move.

**Verification.** This worktree's `runs/` holds exactly the tracked `scores.jsonl` set. The
untracked local copies (`-pre113`/`-pre135`/`-pre140`, `rerun-2026-11-03`, `opus-run-2026-10-11`)
live only in the main checkout, so the oracle here sees what CI sees.
`test_gurmukhi_verse_counter.py`, `test_devanagari_avagraha.py` and `test_sggs_ang_only.py`
gave 124 passed, 0 skipped.
