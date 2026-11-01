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

**Scope decision for Part 2 (architect-confirmed 2026-10-24).** Option (a): ship **containment + a
refusal-probability cross-check now**; passage equivalence is **explicitly OFF unless an index is
supplied**, not "empty until later". Concretely:

- The judge takes an optional **`--equivalence-index <path>`**. **Without it**, the rubric does
  **not ask the equivalence question at all**, and the sidecar records equivalence as
  **`not_evaluated`** — never as a no-match or a silent null, so no consumer can misread an absent
  judgment as a negative verdict.
- The equivalence-index producer is **not built in #21**: it is being built **concurrently in #32**
  (a sibling builder), whose cross-edition reading needs the same data. This spec **consumes** that
  producer's schema verbatim (below) and does **not** invent its own. #21 must **not depend on #32's
  branch** — its tests use a hand-written fixture in this schema.
- `jev.py` must **not** import `cross_translation` at top level: the import is dropped entirely (no
  stub module). The alternate-wordings lookup is driven solely by a supplied `--equivalence-index`.

**Equivalence-index file schema (consumed verbatim from #32; architect-pinned 2026-10-24):**
- Index file (`--equivalence-index <path>`): **JSONL, one row per `(work, citation, language)`**,
  each row `{ "work": str, "citation": str, "language": str, "wordings": [{ "version": str, "text":
  str }, …] }`. Same-canonical-language editions only; restricted editions already filtered out by the
  producer; **rows with a single wording are omitted**.
- Manifest at `<path>.manifest.json`: `{ "corpus_hash": str, "row_count": int, "digest": str,
  "excluded_restricted": [version ids] }`.
- **Consumer rules:** **fail fast** if the manifest is missing, or if its `corpus_hash` differs from
  the run manifest's `corpus_hash`; **record the index `digest`** on each sidecar row that used the
  index.

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
- a contributor's PR #30 ("Part 2 of 3": the Jev judge) contains a working `jev.py` — closed-question
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
  - The real HTTP-200 response shape matches the contributor's `interpret()` exactly:
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
  already enforces this). For Part 2 this registration is **selection/discovery-only**: it makes the
  evaluator nameable and keeps the CLI/recipe coherent, but the typed verdicts are written to a
  **sidecar judgments file** (authoritative schema below), **not** merged into `scores.jsonl`. The
  merge-into-score-rows path the `graders.py` docstring envisions is an explicit follow-up for *new*
  runs; it is **not built here** and the deterministic headline is never mutated. (Because
  `submetrics_for` only emits keys in `_CANONICAL_ORDER`, a non-inline grader's `metric_keys` would
  not reach `scores.jsonl` from `score` anyway — the sidecar is where its fields live.)
- **The resolved judge build is part of the grader's identity**, treated like a panel fingerprint
  (architect-decided 2026-10-24). `jev-latest` floats, so the build it resolved to
  (`typesafe/jev-1.14-20261014` today) is recorded on **every sidecar row**, in the **sidecar
  header/manifest**, and in the **evaluator provenance** that `score --evaluator` emits — so a summary
  states which judge build produced the verdicts. **Resuming onto an existing sidecar whose recorded
  resolved build differs from the current call's fails fast** with a clear error naming both builds.
  There are **no mixed-build files** — the earlier "flag a mixed-build file" idea is superseded by
  this hard fail.
