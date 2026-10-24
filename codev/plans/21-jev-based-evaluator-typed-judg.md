# Plan: Jev-based evaluator — typed judge verdicts for containment and passage equivalence

**Specification**: [codev/specs/21-jev-based-evaluator-typed-judg.md](../specs/21-jev-based-evaluator-typed-judg.md)

## Executive Summary

Implements the spec's **Approach 1** (sidecar judgments file + non-inline grader registration): carry
over Jonathan Karr's `jev.py` from PR #30 — the live-verified Decisions-API judge — with the
corrections and hardening the spec requires, write typed verdicts to a resumable **sidecar**
(`judgments.jsonl` + a header manifest) beside a run, register a non-inline `jev` grader so the Spec 15
seam / CLI / recipe stay coherent, and validate on the committed tutorial run. The deterministic
headline in `score.py` is never touched; refusal stays an OUTCOME in `outcomes.py`; the judge's
refusal probability is diagnostic only.

Four phases, each a single atomic commit inside **one PR** ("Part 2 of 3 of #30", closes #21):

1. **Jev judge pass + CLI** — the core judge over an answers file (containment + refusal-diagnostic;
   equivalence records `not_evaluated` with no index), resumable/stale-safe, resolved-build-as-identity
   with fail-fast on a build-mismatched resume, task-type filter, restricted-target guard, pre-flight
   cost estimate + `--limit`, spend from the API's `usage.cost`. The commit that carries Karr's code
   preserves **his authorship** (`git commit --author="Jonathan Karr <jka83321@gmail.com>"`).
2. **Grader seam registration + evaluator provenance + recipe** — register the `jev` descriptor in
   `graders.py`; surface the resolved judge build in the evaluator provenance a summary emits; extend
   the `CODE_WALKTHROUGH.md` "add an evaluator" recipe.
3. **Equivalence-index consumer** — `--equivalence-index` consuming #32's schema verbatim (manifest
   `corpus_hash` fail-fast, index `digest` per row), asking the equivalence question only when an index
   is supplied; tested against a hand-written fixture, no dependency on #32's branch.
4. **Validation on the committed tutorial run** — show the architect the pre-flight estimate, run the
   live judge pass to a sidecar beside the tutorial run (new evidence, never mutating
   `scores.jsonl`/`summary.json`), produce the agreement report (containment vs `contains_reference`,
   refusal probability vs the `refused` outcome; `p ≥ 0.5` + raw distribution), manually review every
   disagreement cell, confirm the audit gate passes and committed evidence is byte-identical, and write
   it up in the review.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "Jev judge pass and CLI"},
    {"id": "phase_2", "title": "Grader seam registration and evaluator provenance"},
    {"id": "phase_3", "title": "Equivalence-index consumer"},
    {"id": "phase_4", "title": "Validation on the committed tutorial run"}
  ]
}
```

## Phase Breakdown

### Phase 1: Jev judge pass and CLI

**Dependencies**: None

#### Objective

Deliver a paid, explicitly-invoked, resumable judge over an answers file that records containment and a
refusal-probability diagnostic per text-retrieval cell to a sidecar, with every reproducibility and
safety guard from the spec. Value: a run's near-misses can be judged end-to-end against the live Jev
Decisions API, independent of any edition index.

#### Files to Create / Modify

- Create `pipelines/sacredbench/jev.py` — carried from PR #30 with corrections: `JEV_MODEL =
  "jev-latest"`; **no `cross_translation` import** (drop it entirely; `alternate_wordings` becomes a
  no-op stub taking an optional in-memory index that Phase 3 supplies — no module import); the
  judgment state omits the equivalence question when no index is present and the row records
  `equivalence: "not_evaluated"`; the resume key binds `answer_digest` (sha256 of the exact answer
  string) + `rubric_id` + `question_set_digest`; a sidecar **header/manifest** records the resolved
  build + `rubric_id` + question-set digest; resuming onto a sidecar whose recorded resolved build
  differs **raises `JevError` naming both builds**; `interpret()` fail-fast kept and pinned to a
  committed fixture; task-type filter (judge only `retrieve_quote`/`complete_unit`, report the rest as
  skipped); restricted-target guard (refuse/skip a cell whose `(work, version, language)` maps to a
  `restricted` catalogue target before any send); a pre-flight estimate (pending × typical per-cell
  cost) printed before calls; a `--limit` on cells per invocation; spend summed from the API-returned
  `usage.cost`.
- Modify `pipelines/sacredbench/cli.py` — add the `judge` command (answers path → sidecar out;
  `--limit`, `--model`, `--concurrency`, pre-flight estimate; `--equivalence-index` accepted but
  wired in Phase 3).
- Create `pipelines/tests/test_jev.py` — carried/adapted from PR #30.
- Create `pipelines/sacredbench/testdata/jev_decision_sample.json` (or tests fixture dir) — the
  **committed, redacted live Decisions response** the fail-fast tests run against.
- Modify `pipelines/README.md` / `TUTORIAL.md` — the `judge` step (carried from PR #30, model id
  corrected).

#### Deliverables

- [ ] `sacredbench judge <answers.jsonl> --out <sidecar>` judges text-retrieval cells against
      `jev-latest`, writing the spec's sidecar schema with a header manifest.
- [ ] Resolved build recorded per row and in the manifest; build-mismatched resume fails fast.
- [ ] Resume is stale-safe (answer_digest + rubric_id + question_set_digest); failed cells stay pending.
- [ ] Task-type filter; restricted-target guard; pre-flight estimate + `--limit`; spend from `usage.cost`.
- [ ] `equivalence: "not_evaluated"` recorded when no index is supplied; no `cross_translation` import.
- [ ] Tests (including the committed redacted live fixture for `interpret()` fail-fast) pass.

#### Acceptance Criteria

- [ ] Spec success criteria for the judge pass, resume/stale-safety, resolved-build identity, task
      scope, budget guard, and restricted-target guard hold.
- [ ] `grep -r cross_translation pipelines/sacredbench/jev.py` is empty.
- [ ] `.codev/checks/test.sh` (pipelines → uv pytest) passes; no live call in unit tests (judge is
      injected a fake decider, per Karr's `decide=` seam).
- [ ] The commit carrying `jev.py`/`test_jev.py` uses `git commit --author="Jonathan Karr
      <jka83321@gmail.com>"`.

