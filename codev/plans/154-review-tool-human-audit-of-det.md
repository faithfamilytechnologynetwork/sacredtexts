# Plan: Review tool — human labels for checking the matcher

**Specification**: [codev/specs/154-review-tool-human-audit-of-det.md](../specs/154-review-tool-human-audit-of-det.md) (approved 2026-11-10)

## Executive Summary

This plan implements the spec's **Approach 1**: a committed sample, the ported multibench
API, and client-side labels. There are two Python pieces and two TypeScript pieces, and
they meet at two committed file formats.

- **Python (`pipelines/sacredbench`).**
  - `review-sample` draws the even stratified sample from a run (outcome × task × text,
    k = 10 by default) into a self-contained JSON file, committed under `review/samples/`.
  - `review-compare` scores matcher versions against gold-set files.
- **TypeScript.**
  - A new `apps/api` is multibench's API ported nearly verbatim. Its review drafts are
    re-keyed from tradition to sample. It also serves the active sample and the built
    viewer from one origin, so one Hono service plus Postgres is the whole deployment.
  - `apps/viewer` gains the ported review store and API client, and `/review` pages that
    reuse the explorer's cell rendering. The gold-set file is built client-side.
- **Seams.**
  - The **sample file** goes from Python to the API to the UI.
  - The **gold-set JSONL** goes from the UI to Python. A shared fixture in `fixtures/`
    pins it on both sides.

Hosting is **not approved**. Every phase is verified locally, and nothing is provisioned.

