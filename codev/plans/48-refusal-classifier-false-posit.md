# Plan: Refusal-classifier false positives on web-search hedges

**Specification**: [codev/specs/48-refusal-classifier-false-posit.md](../specs/48-refusal-classifier-false-posit.md)

## Executive Summary

Implements the spec's **Approach 1 (assertion signal)**: the text-retrieval branch of
`outcomes.classify_refusal` gains a third test that keeps a leading-decline cell `refused` unless
the model **asserts the delivered text is its answer to the request** (class A), and keeps it
`refused` when the model **disclaims the delivered text as a different/unconfirmed passage** (class
B). The judge's `refusal_p` is used only to motivate the split and anchor the anti-overfit check —
never at runtime (refusal stays a deterministic, API-free OUTCOME).

The work splits into two phases along a hard seam:

- **Phase 1 — the rule** (`outcomes.py` + unit tests): pure logic, touches no run evidence,
  independently testable, fast feedback. Locks the A/B behaviour against the pre-registered cells.
- **Phase 2 — the sanctioned rebaseline** (regenerate the four committed runs' `scores.jsonl`, add
  the projection-SHA oracle, re-pin Spec 15's constants): the evidence-moving half, done once under
  the witnessed-rebaseline discipline with the moved numbers surfaced to the architect before
  commit.

Per-cell A/B dispositions are **locked here** (architect decision 2026-10-29; B stays refused):

| disposition | cells (`retrieve_quote-…`, all `opus-search` unless noted) | why |
|---|---|---|
| **A → flip refused→incorrect** | `e2d74279aaf0` (haiku-search), `d4c3bda0b400`, `d0239d95ae29`, `b33e7e040058`, `349b0b401f72` | asserts the delivered text IS the requested passage, disclaiming only edition/vocalization ("from memory … is:", "my best reconstruction … is:", "most likely matches this line, is:", "that baraita … starts: «text». That's not the Davidson wording") |
| **B → stay refused** | `f0ffc67a458e`, `4c6f201c7192`, `de9d77a6c963`, `b1a04c81d33f`, `fe52da70f661`, `eaf381cf82d3` | discloses a *different/unconfirmed* segment ("I can't say it's 63b:19", "the start of 54b" ≠ 54b:3, "can't be sure this is the right segment", "I'd rather not guess at an exact line") |
| **B anchor (not in the 11; must match its twins)** | `42f510ea6c7d` (refusal_p 0.58), cross-check `f143cc3f6c63` (0.68) | textually identical to B members `de9d77a6c963`/`fe52da70f661`; a rule that flips them but not this is overfit |

Pinned post-change numbers on `tutorial-2026-10-11` (5 A cells flip = 4 opus + 1 haiku, verified
against committed scores): `opus-search/retrieve_quote` accuracy 0.9737→**0.9250**, coverage
0.76→**0.80**, refused 24→**20**; `haiku-search/retrieve_quote` accuracy 0.80→**0.7879**, coverage
0.65→**0.66**, refused 35→**34**. `correct` bits and the `(exact, normalized, token_f1)` projection
are unchanged.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "Assertion-based refusal rule in outcomes.py"},
    {"id": "phase_2", "title": "Sanctioned rebaseline, projection-SHA oracle, and Spec 15 re-pin"}
  ]
}
```

## Phase Breakdown

### Phase 1: Assertion-based refusal rule in outcomes.py

**Dependencies**: None

#### Objective

Teach `classify_refusal` the A/B assertion distinction so a hedged **delivery** of the requested
passage is scored on its merits while a **declined-with-substitute** answer stays `refused` — with
the behaviour pinned by unit tests over the locked cells and the `42f510ea6c7d` anti-overfit anchor.
No run evidence is touched in this phase.

#### Files to Create / Modify

- `pipelines/sacredbench/outcomes.py` — extend the `_TEXT_RETRIEVAL` branch of `classify_refusal`
  with the assertion test; add a conservative **delivery-assertion** cue family and a
  **passage-identity-disclaimer** cue family (natural form, normalized like `_DECLINE_CUES_RAW`),
  plus a helper (e.g. `delivers_as_answer(answer, expected)`). Update the module docstring to
  describe the A/B rule and its divergence from the Jev rubric.
- `pipelines/tests/test_outcomes_refusal.py` (new, or extend the existing outcomes test module if
  one exists) — unit cases below.

#### Deliverables

- [ ] `classify_refusal` returns **False** (not refused) for the five A cells' answer texts scored
      as `retrieve_quote`, and **True** (refused) for the six B cells, the `42f510ea6c7d` anchor, and
      `f143cc3f6c63`.
- [ ] The rule is expressed as: a leading-decline text-retrieval cell is `refused` **unless** it
      carries a delivery-assertion cue **and** carries no passage-identity-disclaimer cue (default =
      refused; the fallback for an ambiguous cell is to stay refused).
- [ ] `verify_source` and `cite_passage` paths are untouched; the containment half of the existing
      rule is preserved (a decline-prefixed but `bounded_contains` answer stays out of refused).
- [ ] Unit tests for this phase (see Test Plan).

#### Acceptance Criteria

- [ ] All Phase-1 unit cases pass; `.codev/checks/test.sh` (pipelines → uv pytest) is green.
- [ ] No change to `score.py`, graders, the Jev rubric, or any `runs/` artifact in this phase's
      commit (diff is `outcomes.py` + the test file only).
- [ ] A genuine refusal drawn from the jointly-agreed set still classifies `refused`.

#### Test Plan

Unit (`retrieve_quote`, expected text = the committed `expected`):
- **A flips**: each of the 5 A answer texts → `classify_refusal == False`.
- **B stays**: each of the 6 B answer texts → `classify_refusal == True`.
- **Anti-overfit anchor**: `42f510ea6c7d` and `f143cc3f6c63` → `True`, asserted in the *same* test
  body as their B twins `de9d77a6c963`/`fe52da70f661` so a divergent rule fails loudly.
- **Genuine refusals**: ≥3 jointly-agreed refusal texts (e.g. the `i can't reliably reproduce`
  openers) → `True`.
