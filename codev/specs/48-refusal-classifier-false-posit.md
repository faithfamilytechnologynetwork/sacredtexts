# Specification: Refusal-classifier false positives on web-search hedges

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/48-*.md.
-->

## Problem Statement

The deterministic refusal classifier (`outcomes.classify_refusal`, Spec 15) **over-calls
`refused`** on a specific class of web-search answers: ones that open with a hedge about not
finding the *exact* edition ("I couldn't find the exact William Davidson Edition text of …") and
then **deliver the passage anyway** — usually in a different vocalization/orthography that the
deterministic containment grader cannot fold.

This matters because `refused` is not a neutral label. A `refused` cell is **excluded from the
accuracy denominator** (`accuracy = correct/(correct+incorrect)`) and **counted in coverage**
(`coverage = (correct+incorrect)/n`). A *false* `refused` therefore silently biases both headline
numbers the FAccT paper cites — it inflates accuracy (by dropping a genuine attempt that was in
fact a miss) and understates coverage. The bias lands entirely on the `*-search` arms, so it
distorts exactly the search-on-vs-off comparison the benchmark exists to make.

The affected parties are the benchmark's consumers: the paper's error analysis, the viewer's
leaderboard/standings, and anyone reading accuracy/coverage per arm. Today the only thing that
catches the error is the Spec 21 Jev refusal cross-check, run by hand.

## Current State

`classify_refusal` (in `pipelines/sacredbench/outcomes.py`) decides a text-retrieval cell is
`refused` iff **both**:

1. a **decline cue** opens the answer (a cue from `_DECLINE_CUES_RAW` appears within the first
   `LEADING_WINDOW = 60` normalized characters), **and**
2. the expected reference text is **not** word-bounded-contained in the answer
   (`not bounded_contains(answer, target)`).

The cue list includes hedges such as `"i couldn't find"`, `"i couldn't get"`,
`"i couldn't retrieve"`, `"i couldn't confirm"`, and `"i can't give you that"`. On the `*-search`
arms, models routinely open with one of these about the *exact edition* and then supply a
best-effort passage in a different vocalization. Because that delivered text is a different
orthography, `bounded_contains` reads 0, so **both** halves of the rule fire and the cell is
labelled `refused` — even though the model demonstrably attempted and delivered an answer.