- **Authoritative judgment-row schema (sidecar).** One JSON object per judged cell:
  `question_id`, `model_id`, `model` (the answer's model), `rubric_id` (prompt/schema version),
  `judge_model` (requested id), `judge_model_resolved` (the build Jev returns), `judge_provider`,
  `decision_id`, `question_set_digest`, `answer_digest` (binds the row to the exact answer judged),
  `index_digest` (the equivalence-index digest when one was used, else absent), `refusal_p`,
  `matches_requested_p` (containment), `kind` + `kind_probabilities` + `kind_confidence` **or**
  `equivalence: "not_evaluated"` when no index was supplied, and `usage` (`in`/`out`/`cost`). A
  sidecar **header/manifest** records the resolved judge build, `rubric_id`, question-set digest, and
  (if used) the index digest for the whole file. This is the contract viewer/paper consumers read.
- Every judged cell is fully reproducible: requested + resolved judge model, decision id, provider,
  the question-set digest, an answer-content digest, the equivalence-index digest if any, and per-cell
  usage.
- The pass is **resumable** (a re-run skips already-judged cells; failed cells stay pending and are
  not written) and its **spend is surfaced** directly from the Decisions API's returned
  `usage.cost` per cell, summed per run. (This is unlike `score`, which derives cost from configured
  panel prices in `configs/models.yaml` and reports UNPRICED without them — Jev needs no price config
  because the API returns the cost.)
- Only **text-retrieval cells** (`retrieve_quote`, `complete_unit`) are judged — the containment and
  passage-wording questions are meaningless for `verify_source` (a Yes/No source check) and
  `cite_passage` (a citation, not a quotation). Non-judged tasks are skipped and reported as skipped,
  not failed.
- The evaluator is **validated on the committed tutorial run** before it is trusted: an agreement
  report against the deterministic tiers (judge containment vs `contains_reference`; judge refusal
  probability vs the `refused` outcome) plus a **manual review of every disagreement cell**,
  documented in the review. The report both (a) classifies agreement using a **fixed threshold
  `p ≥ 0.5`** and (b) tabulates the **raw probability distribution per deterministic outcome class**,
  so the disagreement set is a stable, reproducible set rather than a threshold artefact.

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
- [ ] Each judged cell records the full authoritative schema above (requested + resolved judge model,
      decision id, provider, `rubric_id`, `question_set_digest`, `answer_digest`, `index_digest` when
      an index was used, the typed answers, usage), and the sidecar carries a header/manifest with the
      resolved build, `rubric_id`, question-set digest, and index digest (if any).
- [ ] **The resolved judge build is treated as grader identity.** It is recorded per row, in the
      sidecar manifest, and in the evaluator provenance that `score --evaluator` emits. **Resuming onto
      a sidecar whose recorded resolved build differs from the current call FAILS FAST** with a clear
      error naming both builds; there are no mixed-build files. Pinning a build is permitted.
- [ ] **Passage equivalence is OFF unless `--equivalence-index <path>` is supplied.** Without it the
      rubric does not ask the equivalence question and the sidecar records `equivalence:
      "not_evaluated"` (never a no-match or null). With it, the index is consumed in #32's verbatim
      schema; the pass **fails fast** if the index manifest is missing or its `corpus_hash` differs
      from the run manifest's, and records the index `digest` on each row that used it. #21 does not
      depend on #32's branch (tests use a hand-written fixture).
- [ ] `jev.py` does **not** import `cross_translation` (no top-level import, no stub module).
- [ ] Only `retrieve_quote` and `complete_unit` cells are judged; `verify_source`/`cite_passage` are
      skipped and reported as skipped (not failed, not silently dropped).
- [ ] The pass is **resumable** and **stale-safe**: re-running over the same output skips already-judged
      cells with zero new API calls, where "already judged" is keyed on question × model **× the exact
      answer content** (`answer_digest`) and the `rubric_id`/question-set-digest match — so a changed
      answer, a changed prompt/schema, or a mismatched question set forces a re-judge or fails loud
      rather than silently reusing a stale verdict. A failed cell stays pending (not written) and the
      run reports it.
- [ ] Total Jev spend for a run is **surfaced** from the API-returned `usage.cost` (summed + per-cell),
      and a **pre-flight estimate** (pending cells × typical per-cell cost) is printed before any calls;
      a `--limit` on cells judged per invocation makes the $8 cap enforceable. **The pre-flight estimate
      for the live validation pass is shown to the architect before that pass runs.**
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
- [ ] **Restricted text is never transmitted to the judge.** Because judging sends `requested_text`
      (the expected reference) to a third-party API, the pass refuses (or at minimum warns and skips)
      any cell whose source `(work, version, language)` maps to a `restricted` catalogue target. (This
      is latent today — neither committed run contains a restricted source — but the guard must exist
      before the pass is pointed at an arbitrary run.)
- [ ] A **live-verified Decisions response is committed (redacted) as the test fixture** that the
      fail-fast shape tests (`interpret`) run against, so the parser is pinned to the real wire shape,
      not a hand-written mock (per the project's "mocking the provider seam hides live-only failures"
      lesson).
- [ ] The 'add an evaluator' recipe in `CODE_WALKTHROUGH.md` documents the Jev paid/separate-pass
      evaluator so a future contributor can follow the seam.
- [ ] Carried-over Jev code from PR #30 preserves **a contributor's authorship** on the commit(s)
      that carry it.

## Constraints

- **Baked (architect brief, 2026-10-23) — do not relitigate:**
  - This is **Part 2 of 3 of PR #30**; reuse the contributor's judge code where it still fits and **keep that
    authorship** (`git commit --author`) on carried-over commits.
  - Land through the **Spec 15 graders seam** (`graders.py`, `score --evaluator`) as a
    **separate-pass, paid grader that is NEVER the default**.
  - **Refusal stays an OUTCOME** computed by `outcomes.py`, not a grader. The judge contributes a
    verdict on **containment / passage equivalence only** (a refusal *probability* is permitted only
    as a recorded diagnostic cross-check).
  - **Live-verified shape, fail fast, no fallbacks.** Model id derived from the real response, not the
    docs.
  - **Budget:** cap live spend during this project at **$8 total**; stop and ping the architect above
    it. (Verification to date: ≈ $0.00005.) The cap is made enforceable by a pre-flight cost estimate
    and a `--limit` on cells per invocation — not left to vigilance.
  - **Restricted-text transmission:** the judge call sends the expected reference text to a
    third-party API; the pass must guard against sending any `restricted`-target source, independent
    of the commit-time audit gate.
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
- **Baked (architect decisions, 2026-10-24):**
  - Model id is **`jev-latest`**; the **resolved build is grader identity** (recorded per row + in the
    sidecar manifest + in `score --evaluator` provenance); resume with a different resolved build
    **fails fast**, no mixed-build files; pinning a build is allowed.
  - Scope is option (a): **equivalence OFF unless `--equivalence-index` supplied** → records
    `not_evaluated`; `jev.py` drops the `cross_translation` import entirely.
  - The equivalence-index schema is **#32's, consumed verbatim** (see Scope decision); #21 does **not**
    build the producer and does **not** depend on #32's branch (tests use a hand-written fixture);
    fail fast on a missing index manifest or a `corpus_hash` mismatch with the run manifest; record the
    index `digest` per row.
  - The live validation pass's **pre-flight cost estimate is shown to the architect before it runs**;
    its sidecar is **new evidence beside the tutorial run**, never modifying `scores.jsonl`/
    `summary.json`; audit passes; spend within the $8 cap.
  - `refusal_p` is **diagnostic only**; `outcomes.py` stays the sole source of `refused`.

## Assumptions

- Jev's typed-judge behaviour is stable across the two closed-question types used (`noul` for
  yes/no-with-probability, `choice` for one-of-set) — verified live for this spec.
