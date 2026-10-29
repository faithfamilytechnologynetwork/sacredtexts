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


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — The committed rebaseline is sound, but the reconstruction assertion path still misclassifies reworded class-B substitutes as deliveries.
- claude: REQUEST_CHANGES — Rule and rebaseline are independently verified exact and the iteration-1 fix holds, but the regenerated tutorial evidence breaks two hard-pinned assertions in the viewer's committed-run test, which the runs/**→pipelines dispatcher mapping hides.

### Builder Response to Iteration 2
# Phase 1 (implement) — rebuttal to iteration-2 reviews

Both reviewers returned **REQUEST_CHANGES (HIGH)**; both independently re-verified the rebaseline is
exact (5 flips, correct/similarity SHAs unchanged, panel/usage/generated_at verbatim, three runs
byte-identical) and that the iteration-1 `_NON_IDENTITY` fix holds. Two new blocking points, both
accepted and fixed. No point rejected.

## codex — blocking: `_ASSERT_RECON` missed the non-identity guard (ACCEPTED, FIXED)

Confirmed: iteration-1 added `_NON_IDENTITY` to `_ASSERT_INTRO` only, so "My best reconstruction of a
**different**/closest line is: «script»" still returned `asserts_delivery=True`. **Fix:** the
reconstruction path now also rejects a match whose span contains a `_NON_IDENTITY` modifier (and
checks an in-span negation), mirroring the intro path. Extended
`test_spec48_reworded_class_b_does_not_overfire` with two reconstruction-path cases. All 5 A cells
still deliver (`d4c3bda0b400`'s "reconstruction of the standard Vilna wording" has no modifier); 6 B
+ 2 anchors still refused; pipelines suite 586 passed.

## claude — blocking: the rebaseline broke the viewer's committed-run test, hidden by the dispatcher (ACCEPTED, FIXED)

Confirmed and reproduced by actually running vitest (I installed `apps/viewer` deps, which Claude
could not). `apps/viewer/src/local/tutorialRun.test.ts` loads the **real committed**
`runs/tutorial-2026-10-11` and pinned haiku-search `refused=35`/`wrong=13`; the rebaseline moved
those to 34/14. **Fix:** re-pinned to 34/14 with a Spec-48 comment and refreshed the stale accuracy
prose (lines ~143, 181, 204/206). The accuracy-ordering assertions still held (0.925 > 0.788 > 0.712,
so the ranking and `rows[0]=1.0`/`rows[3]=0.7121` were unaffected) — only the two count assertions
and comments needed updating. **Verified: `pnpm -C apps/viewer test` → 19 files, 187 passed.**

Because my PR now also touches `apps/viewer`, `.codev/checks/test.sh` maps it to the viewer lane, so
the gate runs **both** lanes (viewer 187 + pipelines 586) — the break is no longer invisible for
this PR.

**Dispatcher gap (surfaced to the architect, not unilaterally changed).** The deeper issue Claude
names is real: `.codev/checks/test.sh` maps `runs/**` to the pipelines lane only, yet the viewer
vitest reads committed `runs/`, so a *runs-only* rebaseline (a future one, or #52's Arabic moves)
would skip vitest — the lessons-critical multi-app trap. I recommended mapping `runs/**`/`texts/**`
to both lanes (cost: pipeline builders need pnpm) and left the decision to the architect, since it is
shared infra affecting every builder's gate. It does not block this PR, which touches the viewer
directly.

## Non-blocking (both reviewers)

- **`_NON_IDENTITY` conservatism** ("the opening line of Psalm 1 is: …" stranded as refused) and the
  **separate-sentence softness** (a B disclaimer in a different sentence from the assertion still
  reads as A — intrinsic to the locked assertion-only form, as the A cell `d4c3bda0b400` itself
  disclaims its segment number in a separate clause): both **documented in the module** and flagged
  for #52, not re-litigated here.
- **`_SCRIPT` is a Hebrew/Arabic/Greek allowlist** (Latin/Devanagari/Han hedged deliveries stay
  refused): documented as a LIMITATION; adding a tradition would extend the range.
- **Moved similarity/containment means** (opus-search `token_f1` 0.9098→0.8758, `normalized`
  0.8684→0.825, `contains_reference` 0.9737→0.925; haiku-search likewise) **surfaced to the
  architect** and will go in the Phase-2 review enumeration beside accuracy/coverage/refused.

## Net

Two code fixes (recon non-identity guard; viewer test re-pin) + regression-test extensions + doc
notes. Both lanes green (viewer 187, pipelines 586). No committed scoring number moved beyond the 5
approved flips (the viewer re-pin only tracks numbers the rebaseline already moved).


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
