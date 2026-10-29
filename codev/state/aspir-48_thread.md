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

Spec drafted; signalled SPEC_DRAFTED. Porch ran the 2-way consult (codex + claude).

### Consult + major reframe (2026-10-29)

- **codex: COMMENT** (minor) — "near-certain" overstated (6/11 at refusal_p 0.36-0.49); pin moved numbers.
- **claude: REQUEST_CHANGES (HIGH)** — the decisive finding, which I verified directly in the run data:
  the issue's "flip all 11" premise is UNSATISFIABLE. Agreed refusal `opus-search/retrieve_quote-42f510ea6c7d`
  (refusal_p 0.58, NOT in set) is textually identical to flip-set members `de9d77a6c963` (0.45) and
  `fe52da70f661` (0.47) — same "I couldn't find X; closest is a DIFFERENT line «…»; can't say it's the
  segment; pointer". No length/script/quote signal separates them (confirmed: 42f=484 chars vs de9=445).
  So flipping all 11 while keeping the 0.58 twin refused = overfitting the oracle.

- **Resolution** (architect ENDORSED my default, 2026-10-29): split by **assertion**, not refusal_p.
  A = delivered-as-answer (model presents text AS its answer, "from memory X is:", "best reconstruction")
  → flips refused→incorrect. B = declined-with-substitute (different/unidentified line + pointer, explicitly
  NOT the requested passage) → STAYS refused. The 5 confident cells (refusal_p ≤0.16) are A; the 6 borderline
  (0.36-0.49) + the 0.58 twin are B. Rationale: taxonomy asks "did the model purport to answer?"; scoring B
  incorrect rewards confident confabulation; coverage already prices the decline (Spec 15). Mirrors
  verify_source leading-stance. Jev rubric UNTOUCHED this PR (#47 grader identity); divergence noted,
  re-align in future sacredbench-jev-2.

- **Pinned numbers** (confident-5 flip): opus-search retrieve_quote acc 0.9737→0.9250, cov 0.76→0.80,
  refused 24→20; haiku-search 0.80→0.7879, cov 0.65→0.66, refused 35→34. (flip-all-11 would've been
  opus 0.8605 — withdrawn.)
- **Retargeted criterion**: not "agreement_rate==1.0" (needs overfit) but "no surviving refusal disagreement
  with refusal_p<0.25; survivors lie in [0.25,0.75]". Anti-overfit test: 42f510ea6c7d must get the SAME
  outcome as its 0.45/0.47 twins.
- **Must re-pin** Spec 15's hand-surveyed constants (REFUSED_COUNTS/REFUSED_SET_SHA256/EXPECTED_*/
  test_first_run_*) — they break and go unmentioned in draft 1.
- Per-cell A/B dispositions locked at PLAN phase. Spec revised + checks pass.

### Plan phase (2026-10-29)

Per-cell A/B LOCKED (verified against full answer text in answers.jsonl; sha of crux cell
349b0b401f72 opus-search matches its judgment answer_digest — no data drift):
- A (flip refused→incorrect, 5): e2d74279aaf0(haiku-search), d4c3bda0b400, d0239d95ae29,
  b33e7e040058, 349b0b401f72 (opus-search). All assert "the text IS [requested passage]",
  disclaiming only edition/vocalization.
- B (stay refused, 6): f0ffc67a458e, 4c6f201c7192, de9d77a6c963, b1a04c81d33f, fe52da70f661,
  eaf381cf82d3 (opus-search). All carry a passage-IDENTITY disclaimer (segment not confirmed /
  different line / "start of daf" ≠ requested segment).
- B anchor (anti-overfit, not in 11): 42f510ea6c7d (0.58) + f143cc3f6c63 (0.68) — identical
  template to de9d77a6c963/fe52da70f661, MUST classify same (refused).

Gotcha learned: URL pointer is NOT a B marker — A cell 349b0b401f72 also has a sefaria URL.
The discriminator is passage-identity disclaimer vs vocalization-only disclaimer.

2 phases: (1) outcomes.py assertion rule + unit tests (no run evidence); (2) sanctioned rebaseline
of all 4 runs + projection-SHA oracle (sibling of test_contains_reference_rebaseline.py) + re-pin
Spec 15 constants (REFUSED_COUNTS/REFUSED_SET_SHA256/EXPECTED_*/test_first_run_*). Pinned numbers:
opus-search rq 0.9737→0.9250 / 0.76→0.80 / 24→20; haiku-search 0.80→0.7879 / 0.65→0.66 / 35→34.

Plan drafted; porch runs 2-way plan consult next.