**Evidence (pre-registered test set).** Spec 21 phase-4 validation produced
`runs/tutorial-2026-10-11/jev_agreement.json`. Its refusal confusion matrix shows **11 cells where
the deterministic outcome is `refused` but the judge's `refusal_p` is low** (`deterministic_only =
11`, `judge_only = 0`): these are the only refusal disagreements on the run, and every one is a
`retrieve_quote` cell on a `*-search` arm. The 11 (model_id, question_id) pairs:

| model_id | question_id | refusal_p | matches_requested_p |
|---|---|---|---|
| opus-search | retrieve_quote-349b0b401f72 | 0.16 | 0.63 |
| opus-search | retrieve_quote-4c6f201c7192 | 0.45 | 0.09 |
| opus-search | retrieve_quote-b1a04c81d33f | 0.46 | 0.08 |
| opus-search | retrieve_quote-b33e7e040058 | 0.11 | 0.28 |
| opus-search | retrieve_quote-d0239d95ae29 | 0.09 | 0.93 |
| opus-search | retrieve_quote-d4c3bda0b400 | 0.04 | 0.27 |
| opus-search | retrieve_quote-de9d77a6c963 | 0.45 | 0.04 |
| haiku-search | retrieve_quote-e2d74279aaf0 | 0.03 | 0.87 |
| opus-search | retrieve_quote-eaf381cf82d3 | 0.49 | 0.33 |
| opus-search | retrieve_quote-f0ffc67a458e | 0.36 | 0.04 |
| opus-search | retrieve_quote-fe52da70f661 | 0.47 | 0.45 |

All 11 share the shape: a leading "I couldn't find/get/confirm the exact …" followed by a delivered
passage (often in original Hebrew/Aramaic/Arabic script). In 3 of them (`matches_requested_p` ≥
0.63) the judge thinks the delivered text actually matches the requested passage; in the rest the
delivery is a genuine miss. Either way the judge is near-certain it is **not a refusal**.

The committed run evidence already carries the baseline these numbers come from — e.g. on
`tutorial-2026-10-11`, `opus-search/retrieve_quote` reports accuracy 0.9737 / coverage 0.76 /
refused 24, and `haiku-search/retrieve_quote` reports accuracy 0.80 / coverage 0.65 / refused 35.
Those are the figures a correct classifier must move.

## Desired State

`classify_refusal` distinguishes a **hedged-but-delivering** answer from a **genuine
non-delivery**. An answer that opens with a hedge about the exact edition and then supplies a
best-effort passage is an **answer with a disclaimer**, scored on its merits (`correct` /
`incorrect` by the selected graders), **not** `refused`. A genuine decline — the model states it
is not providing the text and provides none — stays `refused` exactly as today.

Concretely, after the change, on `tutorial-2026-10-11`:

- All **11** pre-registered cells flip `refused → incorrect` (their `correct` bit is already 0 —
  the delivered text is a non-matching vocalization under the default deterministic graders, and
  the judge/equivalence flip is Spec 21/#32 diagnostic territory, out of scope here).
- The refusal cross-check reaches **perfect agreement** with the judge on this run
  (`deterministic_only` 11 → 0; refusal `agreement_rate` 0.9725 → 1.0).
- Accuracy drops and coverage rises on the two search arms by exactly the amount those 11 genuine
  misses re-enter the denominator — the direction the paper needs corrected.
- **No other cell's outcome moves** on this run, and the `(exact, normalized, token_f1)` similarity
  projection is byte-identical (those fields are untouched).

Because the classifier is global, the same corrected rule is re-applied to **every committed run**,
regenerating their `scores.jsonl` as a **sanctioned, oracle-witnessed rebaseline** (not a forbidden
re-score). Any outcome that moves on a run other than `tutorial-2026-10-11` must be a true
correction of the same hedge-then-deliver class, enumerated and surfaced to the architect before
the moved numbers are committed.

## Success Criteria

- [ ] All **11** pre-registered `(model_id, question_id)` cells in `tutorial-2026-10-11` have
      `outcome == "incorrect"` (were `refused`) after re-scoring; their `correct` bit stays 0.
- [ ] On `tutorial-2026-10-11`, the refusal cross-check `deterministic_only` count is **0** and the
      refusal `agreement_rate` is **1.0** (the 116 jointly-agreed refusals stay `refused`; the 273
      not-refused stay not-refused).
- [ ] **No non-pre-registered cell** flips outcome on `tutorial-2026-10-11`; the per-run
      `(model_id, question_id) → (exact, normalized, token_f1)` projection SHA is unchanged
      (contains_reference and the similarity tiers do not move).
- [ ] The rebaseline is **witnessed**: an oracle test (sibling of
      `test_contains_reference_rebaseline.py`) pins the pre-change projection SHA and the exact
      pre-registered flip set per affected run, and fails if anything outside the pre-registered set
      moves.
- [ ] For every **other** committed run, any outcome that changes is enumerated with its answer
      text, confirmed to be the hedge-then-deliver class (a true correction), and surfaced to the
      architect before commit; a run with no such cells has byte-identical `scores.jsonl`.
- [ ] A **genuine refusal** (leading decline cue, no delivered passage) is still classified
      `refused` — verified by unit cases drawn from the jointly-agreed refusal cells, not only by
      the flip set.
- [ ] The copyright audit gate (`audit.py`, `.codev/checks/test.sh`) still passes over the
      regenerated artifacts; no restricted-derived artifact is committed.
- [ ] `verify_source` refusal handling (`parse_yes_no` / `parsed is None` in `score._with_outcome`)
      is **unchanged** — this spec touches only the text-retrieval refusal path.

## Constraints

- **Refusal stays an OUTCOME, not a grader, and stays deterministic.** The headline outcome must
  remain cheap, reproducible, byte-stable, and free of any API call. The Jev judge's `refusal_p` is
  the **cross-check / oracle** that defines the pre-registered set — it must **not** become an input
  to `classify_refusal` at runtime.
- **Pre-registered set is fixed.** The adjudication of `classify_refusal` is tied to the exact 11
  cells enumerated in issue #48 and above; do not substitute a different or larger "representative"
  set for the tutorial-run flip set.
- **Sanctioned-rebaseline discipline (lessons-critical).** Never silently re-score committed
  evidence. A deliberate scoring-contract change rebaselines committed `scores.jsonl` once,
  panel/usage fed back verbatim, witnessed by a projection-SHA oracle + a pre-registered flip/refused
  set, with the moved numbers surfaced to the architect first. Re-score into the existing run dirs
  **only** under this discipline; otherwise write to a fresh `runs/<id>/`.
- **Parallel work on the scoring contract.** Builder aspir-52 (#52) is concurrently changing
  `normalize()`/orthography, which also rebaselines committed scores. Expect a rebase + oracle
  re-run if #52 merges first. Keep this adjudication tied to `outcomes.py` and the 11 cells so the
  two rebaselines remain separable.
- The change lives in the `pipelines/sacredbench` uv project; run via
  `uv --project pipelines run python -m sacredbench …`. Tests run through the per-builder dispatcher
  `.codev/checks/test.sh` (pipelines → uv pytest).
- Existing byte-for-byte re-score guards (`test_first_run_regression`, `test_tutorial_run`) must be
  reconciled with the moved numbers the same way Spec 15 did — the rebaseline is witnessed by the
  oracle test, not by those now-circular guards.

## Assumptions

- The 11 cells in `jev_agreement.json` are a faithful, stable enumeration of the false-positive
  class on `tutorial-2026-10-11` (they are committed run evidence, not regenerated here).
- `answers.jsonl` for each committed run is intact and keyless re-scoring reproduces the panel/usage
  verbatim (score does not call providers); the rebaseline only recomputes graders/outcomes.
- The hedge-then-deliver class is detectable deterministically from the answer text alone (see
  Solution Approaches); if it turns out it is not cleanly separable without the judge, that is a
  blocker to surface, not a reason to wire the judge into the outcome layer.
- Depends on no other in-flight branch; #52's rebaseline is a sequencing concern, not a code
  dependency.

## Solution Approaches

The classifier's two-half rule (leading cue AND reference-not-delivered) is sound; the gap is that
"reference not delivered" is approximated by `bounded_contains`, which a different *vocalization* of
the right passage defeats. The fix must sharpen "did the model actually decline to deliver?" without
consulting the paid judge.

### Approach 1 (recommended): Detect best-effort delivery past the hedge

Treat the leading hedge as a disclaimer, not a refusal, when the answer goes on to **deliver
substantial passage content** after it. The distinguishing marker across all 11 cells is that the
answer continues well beyond the hedge with quoted/original-script scripture content — this is the
same intuition the existing "leading window" already encodes (a cue that OPENS is a refusal; a cue
that TRAILS a delivered verse is a disclaimer), extended to the case where the delivery *follows*
the hedge rather than preceding it.

- **Pros:** keeps refusal deterministic and byte-stable; preserves genuine refusals (which have no
  substantial delivery past the hedge); directly models the real distinction the judge is making;
  narrowly scoped to the text-retrieval branch.
- **Cons:** needs a robust, script-aware "substantial delivery" signal that does not itself
  false-negative on genuine refusals that happen to quote the *citation* or a short fragment; the
  threshold must be pinned against both the 11 flip cells and the jointly-agreed refusals.
- **Risk/complexity:** medium. The exact delivery signal (length past hedge, presence of a quoted
  span, original-script character run) is a plan-level decision; the spec fixes only that the signal
  must flip all 11 and move none of the agreed refusals.

### Approach 2: Narrow the decline-cue list

Remove or qualify the hedge cues (`"i couldn't find"`, `"i couldn't get"`, `"i couldn't confirm"`,
`"i can't give you that"`) that fire on these answers.

- **Pros:** smallest diff; purely data-driven.
- **Cons:** throws away genuine refusals that use the same words with no delivery (over-corrects in
  the other direction — converts false `refused` into false `incorrect`/`correct`); the cue list is
  deliberately conservative, and these same cues legitimately open real declines on the non-search
  arms. Fragile and hard to witness cleanly.
- **Risk/complexity:** low effort, high correctness risk. **Not recommended** alone.

### Approach 3: Make refusal advisory from the judge

Let `refusal_p` override the deterministic label.

- **Pros:** matches the judge exactly.
- **Cons:** violates the core contract — makes the headline outcome depend on a paid, non-stable
  API pass; non-starter per Constraints.
- **Risk/complexity:** **Rejected.**

**Recommendation: Approach 1**, with Approach 2's cue audit used only as corroboration (confirming
which cues fire on the 11) — not as the mechanism.

## Open Questions

- **Critical** — Is the hedge-then-deliver class cleanly separable from genuine refusals by the
  answer text alone, across *all* committed runs (not just the 11)? If a run contains a borderline
  cell the rule moves that the judge would call a true refusal, that is a design signal to surface.
- **Important** — Which committed runs beyond `tutorial-2026-10-11` contain cells the new rule
  moves, and are all such moves confirmable as the same class? (Enumeration is plan work; the answer
  shapes the oracle's per-run flip sets.)
- **Important** — Sequencing with #52: do we rebase onto #52's rebaselined `scores.jsonl` if it
  merges first, re-pinning the oracle SHAs, or land first? (Architect's call; default is land
  independently and rebase if needed.)
- **Nice-to-know** — Should the 3 high-`matches_requested_p` cells (judge thinks the delivery
  matches) be annotated as equivalence candidates for #21/#32, or left purely as `incorrect` here?
  (Out of scope for the outcome fix; worth a note.)

## Test Scenarios

- **Flip set (happy path):** each of the 11 pre-registered answers, scored as `retrieve_quote`,
  yields `outcome == "incorrect"` (not `refused`).
- **Genuine refusal preserved:** answers drawn from the 116 jointly-agreed refusal cells (leading
  decline, no delivered passage) still yield `refused`.
- **Deliver-then-caveat preserved:** the existing case (verse delivered, caveat trailing) remains an
  answer, unchanged.
- **Edge — hedge then short non-delivery:** "I couldn't find it. You can check Sefaria." (hedge, a
  pointer, but no passage) stays `refused` — a pointer is not a delivery.
- **Edge — hedge then citation-only echo:** a hedge followed only by re-stating the citation (no
  passage text) stays `refused`.
- **Regression — whole-run outcome diff:** re-scoring each committed run moves outcomes on exactly
  its pre-registered/enumerated set and nothing else; `(exact, normalized, token_f1)` projection SHA
  unchanged per run.
- **Cross-check:** regenerating `jev_agreement.json` for `tutorial-2026-10-11` shows refusal
  `deterministic_only == 0`.
- **Audit:** `audit.py` passes over regenerated artifacts.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Delivery-detection over-corrects, flipping genuine refusals to answers | Medium | High | Pin the rule against both the 11 flips AND a sample of the 116 agreed refusals; oracle test fails if any agreed refusal moves |
| Other committed runs move cells that are not the target class | Medium | High | Enumerate every moved cell per run with its answer text; architect confirms each before commit; oracle pins per-run flip sets |
| Silent/accidental re-score corrupts committed panel/usage | Low | High | Sanctioned-rebaseline discipline: panel/usage fed back verbatim, projection-SHA oracle, moved numbers surfaced before commit |
| #52 merges first and re-pins the same committed scores | Medium | Medium | Keep change isolated to `outcomes.py` + the 11 cells; rebase and re-run oracle; re-capture pre-change SHAs from the merged baseline |
| Judge disagreements are themselves noisy on the borderline cells | Low | Medium | Use `refusal_p` only to *define* the pre-registered set (already committed evidence), never as a runtime input |

## References

- Issue #48 — Refusal-classifier false positives on web-search hedges (Jev cross-check, Spec 21 F1).
- Spec 15 — scoring contract: refusal as an outcome (`codev/specs/15-scoring-contract-contains-exac.md`).
- Spec 21 — Jev-based evaluator / refusal cross-check (`codev/specs/21-jev-based-evaluator-typed-judg.md`), PR #47.
- `runs/tutorial-2026-10-11/jev_agreement.json` — the 11 disagreements (pre-registered set).
- `pipelines/sacredbench/outcomes.py` — `classify_refusal`, `leading_decline`, `_DECLINE_CUES_RAW`.
- `pipelines/sacredbench/score.py` — `_with_outcome`, `bounded_contains`, `normalize`, `parse_yes_no`.
- `pipelines/tests/test_contains_reference_rebaseline.py` — the rebaseline-witness pattern to mirror.
- Related: #41 (independent-rater work), #52 (concurrent `normalize()`/orthography rebaseline), #32 (equivalence index).