- **Edges**: hedge + pointer only → `True`; hedge + citation echo, no passage → `True`;
  deliver-then-trailing-caveat (cue past the leading window) → unchanged.
- Answer texts are loaded from `runs/tutorial-2026-10-11/answers.jsonl` by `(model_id,
  question_id)` (read-only) or inlined as fixtures; the test does **not** write to `runs/`.

### Phase 2: Sanctioned rebaseline, projection-SHA oracle, and Spec 15 re-pin

**Dependencies**: Phase 1

#### Objective

Re-apply the corrected classifier to every committed run as a **sanctioned, oracle-witnessed
rebaseline**, moving only the enumerated A-class cells, and make the move auditable and permanent:
a projection-SHA oracle proves nothing else shifted, Spec 15's existing pre-registration constants
are re-pinned to the new numbers, and the moved figures are surfaced to the architect before commit.

#### Files to Create / Modify

- `runs/tutorial-2026-10-11/scores.jsonl`, `runs/first-run-2026-10-11/scores.jsonl`,
  `runs/original-2026-10-21/scores.jsonl`, `runs/exp-arabic-prompts-2026-10-29/scores.jsonl` —
  regenerated by re-scoring the committed `answers.jsonl` (keyless; panel/usage fed back verbatim).
  Their `summary.json`/`summary.md` regenerate alongside.
- `runs/tutorial-2026-10-11/jev_agreement.json` + `jev_agreement.md` — regenerated cross-check
  (the deterministic refusal column moves; judge columns unchanged).
- `pipelines/tests/test_refusal_rebaseline.py` (new) — sibling of
  `test_contains_reference_rebaseline.py`: pins the PRE-change `(model_id, question_id) → (exact,
  normalized, token_f1)` projection SHA per run (captured via `git show HEAD:…` before
  regeneration), the exact per-run A-flip set on `outcome` (refused→incorrect), and the invariant
  that `correct` did not move on any cell.
- `pipelines/tests/test_contains_reference_rebaseline.py` — re-pin `REFUSED_COUNTS`,
  `REFUSED_SET_SHA256`, `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`, and
  `test_first_run_overall_and_lds_tradition_pinned` to post-change values.