- The committed tutorial run's answers embed the question (`source`, `expected.text`, `citation`),
  which the judge state requires — verified against `runs/tutorial-2026-10-11/answers.jsonl`.
- `OPENROUTER_API_KEY` is present in the project-local `.env` (symlinked to `sacredtexts/.env`) and
  carries decisions-API access.
- The passage-equivalence feature's "indexed other wordings" come from an `--equivalence-index` built
  by **#32** (concurrent sibling builder) in a fixed schema (see Scope decision). #21 consumes it but
  does not build it and does not depend on #32's branch — the equivalence path is off (recording
  `not_evaluated`) whenever no index is supplied.

## Solution Approaches

### Approach 1: Sidecar judgments file + non-inline grader registration (recommended)

Carry over the contributor's `jev.py` (resumable `judgments.jsonl` sidecar beside a run) with the model id
corrected to `jev-latest` and the shape validated against the live API; register the `jev` grader in
`graders.py` as non-inline/verdict-less/`default=False` so the seam, CLI, and recipe are coherent;
validate on the tutorial run via an agreement report + manual disagreement review.

- **Pros:** reuses verified code; the sidecar never touches committed `scores.jsonl`, satisfying the
  "byte-identical evidence" and "never re-run score" constraints directly; resumability/spend already
  implemented; smallest diff; preserves the contributor's authorship cleanly.
