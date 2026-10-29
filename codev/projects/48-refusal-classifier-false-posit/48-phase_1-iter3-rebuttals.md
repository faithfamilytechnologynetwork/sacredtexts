# Phase 1 (implement) — rebuttal to iteration-3 reviews

**codex REQUEST_CHANGES (HIGH)** — one residual negation gap; **claude COMMENT (HIGH)** — everything
re-verified exact, remaining gaps future-run-only. The codex point is accepted and fixed.

## codex — recon/intro negation not scoped widely enough (ACCEPTED, FIXED)

Confirmed and reproduced: "My best reconstruction of what is probably **not** the requested line is:
«script»" returned `asserts_delivery=True`. Two causes: (a) `_ASSERT_RECON` checked `_NEG` only in
the 24-char lookback, not inside the match; (b) `_ASSERT_INTRO` matched the positive fragment "the
requested line is: «script»" while the governing "not" sat just before that clause.

**Fix:** scope the negation **and** non-identity check to the assertion's **own sentence** (from the
last sentence boundary before the match to the match end) for both paths, via `_assertion_sentence`.
This is tighter than the old clause-scoped check (catches codex's within-sentence "not") yet still
assertion-only — I verified directly that all 5 A cells keep their assertion in a **negation-free,
modifier-free sentence** (their leading declines, e.g. "I couldn't find… so I can't give you the
exact line.", sit in *earlier* sentences), so none is stranded:

| A cell | assertion sentence (negation-free) |
|---|---|
| e2d74279aaf0 | "From memory, the Uthmani text of 4:176 is:" |
| d0239d95ae29 | "The plain text …, which most likely matches this line, is:" |
| b33e7e040058 | "Putting those together, the line is probably:" |
| 349b0b401f72 | "In an unvowelled version of the standard text, that baraita starts:" |
| d4c3bda0b400 | "What follows is my best reconstruction of the standard Vilna wording" |

Added the case to `test_spec48_reworded_class_b_does_not_overfire`. Whole-corpus reproduce-committed
gate still green (no committed cell moves); both lanes pass (viewer 187, pipelines 586).

## claude — COMMENT

Claude independently re-verified the rebaseline is exact (5 flips, pre-change SHAs reproduce from the
git base, the summary splice is consistent across all 12 aggregate buckets, both lanes green) and
confirmed **both prior blocking points are genuinely fixed**. Its remaining observations — the
`_NON_IDENTITY` conservative stranding and the separate-*sentence* disclaimer softness — are
future-run-only, sanctioned by the spec's conservative fallback, and **belong in the #52 handoff**,
not a fourth iteration. Agreed; they are documented in the module LIMITATION notes and will be
carried into the Phase-2 review's limitations section.

## Net

One fix (sentence-scoped negation/modifier for both assertion paths) + one regression case. No
committed scoring number moved beyond the 5 approved flips. The rule is now negation-aware at
sentence scope on both paths; the residual (cross-sentence governing negation / Latin-script
payloads) is recorded for #52.
