# SacredBench viewer

A local-only single-page app for exploring benchmark runs: a leaderboard of which models
were tested and how they scored per task and per tradition, a drill-in error explorer for
any model's per-question failures, and a cross-run "current standings" view. It reads a
run's artifacts directly — no GitHub data layer, no backend API.

## What it reads

A run lives in `runs/<id>/` and the viewer loads four artifacts
(`pipelines/sacredbench score` output):

- `summary.json` — per-model × task (and × tradition) accuracy **and coverage** (plus the
  correct/incorrect/refused counts), token `usage`, and the model `panel` (provider, model
  (raw id), the `tools` list, endpoint, and `served_by`).
- `scores.jsonl` — per-question metrics (exact / normalized / token-F1 / contains_reference /
  correct) plus the `outcome` (correct / incorrect / refused).
- `answers.jsonl` — each model's answer plus the prompt and expected text.
- `questions.jsonl` — the authoritative question roster, so a model's **un-answered**
  questions show as missing cells.

Two kinds of virtual run are built on the fly from per-file summaries (`vite/runsEndpoint.ts`):

- `panel` rolls up every `runs/<model>/base/**/summary.json`.
- `<name>` rolls up a named panel folder: a top-level `runs/<name>/` with no `summary.json`
  of its own whose children are model folders, `runs/<name>/<model>/base/**/summary.json`
  (what `items/for-test/join_run.py --run-dir runs/<name>` writes, e.g.
  `runs/rerun-2026-11-03/`). Its models stay out of `panel`.

Each is dated by its newest per-file summary (`generated_at`, else that file's mtime), so the
home page opens the newest panel. Per-file summaries carry no `panel` block, so standings key
virtual panels on the bare model id: an in-flight rerun replaces each model's row (newest
wins) and becomes the home default. Name the folder `exp-…` to keep a rerun out of both.

`src/lib/localResults.ts` fetches and joins these (`loadRun` for a full run,
`loadSummary` for just the per-model rollup the standings view and the `/errors` picker need);
`src/lib/runIndex.ts` lists the runs and picks the default one (`selectRunId`); `src/lib/leaderboard.ts`
derives the leaderboard ranking/columns/token totals, `src/lib/explorer.ts` the per-question
classification and filters, and `src/lib/aggregate.ts` the cross-run standings rollup.

## Running it

```sh
pnpm -C apps/viewer install
pnpm -C apps/viewer dev          # then open the printed URL
```

- `/` shows the **leaderboard** for the most-recent run under `runs/`: models ranked by
  overall accuracy, with a **coverage** column of equal weight beside it (accuracy = right
  *when it answers*; coverage = how often it answers — the rest refused), per-task and
  per-tradition columns, per-model token totals, and — when a run has search-on/off arms of
  the same model — a **"Search on vs off"** contrast (accuracy + coverage per arm, with the
  Δaccuracy). A run selector switches between the runs present; the selection lives in the URL
  as a bare run id (`/?run=<id>`), so a view is shareable and survives refresh. If `runs/` is
  empty you get an informative empty state; if a selected run can't be loaded you get a
  localized error while the selector and other runs stay usable.
- Clicking a model (or a task / tradition cell) opens the **error explorer**
  (`/run/$runId/model/$modelId`): every question for that model with its outcome — correct /
  incorrect / **refused** / missing — and for each one the prompt, the expected text, the
  model's answer, and the per-metric scores (exact / normalized / token-F1) side by side.
  Filter by task, tradition, correctness, failure mode (missing cell / **refused** / wrong
  answer), and failure kind; the filters live in the URL
  (`?task=&tradition=&correct=&kind=&mode=`, where `mode` is `missing` / `refused` / `wrong` and
  `kind` is a failure kind such as `near_copy` / `other_script` / `wrong_verdict`).
- **Errors** (`/errors`, linked in the header) is the way into the error explorer without going
  through the leaderboard: pick a run (the same default as the home page; the choice lives in
  `?run=<id>`), and it lists that run's models with their accuracy and coverage, each linking to
  `/run/<id>/model/<model>`.
- **Standings** (`/standings`, linked in the header) is the cross-run view: one row per
  model showing its **most recent** result across all runs, keyed on the run panel's
  `(provider, model, tools)` identity (a missing `tools` ⇒ `[]`), so search-on/off stay
  distinct rows while two runs of the same model with the same tools dedupe to one, with
  the source run's id and date linking back into that run's leaderboard.
