# Plan 48 — rebuttal to iteration-1 reviews

Both reviewers returned **REQUEST_CHANGES (HIGH)**. I verified every factual claim directly against
the run data and the test suite; all held, so the plan is revised, not defended. Summary of
dispositions below (A = accepted and changed; no claim was rejected).

## Claude (REQUEST_CHANGES)

**1. Conjunctive rule falsified by its own A set — ACCEPTED (blocking).**
Confirmed: A-cell `d4c3bda0b400` opens "I couldn't confirm the exact Sefaria text, and **I'm not
sure which passage is segment 9**" — a passage-identity disclaimer, yet it is a locked A cell. A
"assertion AND no-disclaimer" gate strands it `refused`. **Change:** the rule is now **assertion-only**
— `refused` unless a *positive identity assertion* fires; the absence of a disclaimer is not
consulted. Documented in the Executive Summary ("Rule form") and Phase 1 deliverables.

**2. `"from memory"` blast radius ~30× — ACCEPTED (blocking).**
Confirmed by my own count: `"from memory"` occurs in **147 currently-refused cells** (38 tutorial /
34 first-run / 75 original), almost all negated declines ("I can't reliably reproduce … from
memory"). A flat substring cue flips them all. **Change:** the assertion test is specified as
**positive-frame and negation-aware** ("… text of ‹cit› **is**:", "… **starts**:", not under a
negation), explicitly *not* a flat `_DECLINE_CUES_RAW`-style tuple. A dedicated unit case asserts
`"from memory"`-under-decline cells stay `refused`.

**3. Pinned numbers stated as acceptance criteria, but contingent — ACCEPTED.**
Confirmed the trigger: A `d0239d95ae29` ("most likely matches this line, is:") vs B `eaf381cf82d3`
("segment 3 most likely falls somewhere in this passage, but I couldn't check it") may not separate
without single-cell hand-fitting. **Change:** the numbers (0.9250 / 0.80 / 20 etc.) are now marked
**contingent targets, re-derived from the actual flip set and surfaced**; the sanctioned fallback
(strand ambiguous cell as `refused` + surface) is explicit, and the hard gates are the anti-overfit
anchor and the no-global-drift sweep, not the exact figures.

**4. Cross-run discovery belongs in Phase 1, incl. `complete_unit` — ACCEPTED.**
Confirmed `original-2026-10-21` has **89 refused `complete_unit`** cells (and `_TEXT_RETRIEVAL`
covers `complete_unit`). **Change:** a read-only **whole-corpus blast-radius sweep** is now a Phase-1
deliverable and gate — over all four runs and all `_TEXT_RETRIEVAL` tasks — asserting the global
`refused_pre − refused_post` set equals the locked flip set *before* any evidence is regenerated.
Non-tutorial flip sets are pre-registered **empty unless the sweep proves otherwise** (then
enumerate + architect-confirm).

**5. Outcome-flip witness is circular — ACCEPTED.**
Confirmed re-pinning `REFUSED_SET_SHA256` from post-change data proves nothing. **Change:** the new
`test_refusal_rebaseline.py` freezes a **pre-change** `(model_id, question_id) → outcome` SHA (via
`git show HEAD:…`) and asserts `apply(flip_set, prechange_outcomes) == postchange_outcomes` exactly,
plus an unchanged `correct` projection SHA and the existing `(exact, normalized, token_f1)` SHA.

## Codex (REQUEST_CHANGES)

**1. Arabic run has no `answers.jsonl`/`scores.jsonl`/summaries — ACCEPTED.**
Confirmed: `runs/exp-arabic-prompts-2026-10-29/` has `answers-{en,ar,ar-normalized}.jsonl`,
`scores-{en,ar}.jsonl`, a local `analyze.py` and `build_questions.py`, and **no** `summary.*`.
**Change:** Phase 2 regenerates this run through its own `analyze.py` path, driving both `-en` and
`-ar`, preserving the documented orthography-fold normalization — not a `score_file` over a
nonexistent `answers.jsonl`. (Note folded into the plan: #52 will later move some Arabic cells again
via fold-aware containment; that is #52's witness, per the architect's merge-order decision.)

**2. Pre-register cross-run flip sets before implementation — ACCEPTED.**
Addressed by the Phase-1 sweep (Claude #4): pre-registered sets (tutorial = 5 A cells; others =
empty unless proven), validated read-only before regeneration.

**3. Projection SHA can't prove `correct`/`outcome` unchanged — ACCEPTED.**
Same change as Claude #5: pre-change outcome **and** `correct` projections frozen; the registered
`refused→incorrect` transform must reproduce the post-change projection exactly.

**4. Classifier HOW underspecified — ACCEPTED (partially).**
The rule *form* is now locked (assertion-only, positive-frame, negation-aware, default-refused
fallback) with candidate assertion frames and the payload/negation conditions named. The exact cue
membership is curated at implement against the 13 pinned cells + the whole-corpus sweep — this is
the right altitude for a plan: the form and its validation are fixed, so implement cannot re-decide
the mechanism, only tune the cue list against a failing test. I judged fully enumerating the cue
strings in the plan to be premature precision given the sweep is the real validator; flagging this
as a deliberate, bounded deferral rather than an omission.

**5. `original` `facct.{json,md}` + `test_original_run_regression.py` — ACCEPTED.**
Confirmed both exist; `facct.py` reads `refused`/`accuracy`/`coverage` verbatim from
`metrics.outcome`, and `test_facct.py` uses only synthetic fixtures (staleness uncaught). **Change:**
`facct.{json,md}` regeneration is a Phase-2 deliverable whenever `original` outcomes move;
`test_original_run_regression.py` and `test_first_run_regression.py` are named in the reconcile list;
panel/roster/judge-provenance/`generated_at` preservation is called out explicitly.

## Net

Six substantive changes across the Executive Summary, both phases, and the Risks table; no point
rejected. The load-bearing shift is **rule form** (assertion-only + negation-aware) and a **Phase-1
whole-corpus gate** that makes the "from memory" footgun and any cross-run surprise fail *before*
the irreversible rebaseline, which is exactly where the risk lives.
