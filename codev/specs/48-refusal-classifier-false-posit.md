# Specification: Refusal-classifier false positives on web-search hedges

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/48-*.md.
-->

## Problem Statement

The deterministic refusal classifier (`outcomes.classify_refusal`, Spec 15) **over-calls
`refused`** on a class of web-search answers that open with a hedge about not finding the *exact*
edition ("I couldn't find the exact William Davidson Edition text of …") and then emit scripture
text. Some of these answers are genuine best-effort **deliveries** of the requested passage (often
in a vocalization/orthography the deterministic containment grader cannot fold); the model
presents the text *as its answer*. The classifier labels them `refused` purely because the leading
hedge fires a decline cue and the differently-vocalized delivery defeats `bounded_contains`. These
are the false positives.

This matters because `refused` is not a neutral label. A `refused` cell is **excluded from the
accuracy denominator** (`accuracy = correct/(correct+incorrect)`) and **counted in coverage**
(`coverage = (correct+incorrect)/n`). A *false* `refused` therefore silently biases both headline
numbers the FAccT paper cites — it inflates accuracy (by dropping a genuine attempt that was in
fact a miss) and understates coverage. The bias concentrates on the `*-search` arms (web search is
what lets the model hedge about "the exact edition" and then paste a retrieved span), so it
distorts the search-on-vs-off comparison the benchmark exists to make. It is **not** exclusive to
them — `first-run-2026-10-11` carries non-search refusals driven by the same cue family, so the
rebaseline must inspect every committed run, not only the search arms (see Current State / Desired
State).

**The hard part is that not every hedged answer is a delivery.** A second class — the model offers
a *different or unidentified* line plus a "you can see it at …" pointer, explicitly stating the
text is **not** the requested passage — is a genuine decline (an offered substitute is not an
answer to "retrieve passage X"). Distinguishing **delivered-as-answer** from
**declined-with-substitute** is the actual design problem, because the two look nearly identical on
the surface and the Jev judge itself straddles the boundary (see Current State).

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
the deterministic outcome is `refused` but the judge's `refusal_p` is below the 0.5 threshold**
(`deterministic_only = 11`, `judge_only = 0`): these are the only refusal disagreements on the run,
and every one is a `retrieve_quote` cell on a `*-search` arm. The 11 (model_id, question_id) pairs,
with a provisional reading of which class each belongs to (confirmed against full answer text):

| model_id | question_id | refusal_p | matches_req_p | provisional class |
|---|---|---|---|---|
| opus-search | retrieve_quote-e2d74279aaf0 (haiku-search) | 0.03 | 0.87 | delivered (from memory) |
| opus-search | retrieve_quote-d4c3bda0b400 | 0.04 | 0.27 | delivered (best reconstruction) |
| opus-search | retrieve_quote-d0239d95ae29 | 0.09 | 0.93 | delivered (best guess, marks) |
| opus-search | retrieve_quote-b33e7e040058 | 0.11 | 0.28 | delivered (two-source reconstruction) |
| opus-search | retrieve_quote-349b0b401f72 | 0.16 | 0.63 | delivered / adjacent segment |
| opus-search | retrieve_quote-f0ffc67a458e | 0.36 | 0.04 | substitute (unsure segment) |
| opus-search | retrieve_quote-4c6f201c7192 | 0.45 | 0.09 | substitute / no delivery |
| opus-search | retrieve_quote-de9d77a6c963 | 0.45 | 0.04 | substitute (different line + pointer) |
| opus-search | retrieve_quote-b1a04c81d33f | 0.46 | 0.08 | substitute / pointer only |
| opus-search | retrieve_quote-fe52da70f661 | 0.47 | 0.45 | substitute (different line) |
| opus-search | retrieve_quote-eaf381cf82d3 | 0.49 | 0.33 | substitute / no delivery |

(The haiku-search row is `e2d74279aaf0`; the other 10 are opus-search.)

**The 11 are not a clean, uniform set — reading them as one is the spec's central correction.** Two
facts, both verified directly against the run data, reshape the problem:

1. **Six of the eleven are 0.5-threshold artifacts, not judge convictions** (`refusal_p` 0.36, 0.45,
   0.45, 0.46, 0.47, 0.49 — a hair under the recorded `threshold = 0.5`). Only five are confident
   non-refusals (`refusal_p ≤ 0.16`). Treating a 0.49 as "the judge says not-refused" with the same
   weight as a 0.03 reads noise as signal.