- **Cons:** judgments live beside `scores.jsonl` rather than *inside* each score row, so viewer/paper
  consumers read a second file. (Viewer integration is a separate part of the #30 split anyway.)
- **Required edits to the carried-over code** (not just a config change): correct `JEV_MODEL` to
  `jev-latest`; **drop the `cross_translation` import entirely** (no stub) and drive alternates only
  from an optional `--equivalence-index` in #32's schema (manifest + `corpus_hash` fail-fast, record
  index digest); record the resolved build per row + manifest + provenance and **fail fast on a
  build-mismatched resume**; strengthen the resume key to bind `answer_digest` + `rubric_id` +
  `question_set_digest`; make the `kind`/equivalence question conditional on an index (`not_evaluated`
  otherwise); add the task-type filter, the restricted-target guard, and the pre-flight estimate +
  `--limit`; register the `jev` descriptor in `graders.py`; extend the `CODE_WALKTHROUGH.md` recipe.
- **Risk/complexity:** Low–Medium. The edition-index dependency is resolved (consume #32's schema;
  off by default), so the residual risk is mainly live-API shape drift, covered by the pinned fixture.

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
risk to committed evidence, and keeps the contributor's contribution intact. A documented merge-into-scores path
for *new* runs can be noted for a later part without being built here.

## Open Questions

- **RESOLVED (architect, 2026-10-24) — passage-equivalence edition index.** Option (a) with
  tightening: equivalence is **OFF unless `--equivalence-index` is supplied** (records
  `not_evaluated`, never a silent negative); the index schema is **#32's, consumed verbatim**; #21
  does not build the producer and does not depend on #32's branch; `jev.py` drops the
  `cross_translation` import entirely. (See Scope decision + Constraints.)
- **RESOLVED (architect, 2026-10-24) — floating `jev-latest` build.** The resolved build is grader
  identity; a build-mismatched resume **fails fast**; no mixed-build files.
- **Important — committed surface.** Is the sidecar `judgments.jsonl` the only committed artifact for
  Part 2 (viewer/paper consumption being other parts), or should a merge-into-`scores.jsonl` path for
  *new* runs also ship now? *Recommendation: sidecar only; document the merge path.*
- **RESOLVED (architect, 2026-10-24) — validation scope.** The **tutorial run only**; its judgment
  sidecar is new evidence beside the run, never modifying `scores.jsonl`/`summary.json`; the live
  pass's pre-flight cost estimate is shown to the architect before it runs.
- **Important — agreement threshold.** The agreement report needs a rule to turn a probability into
  agree/disagree. *Resolved in this spec:* fixed `p ≥ 0.5` **and** a raw per-outcome-class
  distribution, so the disagreement set is stable and threshold-robust.
- **Nice-to-know — defaults.** Concurrency and retry defaults for the pass (the contributor uses 4 workers,
  2 retries).

## Test Scenarios

- **Happy path (live, tutorial run):** judge the committed tutorial answers to a sidecar; every cell
  gets a typed verdict + probabilities + resolved build + usage; summary reports counts and total
  cost.
- **Resumability + stale-safety:** re-running over a partially-written output makes **zero** new API
  calls for already-judged cells; a cell whose answer content changed (`answer_digest` differs), or a
  `rubric_id`/question-set-digest mismatch, forces a re-judge or fails loud rather than reusing a stale
  verdict; interrupting mid-run leaves a valid, appendable file.
- **Build-roll:** resuming onto a sidecar whose recorded resolved build differs from the current call
  **fails fast** with an error naming both builds; a same-build resume proceeds. The resolved build
  appears in the sidecar manifest and in `score --evaluator` provenance.
- **Equivalence off by default:** without `--equivalence-index`, no equivalence question is asked and
  each row records `equivalence: "not_evaluated"`.
- **Equivalence with index:** given a hand-written fixture index (+manifest) in #32's schema whose
  `corpus_hash` matches the run manifest, the equivalence question is asked and the row records the
  `kind` plus the index `digest`; a **missing manifest or a `corpus_hash` mismatch fails fast**.
- **Task scope:** `verify_source`/`cite_passage` cells are skipped and reported as skipped; only
  `retrieve_quote`/`complete_unit` are judged.
- **Fail-fast on shape:** a response missing `answers`, or with a mistyped `noul`/`choice`, or an
  unknown `kind`, raises and the cell stays pending — no fallback value is written. The fixture for this
  is the committed, redacted live response.
