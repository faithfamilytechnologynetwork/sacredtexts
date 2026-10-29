# Phase 2 impl consult — iter 1 rebuttals (codex + claude, both REQUEST_CHANGES / HIGH)

Both reviewers independently verified the core design correct and non-circular (58 movers all
`incorrect→correct`, SIM frozen recomputed from `b93e881`, splices byte-identical, both lanes green)
and converged on the same primary gap. All blocking items folded.

## 1. `jev_agreement.{json,md}` left stale — FIXED (both reviewers, blocking)

**Finding:** the tutorial Jev cross-check still reported the pre-fold containment column (agreement
0.9325, judge-only 27, both 239) against scores that now contain 259; it is a named Phase-2 file and
a spec SC ("No `jev_agreement.md` disagrees with its source scores"), and regeneration is free
(committed `judgments.jsonl`, deterministic — no paid judge call). I had wrongly deferred to #48's
"retain as historical" precedent; my own plan said regenerate.

**Fix:** regenerated via `judge-agreement answers scores judgments`. Containment agreement
0.9325 → **0.9825** (both 239 → 259, **judge-only 27 → 7, deterministic-only 0 throughout**); the
new report labels the containment and refusal columns separately. Rewrote the tutorial README note
from "historical / read refusal from summary.json" to the current, consistent framing, and surfaced
the corroboration (the Jev judge independently matched 20 of the fold's newly-credited cells, and the
fold credited nothing the judge rejected — independent no-wrong-credit evidence) in the README and
the review doc's moved-numbers section. The refusal column is unchanged by Spec 52 (0.985).

## 2. Witness pinned counts, not cell identities — FIXED (codex, blocking-ish)

**Finding:** `test_orthography_rebaseline.py` pinned per-run mover COUNTS, so a compensating
add/remove swap could pass; original and exp lacked exact-set coverage.

**Fix:** replaced `ORTHO_MOVER_COUNT` with `ORTHO_MOVERS` — the exact `(model_id, question_id)` set
per run (tutorial 20, original 15, first-run ∅, exp-ar 14, exp-en 9), each re-derived from committed
answers via `fold_aware_contains ∧ ¬bounded_contains` and asserted as an exact set equality (reports
unexpected/missing on failure).

## 3. Dropped witness item (4) summary↔scores self-consistency — FIXED (claude, non-blocking)

**Finding:** `original-2026-10-21/summary.json` had no durable pin, leaving the surgical hand-splice
(the aspir-48 scar) unguarded against future drift.

**Fix:** added `test_summary_agrees_with_scores` — recomputes per-model/per-task
accuracy/coverage/correct/incorrect/refused from `scores.jsonl` and asserts equality with
`summary.json` for tutorial and original. (Suite 625 → 629.)

## 4. Directionality claim over-stated for a mixed Imla'i reference — FIXED as a scope/claim fix (codex)

**Finding:** an Uthmani answer fails against a MIXED defective/plene Imla'i expected (`هٰذَا ٱلْكِتَٰبُ`
vs `هذا الكتاب`): the two global answer forms either delete or materialise every dagger, so neither
reproduces a per-word mix — contradicting the "direction-independent" claim.

**Disposition:** the claim is narrowed, not the code — the dual answer form is **load-bearing** (14
committed cells match only via the plene form, where the answer wrote a dagger the reference wrote as
a full alef), so it stays. The gap is specifically a reference *itself* written in mixed Imla'i; the
per-position optionality is carried by the reference's daggers, which a dagger-less Imla'i reference
cannot supply. **This never arises on the committed corpora** — references are the corpus orthography
(Uthmani QUL for the Qur'an, carrying the daggers), and #39's Arabic subset scores against the same
corpus. Corrected the `fold_aware_contains` docstring and added the boundary to the review's
known-limitations (beside the Q14:34 `ءَا↔آ` under-credit residual). No committed score is affected.

## Not changed (reviewer-endorsed)

- Deferring the `ءَا↔آ` (hamza-alef ↔ alef-madda) rule to a follow-up with its own collision
  analysis — both the design and claude called this the right scope call; documented as a residual.
- `normalize()`, the equality submetrics, the containment-only blast radius — verified correct;
  unchanged.