2. **A structurally identical cell sits on the *other* side of the threshold.** The *agreed*
   refusal `opus-search/retrieve_quote-42f510ea6c7d` (`refusal_p = 0.58`, **not** in the set) is the
   same template as flip-set members `de9d77a6c963` (0.45) and `fe52da70f661` (0.47): "I couldn't
   find X; what I found / the closest was a *different* line «original-script span»; I can't say
   it's the requested segment; see it at <url>." Length cannot separate them (`42f510ea6c7d` is 484
   chars, `de9d77a6c963` 445), nor can "original-script run" or "quoted span." A principled
   deterministic rule **must classify these three the same way**; a rule that flips the two 0.45/0.47
   cells but leaves the 0.58 cell `refused` is hand-fitted to the oracle — exactly what the
   witnessed-rebaseline discipline exists to forbid.

The honest split is therefore **by what the model does with the text, not by `refusal_p`**:
**delivered-as-answer** (five confident cells: text offered as the model's answer — "from memory X
is:", "my best reconstruction", "best guess") vs **declined-with-substitute** (the six borderline
cells plus the 0.58 agreed refusal: a different/unidentified line + pointer, explicitly flagged as
not the requested passage). This split correlates with `refusal_p` (delivered ⇒ low; substitute ⇒
near 0.5) but is defined independently of it, so it treats the 0.58 twin consistently.

The committed run evidence carries the baseline — on `tutorial-2026-10-11`,
`opus-search/retrieve_quote` reports accuracy 0.9737 / coverage 0.76 / refused 24 (correct 74,
incorrect 2, n 100), and `haiku-search/retrieve_quote` reports accuracy 0.80 / coverage 0.65 /
refused 35 (correct 52, incorrect 13, n 100). A prior **human** pre-registration already surveyed
these refusals: `test_contains_reference_rebaseline.py` pins `REFUSED_COUNTS` (opus-search 24,
haiku-search 35), `REFUSED_SET_SHA256`, `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`, and
`test_first_run_overall_and_lds_tradition_pinned`. This spec overturns part of that human survey on
the strength of the Jev cross-check and must re-pin those constants, not ignore them.

## Desired State

`classify_refusal` separates text-retrieval answers by a single **assertion** test — *did the
model purport to answer?*:

