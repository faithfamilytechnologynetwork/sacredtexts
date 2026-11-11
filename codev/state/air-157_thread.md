# air-157 thread

Issue #157 — review tool results page + `review-compare --from-service`.

## 2026-11-10 — start
- Spawned in strict AIR mode; porch at implement iteration 1. Exploring apps/api, /review viewer routes, review-compare.

## 2026-11-11 — implemented, verified locally
- Shape: viewer `/review/results` (lib/reviewResults.ts, computed from `goldRows` so it can't diverge
  from the download), API `GET /api/gold-set` (a port of the viewer's gold-set writer that reads the
  draft like the viewer's zod loader), CLI `review-compare --from-service` (stdlib urllib: login →
  gold set → logout; https only except localhost; creds from REVIEW_EMAIL/REVIEW_PASSWORD or prompt).
- Parity pins: `fixtures/review_gold_set.jsonl` (three writers) and new `fixtures/review_results.json`
  (= review-compare --version committed minus `version`/`arms`).
- Surprise: integer half-even rounding diverges from Python's `round(100*a/n, 1)` at n ≥ 2000
  (e.g. 1/2000 → Python 0.1). The browser reads the double's exact decimal digits (`toFixed(100)`) and
  rounds half-even, so it matches Python for every n.
- Over AIR's ~300 LOC (~480 prod + ~370 tests); architect said stay AIR and will run a consult
  integration review on the PR.
- Scope add from the architect (owner ruling): the hosted image builds the viewer with `build:pages`,
  so `/` is the real leaderboard. The service needed Pages parity on `/runs/*`: `_headers` (text/plain,
  so it compresses; no-cache on _index/_gaps) and a 307 for encoded run ids (`archive%2F…`). Without the
  307 the archive runs silently fell back to the SPA shell.
- Verified: local sign-up → label → Results → `review-compare --from-service http://localhost:8080`
  (same numbers, no creds in output, CLI session row deleted). Image from `git archive` paths: 43 s
  build, 118 MB compressed, cold start 0.8 s; baked runs byte-identical to a local build:pages
  (apart from `_index` mtimes).
- `sacredtexts.iaser.ai` did not answer from here on 2026-11-11; READMEs use it as instructed.
