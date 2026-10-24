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

#### Retrieving the carried-over code

`jev.py` is **not** in this worktree — it lives only in PR #30 (fork
`JonathanKarr33:faact_mprovements_karr`). Obtain it via `gh pr diff 30` (or
`gh api repos/<owner>/<repo>/contents/pipelines/sacredbench/jev.py?ref=faact_mprovements_karr`). Its
only non-stdlib imports are `sacredbench.cross_translation` (`EditionIndex`, `cite_key`) and
`sacredbench.score.normalize`; nothing from PR #30's `providers.py`/`config.py`/`collect.py` is needed.
The commit carrying it uses `git commit --author="Jonathan Karr <jka83321@gmail.com>"`.

#### Files to Create / Modify

- Create `pipelines/sacredbench/jev.py` — carried from PR #30 with corrections: `JEV_MODEL =
  "jev-latest"`; **drop the `cross_translation` import entirely** (no stub module) — `cite_key` is
  **re-implemented locally** in `jev.py`, and `alternate_wordings` takes an optional in-memory index
  that Phase 3 supplies; import only `score.normalize` from the package; the judgment state omits the
  equivalence question when no index is present and the row records `equivalence: "not_evaluated"`;
  the resume key binds `answer_digest` (sha256 of the exact answer string) + `rubric_id` +
  `question_set_digest`; a sidecar **header/manifest** records the resolved build + `rubric_id` +
  question-set digest (Phase 3 adds `index_digest` to this identity); resuming onto a sidecar whose
  recorded resolved build differs **raises `JevError` naming both builds**; `interpret()` fail-fast
  kept and pinned to a committed fixture; **missing `OPENROUTER_API_KEY` raises before any call**;
  task-type filter (judge only `retrieve_quote`/`complete_unit`, report the rest as skipped);
  restricted-target guard (refuse/skip a cell whose `(work, version, language)` maps to a `restricted`
  catalogue target before any send); a pre-flight estimate (pending × typical per-cell cost) printed
  before calls; a `--limit` on cells per invocation; spend summed from the API-returned `usage.cost`.
  Keep Karr's `summarize(path)` and surface it (below).
- Modify `pipelines/sacredbench/cli.py` — add the `judge` command (answers path → sidecar out;
  `--limit`, `--model`, `--concurrency`, pre-flight estimate) and a `judge-summary` surface (or
  `judge --summarize`) that reports counts + resolved build(s) over a finished sidecar **without
  calls**. **`--equivalence-index` is NOT added in this phase** (Phase 3 adds it); Phase 1 does not
  accept the flag.
- Create `pipelines/tests/test_jev.py` — carried/adapted from PR #30.
- Create `pipelines/tests/testdata/jev_decision_sample.json` — the **committed, redacted live
  Decisions response** the fail-fast tests run against (the live-verified shape from the spec).
- Modify `pipelines/README.md` / `TUTORIAL.md` — the `judge` step (carried from PR #30, model id
  corrected). Defer `--equivalence-index` docs to Phase 3.

#### Deliverables

- [ ] `sacredbench judge <answers.jsonl> --out <sidecar>` judges text-retrieval cells against
      `jev-latest`, writing the spec's sidecar schema with a header manifest.
- [ ] Resolved build recorded per row and in the manifest; build-mismatched resume fails fast.
- [ ] Resume is stale-safe (answer_digest + rubric_id + question_set_digest); failed cells stay pending.
- [ ] Task-type filter; restricted-target guard; pre-flight estimate + `--limit`; spend from `usage.cost`.
- [ ] `equivalence: "not_evaluated"` recorded when no index is supplied; no `cross_translation` import.
- [ ] `summarize` surface reports counts + resolved build(s) over a finished sidecar with zero calls.
- [ ] A single-cell **live smoke** (≈ $0.00003) at the end of the phase confirms model id / auth /
      shape end-to-end before later phases build on the HTTP/parse code (per the hot-tier "mocking the
      provider seam hides live-only failures" lesson); it is one cell, far under the cap, and the
      verified shape is already pinned by the fixture.
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

- Unit (no network): fake decider returns a canned response; assert sidecar row schema + field names
  (`refusal_p`, `matches_requested_p`, `kind`/`not_evaluated`), manifest, resume skip (zero decider
  calls on re-run), build-mismatch fail-fast, stale-answer re-judge, task-type skip, restricted-target
  skip, pre-flight/`--limit` behaviour, and `summarize` no-op counts.
- **Concurrency / manifest identity:** the first response establishes the sidecar's resolved-build
  identity; later responses (including simultaneously in-flight ones) must match it before being
  written — a differing in-flight build is rejected, not appended.
- **Credential fail-fast:** missing `OPENROUTER_API_KEY` raises before any call.
- **Negative on the pipeline:** assert `score` and `collect` never import/invoke the judge (no judge
  call path reachable from those commands).
- Fail-fast: feed malformed responses (missing `answers`, mistyped `noul`/`choice`, unknown `kind`) →
  `JevError`, cell stays pending. Fixture = the committed redacted live response.
- Manual: the single-cell live smoke above (one real call).

### Phase 2: Grader seam registration and evaluator provenance

**Dependencies**: Phase 1

#### Objective

Make the evaluator a first-class, discoverable member of the Spec 15 seam and make a run's summary
state which judge build produced any verdicts — without letting `jev` run inline or changing the
default headline. Value: the CLI, the grader registry, the recipe, and the summary provenance are
mutually consistent.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/graders.py` — register the `jev` descriptor with metric-key names
  that **match the sidecar contract**: `Grader("jev", ("matches_requested_p", "refusal_p", "kind"),
  None, default=False, inline=False)` (verdict-less, non-inline, non-default). Update the module
  docstring (the "We do not build it here" note) to say it is now registered. `resolve_evaluators`
  already fails fast when it is selected inline.
