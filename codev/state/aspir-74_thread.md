# Builder thread — aspir-74: trim Arabic hadith pool to the six books (Kutub al-Sittah)

## Project
Issue #74. Remove Muwatta Malik, Musnad Ahmad, Sunan al-Darimi (the 7th–9th of al-kutub
al-tis'a) from the Arabic hadith pool. Pool 20→17 texts, generate 560→476 questions.

## Ordering / base
PR #73 (Saheeh International English Qur'an) MERGED — main at 493f700, ANCHOR_CORPUS_HASH now
`de2c8679cbde3cf5`, ANCHOR_DIGEST unchanged `93b71460742a8ecd`, **27 catalogue targets** (Saheeh
is English → out of pool, so pool stayed 20). After my trim: 24 targets, 17-text pool.
→ merge origin/main, re-pin BOTH anchors ONCE from that base (both move: removing in-pool texts
changes corpus_hash AND digest, unlike #73 which moved only corpus_hash).

## Specify phase (done drafting, 2026-11-01)
Key findings from exploration:
- `source.yaml`: 10 Qur'an+hadith targets today; remove 3; header comment "nine"→"six".
- 3 payloads (malik/ahmed/darimi.json) are COMMITTED/tracked public-domain → `git rm`, not gitignore.
- `test_catalogue.py::test_real_catalogue_default_pool_is_twenty`: pins len(targets) (27 post-#73)
  + 20-text pool set → update to 24 targets, 17-text set, rename to seventeen.
- `test_original_run_regression.py`: re-pin ANCHOR_CORPUS_HASH + ANCHOR_DIGEST (current-corpus
  anchor). The committed manifest's own digest pin (de65959a99dea9b3) is frozen — unchanged.
- `_family` groups hadith by document_type, NOT a 9-list → no logic change, only comments.
- Stale "nine" wording to fix: source.yaml header, generate.py (41,166,400), catalogue.py (5),
  test_generate.py (347). texts/README.md & CODE_WALKTHROUGH.md had NO "nine hadith" at spec time.

## The real design decision: FAccT card on a removed selected edition
- `runs/original-2026-10-21` selected all 9 hadith (manifest selected_texts = 17, n_questions=476).
  Its manifest entries carry ONLY {work,version,language} — no tradition/license/doc_type.
- `facct._census` RAISES FacctError("selected text … has no catalogue target") when a selected
  text isn't in the live catalogue (written for the ADD case via post_run_filter, not REMOVE).
- TWO tests rebuild the committed card and will break: 
  test_original_run_regression::test_committed_facct_card_matches_the_run, and
  test_facct::test_real_run_census_and_counterfactual.
- `selected_corpus_hash` also would move (payloads deleted) — but _census raises first.
- DECISION (recommended, Approach 1): FAIL LOUDLY + FREEZE. build_facct raises a specific error
  naming the missing edition(s)+#74; committed facct.json/.md left byte-identical (never edit
  committed evidence); re-express the two tests to assert the loud failure with a reason comment.
  Approach 2 (degrade/keep rebuildable) rejected: manifest lacks metadata, payloads deleted →
  would need dishonest out-of-band snapshot + faked selected_corpus_hash. Fighting the issue.
- Surfaced to architect as FYI (mild one-way door: historic card becomes un-rebuildable).

## Status
Spec drafted + committed. Awaiting porch 3-way consult (porch runs it after SPEC_DRAFTED signal).
