# spir-154 thread — review tool (human audit of deterministic scoring)

## 2026-11-09 — specify

- No spec existed; drafted `codev/specs/154-review-tool-human-audit-of-det.md` from the issue's
  proposed defaults (to be settled at the spec gate) rather than asking clarifying questions.
- Data facts (from the real run, not docs): `runs/facct-2026-11-03` = 32,478 scored cells / 304
  score files; NO `questions.jsonl` (question embedded in each answers row); cell id
  `(run, model_id, question_id)` unique. Containment-only correct: retrieve 737, complete 670.
- Copyright wrinkle: NRSV is `restricted` but audit.py allows ≤500 distinct verses/file; the FAccT
  run's 1,920 NRSV cells cover only 31 verses. Spec defaults to the issue's literal "no restricted
  cell served" (exclude NRSV) and raises inclusion as OQ2.
- Recommended approach: committed, audited, seeded stratified **review set** (Python, pipelines)
  → API (multibench port + re-keyed review slice: ingest, claim-based language-filtered assignment
  with overlap, server-enforced blind-before-reveal, per-cell drafts + immutable submissions)
  → viewer review routes → pseudonymous committed export → Python agreement report.
- Critical OQs for the gate: the human rubric per task (draft in spec), NRSV inclusion.

## 2026-11-09 — spec consult iter 1 (codex + claude: both REQUEST_CHANGES), folded

