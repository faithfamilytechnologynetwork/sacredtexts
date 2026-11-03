# task-XYY1 — viewer: Errors nav link + /errors picker page

**2026-11-02** — Task builder (no porch project). Scope: apps/viewer only; nothing under runs/ or pipelines/.

## What was built
- `Errors` link in the header nav (`RootLayout.tsx`), ahead of Gaps and Standings.
- `/errors` route (`router.tsx`, `?run=<id>` validator copied from the index route) → `ErrorsPage.tsx`:
  loads the run index like LeaderboardPage, reuses `RunSelector`, reads only `summary.json`
  (`loadSummary`), lists models via `leaderboardRows` (same ranking as the leaderboard) with
  `formatCell` / `formatCoverage` of the `_overall` cell, each model linking to
  `/run/<runId>/model/<modelId>`.

## Decision: shared default-run helper
The brief said "default to the same run LeaderboardPage defaults to". Rather than copy the
`benchmarkRuns(runs)[0] ?? runs[0]` expression, I moved it into `selectRunId(runs, requested)` in
`lib/runIndex.ts` and pointed LeaderboardPage at it, so the two pages can't drift. No behaviour change
for `/` (its 10 route tests still pass); 4 unit tests added in `runIndex.test.ts`.

## Verification
- `pnpm -C apps/viewer test`: 22 files / 245 tests pass (7 new in `ErrorsPage.test.tsx`).
- `pnpm -C apps/viewer check-types` is clean. The repo has no lint config or lint script, so the typecheck is the only static check.
- Real data: Chrome extension was not connected, so instead ran the page's own helpers through
  vite-node against a live `vite dev` serving the worktree's `runs/`: default run = `panel` (16 models),
  links `/run/panel/model/<id>`, e.g. fable 62% (n=1200) · 96% coverage. `/errors` deep link → 200.
  Not eyeballed in a browser.

## Not done / notes
- The Errors nav link is not highlighted while on an explorer page (`/run/...`), only on `/errors`.
  Easy follow-up if wanted.

## Integration review round (2026-11-03, architect `main`, PR #127)
Fixed the three "fix before merge" items + the arch-critical route line; follow-ups left open.
1. **Stale frame**: reproduced first with a MutationObserver test (it caught `/run/run-a/model/haiku`
   and `/run/run-a/model/gemma-4` painted for one frame after switching runs), then fixed: the settled
   `RunState` carries `runId`; only a state whose `runId === selectedId` renders, else it's loading.
   That also removed the `selectedId!` assertion and makes the error message name the right run.
   The same pattern exists in **LeaderboardPage** (pre-existing, not touched here). Worth a follow-up,
   ideally folded into the shared-hook follow-up.
2. **Home-page exp-* default**: the LeaderboardPage default test now has a loadable `exp-newest-*`
   as index[0]. Mutation-checked: replacing `benchmarkRuns(runs)[0]` with `runs[0]` fails it.
3. `<h1>Errors</h1>` + intro hoisted above `RunSelector` (tests pin it in run-loading and run-error
   states); table has `<caption class="sr-only">Models in run <id></caption>`.
- `arch-critical.md` route list: + `/errors`, `/gaps`.
- Viewer: 22 files / 247 tests pass; check-types clean.
