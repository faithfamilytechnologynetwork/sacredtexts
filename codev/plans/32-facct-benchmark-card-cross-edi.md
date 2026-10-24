# Plan: FAccT benchmark card + cross-edition reading over the current scoring contract

**Specification**: [codev/specs/32-facct-benchmark-card-cross-edi.md](../specs/32-facct-benchmark-card-cross-edi.md)

## Executive Summary

The spec's recommended approach (Approach 1) is to carry over Jonathan Karr's PR #30 `facct.py` and
`cross_translation.py`, strip the October-11 scoring contract out of them, and re-point the card at
the contract on `main` (outcomes from `scores.jsonl`, containment headline, 17-text pool). The
architect fixed three decisions on top of that: the edition index becomes a **shared, standalone
producer** with a frozen JSONL/manifest export (because issue #21 consumes the same data); the viewer
card view is **out of scope**; and **every number in the card is derived at build time** from
`scores.jsonl` / `summary.json`, never typed.

The work decomposes along those seams, foundation-first:

1. **EditionIndex module + export** — the shared producer the counterfactual and #21 both need, with
   its frozen schema and the restricted-filter guard. Nothing downstream can be built without it.
2. **Card data (`facct.json`)** — census + outcomes + edition counterfactual, all counting logic and
   the fail-fast validation, emitting the machine-readable card. This phase owns every number.
3. **Card prose (`facct.md`)** — the one editable prose block and the human-readable card rendered
   *from* the Phase-2 data, with the anti-drift guarantee (no typed numbers).
4. **Generate & commit the card** for `runs/original-2026-10-21`, gated by `audit.py`.

Phases 1–3 are pure code+tests under `pipelines/`; Phase 4 produces the committed run artifact the
issue asks for. Phases that carry Jonathan's code over are committed with his authorship
(`git commit --author="Jonathan Karr <jka83321@gmail.com>"`). No live API calls in any phase.

**Scope decision** (spec Nice-to-know): the three-edition agreement table (how often KJV/ASV/WEB
agree after normalization) is **excluded** from this PR. The counterfactual is the headline; the
agreement table is supporting colour that would add a second reading track against Waleed's
one-linear-recipe docs bar. It can be a follow-up if the paper wants it.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "Shared EditionIndex module and export CLI"},
    {"id": "phase_2", "title": "FAccT card data: census, outcomes, edition counterfactual (facct.json)"},
    {"id": "phase_3", "title": "FAccT markdown card with single prose block (facct.md)"},
    {"id": "phase_4", "title": "Generate and commit the card for runs/original-2026-10-21"}
  ]
}
```

## Phase Breakdown

### Phase 1: Shared EditionIndex module and export CLI

**Dependencies**: None

#### Objective

Lift Jonathan's citation/edition-index machinery out of `cross_translation.py` into a standalone,
reusable module that both the card (in-process) and issue #21 (via a file) consume. Produce the
frozen JSONL + manifest export and the `license != restricted` guard. This is the foundation every
later phase builds on.

#### Files to Create / Modify

- Create `pipelines/sacredbench/edition_index.py` — the shared module: a `Passage`/`EditionIndex`
  data model, `cite_key` (Bible-style `Book chapter:verse` parsing), `index_documents`, and a loader
  that reads **`texts/raw/**` via `convert.convert_target(payload_paths, target)`** — the same path
  `audit.restricted_text_fingerprints` uses — **not** `texts/standardized/` (gitignored, absent in
  CI). The loader is restricted-filtered via `catalogue.select_targets(include_restricted=False)`.
  Add `export_rows(index)` producing the frozen row schema and `write_export(index, out_path)` writing
  JSONL + `<out>.manifest.json`. Carried over and reworked from PR #30 `cross_translation.py`.
- Modify `pipelines/sacredbench/cli.py` — add `@app.command("edition-index")` with `--out <path>`
  (and `--raw-root`), wiring `EditionIndexError` into the top-level error handler.
- Create `pipelines/tests/test_edition_index.py` — schema, ordering, omission, restricted-exclusion,
  and determinism tests.
- Modify `pipelines/README.md` — one line documenting the `edition-index` subcommand.

#### Deliverables

- [ ] `edition_index.py` exposes the in-process `EditionIndex` (used by the card) and the file export.
- [ ] Export row schema is exactly `{"work": str, "citation": str, "language": str, "wordings": [{"version": str, "text": str}, …]}` — one row per `(work, citation, language)`, `wordings` sorted by version, same-canonical-language editions only, `license != restricted` filtered, **single-wording rows omitted**. Rows are emitted in a deterministic order (sorted by `(work, citation, language)`).
- [ ] Manifest `<out>.manifest.json` is exactly `{"corpus_hash": str, "row_count": int, "digest": str, "excluded_restricted": [<version ids>]}`, with these pinned definitions (frozen for #21):
  - `corpus_hash` = `generate.corpus_hash(docs)` (existing sha256 `hexdigest()[:16]`) over all indexed same-canonical-language docs (before the single-wording omission).
  - `digest` = sha256 `hexdigest()[:16]` of the written JSONL file bytes (the repo's `question_set_digest` convention).
  - `excluded_restricted` = the sorted, de-duplicated version ids of targets dropped by the `license != restricted` filter.
- [ ] `sacredbench edition-index --out <path>` writes both files, mirroring the `questions.jsonl` convention (JSONL + sibling `.manifest.json`).
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] A restricted target (e.g. NABRE — `work: The Bible`, `canonical_language: en`) present locally never appears in any exported row and is named in `excluded_restricted`.
- [ ] Only editions whose `language == canonical_language` are indexed; a citation with one indexed wording produces no row.
- [ ] `wordings` are sorted by `version`; `row_count` equals the emitted rows; `digest` is the recomputed sha256[:16] of the file bytes.
- [ ] The export is byte-stable across two runs on identical inputs, and a change to any indexed wording changes `corpus_hash` and `digest` (determinism + sensitivity).
- [ ] `uv --project pipelines run pytest` passes; the audit check in `.codev/checks/test.sh` still passes.

#### Test Plan

- Unit: build an index from a small fixture of two public-domain Bible editions sharing a citation and
  one text with a single edition; assert one two-wording row, no single-wording row, versions sorted,
  rows in `(work, citation, language)` order.
- Compliance: inject a `restricted`-licensed target into the fixture catalogue; assert it is absent
  from rows and present (sorted, de-duped) in `excluded_restricted`.
- Manifest: assert the four manifest keys; that `corpus_hash` is `generate.corpus_hash` over the
  indexed docs; that `digest` is the file's recomputed sha256[:16]; that identical inputs produce
  byte-identical files and a mutated wording moves both hashes.

### Phase 2: FAccT card data: census, outcomes, edition counterfactual (facct.json)

**Dependencies**: Phase 1

#### Objective

Build the card's machine-readable data: the run census, the three outcomes read straight from
`scores.jsonl` / `summary.json`, and the Bible `retrieve_quote` edition counterfactual computed via
the Phase-1 module. This phase owns **every number** and the fail-fast validation; it writes
`facct.json`. No second refusal definition, no `fabrication` label.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/score.py` — promote the `contains_reference` containment predicate to
  a public function (the current private `_bounded_equal`, word-bounded over the script-aware
  `normalize`), so the counterfactual reuses the **exact** contract predicate rather than a second
  `in` check. (`normalize`'s Arabic/Hebrew-marks-before-punctuation order is load-bearing — reuse
  verbatim, never reimplement.)
- Create `pipelines/sacredbench/facct.py` (reworked from PR #30) — a `build_facct(run_dir)` that:
  loads `scores.jsonl`, `summary.json`, `answers.jsonl`, and `questions.jsonl.manifest.json`; joins
  score↔answer rows on `(question_id, model_id)`; assembles the census (tradition / language /
  document_type / license from the catalogue targets + manifest, source languages with zero questions,
  excluded texts with manifest reasons); reads outcomes from `metrics.outcome`; computes the
  counterfactual (incorrect Bible `retrieve_quote` cells whose answer contains some *other* indexed
  edition's wording, using the promoted `score` containment predicate + `score.normalize`), tagging
  `other_edition` and reporting numerator + denominator per model; and validates the evidence, raising
  `FacctError` (no partial write) on any inconsistency. Writes `facct.json` to a fixed path under the
  run dir.
- Modify `pipelines/sacredbench/cli.py` — add `@app.command("facct")` taking a `run_dir` and writing
  `facct.json` into it by default; wire `FacctError`.
- Create `pipelines/tests/test_facct.py` — outcome-fidelity, counterfactual, exclusion, fail-fast,
  forbidden-vocabulary, and no-private-matcher tests over a small fixture run.

#### Deliverables

- [ ] `facct.json` carries: census (17 selected texts by tradition/language/document_type/license; zero-question source languages; 2 excluded texts with reasons), per-model/per-task outcome counts taken verbatim from `scores.jsonl`, and the counterfactual block (numerator, denominator, tagged cells) scoped to Bible `retrieve_quote`.
- [ ] Outcomes come only from `metrics.outcome`; no refusal is recomputed; no `fabrication` label and no second refusal regex exists anywhere in the module.
- [ ] The counterfactual's containment is the promoted `score` predicate + `score.normalize`, reused verbatim; `facct.py` defines no containment/normalization of its own (a test asserts this).
- [ ] The counterfactual excludes `complete_unit` (partial gold) and never matches a non-Bible citation to a Bible edition; the requested edition does not count as `other_edition`.
- [ ] Fail-fast: a missing file, a non-joining row, an unresolved catalogue target, or a `scores.jsonl`↔`summary.json` count disagreement raises `FacctError` and writes no `facct.json`.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] For each model×task, `facct.json`'s correct/incorrect/refused equal the counts derived from the fixture `scores.jsonl` (and match `summary.json`); a deliberate fixture mismatch fails a test.
- [ ] A Bible `retrieve_quote` cell containing the WEB wording of a KJV-requested citation, scored `incorrect`, is tagged `other_edition` and counted in the numerator; a genuinely wrong answer is not; a `complete_unit` cell is never tagged nor in the denominator.
- [ ] Qur'an `2:255`, a hadith number, and a Talmud daf:line citation are never matched to a Bible edition.
- [ ] Generating the card does not modify `scores.jsonl` / `answers.jsonl` / `summary.json` and makes no network call.
- [ ] `uv --project pipelines run pytest` passes.

#### Test Plan

- Unit/integration: a fixture run dir (handful of cells across the four tasks and ≥2 Bibles) with a
  known `scores.jsonl`; assert census contents, outcome counts, and the counterfactual numerator/
  denominator and tags.
- Edge: non-Bible citations excluded; `complete_unit` excluded; requested-edition-only answer not
  tagged.
- Error: each fail-fast trigger raises `FacctError` and leaves no `facct.json` behind.
- Regression: assert the generated `facct.json` contains no `fabrication` and that the module defines
  no refusal matcher of its own (imports outcomes only via the committed `scores.jsonl`).
- Contract-reuse: assert the counterfactual's match agrees with `score`'s `contains_reference` on the
  same boundary/normalization cases the scorer is tested on (word boundaries, script-aware folding),
  and that `facct.py` references the promoted `score` predicate rather than its own.

### Phase 3: FAccT markdown card with single prose block (facct.md)

**Dependencies**: Phase 2

#### Objective

Render the human-readable card `facct.md` from the Phase-2 data, with all card prose (the claim this
run supports, what would make it fail, what the card will not conclude, community/scholar review not
attached) in **one editable constants block** so Jonathan can revise wording without touching counting
logic — and with **every number interpolated from the data, never typed**, so the card cannot drift.
At the end of this phase the single command `sacredbench facct <run_dir>` writes **both**
`facct.json` and `facct.md` into the run dir by default (markdown is not an opt-in flag).

#### Files to Create / Modify

- Modify `pipelines/sacredbench/facct.py` — add a single clearly-marked prose constants block and a
  `report_markdown(report)` that renders `facct.md` purely from the `build_facct` data structure.
- Modify `pipelines/sacredbench/cli.py` — the `facct` command writes **both** `facct.json` and
  `facct.md` into `<run_dir>` by default (fixed names). Any `--json`/`--md` override is validated to
  resolve **within** `<run_dir>`; both artifacts are rendered and validated in memory **before** either
  is written, so a failure leaves neither file created or modified.
- Modify `pipelines/tests/test_facct.py` — add the drift-guard, prose-structure, output-path-safety,
  and both-or-neither tests.
- Modify `pipelines/README.md` — one line: `facct <run_dir>` writes `facct.{json,md}` beside the run.

#### Deliverables

- [ ] `sacredbench facct <run_dir>` writes both `facct.json` and `facct.md` into the run dir by default;
  an override path outside the run dir is rejected.
- [ ] `facct.md` presents the census, the three outcomes with accuracy beside coverage, and the
  edition counterfactual (numerator + denominator + the Bible-`retrieve_quote`-only scope note),
  under the four prose sections, following Waleed's docs bar (one linear read, non-engineer readable,
  no asides). It embeds only citations and derived numbers — **no verse/passage bodies**.
- [ ] All prose lives in one constants block; no analysis/counting logic is interleaved with it.
- [ ] Every headline number in `facct.md` is interpolated from the `build_facct` data (which is
  derived from `scores.jsonl` / `summary.json`); no figure is a string literal.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] A test asserts each headline figure rendered in `facct.md` equals the corresponding value in the
  fixture `summary.json`; editing the fixture `summary.json` changes the rendered card and fails any
  stale expectation (proving nothing is typed).
- [ ] The word "fabrication" does not appear in `facct.md`; the three outcomes and the `other_edition`
  tag are the only answer classifications.
- [ ] A failure during rendering (e.g. a validation error) leaves neither `facct.json` nor `facct.md`
  written or partially updated; an override path outside the run dir raises before any write.
- [ ] `uv --project pipelines run pytest` passes.

#### Test Plan

- Unit: render `facct.md` from a known report; assert the four prose sections are present and the
  numbers equal the data.
- Drift guard: mutate a count in the fixture `summary.json`, rebuild, assert the rendered number moves
  with it.
- Output safety: an override path escaping `<run_dir>` is rejected; a forced render failure leaves
  neither file (both-or-neither).
- Vocabulary: assert `facct.md` contains no `fabrication` and no second refusal phrasing.

### Phase 4: Generate and commit the card for runs/original-2026-10-21

**Dependencies**: Phase 2, Phase 3

#### Objective

Produce the actual deliverable the issue names: run the finished `facct` command over the committed
`runs/original-2026-10-21/` and commit `facct.json` + `facct.md` beside it, verified copyright-clean.

#### Files to Create / Modify

- Modify `pipelines/sacredbench/audit.py` — extend the scanned suffix set (currently `.json` /
  `.jsonl` only, so `.md` is skipped entirely) so committed `.md` artifacts are **content-scanned**
  for restricted text. The card is now within the copyright gate, not merely beside it.
- Modify `pipelines/tests/test_audit.py` — add a test proving restricted wording injected into a
  Markdown file fails the audit (so the `.md` coverage is real, not nominal).
- Modify `pipelines/tests/test_original_run_regression.py` — add a drift-guard assertion tying the
  **committed** `runs/original-2026-10-21/facct.json` to the committed `summary.json`, so a future
  sanctioned rebaseline cannot silently leave the card stale.
- Create `runs/original-2026-10-21/facct.json` and `runs/original-2026-10-21/facct.md` — generated, not
  hand-written.
- Modify `runs/original-2026-10-21/README.md` — one line noting the card and how it was produced.

#### Deliverables

- [ ] `audit.py` content-scans `.md`; `test_audit.py` proves injected restricted wording in Markdown
  fails.
- [ ] `facct.{json,md}` generated by `sacredbench facct runs/original-2026-10-21` committed beside the
  run.
- [ ] A committed-card drift guard in `test_original_run_regression.py` ties `facct.json` to
  `summary.json`.
- [ ] Tests for this phase (audit gate + drift guard).

#### Acceptance Criteria

- [ ] With the `.md` extension, `audit.py` (via `.codev/checks/test.sh`) reports no restricted-origin
  or restricted-content artifact for **both** `facct.json` and `facct.md`.
- [ ] No `generate` / `collect` / `score` was run against the committed run; the sha256 of
  `scores.jsonl`, `answers.jsonl`, and `summary.json` is **byte-identical before and after** card
  generation (captured and compared, not inferred from `git status`).
- [ ] The edition counterfactual on the real run reports a numerator and denominator (≈32 incorrect
  Bible `retrieve_quote` cells across the panel) consistent with the committed scores.

#### Test Plan

- Compliance: run the extended `audit.py` over the committed card; assert clean; the new `.md`
  injection test fails on planted restricted text.
- Integrity: record sha256 of the three evidence files before generating the card and assert they are
  unchanged after; the only added paths under the run dir are `facct.{json,md}` and the README line.
- Drift guard: the regression test recomputes the card's headline figures from the committed
  `summary.json` and asserts the committed `facct.json` matches.
- Manual: read `facct.md` end-to-end against the docs bar before the PR; loop Jonathan in on the
  wording at PR time.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A vestige of the Oct-11 contract (`fabrication`, the `_REFUSAL` regex) survives the rework of `facct.py` | Medium | High | Rewrite `facct.py` from the data model up rather than patching; regression test asserts forbidden strings absent and outcomes come from `scores.jsonl` |
| The frozen EditionIndex schema is later changed and breaks #21's consumer | Low | Medium | Schema frozen in the spec; an export-schema test pins row + manifest shape so a change is caught |
| A restricted edition reaches the exported index file on a machine holding its payload | Low | High | Index from `select_targets(include_restricted=False)`; test the exclusion with a restricted target present; `audit.py` gate |
| A typed-in figure drifts from the run (as Spec 26 docstrings once did) | Medium | Medium | Render every number from the data; drift-guard test ties `facct.md` figures to `summary.json` |
| Partial card written before an inconsistency is detected | Low | Medium | Validate all evidence before writing; raise `FacctError` with no partial file |
| The counterfactual uses a second, divergent containment rule (the exact failure the spec forbids for refusals) | Medium | High | Promote `score`'s `contains_reference` predicate to public and reuse it + `score.normalize` verbatim; test the card defines no matcher of its own and agrees with the scorer's boundary/normalization cases |
| `audit.py` skips `.md`, so the committed `facct.md` is never copyright-scanned | Medium | High | Extend the audit suffix set to `.md`; add a test that injected restricted Markdown fails; keep the card to citations + numbers (no passage bodies) |
| Carried-over code loses Jonathan's authorship | Medium | Low | Commit Phases 1–3 with `git commit --author="Jonathan Karr <jka83321@gmail.com>"` |

## Documentation Updates

- `pipelines/README.md` — add the `edition-index` and `facct` subcommands (one line each).
- `pipelines/sacredbench/audit.py` docstring — note that `.md` artifacts are now content-scanned.
- `runs/original-2026-10-21/README.md` — note the generated card.
- `codev/reviews/32-facct-benchmark-card-cross-edi.md` — written in the review phase (lessons:
  the shared-producer schema freeze, the anti-drift derived-numbers discipline).
- No change needed to the HOT arch/lessons tiers unless the review surfaces a cross-cutting lesson.
