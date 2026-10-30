# Phase 2 impl consult — iter 3 rebuttals

**codex: APPROVE (HIGH), no issues.**

**claude: REQUEST_CHANGES (HIGH)** — caught a real, self-corrected error in my documentation of the
`ءَا`↔`آ` residual. Surfaced to the architect, who chose **option (B)** (document + pin + defer the
fold extension, with requirements). All folded.

## claude blocking: the `ءَا`↔`آ` residual was understated (claimed 1 cell / no bias) — FIXED
claude's census of 8 cells is correct; I reproduced it exactly with a proper detector (delete a
hamza immediately before an alef, then run the existing optional-ā fold) and verified the asymmetry
by hand. The residual is **8 committed cells** (all `contains_reference=0`), and on the tutorial run
it is **asymmetric** — haiku-search wrote «ءَا» (credited), haiku wrote «آ» (uncredited) on the same
verse, so ~2–3 pts of the committed haiku→haiku-search "search lift" is this residual, not retrieval.
The committed rebaseline remains a strict superset (under-credit only; nothing wrongly credited).

Per the architect's (B) requirements:
1. **Pre-registered** the exact 8-cell set in `test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL`
   + `test_hamza_alef_residual_is_pre_registered_and_uncredited` (asserts all 8 are
   `contains_reference=0` today — the follow-up fold's ready-made oracle).
2. **Filed the follow-up issue #60** (fold extension `ءَا`↔`آ` + `ىٰ`↔maqsura, the pinned set, the
   asymmetry evidence incl. 1d74fc87541b/a8df3e43d35d/8c4ce779621f); referenced from the PR body,
   the tutorial README, the exp README, and the review doc.
3. **Quantified** the artifact in the tutorial README (~2–3 pts, haiku under-credited) and corrected
   its "3 missing = content errors" claim (2 of the 3 are the residual); added the asymmetry note to
   the exp README (its 4 cells are symmetric, so no en/ar skew there).
4. The moved-numbers **packet** handed to the architect at the pr gate includes the residual census.

## claude minor 1: probes `_LETTER_FOLD` divergence undocumented — FIXED
Documented in `fold_arabic_letters`: it is a looser PROBE-ONLY fold (collapses `آ→ا`, `ة→ه`
outright), deliberately NOT the scoring contract; never feeds a headline.

## claude minor 2: `_single_citation_correct` fold-branch loose for short Arabic citations — FIXED
Added a NOTE at the cite_passage call: a verified no-op on committed evidence (0 Arabic citations);
if #39 introduces Arabic citations, revisit the citation predicate rather than inheriting the
verse-length fold.

Suite after fixes: pipelines 638 pass / 2 skip (witness 25); viewer 187; audit OK. Advancing to the
pr gate (human approval) — I do not self-approve.
