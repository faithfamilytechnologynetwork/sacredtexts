### Iteration 1 Reviews
- codex: REQUEST_CHANGES — The plan is well structured, but it replaces the specification’s mandatory zero-collision gate with a weaker hand-review process and underspecifies the rebaseline oracle.
- claude: REQUEST_CHANGES — Strategy and rule derivation are sound, but the plan under-scopes the shared-primitive blast radius: it omits the primary Arabic regression guard, misses a generate-digest cascade, leaves the containment fork unresolved (which falsifies its #48 refusal-independence claim), and lacks a mark-skipping word-boundary predicate that 2,972 real corpus words require.

### Builder Response to Iteration 1
# Plan 52 — Rebuttal to iteration-1 plan consults

Both reviewers returned **REQUEST_CHANGES** (HIGH) while explicitly endorsing the strategy,
rule derivation, sequencing, and the Spec-15-protecting choices. Every point is **accepted**;
the fixes are additive scope + three forced decisions, not a redesign. Load-bearing claims were
re-verified against the code before revising (generator uses `normalize`; `bounded_contains`
consumers; `test_original_run_regression` asserts; the mark-adjacency trap).

## Forced decisions (both consults converged)

**Scoping — scoring-only `score_normalize()`, shared `normalize()` untouched.** Verified
`generate.py:70,232,248,418` and `editions.py` import the shared `normalize()`; folding there
moves verify_source negative-selection and the committed `ANCHOR_DIGEST`
(`test_original_run_regression.py::test_regenerating_original_run_reproduces_digest`), making the
reference run non-reproducible, and touches the copyright path (`audit.py` → `strip_script_marks`).
The spec mandates the pre-Mn ordering but not the host function. Resolution: `normalize()` stays
byte-identical; the fold lives in `score_normalize()`; generation/editions/audit untouched; digest
stable. (claude #2, #7-audit; codex-adjacent.)

**Containment contract — extend the single `bounded_contains`, not a parallel function.** Its
callers are `score_answer`, `outcomes.classify_refusal:133`, `facct.py:277`, `probes.py:203`; a
parallel Arabic fn would let facct silently diverge while `test_facct.py:505` still passes.
Resolution: `bounded_contains` uses `score_normalize` + whitespace-insensitive Arabic handling;
one contract for all callers. (claude #3.)

**Refusal-independence corrected.** Consequence of the above: `outcomes.classify_refusal` folding
means some Arabic `refused` cells reclassify (a decline-prefixed Imla'i delivery is no longer
mislabelled refused — correct behaviour). So the flip set is **not** refusal-independent and a
#48 rebase is **not** automatically clean; the witness is re-run after a rebase. The plan's risk
row and witness are corrected, and the architect was notified (my earlier claim was wrong).
(claude #3 second half.)

## claude (REQUEST_CHANGES)

1. **`test_original_run_regression.py` omitted (the Arabic guard, 840 cells).** ACCEPTED — added to
   Phase 2: re-pin its re-score + facct asserts; the digest assert is confirmed stable because
   `normalize()` is untouched.
2. **Generator-code drift / `ANCHOR_DIGEST`.** ACCEPTED — avoided by the scoring-only normaliser
   decision above; digest stays pinned, no re-pin needed.
3. **Containment fork + refusal coupling.** ACCEPTED — resolved as above; #48 reasoning corrected.
4. **Word-final detection must skip marks (2,972 words; `وَعَلَىٰٓ`).** ACCEPTED — the fold's
   boundary predicate skips Mn + `_SCRIPT_EDITORIAL` to find the next real letter; a stacked-mark
   unit test on `وَعَلَىٰٓ` (must stay `وعلي`, not `وعلا`) added to Phase 1.
5. **Experiment-run file layout wrong.** ACCEPTED — Phase 2 now uses the run's real layout
   (`scores-en.jsonl`/`scores-ar.jsonl`, its own `analyze.py`, no summary) and states the
   `answers-ar-normalized.jsonl` disposition (keep as provenance; the fold supersedes it).
6. **`سَأَلَ`≠`سَالَ` unsatisfiable + dropped.** ACCEPTED — recorded as a pre-existing merge (both
   `→سال` today via hamza-seat decomposition), out of scope, in Phase-1 deliverables.
7. **Smaller items.** ACCEPTED — audit comment clarified by the scoping decision (fold is in
   `score_normalize`, not inside `strip_script_marks`, so the copyright fingerprint is unchanged);
   `TUTORIAL.md:275-278` + `CODE_WALKTHROUGH.md` added to Phase-3 doc refresh; cite_passage Arabic
   cells noted as movable and included in the hand-verification budget (the answer-script partition
   already covers them).

## codex (REQUEST_CHANGES)

1. **Non-collision gate weakened vs spec.** ACCEPTED in substance, with a flagged refinement: a
   literal word-level zero-collision gate is infeasible (it would reject the core maqsura→ya fold,
   and `نبى`/`نبّئ` is mostly pre-existing). The operative hard gate is hand-verification of every
   moved cell at scoring granularity (no wrong credit — the spec's intent); the vocab sweep is a
   diagnostic that must show introduced non-variant merges cause no wrong credit on any committed
   answer. Surfaced to the architect rather than silently overriding the spec SC.
2. **Witness must pin the full before/after projection delta, not just flips.** ACCEPTED — the new
   `test_orthography_rebaseline.py` pins every Arabic cell whose `normalized`, `token_f1`,
   `contains_reference`, `correct`, or `outcome` changes.
3. **Experiment-run layout.** ACCEPTED — same as claude #5.
4. **End-to-end word-boundary test through `score_answer`.** ACCEPTED — Phase 2 asserts, through
   `score_answer`, that Arabic `exact`/`normalized`/tokenisation are unchanged by the word-boundary
   rule while only `contains_reference` supplies the match.

## Net

No disputes. Strategy unchanged; the revision closes the shared-primitive blast radius (scoping,
containment contract, the omitted Arabic guard, the mark-skipping predicate), strengthens the
witness to a full projection delta, corrects the refusal-independence claim, and flags one
spec-vs-feasibility refinement to the architect.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
