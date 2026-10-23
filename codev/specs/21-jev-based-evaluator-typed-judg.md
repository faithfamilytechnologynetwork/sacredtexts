# Specification: Jev-based evaluator — typed judge verdicts for containment and passage equivalence

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/21-*.md.
-->

## Problem Statement

The Spec 15 scoring contract decides the headline `correct` bit **deterministically**: string
graders (`strict` ⇒ `normalized`, `containment` ⇒ `contains_reference`) plus an always-on
`token_f1` diagnostic, with refusal handled as an OUTCOME. This is the right default — it is cheap,
reproducible, and byte-stable. But two questions it cannot answer deterministically have no second
opinion today:

1. **Containment near-misses.** When a model returns the *right* scripture passage but in an
   orthographic/vocalization variant that normalization cannot fold (e.g. web-retrieved Uthmani
   Arabic that differs from the indexed edition in marks/spacing beyond what `normalize()` deletes),
   `contains_reference` reads 0 even though a human would say the text *is* there. These surface as
   high-`token_f1` cells that the headline still scores as misses. There is no typed, probabilistic
   signal distinguishing "genuinely wrong" from "right passage, different orthography".

2. **Passage equivalence.** When a miss is actually *another indexed edition's or tradition's
   wording of the same citation*, nothing in the current pipeline flags it. Disagreement analysis
   is entirely manual.

Phase-1 authors and the paper's error analysis currently resolve both by hand. A typed judge that
returns a verdict **with a probability** per cell would make that analysis a recorded, resumable,
auditable pipeline artifact instead of an ad-hoc read.

This is **diagnostic tooling, not a new headline.** The maintainer decision on Spec 15 is that the
headline stays deterministic; this spec adds a recorded second opinion beside it, never a
replacement for it.

## Current State

- Scoring is deterministic and selectable (`score --evaluator`), headline = OR of selected inline
  graders' verdicts; `graders.py` already **models** the paid judge seam: a non-inline, verdict-less,
  `default=False` grader descriptor whose metric fields are produced and merged by *its own* pass,
  never computed inline by `score`. `resolve_evaluators` fails fast if such a grader is selected
  inline. The slot exists; nothing fills it.
- Refusal is an OUTCOME in `outcomes.py` (`classify_refusal`, `_with_outcome`), excluded from
  `accuracy`, surfaced as `coverage`/`refused_rate`. There is no cross-check on that classification.
- There is **no paid, semantic, or judge-based evaluation step** in the pipeline. Every scoring run
  is free, local, and deterministic.
- Jonathan Karr's PR #30 ("Part 2 of 3": the Jev judge) contains a working `jev.py` — closed-question
  Jev judgments over an answers file, written to a resumable `judgments.jsonl` sidecar — plus a
  `sacredbench judge` CLI command, prompts (three closed questions: refusal / matches_requested /
  kind), and a test. It was never merged. Its model id (`typesafe/jev-1.13`) is wrong (see Current
  State → live verification below), and its passage-equivalence feature imports an `EditionIndex`
  from `cross_translation.py`, a **sibling part of the #30 split that is not yet on `main`**.
- **Live verification (performed for this spec, against the real OpenRouter Decisions API):**
  - The servable decisions model id is **`jev-latest`**, which resolves to build
    **`typesafe/jev-1.14-20261014`**. Both `typesafe/jev-1.13` and `typesafe/jev-router` return
    `"Model … does not exist"` from `POST /api/alpha/decisions`. (`typesafe/jev-router` is a catalog
    entry in `v1/models` with an empty `endpoints` list — not servable.)
  - The real HTTP-200 response shape matches Karr's `interpret()` exactly:
    `{ model, provider, id, answers: { refusal:{type:"noul",noul:p}, matches_requested:{type:"noul",noul:p},
    kind:{type:"choice",choice,probabilities{…},confidence} }, usage:{input_tokens,output_tokens,cost} }`.
  - Cost is tiny: a three-question call cost ≈ $0.000027; total verification spend ≈ $0.00005.

## Desired State

