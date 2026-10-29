# Builder aspir-48 — Refusal-classifier false positives (#48)

## Specify phase (2026-10-29)

**Problem**: `outcomes.classify_refusal` over-calls `refused` on `*-search` answers that hedge
("I couldn't find the exact edition…") then deliver the passage in a different vocalization that
`bounded_contains` can't fold. Both halves of the rule (leading cue + reference-not-delivered) fire,
so a genuine attempt is labelled `refused` and dropped from the accuracy denominator — biasing the
paper's search-arm accuracy/coverage.

**Pre-registered set**: the exact 11 `(model_id, question_id)` cells in
`runs/tutorial-2026-10-11/jev_agreement.json` where deterministic=`refused` but judge `refusal_p`
low (`deterministic_only=11`, `judge_only=0`). All `retrieve_quote`, 10 opus-search + 1 haiku-search.
Enumerated in the spec table. These flip `refused → incorrect` (correct bit already 0).

**Recommended approach**: detect best-effort delivery past the hedge (Approach 1) — keeps refusal
deterministic/byte-stable, does NOT wire the judge into the outcome layer (that's the cross-check,
not a runtime input). Rebaseline committed scores.jsonl under the sanctioned-rebaseline discipline
(projection-SHA oracle + pre-registered flip set, à la `test_contains_reference_rebaseline.py`),
surface moved numbers to architect before commit.

**Open**: which runs beyond tutorial-2026-10-11 the global rule also moves (plan must enumerate);
sequencing vs #52 (aspir-52, concurrent normalize()/orthography rebaseline — architect heads-up
2026-10-29: expect rebase + oracle re-run if their PR merges first).

Spec drafted; signalled SPEC_DRAFTED. Porch runs the 3-way consult next.
