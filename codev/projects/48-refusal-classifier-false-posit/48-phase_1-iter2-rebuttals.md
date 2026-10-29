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
