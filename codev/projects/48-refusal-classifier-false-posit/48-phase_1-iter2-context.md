### Iteration 1 Reviews
- codex: APPROVE — Phase 1 correctly implements the assertion-based refusal rule, preserves B-class refusals, and witnesses exactly the five approved tutorial flips without broader outcome drift.
- claude: REQUEST_CHANGES — Rebaseline is independently verified exact and the A/B adjudication is sound, but the assertion regex excludes the canonical class-B "closest/different line" pattern only by accident of the indefinite article — a trivial rewording scores a decline as `incorrect`.

### Builder Response to Iteration 1
# Phase 1 (implement) — rebuttal to iteration-1 reviews

Verdicts on the current code: **codex APPROVE (HIGH)**, **claude REQUEST_CHANGES (HIGH)**. Both
independently re-verified the rebaseline (5 cells, correct/similarity SHAs unchanged, panel/usage
verbatim, three runs byte-identical, 585→586 passing). Claude's one blocking point is accepted and
fixed; non-blocking notes addressed or acknowledged. No point rejected.

## claude — blocking: `_ASSERT_INTRO` over-fires on reworded class-B shapes (ACCEPTED, FIXED)

Confirmed and reproduced: `"The closest line I found is: «script», but I can't confirm it's that
segment"` and `"The opening text of the daf is: «script»"` both returned `asserts_delivery=True`.
The B exclusion had been leaning on (a) the indefinite article in the real cell `de9d77a6c963` ("**a**
different line") and (b) the `daf`/`begins` keyword lists — both defeated by a one-word rewording,
and the post-payload negation sits outside the matched clause. Unmitigated for future runs, and #52
builds on this function.

**Fix** (`outcomes.py`): added `_NON_IDENTITY` — a non-identity modifier
(`different|closest|other|another|next|previous|preceding|following|surrounding|nearby|adjacent|
opening|opens|begins|neighbouring`) inside the assertion clause now disqualifies it. This
generalizes the authors' own `daf`/`segment` (dropped from `_UNIT`) and `begins`/`opens` (dropped
from `_VERB`) exclusions into one principled rule. Verified exactly as the reviewer predicted:

- all 5 A cells still read as deliveries; all 6 B + 2 anchors still `refused`;
- whole-corpus reproduce-committed gate across all 5 (run, scores) pairs stays green — **no
  committed number moves, no re-rebaseline**;
- both probe shapes (and a third, "the preceding passage reads: «script»") now `refused`, pinned in
  a new `test_spec48_reworded_class_b_does_not_overfire`.

## claude — non-blocking

1. **`_SCRIPT` is a Hebrew/Arabic/Greek allowlist** → a hedged **Latin**-script (or Devanagari/Han)
   delivery is never a payload, so the original false-`refused` survives on that axis, and a new
   tradition would need `_SCRIPT` extended (brushes arch-critical's "adding a tradition never
   changes core pipeline code"). **Documented** as a LIMITATION in the module and noted for the
   review; not expanded here (out of scope — the committed corpora are Hebrew/Arabic/Greek/Latin and
   the Latin cells in evidence don't exhibit the hedge-then-deliver shape).
2. **`_SCRIPT` admits harakat/digits, contradicting "letter ranges only"** — comment corrected;
   harmless because a positive assertion frame is still required.
3. **A-cell test passed `{"text": ""}`** — now loads the real `expected` text, so the test exercises
   the assertion escape against genuine (non-containing) orthography variants.
4. **Lint** — `EXP` shadowing removed in the edge test; the private `_TEXT_RETRIEVAL` import is kept
   deliberately (the test must iterate exactly the classifier's text-retrieval task set, and
   importing the single source of truth is better than duplicating the tuple).

## codex — APPROVE

No blocking issues. Codex confirmed the rule preserves B-class refusals and witnesses exactly the
five approved flips without broader drift — consistent with the strengthened reproduce-committed
gate added in the prior iteration (its earlier REQUEST_CHANGES points: gate strength, edge-test end
behavior, and phase-boundary reconciliation, all folded before this consult).

## Net

One code change (`_NON_IDENTITY` guard) + one new regression test + doc/comment/test polish. The
fix hardens the rule for every future run and for #52 while moving nothing in the committed
evidence. Suite: **586 passed, 2 skipped**.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