- **Fail-fast on credentials:** missing `OPENROUTER_API_KEY` raises before any call.
- **Budget guard:** a pre-flight estimate prints before calls; `--limit` stops the pass at N cells so a
  run cannot silently exceed the cap.
- **Restricted-target guard:** a cell whose source maps to a `restricted` target is refused/skipped
  before its reference text is sent to the API.
- **Non-default seam:** `score` with no `--evaluator` is byte-identical to before; `score --evaluator
  jev` fails fast; default headline unaffected.
- **Agreement analysis:** containment judge vs `contains_reference`, and judge refusal probability vs
  the `refused` outcome, are tabulated at `p ≥ 0.5` and as a raw distribution; disagreement cells
  enumerated for manual review.
- **Evidence integrity:** committed `scores.jsonl`/`answers.jsonl` for the tutorial and original runs
  are byte-identical after the work; the audit gate passes.
- **No-op on a fully-judged file:** `summarize` over a complete output reports the right counts and
  resolved build(s) without calls.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Edition index (equivalence) unavailable — producer is in concurrent #32 | Medium | Low | Equivalence OFF by default (records `not_evaluated`); consume #32's schema verbatim; tests use a hand-written fixture; no dependency on #32's branch |
| Accidentally re-scoring / overwriting committed run evidence | Low | High | Always write to a fresh/sidecar path; add an evidence byte-identity check to the review checklist; audit gate in test.sh |
| Jev API shape drift vs the contributor's code (wrong model id, field changes) | Medium | Medium | Model id and full shape **live-verified** for this spec; fail-fast on any unexpected field; committed redacted live fixture pins the parser; record resolved build per cell |
| `jev-latest` build rolls between passes → mixed builds in one file/report | Medium | Medium | Resolved build is grader identity (row + manifest + provenance); build-mismatched resume **fails fast**, no mixed-build files; allow pinning a build |
| Stale verdict reused after an answer/prompt change | Medium | Medium | Resume key binds `answer_digest` + `rubric_id` + question-set digest; mismatch re-judges or fails loud |
| Live spend exceeds budget | Low | Medium | Pre-flight estimate + `--limit`; validation is the small tutorial run; per-call cost ≈ $3e-5; hard $8 cap with stop+ping; resumability avoids re-spend |
| Restricted reference text transmitted to the judge API | Low | High | Guard refuses/skips `restricted`-target cells before any send (separate from the commit-time audit gate); latent today (no committed restricted source) |
| Key or restricted text leaking into a public commit | Low | High | Key from env only (never a file); audit gate; judge evidence committed only over public-domain tutorial content |
| Jev verdict mistaken for the headline | Low | High | Non-inline/verdict-less/`default=False` registration; refusal stays an outcome; documented as diagnostic tier in the recipe |

## References

- Issue #21 — Jev-based evaluator: typed judge verdicts for containment, refusal, and passage
  equivalence.
- PR #30 (a contributor) — "Type of Theological Errors, temperature, FaCCT improvements etc"; source
  of `jev.py`, the `judge` CLI, the closed-question prompts, and `test_jev.py`. This spec is **Part 2
  of 3**.
- Spec 15 — the evaluator/grader seam and the refusal-as-outcome decision (`graders.py`, `score.py`,
  `outcomes.py`).
- Spec 26 — original-language default and `verify_source` hardening (context for the question pool).
- `CODE_WALKTHROUGH.md` — "Adding an evaluator (a named grader)" recipe (to be extended for the paid
  separate-pass evaluator).
- Architect brief, 2026-10-23, and decisions of 2026-10-24 — baked decisions captured in Constraints
  (model id `jev-latest` + resolved-build-as-identity; scope option (a) with `--equivalence-index`
  off-by-default; #32's index schema consumed verbatim; pre-flight estimate shown before the live pass).
- Issue #32 (concurrent sibling) — produces the `--equivalence-index` file this spec consumes.
- Live verification: OpenRouter `POST /api/alpha/decisions`, model `jev-latest` →
  `typesafe/jev-1.14-20261014`; `v1/models` catalog entry for `typesafe/jev-router` (empty endpoints).
