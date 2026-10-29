# Plan: Refusal-classifier false positives on web-search hedges

**Specification**: [codev/specs/48-refusal-classifier-false-posit.md](../specs/48-refusal-classifier-false-posit.md)

## Executive Summary

Implements the spec's **Approach 1 (assertion signal)**: the text-retrieval branch of
`outcomes.classify_refusal` gains a test that keeps a leading-decline cell `refused` **unless** the
model makes a **positive identity assertion** that the delivered text *is* (its best rendering of)
the requested passage (class A). It stays `refused` otherwise — including when the model delivers a
*different / start-of-daf / unconfirmed-which-part* span (class B). The judge's `refusal_p` is used
only to motivate the split and anchor the anti-overfit check — never at runtime (refusal stays a
deterministic, API-free OUTCOME).

**Rule form (locked by the plan consult, both reviewers HIGH).** The rule is **assertion-only**,
not "assertion AND no-disclaimer":

- A conjunctive *no-disclaimer* gate is **falsified by the locked A set** — A-cell `d4c3bda0b400`
  itself opens "I'm not sure which passage is segment 9", lexically identical to B-cell disclaimers.
  So the rule must trigger on the **presence of a positive identity assertion**, not on the
  *absence* of a disclaimer.
- The assertion signal must be **positive-frame and negation-aware**, not a flat substring family:
  a bare `"from memory"` cue appears in **147 currently-refused cells** (38 tutorial / 34 first-run
  / 75 original), almost all genuine declines ("I can't reliably reproduce … from memory"). The
  signal is the positive frame "*the text of ‹citation› **is**:*" / "*my best reconstruction … **is**:*" /
  "*that ‹unit› **starts**:*" / "*most likely matches this line, **is**:*", **not under a negation**.