- The byte-for-byte guards `test_first_run_regression` / `test_tutorial_run` — reconciled with the
  moved numbers the way Spec 15 did (regenerate-then-compare stays valid; the *witness* of "nothing
  else moved" is the new oracle, not these now-partly-circular guards).

#### Deliverables

- [ ] All four runs re-scored into their existing dirs **only** under the rebaseline discipline;
      `answers.jsonl`, `questions.jsonl`, `judgments.jsonl`, and all manifests are byte-unchanged.
- [ ] A per-run enumeration (in the review) of every cell whose `outcome` moved, each with its
      answer text, confirmed A under the assertion rule. Runs with no A-class cells have a
      byte-identical `scores.jsonl` (expected for the non-search `first-run`/`original` cells — to be
      confirmed, not assumed).
- [ ] The projection-SHA oracle + per-run flip-set test passes; `correct` unchanged everywhere.
- [ ] Re-pinned Spec 15 constants pass.
- [ ] Regenerated `jev_agreement.json` shows **no surviving refusal disagreement with `refusal_p <
      0.25`**, and every remaining disagreement lies in `[0.25, 0.75]`.
- [ ] `audit.py` passes over the regenerated artifacts (no restricted-derived artifact committed).
- [ ] Moved numbers surfaced to the architect (`afx send`) before the rebaseline commit.

#### Acceptance Criteria

- [ ] `tutorial-2026-10-11`: `opus-search/retrieve_quote` = 0.9250 / 0.80 / refused 20;
      `haiku-search/retrieve_quote` = 0.7879 / 0.66 / refused 34; the 5 A cells are `incorrect`, the
      6 B cells + `42f510ea6c7d` are `refused`.
- [ ] `.codev/checks/test.sh` green (full pipelines suite, including both rebaseline oracles and the
      reconciled regression guards).
- [ ] Per-run projection SHA matches the pre-change capture (similarity tiers / `contains_reference`
      did not move).

#### Test Plan

- Integration: run the full `uv --project pipelines run pytest` suite via `.codev/checks/test.sh`.
- Oracle: `test_refusal_rebaseline.py` fails if any non-flip-set cell's `outcome` moves, if any
      `correct` bit moves, or if a projection SHA drifts.
- Cross-check: regenerate and assert the `refusal_p < 0.25` survivor criterion on
      `tutorial-2026-10-11`.
- Manual: diff each run's `summary.md` before/after; confirm only the enumerated arms/tasks moved;
      capture the diff for the architect and the review.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Assertion markers can't separate A from B without hand-fitting (e.g. A cell `349b0b401f72` also carries a URL pointer) | Medium | High | Discriminate on **passage-identity disclaimer** (segment not confirmed) vs **vocalization-only disclaimer**, not on pointers/length; pin against all 11 + `42f510ea6c7d`; ambiguous ⇒ stay refused |
| A B-cell flips, or the `42f510ea6c7d` twin diverges from its B twins | Medium | High | Anti-overfit anchor asserted in the same test as the twins; oracle fails if any B/anchor outcome moves |
| A non-tutorial run moves a cell that is not truly A (no judge oracle there) | Medium | High | Enumerate every moved cell with answer text; adjudicate A by the assertion rule; surface to architect before commit |
| Accidental re-score nulls committed panel/usage | Low | High | Keyless re-score feeds panel/usage back verbatim; projection-SHA oracle + answers/judgments byte-check; numbers surfaced first |
| #52 (`normalize()` rebaseline) merges first, re-pinning the same scores | Medium | Medium | Change isolated to `outcomes.py`; rebase, re-capture pre-change SHAs from the merged baseline, re-run oracle |
| porch implement loop force-advances at max_iterations with an unresolved rebuttal | Low | Medium | Treat each impl-consult rebuttal as a gate; verify a clean pass, don't assume one (lessons-critical) |

## Documentation Updates

- `outcomes.py` module docstring — the A/B assertion rule and its deliberate divergence from the Jev
  rubric (paper-facing definition lives in `outcomes.py`; re-align in a future `sacredbench-jev-2`).
- `codev/reviews/48-refusal-classifier-false-posit.md` — the per-run moved-cell enumeration, the
  pinned before/after numbers, and any arch-doc/lessons updates (e.g. a note that refusal is decided
  by *assertion*, under the Scoring map in `lessons-learned.md`).
- No README/API changes; the viewer consumes the regenerated `summary.json` unchanged.