- The dev server exposes the repo's (gitignored) `runs/` at `/runs/` via a dev-only Vite
  middleware (`serveRuns` in `vite.config.ts`, logic in `vite/runsEndpoint.ts`), including
  a `/runs/_index` run index. Symlinked run directories are intentionally omitted from the
  index (the endpoint rejects symlink traversal).
- `pnpm build` produces the static SPA with **no run data**. `server/index.mjs` (a minimal hono
  host with history fallback) serves it. With no `/runs` endpoint, the home page's index
  fetch gets the SPA shell (HTML) and the app shows the empty state; it never crashes. To ship
  the runs, use the Cloudflare Pages build below.

## Deploying to Cloudflare Pages

`pnpm build:pages` builds the SPA and then bakes the run data into `dist/runs/`. It runs
`scripts/bake-runs.ts`, which asks the dev endpoint for every URL the viewer can request and
writes each answer to disk: the run index, the gap list, every run's four artifacts, and the
virtual panel runs (`panel` and each named panel folder). The baked files are byte-identical to what `pnpm dev` serves
(`vite/bakeRuns.test.ts` checks every URL against the real `runs/`).

Deploy from the repo root, on `main`, after a one-time `npx wrangler login` by the account
owner:

```sh
pnpm -C apps/viewer build:pages && pnpm -C apps/viewer dlx wrangler pages deploy --branch main
```

`apps/viewer/wrangler.toml` names the project (`sacredtexts-viewer`) and the output dir
(`dist`). On the first deploy wrangler offers to create the project; choose `main` as its
production branch.

How the static site works:

- **Deep links** (`/standings`, `/gaps`, `/errors`, `/run/<id>/model/<model>`): Pages serves
  `index.html` for any path that is not a file, as long as `dist/` has no top-level
  `404.html`. There is no `_redirects` file because wrangler ignores `/* /index.html 200` as
  an infinite loop.
- **Large artifacts**: Pages rejects any file over 25 MiB, and the panel's `answers.jsonl` is
  about 50 MB. The bake splits any artifact over 20 MiB at line boundaries into
  `<name>.partNNN` files plus a `<name>.parts.json` manifest. When the whole file is missing,
  the viewer reads the manifest, joins the parts, and checks the size, sha256 and row count
  before using them (`src/lib/shards.ts`). `pnpm dev` never shards.
- **Headers** (`public/_headers`): `/runs/*` is sent as `text/plain` so Cloudflare compresses
  it, and `/runs/_index` and `/runs/_gaps` are `no-cache`.
- `build:pages` fails, without deploying anything, if `runs/` is empty, if any file in
  `dist/` is over 25 MiB, or if a `404.html` would turn off the deep-link fallback.

To check the build locally before deploying, run it on Cloudflare's own runtime (no login
needed):

```sh
pnpm -C apps/viewer build:pages && pnpm -C apps/viewer dlx wrangler pages dev
```

Don't use `npx serve -s dist` for this check. Its SPA rewrite answers extension-less paths
such as `/runs/_index` with `index.html`, so the viewer shows "no runs". Pages serves the
real file.

The committed sample run `runs/archive/first-run-2026-10-11/` renders out of the box when it is
the only run present; `src/local/realRun.test.ts` pins it through `loadRun`,
`src/routes/LeaderboardPage.test.tsx` renders it through the leaderboard,
`src/routes/ExplorerPage.test.tsx` drills into it, and
`src/routes/StandingsPage.test.tsx` rolls it up as standings — all in the test gate, so the
committed evidence can't drift out of the viewer's schema.

## Status

The multibrowser surface this app was seeded from (`/t/...` traditions, the
GitHub-data-layer `/results`/`/raw` views, the `/review*` flows, and their components and
data layer) has been **removed**. The viewer is the three Spec 2 surfaces over local
`runs/`: the **leaderboard home + run selector**, the **error explorer**, and the
**cross-run standings** view.

## Provenance

The app was seeded from `multibench/apps/multibrowser` (commit 14f6c9d4). That history —
including the client-side GitHub data layer and its unauthenticated-rate-limit lessons —
is preserved in `README.multibrowser.md` for reference; none of that surface ships any
more.
