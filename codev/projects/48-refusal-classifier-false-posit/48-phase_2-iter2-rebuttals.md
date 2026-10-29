# Phase 2 — impl-consult iteration 2 rebuttals

**claude: APPROVE (HIGH)** — independently re-verified the rebaseline exact (5 cells, outcome-only,
frozen SHAs reproduce from the merge base, three runs byte-identical, Jev 0.985/6, both lanes green),
confirmed iteration 1's REQUEST_CHANGES fully resolved, and confirmed the viewer `92 vs 93` dispute is
a true false positive. Non-blocking carry-forwards noted and accepted (see below). Nothing to address.

**codex: REQUEST_CHANGES (HIGH)** — two factual-precision issues that my iteration-1 doc-sync
introduced (the rebaseline itself was re-confirmed correct). Both accepted and fixed in commit
`206692f`.

---

## Issue 1 — README Talmud bullet overstated the moved count (ACCEPTED, fixed)

My iteration-1 wording said opus-search's Talmud cells were "8 correct retrievals *plus* 6
confident-but-wrong deliveries that the pre-fix rule had hidden as refusals" — implying all six
`incorrect` cells moved from `refused`. Only **four** moved. Pre-fix opus-search Judaism was
`8 correct / 2 incorrect / 24 refused`; post-fix it is `8 / 6 / 20`. The flip set is exactly the four
opus-search Talmud A-cells (`d4c3bda0b400`, `d0239d95ae29`, `b33e7e040058`, `349b0b401f72`); the other
two `incorrect` cells were already scored wrong before Spec 48.

**Changed:** reworded to "8 correct retrievals and 6 wrong deliveries, of which **Spec 48 newly
exposed 4** that the pre-fix rule had hidden as refusals (the other 2 were already scored `incorrect`
before the fix)." (The headline prose already said "four of the newly-answered Talmud cells" — correct
— so only this bullet needed the fix.)

## Issue 2 — lessons-learned framed the assertion escape as an alternative detection condition (ACCEPTED, fixed)

My edit read "Detection is deterministic (a leading decline cue AND the reference not delivered — or,
Spec 48, a positive delivery assertion past the decline)". The "or" wrongly reads the positive-delivery
assertion as a *third way to detect refusal*. It is the opposite: a cell with a leading decline and no
containment is `refused` **unless** a positive delivery assertion fires, in which case it is scored
(class A), not refused.

**Changed:** reworded to "Detection is deterministic: a leading decline cue AND the reference not
delivered — **unless** a positive delivery assertion fires past the decline (Spec 48 escape, so a
from-memory / best-reconstruction delivery is scored, not refused)."

---

## Non-blocking carry-forwards (claude, accepted — not phase_2 blockers)

1. **Review-doc enumeration** — `codev/reviews/48-*.md` does not exist yet; the per-run moved-cell
   enumeration (with answer text) and the moved-similarity means are a **review-phase** deliverable.
   The numbers are computed and banked in the builder thread; the review phase will write them out
   rather than inherit them as done. Agreed.
2. **`test.sh` `runs/|texts/` → both-lanes mapping** imposes the pnpm toolchain on a pipelines-only
   builder that touches `runs/`. Documented inline as accepted on this machine; worth confirming in
   other environments. No change this PR.

**Verification:** both lanes green after the fix — viewer 187 passed (19 files), pipelines 586 passed
/ 2 skipped. Only `README.md` and `lessons-learned.md` changed (doc prose only; no score/summary/
oracle artifact touched).