- Because A/B turns on identity assertion, the hardest pair (A `d0239d95ae29` "most likely matches
  this line, is:" vs B `eaf381cf82d3` "segment 3 most likely falls somewhere in this passage, but I
  couldn't check it") may not separate without single-cell hand-fitting. The spec's sanctioned
  fallback applies: **when a cell cannot be cleanly placed, it stays `refused` and is surfaced** — so
  the pinned numbers below are **contingent targets**, re-derived from the actual flip set, not hard
  gates that would force overfitting.

The work splits into two phases along a hard seam:

- **Phase 1 — the rule + whole-corpus blast-radius gate** (`outcomes.py` + unit tests): pure logic,
  touches no run evidence. Locks the A/B behaviour against the pre-registered cells **and** asserts,
  read-only across all four runs, that the global `refused_pre − refused_post` set equals exactly the
  locked flip set (catches the "from memory"-style footgun before any regeneration).
- **Phase 2 — the sanctioned rebaseline** (regenerate each committed run's score evidence in its
  actual on-disk layout, add the pre-change outcome/projection oracle, re-pin Spec 15's constants,
  regenerate `original`'s paper-facing `facct.{json,md}`): the evidence-moving half, done once under
  the witnessed-rebaseline discipline with the moved numbers surfaced to the architect before commit.

Per-cell A/B dispositions are **locked here** (architect decision 2026-10-29; B stays refused):

| disposition | cells (`retrieve_quote-…`, all `opus-search` unless noted) | why |
|---|---|---|
| **A → flip refused→incorrect** | `e2d74279aaf0` (haiku-search), `d4c3bda0b400`, `d0239d95ae29`, `b33e7e040058`, `349b0b401f72` | asserts the delivered text IS the requested passage, disclaiming only edition/vocalization ("from memory … is:", "my best reconstruction … is:", "most likely matches this line, is:", "that baraita … starts: «text». That's not the Davidson wording") |
| **B → stay refused** | `f0ffc67a458e`, `4c6f201c7192`, `de9d77a6c963`, `b1a04c81d33f`, `fe52da70f661`, `eaf381cf82d3` | discloses a *different/unconfirmed* segment ("I can't say it's 63b:19", "the start of 54b" ≠ 54b:3, "can't be sure this is the right segment", "I'd rather not guess at an exact line") |
| **B anchor (not in the 11; must match its twins)** | `42f510ea6c7d` (refusal_p 0.58), cross-check `f143cc3f6c63` (0.68) | textually identical to B members `de9d77a6c963`/`fe52da70f661`; a rule that flips them but not this is overfit |

**Contingent** post-change numbers on `tutorial-2026-10-11`, assuming all five A cells flip (4 opus
+ 1 haiku, verified against committed scores): `opus-search/retrieve_quote` accuracy
0.9737→**0.9250**, coverage 0.76→**0.80**, refused 24→**20**; `haiku-search/retrieve_quote` accuracy
0.80→**0.7879**, coverage 0.65→**0.66**, refused 35→**34**. `correct` bits and the `(exact,
normalized, token_f1)` projection are unchanged. These are **targets, re-derived from the actual
flip set and surfaced** before the Phase-2 commit; if a confident A cell strands as `refused` under
the safe fallback, the numbers move toward baseline and the stranded cell is reported, not
hand-fitted.

**Merge order (architect, 2026-10-29):** this PR lands **first**; builder-52 (#52) rebases onto it.
No dependency on #52; these dispositions stay authoritative. #52 will later extend fold-aware
containment *into* `classify_refusal`, moving some **Arabic** refused-cells again afterward — that is
expected and **#52's witness to carry, not this PR's**.

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

### Phase 1: Assertion-based refusal rule in outcomes.py, gated by a whole-corpus blast-radius check

**Dependencies**: None

#### Objective

Teach `classify_refusal` the positive-identity-assertion distinction so a hedged **delivery** of the
requested passage is scored on its merits while a declined/substitute/unconfirmed answer stays
`refused` — pinned by unit tests over the 13 locked cells **and** by a read-only whole-corpus sweep
that proves the rule moves *exactly* the locked flip set and nothing else across all four runs,
before any evidence is regenerated. No run evidence is written in this phase.

#### Files to Create / Modify

- `pipelines/sacredbench/outcomes.py` — extend the `_TEXT_RETRIEVAL` branch (covers **both**
  `retrieve_quote` and `complete_unit`) of `classify_refusal` with a positive-identity-assertion
  helper (e.g. `asserts_delivery(answer)`): a leading-decline cell is `refused` **unless** the
  answer makes a positive identity assertion. Add a conservative **assertion-frame** family
  (natural form, normalized like `_DECLINE_CUES_RAW`), matched **frame-anchored and negation-aware**
  (the frame must be a positive claim — "… is:", "… starts:", "… reads:", "my best reconstruction …
  is" — not preceded by a negation such as "can't … from memory"). Update the module docstring to
  describe the A/B rule, the assertion-only form (and why the conjunctive form is wrong), and the
  deliberate divergence from the Jev rubric.
- `pipelines/tests/test_outcomes_refusal.py` (new; or extend the existing outcomes test module) —
  unit cases + the whole-corpus sweep below.

#### Deliverables

- [ ] `classify_refusal` returns **False** for the five A cells and **True** for the six B cells, the
      `42f510ea6c7d` anchor, and `f143cc3f6c63`, as `retrieve_quote`.
- [ ] Rule expressed as **assertion-only**: `refused` unless a positive identity assertion fires
      (the absence of a disclaimer is *not* consulted — the conjunctive form strands A-cell
      `d4c3bda0b400`). Default on ambiguity = `refused` (safe fallback).
- [ ] Assertion matching is **negation-aware**: a bare `"from memory"` / `"best guess"` substring
      under a decline ("I can't reliably reproduce … from memory") does **not** fire.
- [ ] Whole-corpus read-only sweep (see Test Plan) passes: global `refused_pre − refused_post` ==
      the locked flip set, across all four runs and **all** `_TEXT_RETRIEVAL` tasks.
- [ ] `verify_source` and `cite_passage` paths untouched; the containment half preserved.

#### Acceptance Criteria

- [ ] All Phase-1 unit cases + the whole-corpus sweep pass; `.codev/checks/test.sh` green.
- [ ] No change to `score.py`, graders, the Jev rubric, or any `runs/` artifact in this phase's
      commit (diff is `outcomes.py` + the test file only).
- [ ] If the sweep surfaces any **non-tutorial** cell in the global delta, it is enumerated with its
      answer text and surfaced to the architect **before** Phase 2; the flip set is not silently
      widened.

#### Test Plan

Unit (loaded read-only from each run's answers by `(model_id, question_id)`, or inlined as
fixtures; no writes to `runs/`):
- **A flips**: each of the 5 A answer texts → `classify_refusal == False`.
- **B stays**: each of the 6 B answer texts → `classify_refusal == True`.
- **Anti-overfit anchor**: `42f510ea6c7d` and `f143cc3f6c63` → `True`, asserted in the *same* test
  body as their B twins `de9d77a6c963`/`fe52da70f661` so a divergent rule fails loudly.
- **Negation footgun**: ≥3 currently-refused cells whose answers contain `"from memory"` under a
  decline → `True` (guards the blast radius).
- **Genuine refusals**: ≥3 jointly-agreed refusal texts (`i can't reliably reproduce` openers) →
  `True`.
- **Edges**: hedge + pointer only → `True`; hedge + citation echo, no passage → `True`;
  deliver-then-trailing-caveat (cue past the leading window) → unchanged.
- **Whole-corpus sweep (the gate):** for each of the four runs, read its answers in the on-disk
  layout (`tutorial`/`first-run`/`original`: `answers.jsonl`; `exp-arabic-prompts`: `answers-en.jsonl`
  **and** `answers-ar.jsonl`/`answers-ar-normalized.jsonl`), run `classify_refusal` over every
  `_TEXT_RETRIEVAL` cell, and assert the set of cells whose refusal-outcome would flip equals the
  pre-registered flip set for that run (tutorial = the 5 A cells; the other three = **empty** unless
  the sweep proves otherwise, in which case the deliverable above gates it).

### Phase 2: Sanctioned rebaseline, projection-SHA oracle, and Spec 15 re-pin

**Dependencies**: Phase 1

#### Objective

Re-apply the corrected classifier to every committed run as a **sanctioned, oracle-witnessed
rebaseline**, moving only the enumerated A-class cells, and make the move auditable and permanent:
a projection-SHA oracle proves nothing else shifted, Spec 15's existing pre-registration constants
are re-pinned to the new numbers, and the moved figures are surfaced to the architect before commit.

Each run is regenerated **in its actual on-disk layout** (verified) — there is no single
`scores.jsonl` convention:

- `runs/tutorial-2026-10-11/` — `scores.jsonl` (+ `summary.json`/`summary.md`); `jev_agreement.json`
  + `jev_agreement.md` regenerated (deterministic refusal column moves; judge columns unchanged).
- `runs/first-run-2026-10-11/` — `scores.jsonl` (+ `summary.json`/`summary.md`).
- `runs/original-2026-10-21/` — `scores.jsonl` (+ `summary.json`/`summary.md`) **and**
  `facct.{json,md}` (paper-facing; `facct.py` reads `refused`/`accuracy`/`coverage` verbatim from
  `metrics.outcome`, and `test_facct.py` uses synthetic fixtures, so staleness is otherwise
  uncaught). This run has the largest refused population (223 `retrieve_quote` + 89 `complete_unit` +
  22 `cite_passage`) and is the Spec-26 reference evidence with no Jev oracle.
- `runs/exp-arabic-prompts-2026-10-29/` — **no** `scores.jsonl`/`summary.*`. It has
  `scores-en.jsonl` + `scores-ar.jsonl`, `answers-{en,ar,ar-normalized}.jsonl`, and a **local
  `analyze.py`** that produced the `-ar` artifacts via the orthography fold. Regeneration must drive
  both the `-en` and `-ar` score files through that run's own `analyze.py` path, preserving the
  documented Arabic-normalization transform — not a plain `score_file` over a nonexistent
  `answers.jsonl`.

Files:

- The score/summary/facct artifacts above — regenerated by re-scoring each run's committed answers
  (keyless; **panel/usage/roster/judge-provenance/`generated_at` fed back verbatim** — confirm the
  regenerator preserves this metadata, since a naive `score_file` may not reproduce all summary
  fields).
- `pipelines/tests/test_refusal_rebaseline.py` (new) — non-circular witness (see below).
- `pipelines/tests/test_contains_reference_rebaseline.py` — re-pin `REFUSED_COUNTS`,
  `REFUSED_SET_SHA256`, `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`,
  `test_first_run_overall_and_lds_tradition_pinned`.
- `pipelines/tests/test_first_run_regression.py`, `pipelines/tests/test_original_run_regression.py`,
  and the tutorial guard — reconciled with the moved numbers (regenerate-then-compare stays valid;
  the *independent* witness of "nothing else moved" is the new oracle).

#### Non-circular witness (per the consults)

A projection over `(exact, normalized, token_f1)` cannot prove `outcome`/`correct` stayed put, and
re-pinning `REFUSED_SET_SHA256` from post-change data is circular. So the oracle freezes
**pre-change** state, captured via `git show HEAD:runs/<id>/<scores-file>` before regeneration:

- `PRECHANGE_OUTCOME_SHA[run]` — SHA of the canonical `(model_id, question_id) → outcome` projection.
- Assert post-change: `apply(flip_set, prechange_outcomes) == postchange_outcomes` exactly — i.e.
  the ONLY transformation is `refused → incorrect` on the registered flip set; every other cell's
  outcome is identical.
- Assert the `(model_id, question_id) → correct` projection SHA is **unchanged** (no `correct` moved).
- Keep the existing `(exact, normalized, token_f1)` projection SHA unchanged too.

#### Deliverables

- [ ] Each run re-scored into its existing dir in its real layout **only** under the rebaseline
      discipline; `answers*.jsonl`, `questions*.jsonl`, `judgments.jsonl`, `analyze.py`, and all
      manifests are byte-unchanged.
- [ ] Per-run enumeration (in the review) of every cell whose `outcome` moved, each with answer
      text, confirmed A. Runs whose Phase-1 sweep registered an **empty** flip set have
      byte-identical score artifacts (confirmed, not assumed).
- [ ] The non-circular oracle passes (outcome transform exact; `correct` and similarity SHAs
      unchanged).
- [ ] Re-pinned Spec 15 constants pass; `facct.{json,md}` regenerated and consistent with the moved
      `original` outcomes.
- [ ] Regenerated `jev_agreement.json` shows **no surviving refusal disagreement with `refusal_p <
      0.25`**; remaining disagreements lie in `[0.25, 0.75]`.
- [ ] `audit.py` passes over the regenerated artifacts.
- [ ] Moved numbers (all runs, incl. `facct`) surfaced to the architect (`afx send`) before commit.

#### Acceptance Criteria

- [ ] `tutorial-2026-10-11` matches the contingent targets (or the re-derived-and-surfaced numbers
      if a cell stranded): A cells `incorrect`, B cells + `42f510ea6c7d` `refused`.
- [ ] `.codev/checks/test.sh` green (full pipelines suite: both rebaseline oracles, all three
      regression guards, `test_facct.py`).
- [ ] Pre-change outcome/correct/similarity SHAs reconcile per run (only registered flips moved).

#### Test Plan

- Integration: full `uv --project pipelines run pytest` via `.codev/checks/test.sh`.
- Oracle: `test_refusal_rebaseline.py` fails on any unregistered `outcome` move, any `correct` move,
      or any projection-SHA drift.
- Cross-check: regenerate and assert the `refusal_p < 0.25` survivor criterion on `tutorial`.
- Manual: diff each run's `summary.md` / `facct.md` before↔after; confirm only enumerated
      arms/tasks moved; capture diffs for the architect and the review.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Assertion cue over-fires on genuine declines (the `"from memory"` footgun: 147 refused cells) | **High** | High | Negation-aware, positive-frame matching ("… is:"/"… starts:"), never a bare substring; the Phase-1 whole-corpus sweep fails if the global delta ≠ the locked flip set |
| Hardest A/B pair (`d0239d95ae29` vs `eaf381cf82d3`, both "most likely") can't separate without single-cell hand-fitting | Medium | Medium | Safe fallback = stay `refused` + surface; numbers contingent/derived, not a hard gate; never add a cell-specific cue to force a flip |
| A B-cell flips, or the `42f510ea6c7d` twin diverges from its B twins | Medium | High | Anti-overfit anchor asserted in the same test as the twins; oracle fails if any B/anchor outcome moves |
| A non-tutorial run moves an unexpected cell (no judge oracle there) | Medium | High | Phase-1 read-only sweep catches it **before** regeneration; enumerate + architect-confirm; flip sets pre-registered (empty unless proven) |
| Arabic run regenerated with wrong tool/layout (no `scores.jsonl`; `-ar` via `analyze.py` fold) | Medium | High | Drive `-en`/`-ar` through that run's own `analyze.py`; preserve the documented normalization; byte-check `answers*`/`analyze.py` |
| `original`'s `facct.{json,md}` left stale (no test catches it) | Medium | High | Regenerate `facct` whenever `original` outcomes move; include in the pre-commit diff review |
| Accidental re-score nulls committed panel/usage/provenance | Low | High | Keyless re-score feeds panel/usage/roster/`generated_at` back verbatim; non-circular outcome/correct SHAs + answers/judgments byte-check; numbers surfaced first |
| #52 lands after me and extends fold-aware containment into `classify_refusal` | Low | Low | Per architect: I land first, #52 rebases and witnesses the later Arabic moves, not this PR |
| porch implement loop force-advances at max_iterations with an unresolved rebuttal | Low | Medium | Treat each impl-consult rebuttal as a gate; verify a clean pass, don't assume one (lessons-critical) |

## Documentation Updates

- `outcomes.py` module docstring — the A/B assertion rule and its deliberate divergence from the Jev
  rubric (paper-facing definition lives in `outcomes.py`; re-align in a future `sacredbench-jev-2`).
- `codev/reviews/48-refusal-classifier-false-posit.md` — the per-run moved-cell enumeration, the
  pinned before/after numbers, and any arch-doc/lessons updates (e.g. a note that refusal is decided
  by *assertion*, under the Scoring map in `lessons-learned.md`).
- No README/API changes; the viewer consumes the regenerated `summary.json` unchanged.
