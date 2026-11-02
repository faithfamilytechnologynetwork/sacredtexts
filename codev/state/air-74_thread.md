# air-74 — Corpus: trim the Arabic hadith pool to the six books (Kutub al-Sittah)

Protocol: AIR (strict). Issue #74. Branch: builder/air-74.

## Decision (owner, Waleed, 2026-11-01)
Arabic hadith pool = the six canonical books (Kutub al-Sittah). Muwatta Malik, Musnad Ahmad,
Sunan al-Darimi leave the catalogue (7th–9th of al-kutub al-tis'a).

## Architect handoff (main, 2026-11-01) — replaces an ASPIR builder; its spec-phase findings:
1. `facct._census` RAISES when a committed run's selected edition leaves the catalogue;
   `runs/original-2026-10-21` selected all 9 hadith. **Decision: FAIL LOUDLY + FREEZE the
   committed card — never fake a `selected_corpus_hash`.** Failure must name #74 + all three
   dropped collections, collect EVERY missing edition (not just the first). Re-express the 2
   card-rebuild tests to assert the loud failure. Keep byte-pin on committed facct.json/md. Add
   a dated prose note to the run README (never touch scores/answers/questions).
2. Pool 20→17 texts, 560→476 questions: re-pin BOTH anchors in test_original_run_regression.py +
   the catalogue pin in test_catalogue.py.
3. Sequencing: main is 493f700 (post-#73, 27 targets). An English-hadith PR for the six books
   (new converter + 6 targets, same source.yaml + anchors) comes within the hour. Before opening
   my PR: merge origin/main and re-pin ONCE from that base.

## What I did
- `texts/raw/Sunni Islam/source.yaml`: removed malik/ahmed/darimi targets; header "nine"→"six"
  (+ Kutub al-Sittah / #74 note).
- `git rm` the 3 payloads (malik.json, ahmed.json, darimi.json).
- `facct._census`: collect ALL missing selected editions → one loud FacctError naming #74 +
  the 3 collections + "no catalogue target" (kept so the generic fail-fast test still matches).
- Re-expressed the 2 card-rebuild tests to assert the loud freeze:
  - test_original_run_regression.py::test_committed_facct_card_is_frozen_and_rebuild_fails_loudly
    (also byte-pins facct.json/md via SHA-256).
  - test_facct.py::test_real_run_frozen_card_fails_loudly_after_hadith_trim.
- test_catalogue.py: 27→24 targets, pool 20→17 (dropped the 3), renamed to _is_seventeen.
- Doc comments nine→six: catalogue.py, generate.py (×3), test_generate.py (×1).
- Run README: additive dated #74 freeze note (evidence bytes untouched).
- Re-pinned anchors in test_original_run_regression.py: ANCHOR_CORPUS_HASH / ANCHOR_DIGEST
  (see below once generate completes).

## Sequencing log (2026-11-01)
- 16:25 architect: "don't wait for #79" → merged abdedee (process artifacts only), pushed. 16:26
  order REVERTED: wait for #79. PR not opened in between (caught before `gh pr create`).
- 16:36 #79 merged (main c5c201f, 33 targets, corpus hash e588c0892cf922ce). Merged main:
  conflicts in source.yaml (kept my 3 removals + their 6 English targets; combined headers),
  test_catalogue.py (33 → 30 targets, pool stays 17), test_original_run_regression.py (combined
  anchor history; ANCHOR_DIGEST stays 48ee2ca017a57afc, ANCHOR_CORPUS_HASH re-pinned from a fresh
  convert + generate over the merged corpus).

## PR #81 round 1 (architect, REQUEST_CHANGES — trim + anchors verified correct)
1. Retracted "rebuild the card" remedy lingered: fixed the live assert message, arch.md (now
   documents the removal-freezes-a-card case and names the new test), run README:159, plus two
   comments the review didn't list (facct.py selected_corpus_hash note, test_facct.py:421).
2. Freeze test now re-derives outcomes from committed scores.jsonl (`_outcome_counts`/`_outcomes`,
   after `_verify_against_summary`) and asserts == frozen facct.json["outcomes"]. Ordered BEFORE the
   loud-failure check so a scores/summary mismatch raises its own "disagree" error instead of a
   wrong-message "#74" failure (review asked for a note about that; reordering removes the trap).
3. Re-homed the deleted real-run pins (zero_question_languages ["grc","la"], the three CARD_PROSE
   correctness strings) on a synthetic four-task fixture; `_make_run`'s writer factored to `_write_run`.
4. `_census` message is generic; #74's note comes from `facct._REMOVED_EDITIONS` (keyed by text key).
   New test: a mixed missing set names all editions, adds the #74 note once; "Nonexistent" alone has no #74.
5. README line 10: "all nine of al-kutub al-tis'a (the nine Arabic hadith collections), plus the Qur'an".
Mutation-checked: a "containment for all four tasks" CARD_PROSE edit and a tampered frozen outcome
both fail the new tests.

## porch tests-check timeout
`porch done 74` → tests check TIMED OUT at 300s (default; no `timeout_ms` in .codev/config.json). The
pipelines suite now takes ~8–8.5 min, so this will hit every pipelines builder. Not a test failure.
Raised with the architect rather than changing shared config inside #74.

## Notes
- Trimmed current corpus = 17 texts (Qur'an + 6 hadith + Talmud-Aramaic + 3 LDS + 3 Bible +
  SGGS + Dhammapada + Gita). This is a DIFFERENT 17 than the run's own 17 (run had 9 hadith, no
  Sikh/Buddhist/Hindu), so ANCHOR_DIGEST ≠ the run's own digest de65959a99dea9b3.
- English-hadith PR adds 6 targets with language=en != canonical ar → OUT of pool, so pool stays
  17 and anchors unchanged; only the catalogue target COUNT moves (24→30) at merge time.