- claude verified every factual claim exact against the run + port source.
- Folded: rubric now aligned to Spec 48 class A/B + #23 leading stance + #150 head + containment,
  with a post-reveal rubric-problem flag for contract disagreement (claude's main point);
  explicit Defaults D1–D10 (codex: settle defaults); deterministic allocation/overlap/order rules
  (sha256(seed‖cell id)); edition language added to strata (language gaps would otherwise bias
  post-stratified estimates); proper estimands (precision/FDR, missed-credit, weighted recall,
  post-stratified weights, Wilson + stratified bootstrap, Krippendorff α, uncovered mass);
  trust anchor for ingest = digest pinned in repo + recomputed; review set + exports must be wired
  into test_audit.py's scan and the dispatcher (test_audit only scans runs/ — fixtures-gap class);
  keyed (HMAC) pseudonyms + languages snapshot; account delete stays cascading (port unchanged),
  figures tied to a committed export; claim-race criterion; #41 worklist in report; local e2e scope.

## 2026-11-10 — owner rulings at spec gate (relayed by architect), spec rewritten

- Owner reframed: internal verification tool + gold set for testing matcher VERSIONS, not a
  publication instrument. Rulings: not blind; even stratified sample (outcome × task × text, k per
  stratum, default 10 ⇒ ~1,400 cells / 151 strata); reviewers pick TEXTS not languages; core
  version-comparison CLI (committed / current re-score / scores file, with movers); include NRSV, no
  copyright machinery; one reviewer base case (no overlap/claims/IRR/pseudonyms); plain counts, no
  stats; one Hono service serving /api + built UI + Postgres, no edge.
- Rewritten spec picks the max-reuse design: multibench draft re-keyed tradition→sample (one draft
  per reviewer per sample holds chosen texts + labels); gold set downloaded client-side; no cell
  tables, no server export. Not approved yet — waiting for architect to relay approval.

## 2026-11-10 — spec approved; plan drafted

- Architect relayed human approval of spec 1ee8cc12 (k=10 default stays a CLI param; hosting NOT
  approved — local only). Ran `porch approve 154 spec-approval --a-human-explicitly-approved-this`
  as instructed by the architect.
- Plan: 6 phases — (1) review-sample builder + committed FAccT sample under review/samples/,
  dispatcher maps review/ → pipelines; (2) gold-set format + review-compare CLI (committed / current
  / scores file, movers fixed/broken) with shared fixtures/ contract; (3) apps/api port re-keyed
  tradition→sample, registered in test.sh; (4) one service: /api/sample + built viewer serving +
  railway.json (not applied); (5) viewer review store/API client port + sample/rubric/gold-set libs;
  (6) /review pages + local e2e in Chrome against local Postgres (homebrew pg17 available).
- Text = edition folder between <model>/base/ and population/ (13 in FAccT; groups encyclicals and
  Masoretic he+arc with no special cases).

## 2026-11-10 — plan consult iter 1 (codex + claude both REQUEST_CHANGES), folded

- Accepted: labels carry their own rubric_version + labelled_at (stamped only on a real edit) so
  downloads are clock-free and byte-identical; body cap 8 MB in bytes (sized for 1,000-char 4-byte
  notes) + client byte guard; 413 / non-retryable 4xx is terminal (multibench retried forever);
  script-text font stack + Gurmukhi test; run-aware dir versions in review-compare; static host
  ported from the in-repo apps/viewer/server/index.mjs (not multibench's edge), viewer
  railway.json left untouched; Phase 6 split → new Phase 7 (local e2e + docs); env table.
- Rebutted claude's "audit the committed sample" — owner ruling 5 explicitly removed copyright
  audit-scan extensions (counsel: fair use). Documented in review/README + arch docs instead.

## 2026-11-10 — plan approved; phase 1 done

- Architect relayed human plan approval (56375ec4); audit-scan rebuttal stands; hosting NOT approved.
  Ran `porch approve 154 plan-approval --a-human-explicitly-approved-this` per the relay.
- Phase 1 (a70314ce + nits feb19864): `sacredbench review-sample` → review/samples/facct-2026-11-03-k10.json
  (seed `spec-154`, k=10: 1,423 cells / 151 strata / 13 texts, 2.8 MB; NRSV 111 cells / 29 verses).
  Pin test regenerates it byte-for-byte; review/ → pipelines lane in test.sh. Full pipelines suite
  green (1520 passed). Consult: codex + claude APPROVE; took claude's nits (load_sample shape checks,
  refuse --out under runs/, texts[].cells → texts[].drawn, error-path tests).
- Note for later phases: test.sh diffs COMMITTED changes vs origin/main — commit a phase before
  `porch done` or the gate tests nothing.

## 2026-11-10 — phase 2: gold-set format + review-compare (5de80e3d)

- `pipelines/sacredbench/review_compare.py` + `sacredbench review-compare GOLD... --version V [--version …] [--json P]`.
  Versions: `committed` (row's scores_path from repo root), `current` (score_answer exactly as score_file
  calls it; no provider import — subprocess test with a socket guard), or a run dir (runs/<run>/ prefix
  swap; mixed-run gold + dir version fails). Movers are over judged rows only, so
  Δagree = fixed − broken (pinned by a test).
- **Format decision Phase 5 must honour:** canonical gold bytes = compact JSON, keys sorted at every
  level, non-ASCII raw, numbers as `JSON.stringify` writes them. The sample file holds Python floats
  like `1.0` (token_f1); JS parses them to `1`, so `dumps_gold_rows` writes integral floats as ints
  and fails on floats whose shortest form differs between the languages (<1e-4). The fixture
  exercises this (`"token_f1":1`).
- Fixtures: `fixtures/review_sample.json` (8 cells, built by the real `build_sample` at k=1 from a
  scratch run: real FAccT prompts/expected for islam/native + hinduism/english, made-up answers and
  run `fixture-run`) + `fixtures/review_gold_set.jsonl`. Movers under committed→current are
  realistic: #118 undisclaimed form-example echo `34:46 أو 3:140` = broken; #94 `Yogi`/`Yogî` = fixed.
- Real data fact: on the committed FAccT sample, `current` == `committed` for all 1,423 cells
  (no scorer drift since the run was scored). Smoke (first 20 cells, labels = shown): 100% / no movers.
- Phase 2 consult iter 1: codex REQUEST_CHANGES (real `python -m sacredbench` entrypoint loads
  `sacredbench.providers` via cli.py's pre-existing imports), claude APPROVE + 4 nits. Fixed in
  4d1d2f26: real-entrypoint offline test (sockets refused, provider SDK imports blocked); fixture →
  10 cells (judged verify_source refusal + false-premise rows); scores_path must be relative w/o '..';
  README/hint nits. Declined the lazy-import refactor of cli.py (touches collect/score/main, out of
  phase scope; providers module loads no SDK) — rebuttal in 154-phase_2-iter1-rebuttals.md.
- Phase 2 consult iter 2: claude APPROVE; codex REQUEST_CHANGES — real bug: `runs/<run>//etc/passwd`
  passed the scores_path check and the raw prefix slice made the dir-version lookup absolute. Fixed in
  b0e0fa61 (canonical-path check at load + component-wise join; regression test bypasses the loader).
  Also took claude's notes: per-task expected-key check, `excluded.both`, smoke test via CLI.
- **For the architect/owner (from claude iter 2):** the fixture's `broken` mover is a real
  rubric-vs-matcher divergence — the approved rubric discounts only a *disclaimed* form-example echo,
  but #118 drops an undisclaimed one beside another citation (`34:46 أو 3:140` scores correct).
- Phase 2 consult iter 3: codex APPROVE (no issues), claude APPROVE (non-blocking) — a clean pass, not a
  max-iteration force-advance. Porch advanced to phase_3 (1c2cbfbf).
- Follow-ups for the review doc (Phase 7), from claude iter 3: (a) record the AR_CITE rubric-vs-matcher
  divergence in codev/reviews/154; (b) README: multi-reviewer agreement is per label, so a cell labelled by
  two reviewers counts twice in `n`; (c) grader_path reads default-grader metrics, so a version scored
  with a non-default grader set gets an approximate path label (breakdown only, never a verdict);
  (d) review/README's "29 distinct verses" NRSV figure is unpinned and can go stale on a regeneration.

## 2026-11-10 — phase 3: apps/api ported (f7b45af0)

- New `apps/api` = multibench `apps/api` @ 14f6c9d4 (its fixes included), re-keyed tradition → sample:
  `/api/review[/:sampleId[/submit|/submissions]]`, columns `sample_id`; `published_issue_url` gone;
  body cap 8 MB in bytes (`REVIEW_BODY_MAX_BYTES`). Migration generated with
  `drizzle-kit generate --name review_store` (SQL reviewed: 4 tables, FKs cascade). 59 vitest on PGlite.
- **Deviation, deliberate:** cookies renamed `mb_*` → `st_session`/`st_csrf`. Cookies are host-scoped,
  not port-scoped, so a local multibench API on `localhost` would clobber our session. Attributes unchanged.
- **Beyond the plan's file list:** added an `api` job to `.github/workflows/tests.yml` (typecheck +
  vitest), otherwise GitHub CI never runs the suite. Registered `apps/api` in `.codev/checks/test.sh`.
- Real-Postgres smoke (throwaway initdb cluster in scratchpad on :55432, NOT the user's :5432 server;
  stopped after): `pnpm migrate` applies and re-runs as a no-op; `pnpm start` walk signup → PUT v0 →
  stale 409 with current → GET → submit 201 → 413 over 8 MB → account delete leaves 0 rows everywhere.
- **For Phase 5:** JSONB does not preserve object key order (labels came back `notes, defect, outcome…`),
  so the store must not rely on key order of the round-tripped draft; the gold-set builder already uses
  a fixed key order.
- Worst-case draft (1,500 × 1,000 four-byte chars + metadata) measures 6,245,326 bytes (~6.2 MB), under
  the 8 MiB cap. The plan's "about 6.5 MB" estimate holds.
- For Phase 7 docs: lessons-critical's dispatcher registry line still lists only pipelines + viewer.
- Phase 3 consult iter 1: codex APPROVE (no issues), claude APPROVE (non-blocking). Took the nit: the
  worst-case size comment in `review.ts` now says ~6.2 MB (measured), matching the README.
  Carried forward: (1) **Phase 4** should reject a draft PUT/submit whose `sampleId` isn't the active
  sample (two-line guard once the sample is loaded); (2) signup/login bodies have no `bodyLimit`
  (inherited from multibench verbatim) — a cheap follow-up, listed for the Phase 7 review doc.

## 2026-11-10 — phase 4: one-service hosting (6c9d640d)

- `SAMPLE_PATH` (required) → `src/sample.ts` validates the envelope once at startup (format 1, the
  pipelines' `TOP_KEYS`, non-empty `sample_id`, cells/strata/texts lists of objects) and
  `GET /api/sample` (auth) serves the committed bytes verbatim (2.8 MB; no per-request re-serialize).
  The viewer still owns the strict per-cell parse (Phase 5).
- Took phase 3's carry-forward: PUT and submit for any id but the active sample → 404
  `{error:"unknown sample"}`. GET / list / DELETE stay open for every id, so a draft from an earlier
  sample is still readable and removable. Two existing tests that PUT to a second sample now seed
  that draft directly in the DB.
- `VIEWER_DIST` (optional) → `src/static.ts` ports `apps/viewer/server/index.mjs` (serveStatic +
  index.html fallback), excluding `/api/*` and serving GET/HEAD only. Any unmatched `/api` path is a
  JSON 404 (with or without a viewer). `/api/review/<junk>` signed out is 401, not 404: the review
  router's auth middleware covers its whole subtree. That's fine, and it's still JSON.
- `apps/viewer/server/index.mjs`, its smoke test and `apps/viewer/railway.json` are untouched, as the
  plan says.
- `vitest.config.ts`: `testTimeout` 20 s. The first cold run timed out (5 s) in each file's first
  PGlite boot while `server.test.ts` was spawning real servers. The warm re-run was 84/84 green.
- Manual check, the same way the hosted config runs it: the exact railway build command from the repo
  root, a throwaway initdb cluster on :55432 (scratchpad, TCP-only, stopped afterwards; the user's :5432
  was not touched), `pnpm -C apps/api migrate`, then `pnpm -C apps/api start` with the
  **Railway-style relative paths** (`../../review/samples/…`, `../viewer/dist`).
  - Results: health 200, `/` and `/review/cell/x` serve index.html, the hashed JS is served as JS,
    `/api/nope` is a JSON 404, `/api/sample` is 401 signed out and byte-identical to the committed
    file signed in, a PUT to the active sample gives v1, and a PUT to another sample is 404.
- **Unverified, flagged in the README:** the repo root has no `package.json`, so Nixpacks/Railpack
  Node detection at a repo-root service root is unproven. It can only be checked on a first deploy,
  which is not approved.
- The README mentions the viewer's Vite `/api` proxy for API-only dev. The proxy itself lands in
  Phase 6 (`vite.config.ts`), per the plan.
- Phase 4 consult iter 1: codex APPROVE (no issues), claude APPROVE (non-blocking). I took all three of
  claude's notes, because the hosting go-ahead (below) makes the first one real:
  - (1) `hono/compress` on every response. The sample is 2.8 MB → ~0.5 MB gzipped; on the real server
    the JS bundle is 689 KB → 187 KB, and it round-trips byte-identical.
  - (2) `PORT=""` used to bind port 0. Now any set PORT that isn't an integer from 1 to 65535 exits 1.
  - (3) a sample with zero cells fails at startup.
  - Each has a test. Not done: an ETag on `/api/sample`, since compression covers most of the cost.
- **Hosting go-ahead, 2026-11-10T21:34Z** (the owner, via the architect): provision is included, after the
  phase-7 local walk passes, in phase order. A new Railway project, one service + Postgres, smallest
  tiers, daily backup. The invite code lives only in Railway and the gitignored root `.env`. The
  multibench Railway project and `apps/viewer/railway.json` are not to be touched. The README's "NOT
  approved" banner stays until provision time, when it's rewritten to say what was actually provisioned.

## Phase 5 — viewer review store, API client, sample and gold-set libraries (2026-11-10)

- New in `apps/viewer/src/lib/`: `review.ts` (the store), `reviewApi.ts`, `reviewSample.ts`,
  `rubric.ts`, `goldSet.ts`, and a test file for each of the first four plus `reviewStore.test.ts`.
  `zod` is back in the viewer's dependencies (resolved `^3.25.76`).
- **Gold-set parity holds byte for byte** with the Python-written `fixtures/review_gold_set.jsonl`. The TS
  writer sorts keys by code point at every level. It doesn't lean on `JSON.stringify` key order, because
  JS puts integer-like keys first (`"9"` before `"10"`) where Python's `sort_keys` doesn't. A test pins it.
- **Store, ported from multibench and re-keyed to samples.** `ReviewState` is `{samples}`.
  - multibench's `reviewer` info, JSON import/export, `evenSample`/`seededSample` and the submission
    client calls are dropped. Nothing here uses them: sampling is the committed Python draw, and the
    reviewer's output is the gold-set download.
  - Every multibench fix has a regression test, and five of them were mutation-checked (each mutation
    turns a test red).
- **Choices worth knowing:**
  - **"unavailable" vs signed out.** `AuthStatus` gains `"unavailable"`. Any non-JSON answer that isn't a
    5xx or a 413 throws `ReviewUnavailableError`, so `initReview` lands on "review service unavailable"
    instead of the sign-in form. A network error still lands on signed-out with the "couldn't reach"
    notice, as in multibench.
  - **413 is judged by status, not body.** The API's 413 is plain text (hono `bodyLimit`'s default), so
    a body-type check alone would have read it as "unavailable".
  - **Terminal saves.** A 413, or any 4xx that isn't 401, 409 or a CSRF 403 (`{error:"csrf"}`), sets
    `errorKind: "rejected"`. No retry timer is armed, `flushReviewSaves` doesn't retry it, the labels
    stay in memory, and the next real edit tries again.
  - **Byte guard.** `putDraft` measures the exact UTF-8 body against `REVIEW_BODY_MAX_BYTES` before
    sending. A test reads `apps/api/src/routes/review.ts` and pins the two caps equal.
  - **Deletes refresh CSRF too.** multibench refreshed the token only on save 403s. Deletes now do it as
    well, otherwise a stale token would loop the delete retry.
  - **Labels.** `CellLabel.outcome` is `null` until picked. A label without an outcome isn't counted in
    progress and isn't in the gold set. `withLabel` stamps `rubric_version`/`labelled_at` only on a real
    change; a no-op returns the same state object, so the store doesn't save.
  - **The gold set fails loudly on bad labels.** A label for a cell the sample doesn't hold, or one that
    lost its stamp, throws instead of writing a file `review-compare` would reject. Labels on texts the
    reviewer has since deselected are still written: they're real judgements.
- Gate: viewer 348/348 (253 existing + 95 new), `check-types` clean.