- Modify `pipelines/tests/test_graders.py` — **required**: its existing fixture does
  `GRADERS["jev"] = …` then `del GRADERS["jev"]` in a `finally`, which would **delete the now-real
  registration** for the rest of the session (order-dependent failures). Fix the fixture to not delete
  a real entry; assert `jev` is registered and non-inline.
- Modify `pipelines/sacredbench/score.py` — add an **explicit opt-in** `score --judgments <path>`
  option (NOT implicit co-location discovery, which would make a re-score of the tutorial run stop
  reproducing its committed `summary.json` after Phase 4). When given, validate the sidecar manifest
  (resolved build + `rubric_id` + question-set digest must bind to this run's answers/question set),
  and record the **resolved judge build** in a **new sibling summary key** (e.g.
  `summary["judge"] = {"model_resolved": …, "rubric_id": …}`). Keep `summary["evaluators"]` a
  `list[str]` (consumed by `LeaderboardTable.tsx:48`, pinned by `test_score.py:256`) and put **no
  cost/usage field** in the summary (`test_tutorial_run.py:66` asserts `"cost"` absent). Without
  `--judgments`, `score` is unchanged.
- Modify `CODE_WALKTHROUGH.md` — extend "Adding an evaluator" with the paid/separate-pass Jev
  evaluator: the sidecar, the non-inline registration, the explicit `--judgments` provenance opt-in,
  and that it never joins the default.

#### Deliverables

- [ ] `jev` registered non-inline/verdict-less/`default=False` with sidecar-consistent metric-key
      names; absent from `DEFAULT_EVALUATORS`; `graders.py` docstring updated.
- [ ] `test_graders.py` fixture fixed so it no longer deletes the real `jev` entry.
- [ ] `score --evaluator jev` fails fast; a default `score` run (no `--judgments`) is unchanged.
- [ ] `score --judgments <path>` records the resolved judge build in a new sibling summary key;
      `evaluators` stays a name list; no `cost` field enters the summary.
- [ ] `CODE_WALKTHROUGH.md` recipe documents the Jev evaluator.

#### Acceptance Criteria

- [ ] Spec success criteria for the non-default seam and resolved-build-in-provenance hold.
- [ ] A default `score` over an existing answers file produces a **byte-identical `scores.jsonl`**; the
      summary matches the baseline **after excluding the always-fresh `generated_at` timestamp** (byte
      identity is not achievable on the summary because `score.py` stamps `generated_at` each run).
- [ ] The full test suite passes **in file-order** (the `test_graders.py` fix prevents an
      order-dependent failure); `.codev/checks/test.sh` passes.

#### Test Plan

- Unit: `resolve_evaluators(["jev"])` raises; `DEFAULT_EVALUATORS` unchanged; `jev` is registered and
  stays registered after `test_graders.py` runs; a default score snapshot matches a pre-captured
  baseline (`scores.jsonl` byte-identical; summary equal modulo `generated_at`); with `--judgments`
  pointing at a fixture sidecar, the summary carries the build in the new key and no `cost` field.
- Manual: `score --evaluator jev` → clear fail-fast message; `score --judgments <fixture>` → provenance
  present.

### Phase 3: Equivalence-index consumer

**Dependencies**: Phase 1

#### Objective

Turn on the passage-equivalence question when (and only when) a `--equivalence-index` is supplied,
consuming #32's file schema verbatim. Value: equivalence becomes functional given an index, with no
dependency on #32's branch and no silent negatives when the index is absent.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/cli.py` — **add** `--equivalence-index <path>` to the `judge` command
  (not present before this phase), plus an explicit `--questions <path>` (or `--run-manifest <path>`)
  so the run's `corpus_hash` has a **defined source**: answer rows carry `question_set_digest` but
  **not** `corpus_hash` — `corpus_hash` lives only in `runs/<id>/questions.jsonl.manifest.json`, so it
  must be located by an explicit option, never by co-location guessing.
- Modify `pipelines/sacredbench/jev.py` — load the index (JSONL rows `{work, citation, language,
  wordings:[{version,text}]}` + `<path>.manifest.json`); **fail fast** if the index manifest is
  missing or its `corpus_hash` differs from the run manifest's `corpus_hash` (located via the explicit
  option above); build the in-memory lookup keyed on `(work, citation, language)` (single-wording rows
  are already omitted by the producer); when present, add the `kind` (equivalence) question to the
  rubric and populate `indexed_other_wordings`; record the index `digest` on each row that used it and
  in the **sidecar manifest**. **Add the index `digest` to the resume identity**: resuming onto a
  sidecar whose recorded `index_digest` differs from the current index fails fast (prevents a
  mixed-index sidecar even when `corpus_hash` is unchanged). When no index is supplied, behaviour is
  exactly Phase 1 (`not_evaluated`).
