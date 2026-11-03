# bugfix-90 thread — items/for-test prompts never name the work (#90)

## Investigate (2026-11-03)

**Reproduced.** Surveyed every committed `items/for-test/**/questions.jsonl`. Work-less edition phrases in prompts:
book-of-mormon ("2013 edition"), judaism prompt-english + english ("William Davidson Edition - Aramaic/English"),
sikhism prompt-english ("the Shabad OS (SGPC Shabadaarth) edition"), buddhism prompt-english ("the Chaṭṭha
Saṅgāyana (VRI) edition"), hinduism english ("the Annie Besant (1922) edition"), encyclicals ("the Vatican English
text (Pope, date) edition"). Native splices: hinduism prompt-native "क्या यह पाठ the Stotra Samhita (Gita Press text)
edition से है?", buddhism prompt-native "Ayaṃ pāṭho the Chaṭṭha Saṅgāyana (VRI) edition potthakato?".
Fine/untouched: christianity (NRSV / Masoretic / Greek NT), islam (owner-signed #75), judaism + sikhism
prompt-native (Hebrew/Punjabi templates already name the work).

**Root cause.** `edition_name(version)` (duplicated in build_questions / build_remaining / build_supplemental)
formats only the catalogue `version` ("the X edition", or X verbatim if it already contains "edition"); the work is
never an input. `_EDITION_DISPLAY` (#75) overrides it only for the two Qur'an editions. The four `EN` templates
(duplicated in 4 scripts) and build_remaining's `SA`/`PI` native templates splice that string in, so all four tasks
inherit it.

**Surprise — the committed question files are NOT reproducible from the builders.** Re-ran each builder in a
scratch copy:
- build_supplemental (BoM, encyclicals): byte-identical. ✅
- build_questions: Islam byte-identical; Christianity/Judaism/Sikhism differ — committed ids don't match the
  builder's own id formula (prompts were edited after ids were assigned), "no" donors were later re-targeted
  (`retarget_verify.py` keeps ids), Judaism-English quotes predate `prompt_text`. Christianity re-run also needs
  network (oremus NRSV).
- build_remaining (Gita, Dhammapada): "yes" rows identical, but every "no" row's donor drifts, because `donors()`
  reads the current question tree, which has grown since.
So "re-run the builders" would change donors and Christianity too — far beyond the wording defect.

**Plan.** (1) Fix the builders: one `edition_name(version, work)` + `_EDITION_DISPLAY` in build_questions that
names the work for every edition; the other scripts import `EN`/`edition_name` instead of duplicating them; SA/PI
native templates name the work in-language. (2) Regenerate the affected committed files with a wording-only
rewrite (parse each prompt against its old template, re-render with the fixed one, recompute the id with the
builder formula); passages, donors and expected answers are untouched. Cross-check: for BoM/encyclicals (and
Gita/Dhammapada "yes" rows) the rewrite must equal the fixed builder's output. (3) Regression test in
pipelines/tests. runs/ untouched (architect: collection in flight on main; re-collection is the architect's call).

## Fix — direction changes (2026-11-03)

- 00:33 architect approved the wording-only rewrite. Implemented: shared `EN` / `edition_name(version, work)` /
  `_EDITION_DISPLAY` in build_questions.py (fail-fast for an unnamed edition), imported by build_remaining /
  build_supplemental / build_christian_original / build_review; SA/PI native templates name the work in-language;
  `review/name_the_work.py` rewrote 18 files (only prompt+id moved, 2420 ids unique). Cross-check vs FIXED builders:
  BoM + encyclicals byte-identical; every other rewritten row whose prompt the builder reproduces also has the same id.
- 00:36 architect DIRECTION CHANGE (owner): FULL RERUN — fold retarget_verify into the builders, one documented
  command regenerates every questions.jsonl, closes #91. Rewrite stopped; nothing committed.
- Flagged to architect: this exceeds BUGFIX's ceiling. Donor selection today is 4 mechanisms that read each other's
  outputs from the tree in a cycle (build_remaining <-> build_christian_original); build_questions' `_donor_rank` already
  encodes the Masoretic/NRSV/BoM near-miss rules but its in-memory pool never contains Masoretic or BoM rows, which is
  why retarget_verify existed. Determinism = two-phase pipeline (all yes-rows, then one donor function over one pool).
  Asked for sign-off on donor-rule defaults + whether to stay under bugfix-90. Waiting.

## Fix — full rerun (architect 00:40: defaults approved, stay under bugfix-90, >300 LOC accepted, 3 h time box)

- One pipeline: `build_questions.py` `main()` = `build_all()` (every set's yes rows: its own 4 traditions +
  `build_christian_original.build` + `build_supplemental.build` + `build_remaining.build`) -> `add_verify_negatives`
  over ONE pool -> `output_files()` ({path: text} from each builder) -> write. Nothing reads the question tree any
  more, so the build-order cycle (build_remaining <-> christian_original) is gone.
- Donor rule = METHODOLOGY.md table, one function `_donor_pool`; per-row seeded RNG (tradition|edition|condition|
  sample|citation) over a sorted, de-duplicated pool. Hadith donors unchanged (Islam byte-identical).
- Network: NRSV (oremus, strict utf-8 decode), WLC + Scrivener at pinned commit SHAs; any failure raises; nothing is
  written until every set is built. Provenance in the Christian passages.json files.
- Reproduction: three full runs (2 scratch + the worktree) byte-identical. One oremus timeout on a back-to-back run
  failed loudly with no partial write (as designed). Offline rebuild test (`test_question_sets_rebuild.py`,
  fetches replaced by committed wording) reproduces all 38 question files.
- vs HEAD: every passage / citation / expected answer unchanged; only prompts (#90 wording) and "no" donors moved;
  1724 of 2420 ids changed (Islam 0). retarget_verify's 4 rules reproduced (Talmud-Aramaic -> Masoretic 15/15,
  Talmud-English -> NRSV Hebrew Bible 15/15, NRSV -> BoM 17/17, Masoretic -> Talmud Aramaic 10+10) -> deleted.
- Old sets broke their own table (Masoretic familiarity drew Sikh/Hindu donors; NRSV donors labelled with the stale
  tradition "The Church of Jesus Christ of Latter-Day Saints") — the new table test fails on HEAD for that reason.
- Pre-existing, unrelated: `test_collect.py` `_DaemonPool` uses ThreadPoolExecutor private `_initializer`, gone in
  Python 3.14 (this env). Not touched by this branch.

## Tests check (2026-11-03)

- `porch check` fails ONLY on 9 pre-existing tests (test_collect 6, test_phase2_tools 3), all
  `_DaemonPool._initializer` on Python 3.14. They are #97, pre-existing (they fail on origin/main 7cff2fd). Per the
  architect: don't patch `_DaemonPool` here; open the PR anyway, and merge origin/main once #97 lands to get a clean gate.