#### Test Plan

- Unit (no network): fake decider returns a canned response; assert sidecar row schema, manifest,
  resume skip (zero decider calls on re-run), build-mismatch fail-fast, stale-answer re-judge,
  task-type skip, restricted-target skip, pre-flight/`--limit` behaviour.
- Fail-fast: feed malformed responses (missing `answers`, mistyped `noul`/`choice`, unknown `kind`) →
  `JevError`, cell stays pending. Fixture = the committed redacted live response.
- Manual: none live in this phase (the live pass is Phase 4).

### Phase 2: Grader seam registration and evaluator provenance

**Dependencies**: Phase 1

#### Objective

Make the evaluator a first-class, discoverable member of the Spec 15 seam and make a run's summary
state which judge build produced any verdicts — without letting `jev` run inline or changing the
default headline. Value: the CLI, the grader registry, the recipe, and the summary provenance are
mutually consistent.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/graders.py` — uncomment/register the `jev` descriptor: `Grader("jev",
  ("jev_matches_requested", "jev_refusal_p"), None, default=False, inline=False)` (verdict-less,
  non-inline, non-default). Confirm `resolve_evaluators` already fails fast when it is selected inline
  (it does); add a test.
- Modify `pipelines/sacredbench/score.py` — when a judgments sidecar + manifest exist for the run,
  record the **resolved judge build** in the summary's evaluator provenance (`summary["evaluators"]`
  neighbourhood), so a summary reports the judge build. No change to the deterministic headline, the
  default evaluator set, or committed-run behaviour.
- Modify `CODE_WALKTHROUGH.md` — extend "Adding an evaluator" with the paid/separate-pass Jev
  evaluator: the sidecar, the non-inline registration, and that it never joins the default.

#### Deliverables

- [ ] `jev` registered non-inline/verdict-less/`default=False`; absent from `DEFAULT_EVALUATORS`.
- [ ] `score --evaluator jev` fails fast; a default `score` run is byte-identical to before.
- [ ] A summary records the resolved judge build in evaluator provenance when a sidecar is present.
- [ ] `CODE_WALKTHROUGH.md` recipe documents the Jev evaluator.

#### Acceptance Criteria

- [ ] Spec success criteria for the non-default seam and resolved-build-in-provenance hold.
- [ ] A default `score` over an existing answers file produces byte-identical `scores.jsonl`/summary vs
      before this spec (guard against regression).
- [ ] `.codev/checks/test.sh` passes.

#### Test Plan

- Unit: `resolve_evaluators(["jev"])` raises; `DEFAULT_EVALUATORS` unchanged; a default score snapshot
  matches a pre-captured baseline; with a sidecar manifest present, the summary carries the build.
- Manual: run `score --evaluator jev` → clear fail-fast message.

### Phase 3: Equivalence-index consumer

**Dependencies**: Phase 1

#### Objective

Turn on the passage-equivalence question when (and only when) a `--equivalence-index` is supplied,
consuming #32's file schema verbatim. Value: equivalence becomes functional given an index, with no
dependency on #32's branch and no silent negatives when the index is absent.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/jev.py` — load `--equivalence-index` (JSONL rows `{work, citation,
  language, wordings:[{version,text}]}` + `<path>.manifest.json`); **fail fast** if the manifest is
  missing or its `corpus_hash` differs from the run manifest's `corpus_hash`; build the in-memory
  lookup keyed on `(work, citation, language)`; when present, add the `kind` (equivalence) question to
  the rubric and populate `indexed_other_wordings`; record the index `digest` on each row that used it.
  When absent, behaviour is exactly Phase 1 (`not_evaluated`).
- Modify `pipelines/sacredbench/cli.py` — wire `--equivalence-index` into the `judge` command.
- Create `pipelines/tests/testdata/equivalence_index.sample.jsonl` + `.manifest.json` — a hand-written
  fixture in #32's schema.
