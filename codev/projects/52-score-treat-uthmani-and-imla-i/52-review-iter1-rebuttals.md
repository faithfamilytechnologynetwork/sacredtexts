# Review phase — PR consult iter-1 rebuttals

**claude: APPROVE (HIGH)** — independently re-verified every quantitative claim (58 cells all
`incorrect→correct`; SIM projection SHAs frozen *non-circularly* against the pre-#52 base `b93e881`;
`facct`/`jev_agreement` recompute byte-identically; no ReDoS; branch up to date with #57/#58/#61).
Four non-blocking items, all folded below.

**codex: REQUEST_CHANGES (HIGH)** — one substantive item (direction-independence for a *mixed
daggerless Imla'i reference*) plus one stale docstring. The substantive item is a **known,
documented, architect-endorsed boundary** (raised by codex's own Phase-2 consult, narrowed in the
review's "Directionality boundary" appendix and the `fold_aware_contains` docstring); I **rebut** that
it is a regression and **address** it by narrowing the public claims and pinning the boundary with a
test.

## codex blocking: "direction independence fails for mixed Imla'i references" — REBUTTED + claims narrowed

codex is factually right that `fold_aware_contains("هَٰذَا ٱلْكِتَٰبَ", "هذا الكتاب") == False` (I
reproduced it). But this is the **intended, documented boundary**, not a defect:

- The per-position optionality (`ا?`) is carried by the **reference's** daggers. A reference written
  in *mixed* Imla'i — defective `هذا` (no long-ā alef) **and** plene `الكتاب` (written alef) in one
  string, with **no daggers** to mark which positions are optional — cannot be reproduced by the two
  *global* answer forms (default dagger-deleted / plene dagger→alef): neither form yields a per-word
  mix. This is exactly the limitation already stated in the `fold_aware_contains` docstring
  (`score.py`) and the review's "Directionality boundary" appendix, and it was the subject of the
  **codex Phase-2 consult** — the architect endorsed the containment-only design with this boundary
  (2026-10-29).
- It is **conservative**: it only ever *withholds* credit, never grants a wrong one (strict superset
  preserved). It arises on **0 committed cells** — every committed reference is the corpus
  orthography (Uthmani QUL, carrying the daggers), and #39's Arabic subset scores against that same
  daggered corpus, so the reverse direction that matters (Imla'i answer vs Uthmani reference) is
  fully covered (verified: `fold_aware_contains("قال هذا الكتاب لقومه", "هَٰذَا ٱلْكِتَٰبَ") == True`).
- Implementing the daggerless-mixed case would require inferring each word's plene/defective class
  with **no orthographic signal** to go on — that is the open #39/#60 problem, not a scoring-wiring
  fix, and widening it blindly risks new collisions.

**Addressed (claims narrowed so they no longer overstate):**
1. **Spec success criterion #1** reworded: credited-as-equivalent in both directions *whenever the
   reference is in the corpus orthography*, with the mixed-daggerless-reference case called out as the
   accepted documented boundary (0 committed cells).
2. **PR body** "direction-independent" softened to the same, with a new *Known limitations* bullet.
3. **New test** `test_mixed_daggerless_imlai_reference_is_the_documented_boundary` pins
   `not fold_aware_contains("هَٰذَا ٱلْكِتَٰبَ", "هذا الكتاب")` alongside the two cases that DO hold
   (daggered reference, pure-plene daggerless reference) — codex's requested coverage, turned into a
   regression guard for the boundary.

## codex minor: stale "not yet wired" docstring in `test_arabic_orthography_fold.py:7-9` — ADDRESSED
Updated: the module docstring now states the fold IS wired into the default scoring path as of
Phase 2 (the 5 call-sites), with `normalize()`/equality submetrics still byte-stable.

## claude minor 1: `outcomes.py:47` docstring still names `bounded_contains` — ADDRESSED
Fixed to `fold_aware_contains` (the actual lazy import at `outcomes.py:341`), with a sentence noting
`classify_refusal` credits a delivered Imla'i variant via the same strict-superset containment.

## claude minor 2: `_single_citation_correct` inherits the verse-length fold — REBUTTED (no-op today; guarded for #39)
Verified a genuine no-op (0 Arabic-script citations across all committed evidence; `ARABIC_CELLS`
*does* count `expected.citation`, so a future Arabic citation trips the partition pin and the
rebaseline witness). The inline NOTE at the cite_passage call already flags it. I am NOT changing the
citation predicate now: leaving cite_passage on the shared `fold_aware_contains` keeps one containment
contract (the design invariant claude itself praised — "no private matcher remains"), and a short-
citation guard is a #39 design decision (where Arabic citations first appear) with its own collision
analysis. Logged as a follow-up, not silently inherited.

## claude minor 3: scope of "only ADDS credit" under `--evaluator strict` — ADDRESSED
Added a SCOPE paragraph to the `fold_aware_contains` docstring: the guarantee is exact for the
containment headline under the **default** graders; under `--evaluator strict`, `_with_outcome`'s
`classify_refusal(...) and not correct` can fold a decline-prefixed Imla'i delivery `refused→incorrect`
(coverage ↑, accuracy ↓) — the same rule `bounded_contains` already applied, just reaching more
deliveries; no committed run uses strict.

## claude minor 4: benchmark signal (haiku-search 33/33, haiku 30/33 on the Qur'an cut) — N/A (working-group note, no code change)
Noted for #39 difficulty design; not a code change.

## Net
Full gate green after the fixes: pipelines **641 pass / 2 skip** (new boundary test = +1), viewer
vitest pass, copyright audit OK. No score artifact moved (docstring/test/claim-only changes;
`ANCHOR_DIGEST` and the frozen SIM SHAs untouched). Advancing to the pr gate (HUMAN approval) — I do
not self-approve.
