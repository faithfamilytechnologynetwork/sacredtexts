# Phase 1 (implement) — Rebuttal to iteration-1 consults

Both reviewers returned **REQUEST_CHANGES** (HIGH) and confirmed the fold logic is correct and
corpus-verified (claude independently counted 211 medial / 400 word-final / 15 bare-medial maqsura
cases and 0 non-adjacent daggers, validating the boundary detector). Two defects + minors; all
accepted and fixed.

## Issue 1 — `arabic_ws_insensitive_contains` was script-blind and unbounded (both reviewers)

The helper deleted ALL whitespace, so it equated Latin `"the rapist"`/`"therapist"` and matched
`Jude 1:3` inside `1:30` and `هدي` inside `المهديون` — breaking the word-boundedness
`bounded_contains` guarantees, which Phase 2 makes the single shared containment contract. FIXED
with claude's strictly-dominating approach, Arabic-gated:

- **Arabic reference** → anchored pattern `(?<!\w) + \s*.join(chars of fold-normalised ref) + (?!\w)`
  — optional whitespace between characters so one-word Uthmani ↔ two-word Imla'i matches in either
  direction, while the anchors keep it bounded.
- **Non-Arabic reference** → plain word-bounded containment, unchanged (so the Latin contract and
  the non-Arabic projection freeze hold).

Added the missing negatives: `Jude 1:3`↛`1:30`, `هدي`↛`المهديون`, `the rapist`↛`therapist`, plus a
positive cross-boundary Arabic match and a non-Arabic bounded match.

## Issue 2 — the corpus diagnostic was blind to the collisions it was meant to list (both)

My `skeleton()` neutralised the fold's own alphabet (ء→ا, ى→ي), so `len(skels)==1` could not see
the one collision class the fold introduces; claude enumerated 7 genuine distinct-word merges that
passed silently, and 4 are from the **hamza ء→ا** rule the spec limitation hadn't named. FIXED:

- The diagnostic now uses a **strict skeleton** that folds only the zero-risk orthography
  (dagger/digraph→alef, wasl, marks, NFKD seats/madda) and **keeps ء and ى distinct** — so it can
  see the real collisions. The full corpus residue is **9 buckets** (claude's 7 plus `شىء/شيـٔا`
  and `برىء/بريـٔا`), now a **pre-registered, hand-annotated allow-list** (`_ACCEPTED_DISTINCT_WORD_
  MERGES`): the test asserts the residue equals it exactly, so a NEW collision (or a vanished one)
  fails and forces re-review. Every non-residue bucket is asserted to be a pure same-word
  Uthmani↔plene reunion.
- The one-sided `< 150` bound is now **two-sided** (`40 < n < 120`) so a no-op fold (0 merges) fails.
- The `score.py` limitation comment now names BOTH the maqsura and hamza classes and lists the 9;
  the spec's known-limitation paragraph is extended the same way (architect directive to document
  the residue — now covering the hamza class claude surfaced). It feeds the Phase-3 architect packet.

## Minors (COMMENT) — both fixed

- **`score_normalize` duplicated `normalize`'s body.** Parameterised a single private
  `_normalize(text, *, fold)`; both public functions delegate, so they cannot drift. The
  byte-for-byte committed-run guards confirm `normalize()` behaviour is unchanged.
- **`_folds_equal` vacuous symmetry** — simplified to one comparison, with a comment that
  direction-independence has teeth only for the containment predicate (which the helper tests cover).

## Net

Suite now **578 passed / 2 skipped**; all four committed-run regression guards unchanged and
passing (default path byte-identical). The two wiring-relevant defects that would have surfaced in
Phase 2 (unbounded containment; undocumented hamza collisions) are closed now, and the distinct-word
residue is a frozen allow-list the rest of the project builds on.
