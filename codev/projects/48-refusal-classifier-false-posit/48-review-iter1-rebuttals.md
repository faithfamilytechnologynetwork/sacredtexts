# Review / PR consult — iteration 1 rebuttals

**claude: APPROVE (HIGH)** — independently reproduced the oracle SHAs from the merge base, the 5-cell
outcome-only delta, the post-fix Jev figures, the 122/<0.13 calibration, and both test lanes. "None
blocking." Minor notes folded or deferred below.

**codex: REQUEST_CHANGES (HIGH)** — one real robustness gap in `asserts_delivery`. Accepted and fixed
in commit `26ec480`.

---

## Issue 1 (codex, blocking) — RECON negation scoped only to the claim, not through the payload (ACCEPTED, fixed)

`asserts_delivery`'s `_ASSERT_RECON` path checked `_NEG`/`_NON_IDENTITY` over `_assertion_sentence(…,
m.start(), m.end())` — i.e. only through the end of the reconstruction *claim* — while accepting a
script payload anywhere later via `_SCRIPT_CHAR.search(answer, m.end())`. So a disqualifier sitting
**between** the claim and the payload was missed:

> "My best reconstruction of the requested line **is not reliable; the adjacent text is:** בראשית ברא"

…produced `asserts_delivery=True` (class B mis-read as a delivery). Confirmed by trace.

**Changed**: the RECON span now extends to the payload's start —
`_assertion_sentence(answer, m.start(), payload.start())` — so a negation / non-identity modifier
anywhere from the claim through the delivered script disqualifies it. Verified the only committed
RECON-path A cell, `d4c3bda0b400` ("my best reconstruction of the standard Vilna wording … Please
check it on Sefaria: «script»"), carries no `_NEG`/`_NON_IDENTITY` token in the widened span, so it
still flips. Added a regression case to `test_spec48_reworded_class_b_does_not_overfire`
(negation-between-claim-and-payload). The INTRO path was already safe (its regex ends with a
`(?=[_SCRIPT])` lookahead, so its span already reaches the payload).

## Issue 2 (claude, minor) — dead `ANSWER_FILES` (ADDRESSED)

`ANSWER_FILES` at `test_outcomes.py:143` was an unreferenced remnant of an earlier lighter sweep,
superseded by the stronger `TRIPLES` gate (`test_spec48_classifier_reproduces_committed_refusals`).
**Removed** — a clean-code requirement, and it removes the misleading impression that
`answers-ar-normalized.jsonl` was being swept when it was not.

## Issue 3 (claude, minor/latent) — gate paired `scores-ar.jsonl` with the wrong answers file (ADDRESSED)

The Arabic triple paired `scores-ar.jsonl` with `answers-ar.jsonl`, but that score file was produced
from `answers-ar-normalized.jsonl` by the run's own `analyze.py` (the orthography fold). **Changed**
the triple to `answers-ar-normalized.jsonl` so the gate recomputes over the answers the scores were
actually derived from. Inert today (the Arabic run has no refusals, so both sets are empty), but it
keeps the gate honest if the run ever gains one. Verified green.

## Issue 4 (claude, minor) — same-sentence disclaimer *after* the payload (DEFERRED to #52, documented)

A disclaimer trailing the payload within the same sentence ("the line is: «script», but that is a
different line") still reads as a delivery, because the checked span ends at the payload start. claude
noted no committed cell is affected and flagged it for #52. **Documented** as a third limitation in the
`_NON_IDENTITY` block comment and added to the review's Follow-up Items. Deferring rather than
extending the span past the payload avoids stranding real A cells whose legitimate prose follows the
delivered text, and respects the architect's merge order (fold-aware refinement lives in #52).

## Issue 5 (claude, note) — AC3 guarded only transitively (ACKNOWLEDGED, no change)

"No surviving refusal disagreement with `refusal_p < 0.25`" is verified manually (post-fix Jev: 6
disagreements, all in `[0.25, 0.75]`) and guarded transitively by the whole-corpus refused-set gate
(which pins the exact refused set, of which the Jev survivors are a function). A direct `refusal_p`
assertion would re-encode the Jev join the rebaseline deliberately keeps as a cross-check, not a
runtime input (spec constraint). Left as-is.

---

**Verification**: both lanes green after the fold — viewer 187 passed (19 files), pipelines 586 passed
/ 2 skipped. Only `outcomes.py` and `test_outcomes.py` changed; no run artifact, oracle, or summary
touched (the rebaseline is unaffected — this sharpens the classifier against an adversarial input and
tidies the test gate).
