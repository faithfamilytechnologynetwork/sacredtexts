# task-7oCH: viewer → Cloudflare Pages (static, baked run data)

## 2026-11-02

**Goal.** `pnpm build:pages` = vite build + bake every `/runs` URL the client can request into
`dist/runs/`, byte-identical to the dev endpoint; deploy config for Pages project
`sacredtexts-viewer`. No deploy, no `wrangler login` (the owner authenticates).

**Blocker found → architect decided (A).** The synthetic panel's `answers.jsonl` is 49.98 MB
(289 nested files, 29,470 rows), which is over Pages' 25 MiB per-file cap. 56% of those bytes
are the `question` object, repeated on every row. Options were shard / per-model / ship
without it / R2. Architect chose **(A) shard**: the bake splits any artifact over 20 MiB at
line boundaries into `<name>.partNNN` files plus `<name>.parts.json` (parts, bytes, rows,
sha256). `fetchArtifact` falls back to the manifest only when the whole file is missing, then
verifies size, sha256 and rows, failing loudly on a mismatch. The dev handler is unchanged.
(B) per-model artifacts is filed as a follow-up.

**Verified in Cloudflare's own asset worker source** (the miniflare copy of workers-shared, plus
wrangler 4.69's `_redirects` parser):
- `/* /index.html 200` is DROPPED as an "infinite loop" rule, and redirects are matched before
  assets. Architect agreed: **no `_redirects`**. Pages' default SPA mode (no top-level
  `404.html`) gives the deep-link fallback, asserted by `assertPagesReady` and deploy.test.
- `%2F` is decoded per segment, so `archive%2F<name>` reaches `runs/archive/<name>/…`. No
  client change was needed for archive run ids.
- wrangler has no MIME type for `.jsonl` / `_index`, so those would go out with no
  Content-Type and uncompressed. `public/_headers` sets `/runs/*` to `text/plain`, which took
  panel `scores.jsonl` from 5.7 MB to 439 KB gzipped locally. `_index` and `_gaps` are
  `no-cache`.

**Surprise.** `npx serve -s dist` is the WRONG local check. Its SPA rewrite takes precedence
over extension-less files, so `/runs/_index` comes back as index.html and the viewer shows
"no runs". The README now says to use `wrangler pages dev`.

**Real-path verification.** Ran `wrangler pages dev` (an already-installed copy; no install,
login or deploy) over the real `build:pages` output, and headless Chrome over `/`,
`/standings`, `/gaps`, `/run/panel/model/opus` and
`/run/archive%2Foriginal-2026-10-21/model/gpt-oss-20b`. The rendered page text is IDENTICAL
to `vite dev` on all five (41,652 lines on the panel opus explorer, whose answers come from 3
shards).

**Tests.** `vite/bakeRuns.test.ts` runs real HTTP on both sides: the dev handler mounted at
`/runs`, and a Cloudflare-rules static server written independently of the bake. It covers
every URL from listRuns/buildPanel/collectGaps, for a fixture (archive id, a run with 404'd
artifacts, panel, gaps, forced shard) and for the real `runs/`. `loadRun` from the static host
deep-equals dev. `src/lib/shards.test.ts` covers the reassembly failure modes. Lane green:
21 files, 217 tests.