- **A — delivered-as-answer:** the model presents scripture text **as its answer**, however hedged
  about the edition ("I couldn't find the exact edition, but from memory it is: …", "my best
  reconstruction", "my best guess"). This is an answer with a disclaimer → scored on its merits
  (`correct`/`incorrect` by the selected graders), **not** `refused`.
- **B — declined-with-substitute (or no delivery):** the model explicitly disclaims delivering the
  requested passage — offering a *different/unidentified* line, a pointer, or nothing ("the closest
  I got was a different line…", "I can't say it's segment X", "you can see it at <url>"). This is a
  decline → stays `refused`, exactly as today.

**Why B stays refused (architect decision 2026-10-29, endorsing the builder default).** The outcome
taxonomy asks "did the model purport to answer?" A model that explicitly disclaims delivering the
requested passage has declined. Scoring it `incorrect` would punish honest calibration and make
confident confabulation strictly dominant — the opposite of what the benchmark should reward.
Coverage already prices the decline, by design (Spec 15). The discriminator is **assertion**, not
surface form, which is what lets the identical-looking 0.58 agreed refusal and its 0.45 twin be
classified the same way (both B). This mirrors `verify_source`'s leading-stance philosophy (what
the model *commits to* decides the outcome).

Concretely, after the change, on `tutorial-2026-10-11`:

- The **delivered-as-answer** cells (the five confident cells, `refusal_p ≤ 0.16`, pending the
  plan's per-cell adjudication) flip `refused → incorrect` — their `correct` bit is already 0 (the
  delivered text is a non-matching vocalization under the default graders; the judge/equivalence
  flip is Spec 21/#32 diagnostic territory, out of scope here).
- The **declined-with-substitute** cells (the six borderline cells) stay `refused`, together with
  the structurally identical agreed refusal `42f510ea6c7d` — so the rule introduces **no new
  judge-vs-deterministic disagreement**.
- Accuracy drops and coverage rises on the search arms by exactly the amount those flipped misses
  re-enter the denominator. Pinned expectations (verified against the committed scores): if the five
  confident cells flip (4 opus-search + 1 haiku-search), `opus-search/retrieve_quote` moves
  accuracy 0.9737 → **0.9250** / coverage 0.76 → **0.80** / refused 24 → **20**, and
  `haiku-search/retrieve_quote` moves accuracy 0.80 → **0.7879** / coverage 0.65 → **0.66** /
  refused 35 → **34**. (For reference, the withdrawn flip-all-11 would have moved opus-search to
  0.8605/0.86/14 — a far larger, unjustified paper move.)
- **No cell outside the plan-locked flip set moves** on this run, and the
  `(exact, normalized, token_f1)` similarity projection is byte-identical (those fields untouched).

Because the classifier is global, the same corrected rule is re-applied to **every committed run**
(`tutorial-2026-10-11`, `first-run-2026-10-11`, `original-2026-10-21`, `exp-arabic-prompts-2026-10-29`),
regenerating their `scores.jsonl` as a **sanctioned, oracle-witnessed rebaseline** (not a forbidden
re-score). Only `tutorial-2026-10-11` has a Jev oracle; for the other three, every outcome that
moves is enumerated with its answer text and adjudicated by the builder against the same A/B
assertion rule, then surfaced to the architect before the moved numbers are committed. A run with
no A-class cells gets a byte-identical `scores.jsonl`.

**The Jev rubric is not changed in this PR.** The paper-facing refusal definition lives in
`outcomes.py`; the rubric's criterion ("supplies a quotation… whether or not it is the one
requested" ⇒ not-refusal) is deliberately *looser* than the assertion rule and this spec knowingly
diverges from it. The rubric is #47's recorded grader identity and must stay byte-stable here; a
future rubric revision (`sacredbench-jev-2`) is the place to re-align it.

## Success Criteria

The flip set is the **delivered-as-answer (A) subset** of the 11, locked per-cell at plan phase
(the five confident cells are the presumptive members). The criteria below are stated so a
principled assertion rule satisfies them *without* hand-fitting to the Jev oracle.

- [ ] Every cell the plan classifies **A (delivered-as-answer)** has `outcome == "incorrect"` (was
      `refused`) after re-scoring; its `correct` bit stays 0.
- [ ] Every cell classified **B (declined-with-substitute)** stays `refused`, **and** the
      structurally identical agreed refusal `opus-search/retrieve_quote-42f510ea6c7d` (refusal_p
      0.58) is classified **the same way as its 0.45/0.47 twins** (`de9d77a6c963`, `fe52da70f661`) —
      a direct anti-overfit check: the rule may not treat textually indistinguishable cells
      differently.
- [ ] **No confident disagreement survives:** no deterministically-`refused` cell on
      `tutorial-2026-10-11` has `refusal_p < 0.25` after the change. Every remaining
      judge/deterministic refusal disagreement lies in the judge's uncertain band
      `[0.25, 0.75]`. (This replaces the unsatisfiable "`agreement_rate == 1.0`".)
- [ ] **Nothing outside the plan-locked flip set moves** on `tutorial-2026-10-11`; the per-run
      `(model_id, question_id) → (exact, normalized, token_f1)` projection SHA is unchanged
      (`contains_reference` and the similarity tiers do not move).
- [ ] The rebaseline is **witnessed**: an oracle test (sibling of
      `test_contains_reference_rebaseline.py`) pins the pre-change projection SHA and the exact
      flip set per affected run, and fails if anything outside it moves.
- [ ] Spec 15's existing pre-registration constants are **re-pinned, not left broken**:
      `REFUSED_COUNTS`, `REFUSED_SET_SHA256`, `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`, and
      `test_first_run_overall_and_lds_tradition_pinned` reflect the post-change outcomes, with the
      moved values surfaced to the architect before commit.
- [ ] For every **other** committed run (`first-run-2026-10-11`, `original-2026-10-21`,
      `exp-arabic-prompts-2026-10-29`), each outcome that changes is enumerated with its answer text,
      adjudicated A under the assertion rule, and surfaced before commit; a run with no A-class cells
      has byte-identical `scores.jsonl`.
- [ ] A **genuine refusal** (explicit disclaimer / no delivered answer) is still `refused` —
      verified by unit cases drawn from the jointly-agreed refusal cells **and** from the B subset,
      not only by the flip set.
- [ ] The copyright audit gate (`audit.py`, `.codev/checks/test.sh`) still passes over the
      regenerated artifacts; no restricted-derived artifact is committed.
- [ ] `verify_source` refusal handling (`parse_yes_no` / `parsed is None` in `score._with_outcome`)
      is **unchanged**, and the **Jev rubric is byte-unchanged** — this spec touches only the
      text-retrieval path in `outcomes.py`.

## Constraints

- **Refusal stays an OUTCOME, not a grader, and stays deterministic.** The headline outcome must
  remain cheap, reproducible, byte-stable, and free of any API call. The Jev judge's `refusal_p` is
  the **cross-check / oracle** that defines the pre-registered set — it must **not** become an input
  to `classify_refusal` at runtime.
- **Pre-registered set is the adjudication target, not an all-flip mandate.** The 11 cells
  enumerated in #48 are the fixed set the rule is *adjudicated against*; the issue's original
  "flip all 11" framing is **withdrawn as unsatisfiable** (architect, 2026-10-29) given the
  `42f510ea6c7d` counterexample. Do not substitute a different or larger set; the A/B split within
  these 11 (plus the 0.58 twin as a consistency check) is the adjudication.
- **A/B by assertion (architect decision, 2026-10-29).** A = model purports to answer (text offered
  as its answer, however hedged) → scored; B = model explicitly disclaims the requested passage →
  `refused`. B stays refused because the taxonomy asks "did the model purport to answer?", scoring
  honest declines as `incorrect` would reward confident confabulation, and coverage already prices
  the decline (Spec 15). Do not re-litigate this in plan/implement.
- **Sanctioned-rebaseline discipline (lessons-critical).** Never silently re-score committed
  evidence. A deliberate scoring-contract change rebaselines committed `scores.jsonl` once,
  panel/usage fed back verbatim, witnessed by a projection-SHA oracle + a pre-registered flip/refused
  set, with the moved numbers surfaced to the architect first. Re-score into the existing run dirs
  **only** under this discipline; otherwise write to a fresh `runs/<id>/`.
- **Jev rubric unchanged.** The rubric is #47's recorded grader identity and must be byte-stable in
  this PR. The assertion rule in `outcomes.py` deliberately diverges from the rubric's looser
  refusal criterion; re-aligning the rubric is deferred to a future `sacredbench-jev-2` revision.
- **Parallel work on the scoring contract.** Builder aspir-52 (#52) is concurrently changing
  `normalize()`/orthography, which also rebaselines committed scores. Expect a rebase + oracle
  re-run if #52 merges first (re-capture the pre-change projection SHAs from the merged baseline).
  Keep this adjudication tied to `outcomes.py` and the 11 cells so the two rebaselines remain
  separable.
- The change lives in the `pipelines/sacredbench` uv project; run via
  `uv --project pipelines run python -m sacredbench …`. Tests run through the per-builder dispatcher
  `.codev/checks/test.sh` (pipelines → uv pytest).
- Existing byte-for-byte re-score guards (`test_first_run_regression`, `test_tutorial_run`) must be
  reconciled with the moved numbers the same way Spec 15 did — the rebaseline is witnessed by the
  oracle test, not by those now-circular guards.

## Assumptions

- The 11 cells in `jev_agreement.json` are committed run evidence (not regenerated here); the Jev
  `refusal_p` values are used only to *motivate* the A/B split and define the anti-overfit
  consistency check, never as a runtime input.
- `answers.jsonl` for each committed run is intact and keyless re-scoring reproduces the panel/usage
  verbatim (score does not call providers); the rebaseline only recomputes graders/outcomes.
- The **assertion** signal (does the model present the text as its answer vs explicitly disclaim it?)
  is detectable deterministically from the answer text. This is the load-bearing assumption; if the
  A/B line cannot be drawn by text alone without either flipping a B cell or stranding an A cell, the
  safe fallback is to **leave the cell `refused`** (do not flip what cannot be cleanly distinguished
  from an agreed refusal) and surface it — never wire the judge into the outcome layer.
- Depends on no other in-flight branch; #52's rebaseline is a sequencing concern, not a code
  dependency.

## Solution Approaches

The classifier's two-half rule (leading cue AND reference-not-delivered) is sound; the gap is that
"reference not delivered" is approximated by `bounded_contains`, which a differently-vocalized but
genuine delivery defeats. The fix must sharpen "did the model purport to answer?" — the A/B
assertion test — without consulting the paid judge. The exact signal is a **plan-level** decision;
the approaches below scope the design space.

### Approach 1 (recommended): Assertion signal — does the model present the text as its answer?

Add a third test to the text-retrieval branch: a leading-decline cell is **not** `refused` when the
answer contains an **assertion of delivery** — a marker that the following text IS the model's
answer ("from memory it is:", "my best reconstruction/guess", "the text is:" introducing a span) —
and **stays** `refused` when it contains an explicit **disclaimer of the requested passage** ("a
*different* line", "I can't say it's segment X", "you can see it at <url>", "I'd rather not guess").

- **Pros:** keeps refusal deterministic and byte-stable; models the actual taxonomy question;
  classifies the identical `42f510ea6c7d` (0.58, B) and `de9d77a6c963`/`fe52da70f661` (0.45/0.47, B)
  *the same way*, so it does not overfit the oracle; narrowly scoped to the text-retrieval branch.
- **Cons:** assertion vs disclaimer is a linguistic signal, not a byte test — it needs a curated,
  conservative marker set (like `_DECLINE_CUES_RAW`), pinned against the five A cells, the six B
  cells, and the 0.58 twin. A genuine delivery with no explicit "here is my answer" framing could be
  stranded (fallback: stays `refused`, surfaced).
- **Risk/complexity:** medium. **This is the recommended direction**; the precise marker set and the
  assertion-vs-disclaimer boundary are locked per-cell at plan phase.

**Rejected sub-idea — "substantial delivery past the hedge" (length / original-script run / quoted
span).** The spec's first draft proposed this; the spec consult falsified it directly: the B-class
agreed refusal `42f510ea6c7d` (484 chars, original-script span, pointer) is *longer* than the
A-adjacent flip cell `de9d77a6c963` (445 chars), so no length/script/quote-presence threshold
separates a substitute from a delivery. Delivery *volume* is not the signal; delivery *assertion*
is.

### Approach 2: Narrow the decline-cue list

Remove or qualify the hedge cues (`"i couldn't find"`, `"i couldn't get"`, `"i couldn't confirm"`,
`"i can't give you that"`) that fire on these answers.

- **Pros:** smallest diff; purely data-driven.
- **Cons:** throws away genuine refusals that use the same words with no delivery (over-corrects the
  other way); the cues legitimately open real declines on the non-search arms. Cannot express the
  A/B distinction at all — the same cue opens both an A and a B answer. Fragile and hard to witness.
- **Risk/complexity:** low effort, high correctness risk. **Not recommended** alone.

### Approach 3: Make refusal advisory from the judge

Let `refusal_p` override the deterministic label.

- **Pros:** matches the judge exactly.
- **Cons:** violates the core contract — makes the headline outcome depend on a paid, non-stable
  API pass; and the judge itself is a coin-flip on six of these cells (0.36–0.49) and inconsistent
  across the identical `42f510ea6c7d`/`de9d77a6c963` pair, so it is not even a reliable oracle here.
  Non-starter per Constraints.
- **Risk/complexity:** **Rejected.**

**Recommendation: Approach 1** (assertion signal), with Approach 2's cue audit used only as
corroboration (confirming which cues fire on the 11), not as the mechanism.

## Open Questions

- **Critical** — Can the assertion signal (A vs B) be drawn by text alone across *all* committed
  runs without flipping a B cell or stranding an A cell? The `42f510ea6c7d` consistency check is the
  acid test on the tutorial run; the three oracle-less runs rest on builder adjudication. If a cell
  cannot be cleanly placed, it stays `refused` and is surfaced (fallback is settled; the open part
  is how many such cells exist).
- **Important** — Per-cell A/B disposition of the six borderline cells — RESOLVED in principle
  (assertion rule; all six read as B on current evidence), **locked per-cell at plan phase** with
  full answer text. Already settled: the five confident cells are A, the 0.58 twin is B.
- **Important** — Which committed runs beyond `tutorial-2026-10-11` contain A-class cells the rule
  moves? (Enumeration is plan work; shapes the oracle's per-run flip sets. `first-run` has non-search
  refusals from the same cue family — must be inspected, not assumed inert.)
- **Important** — Sequencing with #52: rebase onto #52's rebaselined `scores.jsonl` if it merges
  first (re-pinning the oracle SHAs), or land first? Architect's default: land independently and
  rebase if needed.
- **Nice-to-know** — Should the high-`matches_requested_p` A cells (e.g. `d0239d95ae29` 0.93,
  `e2d74279aaf0` 0.87 — judge thinks the delivery matches) be annotated as equivalence candidates
  for #21/#32, or left purely as `incorrect` here? (Out of scope for the outcome fix; worth a note.)

## Test Scenarios

- **A flips (happy path):** each A-class cell (delivered-as-answer — e.g. `e2d74279aaf0` "from
  memory it is:", `d4c3bda0b400` "best reconstruction", `d0239d95ae29` "best guess") scored as
  `retrieve_quote` yields `outcome == "incorrect"` (not `refused`).
- **B stays refused:** each B-class cell (declined-with-substitute — e.g. `de9d77a6c963`,
  `fe52da70f661`, `b1a04c81d33f`) still yields `refused`.
- **Anti-overfit consistency:** `42f510ea6c7d` (the 0.58 agreed refusal) yields the **same** outcome
  as `de9d77a6c963` and `fe52da70f661` — all `refused`. A rule that splits them fails this test.
- **Genuine refusal preserved:** answers drawn from the 116 jointly-agreed refusal cells still yield
  `refused`.
- **Deliver-then-caveat preserved:** the existing case (verse delivered, caveat trailing) remains an
  answer, unchanged.
- **Edge — hedge then pointer only:** "I couldn't find it. You can check Sefaria." stays `refused` —
  a pointer is not an assertion of delivery.
- **Edge — hedge then citation-only echo:** a hedge followed only by re-stating the citation (no
  passage text) stays `refused`.
- **Regression — whole-run outcome diff:** re-scoring each committed run moves outcomes on exactly
  its plan-locked A set and nothing else; `(exact, normalized, token_f1)` projection SHA unchanged
  per run.
- **Cross-check:** regenerating `jev_agreement.json` for `tutorial-2026-10-11` shows **no surviving
  refusal disagreement with `refusal_p < 0.25`** (not `deterministic_only == 0`, which would require
  overfitting).
- **Re-pin:** `test_contains_reference_rebaseline.py`'s `REFUSED_COUNTS`, `REFUSED_SET_SHA256`,
  `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`, and `test_first_run_overall_and_lds_tradition_pinned` pass
  against the regenerated scores.
- **Audit:** `audit.py` passes over regenerated artifacts.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Jev `refusal_p` is itself noise on the borderline cells (6 of 11 at 0.36–0.49; inconsistent across the identical `42f510ea6c7d`/`de9d77a6c963` pair) | **High** | High | Do **not** treat `refusal_p` as ground truth or a flip target; classify by the assertion rule and enforce the `42f510ea6c7d` consistency test; `refusal_p` only motivates and bounds, never decides |
| Assertion rule over-corrects, flipping a B (declined) cell to an answer | Medium | High | Pin against the five A cells, the six B cells, AND the 0.58 twin; oracle fails if any B cell or the twin moves; fallback = leave `refused` when the A/B line is unclear |
| Other committed runs move cells that are not A-class (esp. `first-run` non-search refusals) | Medium | High | Inspect every run; enumerate every moved cell with answer text; adjudicate A under the assertion rule; architect confirms before commit; oracle pins per-run flip sets |
| Silent/accidental re-score corrupts committed panel/usage | Low | High | Sanctioned-rebaseline discipline: panel/usage fed back verbatim, projection-SHA oracle, moved numbers surfaced before commit |
| Spec 15's existing hand-surveyed pre-registration left broken | Medium | Medium | Re-pin `REFUSED_COUNTS`/`REFUSED_SET_SHA256`/`EXPECTED_*`/`test_first_run_*` to post-change values; surface the moved numbers |
| #52 merges first and re-pins the same committed scores | Medium | Medium | Keep change isolated to `outcomes.py` + these cells; rebase and re-run oracle; re-capture pre-change SHAs from the merged baseline |

## References

- Issue #48 — Refusal-classifier false positives on web-search hedges (Jev cross-check, Spec 21 F1).
- Spec 15 — scoring contract: refusal as an outcome (`codev/specs/15-scoring-contract-contains-exac.md`).
- Spec 21 — Jev-based evaluator / refusal cross-check (`codev/specs/21-jev-based-evaluator-typed-judg.md`), PR #47.
- `runs/tutorial-2026-10-11/jev_agreement.json` — the 11 refusal disagreements (adjudication set);
  `judgments.jsonl` holds `42f510ea6c7d` (0.58) and `f143cc3f6c63` (0.68), the agreed-refusal
  consistency anchors.
- `pipelines/sacredbench/outcomes.py` — `classify_refusal`, `leading_decline`, `_DECLINE_CUES_RAW`.
- `pipelines/sacredbench/score.py` — `_with_outcome`, `bounded_contains`, `normalize`, `parse_yes_no`.
- `pipelines/tests/test_contains_reference_rebaseline.py` — the rebaseline-witness pattern to mirror.
- Related: #41 (independent-rater work), #52 (concurrent `normalize()`/orthography rebaseline), #32 (equivalence index).
