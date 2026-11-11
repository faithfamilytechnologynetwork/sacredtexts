# bugfix-159 thread: hosted site bakes only the FAccT run

## Investigate (2026-11-10)

- Reproduced on the live origin: `curl https://sacredtexts.iaser.ai/runs/_index` lists six runs
  (`facct-2026-11-03`, `panel`, four `archive/*`). `listRuns(runs/)` locally gives the same six.
- Root cause: `apps/api/Dockerfile`'s viewer stage does `COPY runs runs`, then `build:pages`
  (`scripts/bake-runs.ts`) bakes whatever is under `runs/`: each named panel folder
  (`facct-2026-11-03`), the default `panel` over the top-level `runs/<model>/base`, and every
  `archive/<name>` with a summary.
- Fix shape: the Dockerfile names each hosted run in its own `COPY runs/<id> runs/<id>` line; that
  list is the one place. Docker fails the build if a named run is missing, and nothing else under
  `runs/` (tracked or not) can reach the bake. bake-runs.ts and the Pages build are untouched.
- Side effect to surface: `/judge` and `/findings` read `/runs/_judge`, built from the Jev
  `judgments-v5.jsonl` sidecars. Those exist only under the top-level panel model folders, none
  under `facct-2026-11-03`, so on the hosted origin both pages will show their empty state
  ("No judgments-v5 files yet."). Live today: 16 judge models. Nothing breaks; the data is just not
  part of the FAccT run.
- Single-run checks: `selectRunId` falls to the most recent benchmark run (facct) when `panel` is
  absent; standings rolls up one run; `_gaps` walks the named panel folder. The review sample's
  `source_run` is `runs/facct-2026-11-03` and is display-only, but it names the one baked run.

## Fix (2026-11-10)

- `apps/api/Dockerfile`: `COPY runs runs` → `COPY runs/facct-2026-11-03 runs/facct-2026-11-03`, with a
  comment saying this is the only place the hosted set is named. The bake script and the Pages
  build are untouched.
- Regression test `apps/viewer/vite/hostedBake.test.ts` (viewer lane, which also runs for any
  `apps/api/**` change): it parses the Dockerfile's context COPYs (no wholesale `.`/`runs` copy, one
  run per line, same path both sides), pins the list to `facct-2026-11-03`, stages exactly those
  runs and bakes them, then checks `_index` = the list, all four artifacts, a Pages-ready dist,
  `_gaps`/`_judge` shapes, and that every review sample's `source_run` is indexed. 3 of 6 fail on
  the old Dockerfile; all pass on the new one. The test lives in the viewer because `tsc` in
  apps/api would typecheck the imported viewer modules under api settings.
- Verified on a real local image (built from the tracked files): bake log `baked 7 URLs for 1
  runs`; over HTTP `/runs/_index` = `[facct-2026-11-03]`, `panel` and `archive/*` get the shell,
  `/` opens on facct, `/standings` rolls up "all 1 run" (16 models). `_judge` is empty, so
  Judge/Findings show their empty state (documented in the README).
- Docs: apps/api/README (what the origin shows, how to change the list, sizes: `dist/runs` 69 MB,
  image 541 MB unpacked / 111 MB gzipped locally), apps/viewer/README, arch.md § Review tool.

## PR #160 and CMAP (2026-11-10)

- CMAP: codex APPROVE (HIGH), claude APPROVE (HIGH), gemini skipped (`agy` exited 3, non-blocking).
  The first dispatch failed for all three with "Multiple projects found". It needs
  `--issue 159 --project-id bugfix-159` from the builder worktree.
- Folded claude's minor items: the Dockerfile and README now say "no other directory under runs/"
  and note that untracked files inside a named run would reach a local build (the git-archive
  deploy is tracked-only). Fixed a misleading anchor text. Re-measured fails-without-fix: 4 of 6
  (the non-empty guard added after the first measurement makes the index test fail too).
- Left as is: the samples test checks every committed sample (stricter than the one active
  `SAMPLE_PATH`, which lives only in Railway); the extra ~10 s bake in the viewer lane.
- For the owner: on the hosted origin, `/judge` and `/findings` go empty, because the Jev
  sidecars sit only under the top-level panel folders. Claude's review agrees there is no clean
  way to keep them without bringing back the `panel` run.