- Modify `pipelines/tests/test_jev.py` — equivalence-path tests.

#### Deliverables

- [ ] `--equivalence-index` consumed in #32's verbatim schema; single-wording rows absent (producer
      omits them) handled; equivalence question asked only when supplied.
- [ ] Missing manifest or `corpus_hash` mismatch with the run manifest → fail fast.
- [ ] Index `digest` recorded per row that used the index.
- [ ] Hand-written fixture tests pass; no import of or dependency on #32 code/branch.

#### Acceptance Criteria

- [ ] Spec success criteria for the equivalence index (off-by-default, fail-fast manifest/corpus_hash,
      index digest per row) hold.
- [ ] `.codev/checks/test.sh` passes.

#### Test Plan

- Unit: with fixture index + matching manifest → equivalence question asked, `other_indexed_wording`
  can fire, row carries index digest. Missing manifest → fail fast. `corpus_hash` mismatch → fail fast.
  No index → `not_evaluated` (Phase 1 behaviour unchanged).

### Phase 4: Validation on the committed tutorial run

**Dependencies**: Phase 1, Phase 2

#### Objective

Prove the evaluator on the committed tutorial run and quantify its agreement with the deterministic
tiers, as new evidence beside the run — the step that earns trust. Value: a recorded, auditable
agreement report + manual disagreement review the paper can cite.

#### Files to Create / Modify

- Create `runs/tutorial-2026-10-11/judgments.jsonl` (+ its header manifest) — **new evidence**; the
  committed `answers.jsonl`/`scores.jsonl`/`summary.json` are **not** modified.
- Create an agreement report artifact (e.g. `runs/tutorial-2026-10-11/jev_agreement.md` + `.json`) —
  containment judge vs `contains_reference`; refusal probability vs the `refused` outcome; `p ≥ 0.5`
  classification **and** the raw per-outcome-class probability distribution; the enumerated
  disagreement set. (A small, optional `agreement`/report helper may live in `jev.py` or a tiny module;
  keep it simple.)
- Modify `codev/reviews/21-jev-based-evaluator-typed-judg.md` — the manual review of every disagreement
  cell and the lessons.

#### Deliverables

- [ ] Pre-flight cost estimate for the live pass **shown to the architect before it runs** (ping + wait).
- [ ] Live judge pass over the tutorial answers → committed sidecar + manifest (public-domain content
      only; audit passes; spend within the $8 cap).
- [ ] Agreement report (threshold + raw distribution) + enumerated disagreements.
- [ ] Every disagreement cell manually reviewed and written up in the review.
- [ ] Committed `scores.jsonl`/`summary.json`/`answers.jsonl` for tutorial + original runs
      **byte-identical** (verified).

#### Acceptance Criteria

- [ ] Spec success criteria for validation, evidence integrity, and the audit/restricted gates hold.
- [ ] `git diff --stat` shows no change to committed `scores.jsonl`/`summary.json`/`answers.jsonl`.
- [ ] `.codev/checks/test.sh` (incl. `audit.py`) passes on the whole run.

#### Test Plan

- Live (budgeted): the tutorial run only; resumable, so a re-run spends nothing. Confirm pre-flight
  estimate ≪ $8 and show it to the architect first.
- Manual: inspect each disagreement cell; classify (orthographic near-miss / edition / refusal-boundary
  / genuine miss); record in the review.
- Integrity: byte-compare committed evidence before/after; run the audit gate.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Live Jev shape drift vs the carried fixture | Low | Medium | Fixture is the live-verified response; `interpret()` fails fast on any unexpected field; resolved build recorded per row |
| `jev-latest` build rolls mid-validation | Medium | Medium | Build-mismatched resume fails fast; build in manifest + provenance; pin a build if needed |
| Accidentally mutating committed run evidence | Low | High | Sidecar-only; byte-compare in Phase 4 acceptance; audit gate |
| Live spend over budget | Low | Medium | Pre-flight estimate shown to architect; `--limit`; tutorial run only; resumable |
| Restricted reference text sent to the API | Low | High | Restricted-target guard in Phase 1 (pre-send), independent of the commit-time audit |
| #32 index schema turns out to differ from the pinned spec | Low | Medium | Consume the architect-pinned schema verbatim; fixture-driven tests; fail fast on manifest/corpus_hash so a wrong index cannot be used silently |
| Karr authorship lost on carried code | Low | Low | Phase 1 commit uses `git commit --author="Jonathan Karr <jka83321@gmail.com>"` |

## Documentation Updates

- `CODE_WALKTHROUGH.md` — extend the "Adding an evaluator" recipe with the paid/separate-pass Jev
  evaluator (Phase 2).
- `pipelines/README.md` / `TUTORIAL.md` — the `judge` step and `--equivalence-index` usage (Phases 1, 3;
  carried from PR #30 with the model id corrected).
- `codev/reviews/21-*.md` — validation findings, agreement numbers, disagreement review, and lessons
  (Phase 4). Surface any arch/lessons-worthy facts to the architect for the hot-tier docs.
- No arch-critical/lessons-critical edit is made directly by this plan (MAINTAIN/arch-doc step owns
  those); flag candidates in the review.