- Create `pipelines/tests/testdata/equivalence_index.sample.jsonl` + `.manifest.json` — a hand-written
  fixture in #32's schema (no dependency on #32's branch).
- Modify `pipelines/tests/test_jev.py` — equivalence-path tests.

#### Deliverables

- [ ] `--equivalence-index` + explicit `--questions`/run-manifest option added to `judge`.
- [ ] Index consumed in #32's verbatim schema; equivalence question asked only when supplied.
- [ ] Missing index manifest, or `corpus_hash` mismatch with the located run manifest → fail fast.
- [ ] Index `digest` recorded per row + in the sidecar manifest; a changed index (differing
      `index_digest`) on resume fails fast, even if `corpus_hash` is unchanged.
- [ ] Hand-written fixture tests pass; no import of or dependency on #32 code/branch.

#### Acceptance Criteria

- [ ] Spec success criteria for the equivalence index (off-by-default, fail-fast manifest/corpus_hash,
      index digest per row) hold.
- [ ] `.codev/checks/test.sh` passes.

#### Test Plan

- Unit: with fixture index + matching manifest → equivalence question asked, `other_indexed_wording`
  can fire, row + manifest carry index digest. Missing index manifest → fail fast. `corpus_hash`
  mismatch (located via `--questions`) → fail fast. **Mixed-index resume:** a second index with the
  same `corpus_hash` but different `index_digest` → fail fast (no silent mixed-index sidecar). No index
  → `not_evaluated` (Phase 1 behaviour unchanged).

### Phase 4: Validation on the committed tutorial run

**Dependencies**: Phase 1, Phase 2

#### Objective

Prove the evaluator on the committed tutorial run and quantify its agreement with the deterministic
tiers, as new evidence beside the run — the step that earns trust. Value: a recorded, auditable
agreement report + manual disagreement review the paper can cite.

#### Files to Create / Modify

- Create `runs/tutorial-2026-10-11/judgments.jsonl` (+ its header manifest) — **new evidence**; the
  committed `answers.jsonl`/`scores.jsonl`/`summary.json` are **not** modified.
