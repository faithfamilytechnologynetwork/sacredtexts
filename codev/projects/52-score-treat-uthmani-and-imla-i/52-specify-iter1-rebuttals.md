# Spec 52 — Rebuttal to iteration-1 spec consults

Both reviewers returned **REQUEST_CHANGES** with HIGH confidence, and both were right on the
substance. I verified every load-bearing claim in a REPL against the real code and run evidence
before revising (lessons-critical: derive from real data, not docs). All points are **accepted**;
none disputed. Summary of what changed in the spec.

## claude (REQUEST_CHANGES)

**1. Enumerated rules can't satisfy SC-1 and non-collision; the ا/ى/ي relation is
context-dependent.** ACCEPTED — this was the most important finding. Verified: the context-free
full collapse of {ا, ى, ي, ـٰ, ٱ} that covers all four residual pairs merges distinct words
(`قَالَ`≡`قِيلَ`, `بَيْت`≡`بَات`, `سَأَلَ`≡`سَالَ`), and a naive ىٰ→ا breaks `عَلَىٰ↔على`
(`علا` vs `علي`). Changes: demoted the "a fold covering all listed pairs resolves every cell"
assumption to an explicit statement that a context-free fold is insufficient; added SC requiring
the fold be **position/context-aware**; added a context-dependence negative test
(`أَتَىٰكُمْ↔أَتَاكُمْ` equal AND `عَلَىٰ↔على` not broken); promoted the exact ى/ىٰ predicate to a
**Critical** open question for the plan.

**2. Word-level collision, not unit-level.** ACCEPTED. `contains_reference` is substring and
`token_f1` is token-based, so a word merge credits a wrong word inside an otherwise-correct answer
and the projection oracle can't see it. Changes: added a **word-level non-collision gate** SC and
constraint (rule rejected if it merges distinct corpus-vocabulary words; non-collision beats
convergence), plus a corpus-vocabulary sweep test.

**3. Word segmentation omitted; SC-2 unreachable without it (measured 10/14 vs 8/14).** ACCEPTED.
The headline example is a word-boundary diff that no character rule resolves. Changes: added
word-boundary as an in-scope gap in Current State and Success Criteria; made it a **Critical** open
question (strip Arabic whitespace in `normalize()` vs restrict to the containment predicate vs leave
2 cells as documented residuals).

**4. Spec-15 four-submetric consequence of stripping Arabic whitespace.** ACCEPTED. Changes: added
an SC and a test scenario requiring the Arabic `exact`/`normalized`/`token_f1`/`contains_reference`
behaviour under the word-boundary rule to be decided and asserted, noting `token_f1` degenerates
toward one token for Arabic — a deliberate documented consequence.

**5. Rebaseline omits derived artifacts.** ACCEPTED. Verified `summary.json`/`md` in all three
runs, `original-2026-10-21/facct.*` (Spec 32), and `tutorial-2026-10-11/jev_agreement.*`
(`judge_only: 27` are exactly this fold's target). Changes: added an SC requiring all score-derived
artifacts be regenerated per run, no `summary.md` disagreeing with `scores.jsonl`.

**6. "Arabic cell" undefined; byte-for-byte guards unnamed.** ACCEPTED. Changes: defined "Arabic
cell" by **answer-script** (so first-run's 2 Arabic answers over English questions count and may
move); named `test_first_run_regression.py` and `test_tutorial_run.py` as the guards that break,
alongside `test_contains_reference_rebaseline.py`, in SC and References.

**7. Minor — madda already folds; real gap is standalone hamza; "dropped" is asymmetric.**
ACCEPTED. Verified madda/seats fold via NFKD+Mn-strip. Changes: rewrote Current State with an
empirical table of what folds today vs the actual gaps; made the standalone-hamza canonical target
an **Important** open question (measured `ارتم` vs `ارايتم` shows "dropped" fails).

## codex (REQUEST_CHANGES)

**1. Folds don't equate يَـٰبُنَىَّ with يَا بُنَيَّ; word-boundary unspecified; global whitespace
deletion risky.** ACCEPTED — same as claude #3/#4. Addressed via the word-boundary gap + Critical
open question + Spec-15 submetric SC.

**2. The #48 coordination signal contradicts changing `normalize()`.** ACCEPTED, and important —
orthography matches flip `normalized` 0→1, so the "`correct` flips while `normalized`==0" signal
(the #15 containment signature) is wrong here. Changes: redefined the oracle as a **before/after
projection delta** (non-Arabic frozen, Arabic flips pre-registered), kept refusal-independence so a
rebase onto #48 stays clean; stated this as a constraint. Also sent the architect a correction of my
earlier (wrong) framing.

**3. Rules underspecified — standalone hamza target, hamza seating, ىٰ precedence.** ACCEPTED.
Addressed by the position-aware SC, the hamza-target open question, and the ordering/precedence
constraints.

**4. Current State inaccurate — madda folds via NFKD; mark range affects Syriac/Thaana/etc.**
ACCEPTED. Changes: corrected Current State (madda/seats already fold); replaced "every other script
unchanged" with "**non-RTL** scripts byte-for-byte unchanged; other RTL-block scripts' marks are
stripped too"; added Hebrew/other-RTL regression coverage as an SC.

**5. Collision gate needs a testable rule + failure disposition.** ACCEPTED. Changes: the
non-collision SC/constraint specifies word granularity, corpus vocabulary, and the disposition
(reject the rule, keep the residual, document it); made the gate mechanics an Important open
question.

**6. Rebaseline scope still "at minimum".** ACCEPTED. Changes: enumerated the four runs concretely
(tutorial, original-2026-10-21, first-run, experiment) plus the derived artifacts, and required
frozen pre-change witnesses rather than ambiguous "re-pinning".

## Net

No disputes. The revision turns the issue's "proposed fix" from a (provably insufficient)
context-free character map into a position-aware, collision-gated fold with an explicit
word-boundary/submetric decision deferred to the plan as Critical open questions, and a correctly
scoped, correctly signalled rebaseline. The two remaining Critical open questions (the ى/ىٰ context
predicate and the word-boundary rule) are implementation decisions the plan phase will settle.