The phases go Python first, because that settles both file formats. Then come the API
port, the one-service wiring, the viewer library layer, and finally the pages and the
local end-to-end walk. Each phase is one commit on the single PR branch.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "Review sample builder and committed FAccT sample"},
    {"id": "phase_2", "title": "Gold-set format and version-comparison CLI"},
    {"id": "phase_3", "title": "API service with accounts and sample-keyed drafts"},
    {"id": "phase_4", "title": "One-service hosting: sample endpoint and built-UI serving"},
    {"id": "phase_5", "title": "Viewer review store, API client, sample and gold-set libraries"},
    {"id": "phase_6", "title": "Viewer review pages"},
    {"id": "phase_7", "title": "Local end-to-end verification and documentation"}
  ]
}
```

## Phase Breakdown

### Phase 1: Review sample builder and committed FAccT sample

**Dependencies**: None

#### Objective

Produce the seeded, even, stratified sample that everything else reads, and commit the
FAccT one.

#### Files to Create / Modify

- `pipelines/sacredbench/review_sample.py` (new)
- `pipelines/sacredbench/cli.py`: add the `review-sample` command (Typer)
- `pipelines/tests/test_review_sample.py` (new)
- `review/samples/facct-2026-11-03-k10.json` (new, generated)
- `review/README.md` (new): what `review/` holds and how each file is made
- `.codev/checks/test.sh`: route `review/**` to the pipelines lane

#### Deliverables

- [ ] **Command.** `uv --project pipelines run python -m sacredbench review-sample
      --run-dir runs/facct-2026-11-03 --seed <s> --per-stratum 10 --out review/samples/<id>.json`.
- [ ] **What the builder reads.**
  - A cell is a row in a `scores.jsonl` joined to its `answers.jsonl` row on
    `(model_id, question_id)`. Every scored row must have its answer row, or the builder
    fails loudly.
  - Only rows with `metrics.outcome` are eligible.
  - Run files are opened read-only.
- [ ] **Texts.** A cell's **text** is the edition folder between `<model>/base/` and
      `population/`. In the FAccT run that gives 13: `islam/native`, `islam/english`,
      `christianity/native/masoretic`, `encyclicals/english`, …. The label shown to people
      is derived from the cells' `source.work` and `source.version`. A folder holding one
      (work, version) is labelled "work — version". A folder holding several works is
      labelled with the tradition and the work count. No special cases are needed: the
      encyclicals group and the Masoretic `he` + `arc` merge both fall out of the folder
      rule.
- [ ] **Grader path** comes from the recorded metrics:
  - retrieve_quote / complete_unit: `exact` if `exact`; else `normalized` if
    `normalized`; else `contained` if `contains_reference`; else `none`;
  - cite_passage: `citation`;
  - verify_source: `verdict`.
- [ ] **Draw.**
  - **Strata** are (outcome, task, text).
  - **Order** within a stratum is by `sha256(seed + "\x00" + cell_id)`, so it doesn't
    depend on file-read order.
  - **Allocation:** take `min(N, k)` from each stratum.
  - **Sample order:** the drawn cells sorted by `sha256(seed + "\x00order\x00" + cell_id)`.
  - **Cell id:** `<run-name>:<model_id>:<question_id>`.
- [ ] **Sample file** (JSON, `"format": 1`, sorted keys, stable 2-space indent, UTF-8,
      trailing newline). It contains:
  - `sample_id`, `source_run`, `seed` and `per_stratum`;
  - `texts`: id, label and drawn count, sorted by id;
  - `strata`: outcome, task, text, `population`, `drawn`, sorted;
  - `cells` in sample order. Each cell has: `cell_id`, `run`, `model_id`,
    `question_id`, `scores_path` (repo-relative), `task`, `text`, `prompt`, `expected`
    (the question's expected dict, verbatim), `answer`, `source` (verbatim), `metrics`
    (verbatim), `outcome` and `grader_path`.
- [ ] **`load_sample(path)`** validates a sample file (`format`, the required keys, cell
      fields) and fails loudly on anything else. Phase 2 and the fixture tests reuse it.
- [ ] **Commit the FAccT sample.** It's generated with k = 10 and a recorded seed:
      about 1,423 cells, 151 strata, NRSV included, about 2–3.5 MB.
- [ ] **Copyright, per the owner's ruling (2026-11-10).** Counsel's position is fair
      use, so NRSV is included. The sample is **not** added to the copyright audit
      scan, and no restricted-origin machinery is added. The existing gate (`audit.py`
      over `runs/`) stays green and untouched. The exception is recorded in
      `review/README.md`, and in arch docs in the review phase, so a future contributor
      doesn't read the unaudited sample as a violation. For the record, the sample's
      NRSV cells cite at most the run's 31 distinct verses, which is inside the existing
      500-verse allowance anyway. No test enforces that.
- [ ] **Dispatcher.** `.codev/checks/test.sh` maps a `review/` change to the pipelines
      lane, and a comment explains why: the committed sample is pinned by a pipelines test.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] Same run + seed + k gives a byte-identical file, and a different seed gives a
      different draw.
- [ ] Every stratum has exactly `min(N, k)` cells, and the recorded `population` equals a
      direct count.
- [ ] The committed FAccT sample regenerates byte-for-byte from `runs/` (pin test).
- [ ] `git diff --stat -- runs/` is empty.
- [ ] `bash .codev/checks/test.sh` passes, including the audit.

#### Test Plan

**Unit tests** run on a tiny synthetic run in `tmp_path`: two models, two texts, mixed
outcomes, one stratum smaller than k, and one unscored row. They cover:
- determinism and seed sensitivity;
- `min(N, k)` per stratum, including the small stratum;
- the unscored row is excluded;
- a scored row with no answer row fails loudly;
- the grader-path mapping for each task;
- text id and label, including a multi-work folder;
- the file is byte-stable.

**Pin test:** rebuild the committed FAccT sample from `runs/` and compare bytes.

### Phase 2: Gold-set format and version-comparison CLI

**Dependencies**: Phase 1 (cell ids, `scores_path`, grader-path rule)

#### Objective

Fix the gold-set row format, and deliver the core tool: score any matcher version
against human labels and list disagreements and movers.

#### Files to Create / Modify

- `pipelines/sacredbench/review_compare.py` (new): load and validate gold rows,
  resolve versions, compute the comparison, format the report
- `pipelines/sacredbench/cli.py`: add the `review-compare` command
- `pipelines/tests/test_review_compare.py` (new)
- `fixtures/review_sample.json` (new): a small hand-built sample, about 8 cells across
  all four tasks and two texts (one RTL)
- `fixtures/review_gold_set.jsonl` (new): the gold set for the labels on that sample.
  Together these two files are the shared contract for Phase 5.
- `review/README.md`: document the gold-set format and the compare command

#### Deliverables

- [ ] **Gold-set row** (JSONL, one object per labelled cell, rows sorted by `cell_id`):
      `format` (1), `sample_id`, `cell_id`, `run`, `model_id`, `question_id`,
      `scores_path`, `task`, `text`, `prompt`, `expected`, `answer`, `source`, and three
      groups:
  - `shown`: `outcome`, `metrics` and `grader_path`, i.e. what the reviewer saw;
  - `label`: `outcome`, which is `correct` | `incorrect` | `refused` | `cant_judge`,
    plus `defect` (bool) and `notes` (string);
  - `rubric_version`, `reviewer_id` (account UUID) and `labelled_at` (ISO 8601).

  The loader rejects an unknown `format`, a missing field, an unknown label outcome, or a
  duplicate `(reviewer_id, cell_id)` across the given files (fail fast).
- [ ] **Versions**, given as repeatable `--version` options:
  - `committed`: reads each cell's `scores_path` now and takes the row for
    `(model_id, question_id)`. A missing file or row fails loudly.
  - `current`: `score.score_answer(task, answer, expected, language=source.language,
    prompt=prompt, work=source.work)` with the default graders. No network.
  - `<dir>`: a **run directory** with the same layout as `runs/<run>/`, for example a
    copy re-scored by `sacredbench score` on another branch.
    - Lookup is run-aware. The row's `scores_path` has its `runs/<run>/` prefix
      replaced by `<dir>/`, and the row for `(model_id, question_id)` is taken from that
      file.
    - Each of these fails loudly: a missing file or row; a duplicate
      `(model_id, question_id)` inside any scores file that is read; or gold rows from
      more than one run combined with a directory version (ambiguous).
- [ ] **Per version.**
  - It derives the grader path from that version's own metrics (the Phase 1 rule).
  - It reports agreement as `agree / n (pct)` overall, per task, per text and per grader
    path. Here `n` excludes `cant_judge` and defect-flagged rows, which are counted on
    their own line.
  - Each per-text line also shows the count per prompt arm (`source.condition`), so a
    text whose draw landed mostly in one arm is visible.
  - It lists the disagreements: cell id, task, text, human outcome and version outcome.
- [ ] **Movers.** With two or more versions, the first version is the baseline. For each
      other version it lists the cells whose outcome changed against the baseline, each
      marked `fixed` (now agrees with the human), `broken` (no longer agrees) or
      `neither`, with a count of each.
- [ ] **Output.** Plain text to stdout by default, and `--json <path>` writes the same
      numbers as JSON. Both are deterministic.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] On the fixture gold set, compare against a hand-built `committed` stand-in and a
      `current` re-score. It produces the hand-computed counts per task, text and path,
      lists the disagreements, and lists the movers. At least one mover is `fixed` and one
      is `broken`.
- [ ] `fixtures/review_sample.json` passes `load_sample`. Every row in
      `fixtures/review_gold_set.jsonl` refers to a cell in it, and its prompt, expected,
      answer, source and shown fields equal that cell's.
- [ ] `cant_judge` and defect rows are excluded from `n` and counted separately.
- [ ] A duplicate label, an unknown format, or a missing committed row each exits
      non-zero with a clear message.
- [ ] A directory version resolves through the run-prefix swap. A directory version
      over gold rows from two runs, and a scores file with a duplicate
      `(model_id, question_id)`, each fail loudly. Both cases have tests.
- [ ] `current` makes no network calls (the test runs offline; no provider module is
      imported).

#### Test Plan

**Unit tests** use the fixture plus small synthetic `scores.jsonl` files in `tmp_path`.
- The fixture includes a retrieve_quote cell where `committed` says `correct` by
  containment and the human says `incorrect`.
- It also includes a cite cell, and a cell where a synthetic "version B" scores file
  flips an outcome toward the human label, so `fixed` is exercised.
- `current` is exercised on real `score_answer` with fixture rows whose outcomes are
  known.

**Smoke test:** run the CLI once on a gold set made from the first 20 committed sample
cells with labels equal to `shown.outcome`. The expected result is 100% agreement for
`committed` and no movers.

### Phase 3: API service with accounts and sample-keyed drafts

**Dependencies**: None (it can be built in parallel with Phases 1–2; it's ordered after
them only so the formats are settled)

#### Objective

Port multibench's `apps/api` wholesale (with its fixes), re-keyed from tradition to
sample, and wire it into the test gate.

#### Files to Create / Modify

New `apps/api/`, ported from `multibench/apps/api` at `main`:

- **Config:** `package.json` (`@sacredtexts/api`, `engines.node` `24.x` to match the
  viewer, the same scripts), `pnpm-lock.yaml`, `tsconfig.json`, `vitest.config.ts`,
  `drizzle.config.ts`, `.env.example`, `.gitignore`.
- **Source:**
  - `src/app.ts`, `src/server.ts`, `src/db.ts`, `src/cors.ts`, `src/migrate.ts`,
    `src/testing/pglite.ts`;
  - `src/auth/*`, `src/middleware/auth.ts`;
  - `src/routes/{auth,account,health,review}.ts`;
  - `src/schema/{index,reviewers,sessions,reviews,submissions}.ts`.
- **Tests:** `src/cors.test.ts`, `src/auth/*.test.ts`, `src/routes/*.test.ts`.
- **Migration:** `drizzle/0000_review_store.sql` plus `drizzle/meta/*`, generated by
  `drizzle-kit generate`, never hand-written.
- **Docs:** `README.md` covering the stack, scripts, configuration, endpoints, auth
  model, migrations and local run.

Also modified:

- `.codev/checks/test.sh`: registry line `apps/api) echo "pnpm -C apps/api test"`.

#### Deliverables

- [ ] **Auth, sessions, CSRF, CORS, account delete, health and the migrator are ported
      unchanged.** That includes the fixes: the exact MIME essence check, the password
      length cap, race-safe signup, CSRF in the response body and `/csrf`, the cross-site
      cookie-clear attributes, and the pg pool error handler.
- [ ] **Review routes re-keyed.** `/api/review/:sampleId` (GET, PUT, DELETE),
      `/api/review` (list), `/api/review/:sampleId/submit` and
      `/api/review/:sampleId/submissions`. The columns `reviews.tradition_id` and
      `submissions.tradition_id` become `sample_id`. Optimistic concurrency (version
      0 = insert, stale → 409 plus the current draft) and insert-only submissions are kept
      as-is.
- [ ] **What's removed:** the GitHub-issue publish column and its validation
      (`published_issue_url`). The spec doesn't need it.
- [ ] **Body cap, in bytes.** The draft and submit cap is raised from 512 KB to **8 MB**.
      It is sized from a maximal serialized draft: 1,500 labels, each with a
      1,000-character note of 4-byte UTF-8 characters, plus ids and metadata, comes to
      about 6.5 MB. The client enforces the 1,000-character note limit (Phase 5).
- [ ] **The schema is generated** with `pnpm exec drizzle-kit generate --name
      review_store`, and the SQL is reviewed in the PR. There is no `db:push` script.
- [ ] Tests for this phase: the ported suites, re-keyed.

#### Acceptance Criteria

- [ ] `pnpm -C apps/api test` passes on PGlite with no external database.
- [ ] `pnpm -C apps/api build` (`tsc --noEmit`) passes.
- [ ] `bash .codev/checks/test.sh` runs the `apps/api` lane when `apps/api` changes.
- [ ] Reviewer isolation is tested: B can't read or overwrite A's draft or submissions.
      Account delete cascades to sessions, drafts and submissions.

#### Test Plan

Port `auth.test.ts`, `review.test.ts`, `health.test.ts`, `cors.test.ts` and the
`auth/*.test.ts` unit tests, with tradition ids becoming sample ids. Add:
- a maximal multilingual draft (1,500 labels × 1,000-character Gurmukhi/Arabic notes) is
  accepted;
- a body over 8 MB gets 413;
- an assertion that `submissions` has no publish column;
- an explicit test that signup is refused while `REVIEW_INVITE_CODE` is unset
  (fail-closed), even with any code supplied.

### Phase 4: One-service hosting: sample endpoint and built-UI serving

**Dependencies**: Phase 1 (sample file format), Phase 3 (service)

#### Objective

Make one Hono service the whole deployment: `/api`, the active sample, and the built
viewer with history fallback, all on one origin. Ship the deploy config and the runbook,
but provision nothing.

#### Files to Create / Modify

- `apps/api/src/sample.ts` (new): load and validate the sample file once at startup
- `apps/api/src/routes/sample.ts` (new): `GET /api/sample`
- `apps/api/src/static.ts` (new): serve the built viewer. It ports the **in-repo** host
  `apps/viewer/server/index.mjs` (`serveStatic({root: DIST})` plus `notFound` →
  `index.html`, pinned by `apps/viewer/src/deploy.test.ts`). The only addition is that
  `/api/*` is excluded from the fallback.
- `apps/api/src/app.ts`, `apps/api/src/server.ts`: wire `SAMPLE_PATH` and `VIEWER_DIST`
- `apps/api/src/{sample,static}.test.ts` (new)
- `apps/api/railway.json` (new): config-as-code for the single service, not applied
- `apps/api/README.md`: topology, environment, local runbook, deploy runbook (gated)

#### Deliverables

- [ ] **`SAMPLE_PATH`** (required) points at a committed sample. At startup the service
      parses it and checks `format: 1` and the required keys. It fails fast (exit 1) on a
      missing or invalid file. `GET /api/sample` (authenticated) returns it. There is one
      active sample.
- [ ] **`VIEWER_DIST`** (optional) points at `apps/viewer/dist`.
  - When set, `GET` requests outside `/api/*` serve static files, and an unmatched path
    serves `index.html`.
  - An unmatched `/api/*` always returns a JSON 404, never `index.html`.
  - If `VIEWER_DIST` is set but its `index.html` is missing, the service fails fast.
  - When unset, the service is API-only (local dev with the Vite proxy).
- [ ] **The existing viewer host and config are left as they are, and documented.**
      `apps/viewer/server/index.mjs`, its `pnpm start`, its smoke test and
      `apps/viewer/railway.json` stay unchanged. They are the pre-existing static-only
      host. Whether any live service still uses that config is the owner's to say, so
      this project doesn't touch or delete it. The `apps/api` README states that the
      **review** deployment uses `apps/api/railway.json` and not the viewer's.
- [ ] **What the review origin shows.** It builds the viewer with `pnpm build`, not
      `build:pages`, so it ships no baked runs. The browsing pages (`/`, `/errors`,
      `/standings`) on that origin show their existing "no runs" empty state. That's
      expected for a review-only origin, and the README and runbook say so.
- [ ] **Railway config (not applied).** The service root is the repo root, and the config
      path is `apps/api/railway.json`.
  - Build: `pnpm -C apps/viewer install --frozen-lockfile && pnpm -C apps/viewer build &&
    pnpm -C apps/api install --frozen-lockfile`.
  - `preDeployCommand`: `pnpm -C apps/api migrate`.
  - Start: `pnpm -C apps/api start`.
  - Health check: `/api/health`.
- [ ] **Environment variables**, all named in the README and in `.env.example`:

  | Variable | Required? | Behaviour |
  |---|---|---|
  | `DATABASE_URL` | required | exit if unset |
  | `REVIEW_INVITE_CODE` | — | unset ⇒ signup closed (fail-closed) |
  | `SAMPLE_PATH` | required | exit if unset or invalid |
  | `VIEWER_DIST` | optional | — |
  | `PORT` | — | defaults to 8080 |
  | `ALLOWED_ORIGINS` | — | kept from the port; empty is correct same-origin |
- [ ] **Runbook** in the README:
  - **Local:** `createdb sacredtexts_review_dev`, export the variables above,
    `pnpm -C apps/api migrate`, `pnpm -C apps/viewer build`, then
    `pnpm -C apps/api start`, and open in Chrome. Chrome is used because the ported
    cookies are `Secure; SameSite=None`, which Chrome accepts on `http://localhost`.
  - **Hosted:** documented provisioning steps under a "requires explicit go-ahead —
    NOT approved" banner.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] `GET /api/sample` returns 401 when signed out and the sample when signed in.
- [ ] A bad `SAMPLE_PATH` fails startup.
- [ ] With a temp dist: `/` and `/review/cell/x` serve `index.html`, `/assets/a.js`
      serves the file, and `/api/nope` gets a JSON 404.
- [ ] `pnpm -C apps/api test` and `build` pass.

#### Test Plan

**Unit tests** for the sample loader: valid, missing file, wrong format, missing key.
**Route tests** via `app.request` with PGlite and a fixture sample. **Static tests** with
a temp dist directory.

**Manual check:** start locally against a scratch Postgres with the committed FAccT
sample and the built viewer, then `curl /api/health` and `/` → index.html.

### Phase 5: Viewer review store, API client, sample and gold-set libraries

**Dependencies**: Phase 2 (gold-set format and fixture), Phase 3 (API contract),
Phase 4 (`/api/sample`)

#### Objective

Port multibench's client store and API client (with every fix), re-keyed to samples, and
add the pure libraries the pages need: sample parsing, pass and progress, rubric, and the
gold-set builder.

#### Files to Create / Modify

- `apps/viewer/package.json` and lockfile: add `zod`, which the tolerant draft parser
  needs (the purge removed it)
- `apps/viewer/src/lib/reviewApi.ts` (new, port), plus `getSample()`. A response that
  isn't JSON (the static Pages host's `index.html`) is reported as "review service
  unavailable", not as signed out.
- `apps/viewer/src/lib/review.ts` (new, port of the async store).
  - `ReviewState.samples` is keyed by sample id. Each `SampleReview` is
    `{ texts: string[], labels: Record<cellId, CellLabel> }`.
  - `CellLabel` is `{ outcome, defect, notes, rubric_version, labelled_at }`, with the
    tolerant zod schema degrading field by field.
  - The pure updaters are `withTexts`, `withLabel` and `withoutSample`. `withLabel(s,
    sid, cellId, patch, now)` stamps `rubric_version = RUBRIC_VERSION` and
    `labelled_at = now` **only when** `outcome`, `defect` or `notes` actually changes.
    So each label keeps the rubric version and time of its last real edit, and an old
    label isn't relabelled with a newer rubric.
- `apps/viewer/src/lib/reviewSample.ts` (new): sample types and a strict parse (fail
  loudly on a bad format); `passCells(sample, texts)` (sample order filtered to the
  chosen texts); `progressByText`; `toQuestionResult(cell)` for rendering reuse
- `apps/viewer/src/lib/rubric.ts` (new): the spec's per-task rubric text, plus
  `RUBRIC_VERSION = "1"`
- `apps/viewer/src/lib/goldSet.ts` (new): build gold-set JSONL from the sample, the
  stored labels (including their own `rubric_version` and `labelled_at`) and the
  reviewer id. It reads **no clock**, so two downloads from unchanged state are
  byte-identical. Fixed key order, sorted by `cell_id`. Notes are capped at 1,000
  characters by the label control.
- Tests (new): `review.test.ts`, `reviewStore.test.ts`, `reviewApi.test.ts`,
  `reviewSample.test.ts` and `goldSet.test.ts`, which asserts parity with
  `fixtures/review_gold_set.jsonl`

#### Deliverables

- [ ] The store keeps multibench's public shape: `useReviewState`, `updateReviewState`,
      `useReviewStatus`, `initReview`, `loginReview`, `signupReview`, `logoutReview`,
      `ensureSampleLoaded`, `prefetchDrafts`, `flushReviewSaves` and `resetReviewStore`.
      The behaviour is ported: debounced saves, per-key serialized ops, last-write-wins
      then server-wins on 409 with a reconcile notice, retry timers, and flush on hide.
- [ ] Every multibench fix is carried over with a regression test:
  - an account switch or 401 wipes state;
  - a failed load never overwrites the saved draft;
  - a CSRF 403 refreshes and retries;
  - a prefetch skips samples that are already loaded (clobber race);
  - editing is gated until the load succeeds;
  - "start over" is persisted via DELETE;
  - an unreachable service fails visibly.
- [ ] Building the gold set from `fixtures/review_sample.json`, with the labels, reviewer
      id and `labelled_at` taken from `fixtures/review_gold_set.jsonl`, reproduces that
      file byte for byte.
- [ ] **Saves that can't succeed stop retrying.** A 413, or any 4xx that isn't 409,
      401 or a CSRF 403, is a **terminal** save failure. It isn't retried. It's shown
      visibly ("this change is too large to save" / the server's message), and the label
      stays in memory. multibench retries every failed save, which would loop forever on
      a permanent 413.
- [ ] **Client-side byte guard.** Before a PUT, the store measures the UTF-8 byte length
      of the serialized draft. If it's over the 8 MB cap, the store raises the same
      terminal error without sending.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] `pnpm -C apps/viewer test` passes, with all existing viewer tests unchanged and
      green.
- [ ] `pnpm -C apps/viewer check-types` passes.
- [ ] The gold-set parity test passes.
- [ ] Python's `review-compare` loader accepts the fixture, which Phase 2 already tests.

#### Test Plan

Port `reviewStore.test.ts` and `review.test.ts` with a fake fetch through
`setReviewFetch`, re-keyed to samples, keeping each fix's regression case. Add:
- `passCells` order and text filtering, including adding a text;
- progress counts;
- tolerant parse of corrupt drafts;
- a non-JSON 200 becomes "unavailable";
- gold-set determinism (two builds from the same state are byte-equal) and fixture
  parity;
- `withLabel` stamps `rubric_version` and `labelled_at` only on a real change, and a
  no-op edit keeps the old stamp;
- a 413 from the fake API is terminal: there is no retry timer, the error is visible and
  the label is kept;
- the byte guard stops an oversized draft without a request.

### Phase 6: Viewer review pages

**Dependencies**: Phase 5 (store and libraries)

#### Objective

Give the reviewer the UI: sign in, pick texts, label cells with the rubric beside them,
see progress, and download the gold set.

#### Files to Create / Modify

- `apps/viewer/src/components/QuestionCard.tsx` (new): one cell's rendering, extracted
  unchanged from `QuestionList`, which now maps over it. The prompt, expected and answer
  elements get `dir="auto"`, `lang` from `source.language`, and the `script-text` class.
- `apps/viewer/src/components/QuestionList.tsx`: use `QuestionCard`
- `apps/viewer/src/styles.css`: a `script-text` font stack. It is local and system fonts
  only, with no web-font download: `system-ui`, "Noto Sans", "Noto Naskh Arabic",
  "Geeza Pro", "Noto Sans Hebrew", "Arial Hebrew", "Noto Sans Gurmukhi",
  "Gurmukhi MN", "Noto Sans Devanagari", "Kohinoor Devanagari", and `sans-serif` last.
  Together these cover Arabic, Hebrew/Aramaic, Gurmukhi, Devanagari, Greek and
  romanized Pali on macOS, Windows and Linux with Noto installed.
- `apps/viewer/src/components/ReviewAuthGate.tsx` (new, port): the sign-in/sign-up form,
  `ReviewerBadge` and `ReviewSaveStatus` (which also shows the Phase 5 terminal error)
- `apps/viewer/src/components/ReviewLabelControl.tsx` (new, adapted from
  `ReviewCheckControl`): the four-way outcome choice, a defect checkbox, and notes with a
  1,000-character limit and counter
- `apps/viewer/src/components/ReviewProgress.tsx` (new, port): labelled / in pass, per
  text and overall
- `apps/viewer/src/routes/ReviewPage.tsx` (new): `/review`
- `apps/viewer/src/routes/ReviewCellPage.tsx` (new): `/review/cell/$cellId`
- `apps/viewer/src/lib/reviewLinks.ts` (new): `cellHref(cellId)` and `cellIdFromParam`.
  A cell id contains `:`, so it is URL-encoded when building links and decoded when
  read. One helper is used everywhere.
- `apps/viewer/src/router.tsx`, `apps/viewer/src/routes/RootLayout.tsx`: the routes and a
  "Review" nav link
- `apps/viewer/vite.config.ts`: a dev-only proxy from `/api` to `http://localhost:8080`
  (overridable with `API_ORIGIN`)
- Tests (new): `src/routes/ReviewPage.test.tsx`, `src/routes/ReviewCellPage.test.tsx`,
  `src/lib/reviewLinks.test.ts`. `QuestionList.test.tsx` stays green unchanged.

#### Deliverables

- [ ] **`/review`.**
  - It's behind the auth gate.
  - It loads the sample, and shows "review service unavailable" when there's no API.
  - It shows a text picker listing the sample's texts with their cell counts. The choice
    persists in the draft. With nothing chosen, it prompts the reviewer to choose.
  - It shows per-text and overall progress, and the pass list, each item linking to its
    cell with its label state.
  - It has a "Download gold set" button that saves `gold-<sample_id>.jsonl`. The name
    uses the sample id, not a cell id or a clock.
- [ ] **`/review/cell/$cellId`.**
  - It shows the `QuestionCard` (prompt, expected, answer), the matcher's verdict badge,
    its submetrics and grader path, the text label and citation, and the model id.
  - It shows the task's rubric with its version.
  - It has `ReviewLabelControl`, previous/next within the pass, and the save status.
  - Editing is disabled until the draft load succeeds (the ported gate).
  - An unknown or out-of-sample cell id shows a not-found message.
- [ ] No `text-white` or `bg-default-900` (the no-invisible-text test covers the new
      files automatically).
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] **Page tests:**
  - the picker filters the pass;
  - labelling calls the store and updates progress;
  - prev/next follow the pass order;
  - Arabic (`ar`), Hebrew (`he`) and **Gurmukhi (`pa`)** cells render with
    `dir="auto"`, the right `lang` and the `script-text` class;
  - the rubric shown matches the task;
  - the download produces the expected JSONL;
  - a non-JSON API response shows "review service unavailable";
  - a cell id containing `:` round-trips through link and route.
- [ ] Existing viewer tests (`QuestionList`, explorer, leaderboard, …) pass unchanged.
      `pnpm -C apps/viewer build` and `build:pages` still succeed.
- [ ] `pnpm -C apps/viewer test` and `check-types` pass.

#### Test Plan

**Page tests** use `renderApp` with a memory history and a fake fetch serving a small
fixture sample (`fixtures/review_sample.json`) and draft API.

### Phase 7: Local end-to-end verification and documentation

**Dependencies**: Phases 1–6

#### Objective

Prove the real user path works locally, against a real Postgres and in a real browser,
and leave the docs a future operator needs. Per lessons-critical, "tests pass" is not
"it works".

#### Files to Create / Modify

- `apps/viewer/README.md`: a Review section covering the routes, the dev proxy, the
  "unavailable" behaviour on the static build, and the review origin having no baked
  runs
- `review/README.md`: the end-to-end workflow, from sample through labelling and download
  to compare
- `codev/reviews/154-review-tool-human-audit-of-det.md`: the walk's steps and results
  (finalized in the review phase)
- Any fixes the walk turns up, in the files they touch

#### Deliverables

- [ ] **Local end-to-end walk** in Chrome against a local Postgres
      (`createdb sacredtexts_review_dev`). Use the Phase 4 environment, with
      `VIEWER_DIST` = the built viewer and `SAMPLE_PATH` = the committed FAccT sample.
  1. Sign up with the invite code.
  2. Pick the Qur'an (Uthmani), the Talmud (Aramaic) and the Sri Guru Granth Sahib.
  3. Check that Arabic, Hebrew and Gurmukhi render legibly and in the right direction.
  4. Label 5 cells, including notes in Arabic and a defect flag.
  5. Reload and confirm the labels persist.
  6. Sign out, then sign in with a second account and confirm it doesn't see the first
     account's labels.
  7. Sign back in, download the gold set twice, and confirm the two files are identical.
  8. Run `review-compare --version committed --version current` on it and get a report.
  9. Confirm `/api/sample` is 401 when signed out.

  The steps and results are recorded in the review document. Screenshots are kept in the
  scratchpad, not committed. Nothing is provisioned.
- [ ] The local database is the only one created, and the runbook names how to drop it.

#### Acceptance Criteria

- [ ] Every walk step passes, or a found defect is fixed and the step re-run.
- [ ] The downloaded file is accepted by `review-compare`.
- [ ] `bash .codev/checks/test.sh` passes for the full branch.

#### Test Plan

**Manual:** the walk above. **Automated:** the full dispatcher gate.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| The port drops a multibench fix | Medium | Medium | Port from `main` file by file with its tests. Phase 5 lists every fix with its own regression test. Diff against the source in review. |
| The gold-set format drifts between TS and Python | Medium | High | One shared fixture in `fixtures/`, asserted by both suites. `fixtures/` already maps to both dispatcher lanes. |
| `review/` changes run no tests (the dispatcher-gap class) | Medium | Medium | Phase 1 maps `review/` to the pipelines lane, where the pin test lives. |
| Secure cookies don't stick on `http://localhost` in Safari | High | Low | The local walk uses Chrome, which treats localhost as secure. Cookie config stays unchanged. The hosted Safari check comes with hosting, which isn't approved. |
| The draft outgrows the body cap | Low | Medium | An 8 MB byte cap sized from a maximal multilingual draft, notes capped at 1,000 characters, and a client-side byte guard. A 413 is terminal and visible, never retried in a loop. |
| Labels misattributed after a rubric change | Low | Medium | Each label stores its own `rubric_version` and `labelled_at`, stamped only on a real edit. Downloads read no clock. |
| Version lookup collides across runs | Low | Medium | Directory versions resolve through the run prefix of `scores_path`. Mixed-run gold sets with a directory version, and duplicate keys in a scores file, both fail loudly. |
| The sample sits outside the copyright audit | — | — | Owner ruling 2026-11-10: counsel's position is fair use, so no audit extension. Recorded in `review/README.md` and arch docs so it isn't mistaken for a violation. |
| Two viewer deploy configs cause confusion | Medium | Low | `apps/viewer/railway.json` and `server/index.mjs` are left untouched. The `apps/api` README names which config the review deployment uses. |
| Node version mismatch between `apps/api` and the viewer on one service | Low | Low | Both pin `24.x`. Local node is 26, and the tests don't depend on version-specific APIs. |
| The sample regeneration pin breaks on a sanctioned rebaseline of committed scores | Low | Medium | The pin test failing is the signal: regenerate the sample deliberately, and state it in that PR. Old gold sets stay valid because they carry their inputs. |
| The static Pages build misreads the HTML fallback as "signed out" | Medium | Low | `reviewApi` treats non-JSON as "unavailable" (Phase 5), and a page test covers it (Phase 6). |
| Accidental provisioning | Low | High | The runbook carries a "NOT approved" banner. No Railway command is run in this project. |

## Documentation Updates

- `apps/api/README.md` (new): stack, endpoints, auth model, migrations, one-service
  topology, local runbook, gated deploy runbook.
- `review/README.md` (new): the sample and gold-set formats, and the `review-sample` and
  `review-compare` commands.
- `apps/viewer/README.md`: a Review section with the routes, the dev proxy, and the
  "unavailable" behaviour on the static build.
- `codev/resources/arch.md` and `arch-critical.md`: a short entry for the review tool
  (`apps/api` + `/review` + the two CLIs, labels as a matcher-version-independent gold
  set). It also records the owner's ruling that `review/` samples are outside the
  copyright audit (counsel: fair use), next to the existing "no committed artifact may
  derive from a restricted source" fact so the two don't read as a contradiction. Done in
  the review phase with the update-arch-docs skill.
- `.codev/checks/test.sh`: comments for the `apps/api` and `review/` lines.