- Create `pipelines/sacredbench/jev_agreement.py` (small, **testable** module, not a one-off script) —
  joins answers × scores × judgments and computes: containment judge vs `contains_reference`; refusal
  probability vs the `refused` outcome; the `p ≥ 0.5` classification **and** the raw per-outcome-class
  probability distribution; the exhaustively enumerated disagreement set. Renders to
  `runs/tutorial-2026-10-11/jev_agreement.{json,md}`.
- Create `runs/tutorial-2026-10-11/jev_agreement.{json,md}` — the report artifact (new evidence).
- Create `pipelines/tests/test_jev_agreement.py` — fixture-based tests for the join and the report.
- Modify `codev/reviews/21-jev-based-evaluator-typed-judg.md` — the manual review of every disagreement
  cell and the lessons.

#### Deliverables

- [ ] Pre-flight cost estimate for the live pass **shown to the architect before it runs** (ping +
      wait). Expected figure: the tutorial run is 100 questions × 4 models = **400 `retrieve_quote`
      cells ≈ $0.011** at the verified ~$2.7e-5/call — well under the $8 cap.
- [ ] Live judge pass over the tutorial answers → committed sidecar + manifest (public-domain content
      only; audit passes; spend within the cap; no index ⇒ equivalence `not_evaluated`).
- [ ] Agreement report (threshold + raw distribution) + enumerated disagreements, via the tested
      `jev_agreement` module.
- [ ] Every disagreement cell manually reviewed and written up in the review.
- [ ] Committed `scores.jsonl`/`answers.jsonl`/`summary.json` for tutorial + original runs unchanged
      (verified — see caveat).

#### Acceptance Criteria

- [ ] Spec success criteria for validation, evidence integrity, and the audit/restricted gates hold.
- [ ] `git diff` shows **no change** to committed `scores.jsonl`/`answers.jsonl`/`summary.json` (the
      validation writes only new sidecar + report files; it never re-runs `score`/`collect`, so even
      the `generated_at` caveat does not arise — the committed summaries are not rewritten at all).
- [ ] `.codev/checks/test.sh` (incl. `audit.py`) passes on the whole run.

#### Test Plan

- Unit (`test_jev_agreement.py`, fixture-based, no network): complete join across answers/scores/
  judgments; the `p ≥ 0.5` boundary; raw per-outcome-class distribution; exhaustive disagreement
  enumeration (no cell dropped).
- Live (budgeted): the tutorial run only; resumable, so a re-run spends nothing. Confirm the ~$0.011
  pre-flight estimate and show it to the architect first.
- Manual: inspect each disagreement cell; classify (orthographic near-miss / edition / refusal-boundary
  / genuine miss); record in the review.
- Integrity: `git diff` the committed evidence before/after; run the audit gate.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Live Jev shape drift vs the carried fixture | Low | Medium | Fixture is the live-verified response; `interpret()` fails fast on any unexpected field; resolved build recorded per row |
| `jev-latest` build rolls mid-validation | Medium | Medium | Build-mismatched resume fails fast; build in manifest + provenance; pin a build if needed |
| Accidentally mutating committed run evidence | Low | High | Sidecar-only; byte-compare in Phase 4 acceptance; audit gate |
| Live spend over budget | Low | Medium | Pre-flight estimate shown to architect; `--limit`; tutorial run only; resumable |
| Restricted reference text sent to the API | Low | High | Restricted-target guard in Phase 1 (pre-send), independent of the commit-time audit |
| #32 index schema turns out to differ from the pinned spec | Low | Medium | Consume the architect-pinned schema verbatim; fixture-driven tests; fail fast on manifest/corpus_hash so a wrong index cannot be used silently |
| Implicit sidecar discovery silently changes a re-score of committed evidence | Low | High | Provenance is an **explicit `score --judgments <path>`** opt-in; default `score` never reads adjacent sidecars |
| Mixed-index sidecar when `corpus_hash` is reused but wordings change | Low | Medium | `index_digest` is part of the sidecar manifest identity and the resume check fails fast on mismatch |
| `test_graders.py` fixture deletes the real `jev` registration | Medium | Medium | Phase 2 fixes the fixture; suite must pass in file-order |
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