A **Jev evaluator** fills the existing Spec 15 paid-grader seam: an explicitly-invoked, paid,
resumable, separate pass that asks Jev (TypeSafe's System-One typed judge) bounded closed questions
about each already-collected answer cell and records **typed verdicts with probabilities** as
diagnostic metrics. Specifically:

- The judge contributes verdicts on **containment** ("does the answer contain the requested text,
  allowing orthographic/vocalization variance?") and **passage equivalence** ("is the answer the
  requested wording, another indexed wording of the same citation, or neither?"). It may also emit a
  **refusal probability as a diagnostic cross-check** on the deterministic refusal outcome — but
  refusal **remains an OUTCOME** owned by `outcomes.py`; the judge never becomes the refusal grader
  and never sets the headline.
- The evaluator is registered through `graders.py` as a **non-inline, verdict-less, `default=False`**
  grader, so it is **never part of the default `score`** and selecting it inline fails fast (the seam
  already enforces this). Its verdict + probability land as additional recorded metrics, merged by
  its own pass — never mutating the deterministic headline.
- Every judged cell is fully reproducible: the **requested** judge model and the **resolved** build,
  the decision id, provider, the complete typed answers, and per-cell usage (input/output tokens and
  cost) are recorded.
- The pass is **resumable** (a re-run skips already-judged cells; failed cells stay pending and are
  not written) and its **spend is surfaced** the way `collect`'s is.
- The evaluator is **validated on the committed tutorial run** before it is trusted: an agreement
  report against the deterministic tiers (judge containment vs `contains_reference`; judge refusal
  probability vs the `refused` outcome) plus a **manual review of every disagreement cell**,
  documented in the review.

Users (the paper authors, benchmark maintainers) get a recorded, auditable answer to "is this miss a
real miss, or an orthographic/edition/tradition variant?" without re-scoring the run or touching the
deterministic headline.

## Success Criteria

- [ ] A `jev` evaluator is registered in `graders.py` as **non-inline, verdict-less,
      `default=False`**; it is absent from `DEFAULT_EVALUATORS`, and `score --evaluator jev` fails
      fast with the existing "separate-pass grader cannot be run inline" error. A default `score`
      run's output is unchanged by this spec.
- [ ] A dedicated, explicitly-invoked CLI step judges an answers file and writes a resumable
      judgments artifact; the judge is **never invoked by `score` or `collect`**.
- [ ] The judge calls the real OpenRouter Decisions API using model id **`jev-latest`** (verified
      servable; resolves to `typesafe/jev-1.14-20261014`), with `OPENROUTER_API_KEY` read from the
      environment only. An unexpected response shape (missing/mistyped `answers` fields) **fails
      loud**; there is no fallback and no silent default.
- [ ] Each judged cell records: requested `judge_model`, resolved judge build, decision id, provider,
      the full typed answers (refusal probability, containment/`matches_requested` probability, `kind`
      choice + per-label probabilities + confidence), and usage (`in`/`out`/`cost`).
- [ ] The pass is **resumable**: re-running over the same output skips cells already judged (keyed on
      question × model × judge model) with zero new API calls; a failed cell stays pending (not
      written) and the run reports it.
- [ ] Total Jev spend for a run is **surfaced** (summed cost + per-cell cost available), comparable to
      how `collect` surfaces spend.
- [ ] Refusal is **not** turned into a grader. `outcomes.py` remains the sole owner of the `refused`
      outcome and the headline is unchanged; the judge's refusal signal is recorded as a diagnostic
      cross-check only.
- [ ] The evaluator is run on the committed **tutorial run** to a **fresh/sidecar path** (never
      overwriting committed `scores.jsonl`/`answers.jsonl`); an **agreement report** vs the
      deterministic tiers is produced and **every disagreement cell is manually reviewed** and written
      up in `codev/reviews/21-*.md`.
- [ ] No committed artifact overwrites or diverges from committed run evidence: committed
      `scores.jsonl` for `runs/tutorial-2026-10-11` and `runs/original-2026-10-21` stays
      **byte-identical**; `collect`/`score` are never re-run over them.
- [ ] The audit gate (`audit.py` in `.codev/checks/test.sh`) passes: **no key material, no NABRE/TLG
      text, no restricted-derived content** in any committed artifact. Live-run judgment output
      committed as evidence (if any) is over public-domain tutorial content only.
- [ ] The 'add an evaluator' recipe in `CODE_WALKTHROUGH.md` documents the Jev paid/separate-pass
      evaluator so a future contributor can follow the seam.
- [ ] Carried-over Jev code from PR #30 preserves **Jonathan Karr's authorship** on the commit(s)
      that carry it.

## Constraints

- **Baked (architect brief, 2026-10-23) — do not relitigate:**
  - This is **Part 2 of 3 of PR #30**; reuse Karr's judge code where it still fits and **keep his
    authorship** (`git commit --author`) on carried-over commits.
  - Land through the **Spec 15 graders seam** (`graders.py`, `score --evaluator`) as a
    **separate-pass, paid grader that is NEVER the default**.
  - **Refusal stays an OUTCOME** computed by `outcomes.py`, not a grader. The judge contributes a
    verdict on **containment / passage equivalence only** (a refusal *probability* is permitted only
    as a recorded diagnostic cross-check).
  - **Live-verified shape, fail fast, no fallbacks.** Model id derived from the real response, not the
    docs.
  - **Budget:** cap live spend during this project at **$8 total**; stop and ping the architect above
    it. (Verification to date: ≈ $0.00005.)
  - **Never re-run `collect`/`score` over committed run evidence** (`runs/original-2026-10-21`,
    `runs/tutorial-2026-10-11`); judge output goes to a fresh `runs/<id>/` or a sidecar; committed
    `scores.jsonl` stays byte-identical.
  - **Public repo:** no key material, no NABRE/TLG (restricted) text in any committed artifact.
  - **PR:** description says "Part 2 of 3 of #30" and closes #21; **no** Generated-with /
    Co-Authored-By lines.
- **Technical / integration:**
  - API key via environment only (`OPENROUTER_API_KEY`), consistent with `providers.py` style.
  - `pipelines/` is the single `sacredbench` uv project; the judge runs via
    `uv --project pipelines run python -m sacredbench …`.
  - Depends on **#15** (merged: the graders seam + `outcomes.py` are on `main`).
  - Keep it simple (no speculative generality beyond the seam that already exists).

## Assumptions

- Jev's typed-judge behaviour is stable across the two closed-question types used (`noul` for
  yes/no-with-probability, `choice` for one-of-set) — verified live for this spec.
- The committed tutorial run's answers embed the question (`source`, `expected.text`, `citation`),
  which the judge state requires — verified against `runs/tutorial-2026-10-11/answers.jsonl`.
- `OPENROUTER_API_KEY` is present in the project-local `.env` (symlinked to `sacredtexts/.env`) and
  carries decisions-API access.
- The passage-equivalence feature's "indexed other wordings" needs an edition index of the question
  pool's citations. See Open Questions (Critical) — the source of that index is **not yet settled**
  because `cross_translation.py` is a sibling part of the #30 split not on `main`.

## Solution Approaches

### Approach 1: Sidecar judgments file + non-inline grader registration (recommended)

Carry over Karr's `jev.py` (resumable `judgments.jsonl` sidecar beside a run) with the model id
corrected to `jev-latest` and the shape validated against the live API; register the `jev` grader in
`graders.py` as non-inline/verdict-less/`default=False` so the seam, CLI, and recipe are coherent;
validate on the tutorial run via an agreement report + manual disagreement review.

- **Pros:** reuses verified code; the sidecar never touches committed `scores.jsonl`, satisfying the
  "byte-identical evidence" and "never re-run score" constraints directly; resumability/spend already
  implemented; smallest diff; preserves Karr's authorship cleanly.
- **Cons:** judgments live beside `scores.jsonl` rather than *inside* each score row, so viewer/paper
  consumers read a second file. (Viewer integration is a separate part of the #30 split anyway.)
- **Risk/complexity:** Low. Main risk is the edition-index dependency for equivalence (Open Questions).

### Approach 2: Merge Jev verdicts directly into each `scores.jsonl` metrics row

Have the separate pass merge `jev_verdict`/`jev_prob` into the open `metrics` map of each score row,
exactly as the `graders.py` seam comment envisions, writing a **new run's** `scores.jsonl` (never a
committed one).

- **Pros:** single-file consumption; matches the seam's literal description.
- **Cons:** for validation on the committed tutorial run we still must not touch its `scores.jsonl`,
  so a sidecar/fresh-copy is required there regardless — i.e. this approach *also* needs a
  non-mutating path for the one run we must validate on. More moving parts, larger diff, more risk of
  accidentally diverging committed evidence.
- **Risk/complexity:** Medium.

**Recommended: Approach 1.** It satisfies every baked constraint with the least code and the least
risk to committed evidence, and keeps Karr's contribution intact. A documented merge-into-scores path
for *new* runs can be noted for a later part without being built here.

## Open Questions

- **Critical — passage-equivalence edition index.** Karr's equivalence judgment feeds Jev the "other
  indexed wordings" of a citation, drawn from an `EditionIndex` in `cross_translation.py`, which is a
  **sibling part of the #30 split not yet on `main`**. Without it, containment and the refusal
  cross-check work fully, but the `other_indexed_wording` label can never fire (equivalence degrades
  to requested/neither). Which path does the architect want?
  (a) ship containment + refusal-diagnostic now, treat equivalence's alternates as empty until the
  cross-translation part lands; (b) vendor a **minimal** citation→wordings index built from the
  committed question pool within this spec; (c) sequence this part after cross-translation merges.
  *Recommendation: (a) now with alternates optional, noting (b) as a cheap follow-up — it keeps Part 2
  independent of the other split parts.*
- **Important — committed surface.** Is the sidecar `judgments.jsonl` the only committed artifact for
  Part 2 (viewer/paper consumption being other parts), or should a merge-into-`scores.jsonl` path for
  *new* runs also ship now? *Recommendation: sidecar only; document the merge path.*
- **Important — validation scope.** Confirm validation is the **tutorial run only** (architect brief
  says tutorial). The `original-2026-10-21` run is larger/paid; judging it would consume budget.
- **Nice-to-know — defaults.** Concurrency and retry defaults for the pass (Karr uses 4 workers,
  2 retries); the leading-stance refusal-probability threshold for the agreement report.

## Test Scenarios

- **Happy path (live, tutorial run):** judge the committed tutorial answers to a sidecar; every cell
  gets a typed verdict + probabilities + resolved build + usage; summary reports counts and total
  cost.
- **Resumability:** re-running the pass over a partially-written output makes **zero** new API calls
  for already-judged cells; interrupting mid-run leaves a valid, appendable file.
- **Fail-fast on shape:** a response missing `answers`, or with a mistyped `noul`/`choice`, or an
  unknown `kind`, raises and the cell stays pending — no fallback value is written.
- **Fail-fast on credentials:** missing `OPENROUTER_API_KEY` raises before any call.
- **Non-default seam:** `score` with no `--evaluator` is byte-identical to before; `score --evaluator
  jev` fails fast; default headline unaffected.
- **Agreement analysis:** containment judge vs `contains_reference`, and judge refusal probability vs
  the `refused` outcome, are tabulated; disagreement cells enumerated for manual review.
- **Evidence integrity:** committed `scores.jsonl`/`answers.jsonl` for the tutorial and original runs
  are byte-identical after the work; the audit gate passes.
- **No-op on a fully-judged file:** `summarize` over a complete output reports the right counts and
  resolved build(s) without calls.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Edition index (equivalence) unavailable — cross_translation not on main | High | Medium | Make the index optional (containment + refusal-diagnostic unaffected); surface as Critical open question; recommend minimal vendored index as follow-up |
| Accidentally re-scoring / overwriting committed run evidence | Low | High | Always write to a fresh/sidecar path; add an evidence byte-identity check to the review checklist; audit gate in test.sh |
| Jev API shape drift vs Karr's code (wrong model id, field changes) | Medium | Medium | Model id and full shape **live-verified** for this spec; fail-fast on any unexpected field; record resolved build per cell |
| Live spend exceeds budget | Low | Medium | Validation is the small tutorial run; per-call cost ≈ $3e-5; hard $8 cap with stop+ping; resumability avoids re-spend |
| Key or restricted text leaking into a public commit | Low | High | Key from env only (never a file); audit gate; judge evidence committed only over public-domain tutorial content |
| Jev verdict mistaken for the headline | Low | High | Non-inline/verdict-less/`default=False` registration; refusal stays an outcome; documented as diagnostic tier in the recipe |

## References

- Issue #21 — Jev-based evaluator: typed judge verdicts for containment, refusal, and passage
  equivalence.
- PR #30 (Jonathan Karr) — "Type of Theological Errors, temperature, FaCCT improvements etc"; source
  of `jev.py`, the `judge` CLI, the closed-question prompts, and `test_jev.py`. This spec is **Part 2
  of 3**.
- Spec 15 — the evaluator/grader seam and the refusal-as-outcome decision (`graders.py`, `score.py`,
  `outcomes.py`).
- Spec 26 — original-language default and `verify_source` hardening (context for the question pool).
- `CODE_WALKTHROUGH.md` — "Adding an evaluator (a named grader)" recipe (to be extended for the paid
  separate-pass evaluator).
- Architect brief, 2026-10-23 — baked decisions captured in Constraints.
- Live verification: OpenRouter `POST /api/alpha/decisions`, model `jev-latest` →
  `typesafe/jev-1.14-20261014`; `v1/models` catalog entry for `typesafe/jev-router` (empty endpoints).
