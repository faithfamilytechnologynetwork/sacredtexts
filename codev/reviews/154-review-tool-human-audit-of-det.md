# Review: Review tool — human audit of deterministic correctness scoring

## Summary

SPIR 154 built a review tool for checking the deterministic matcher against human labels. It has
four parts:

- **A committed sample.** `review-sample` drew one from the FAccT run: 1,423 cells, 151 strata,
  13 texts.
- **A review service.** `apps/api` is ported from multibench's reviewer and re-keyed from tradition
  to sample. One Hono process serves `/api`, the active sample and the built viewer.
- **Review pages in the viewer.** `/review` and `/review/cell/$cellId` handle text picking,
  labelling and progress, plus a byte-stable gold-set download.
- **A comparison command.** `review-compare` scores any matcher version against the gold set and
  lists the movers.

The work ran in 7 plan phases, plus a review phase that provisioned hosting on the owner's
go-ahead. The service is live at <https://review-production-8f474051.up.railway.app> (Railway
project `sacredtexts-review`). One step is still open: the in-browser sign-up → label → reload →
download check on the hosted origin is waiting on a human (see [Hosted deployment](#hosted-deployment-review-phase-2026-11-10)).

## Spec Compliance

- [x] **Sample CLI** (Phase 1). `sacredbench review-sample` reads a run without writing to it, and
  refuses `--out` under `runs/`. It takes min(N, k) cells per outcome × task × text stratum, in
  sha256(seed‖cell id) order, and records the seed, k, the run, the stratum sizes and the order.
  Only scored cells are eligible. The same inputs give byte-identical output, and a different seed
  gives a different draw. All of this is tested.
- [x] **FAccT sample committed** (Phase 1). `review/samples/facct-2026-11-03-k10.json`: seed
  `spec-154`, k = 10, 1,423 cells, 151 strata, 13 texts. NRSV is included (111 cells). A pin test
  regenerates the file byte for byte from `runs/`, and nothing under `runs/` changed.
- [x] **Accounts ported unchanged** (Phase 3). The ported pieces, with multibench's tests:
  - invite-gated signup, fail-closed when the code is unset;
  - login, logout, `me`, the CSRF fetch and account delete.

  The one change is the cookie names; see Deviations. Two accounts review independently: walk
  step 6 had B, signed up in the same tab, see none of A's labels.
- [x] **Text picker** (Phases 5–6). The chosen texts live in the server draft, so they follow the
  reviewer across devices. The pass holds only the chosen texts' cells, in sample order, and with
  nothing chosen there is an explicit prompt. Walk steps 2 and 5 cover it.
- [x] **Labelling page** (Phase 6, plus a Phase 7 fix).
  - It reuses the explorer's `QuestionCard`, so the prompt, expected text, answer, verdict,
    submetrics and grader path show together.
  - It also shows the task's rubric and its version.
  - It records the outcome, notes and the defect flag.
  - RTL scripts render with `dir`/`lang` set and a script-capable font stack.
  - The no-invisible-text checks pass, and progress shows labelled / in pass, per text.
  - Phase 7 added a "Passage source" line on `verify_source` cells.
- [x] **Drafts with the multibench fixes** (Phase 3 for the API, Phase 5 for the client).
  - A stale write gets 409 with the current state, and the client reconciles.
  - Each fix has a regression test:
    - no cross-reviewer state on an account switch or a 401;
    - a failed load never overwrites saved labels;
    - a CSRF 403 refreshes and retries;
    - a slow list load never clobbers a newer one.
  - A session counter also stops requests already in flight from leaking across a reset (codex,
    Phase 5).
  - Bodies are capped at 8 MiB on both sides, and the two caps are pinned equal.
- [x] **Gold-set download** (Phases 5–6).
  - JSONL, one row per labelled cell, holding every field the spec lists. The reviewer is
    identified by account id only.
  - Rows are sorted stably, and the bytes are canonical. A shared fixture pins them equal to the
    Python writer.
  - Two downloads were byte-identical in walk step 7.
- [x] **Version-comparison CLI** (Phase 2).
  - `review-compare` takes `committed`, `current`, or a run directory.
  - It reports agreement overall and per task, text and grader path, and counts `can't judge`
    and defect rows separately.
  - It lists every disagreement, and the fixed / broken / neither movers.
  - A hand-built 10-row gold set pins its numbers, including a real #94 mover that a scorer
    change fixes. Walk step 8 ran it.
- [x] **One service** (Phase 4; walk in Phase 7).
  - One Hono process serves `/api` and the built UI from one origin, against Postgres.
  - Locally, the walk went from sign-up to the comparison and is recorded below.
  - The static Cloudflare build (`build:pages`) still builds. Its review routes show "Review
    service unavailable", which a Phase 6 test covers.
- [x] **Test gate** (Phase 3). `apps/api` is registered in `.codev/checks/test.sh` and runs on
  PGlite with no external database. Final gate: green at 4bb2ca77: `apps/api` 89/89, `apps/viewer` 399/399, `pipelines` 1569 passed / 35 skipped (the copyright audit included).
- [x] **Schema discipline** (Phase 3). There is one migration, `drizzle/0000_review_store.sql`,
  made with `drizzle-kit generate` and reviewed. It is applied by `pnpm migrate`, and on Railway by
  the pre-deploy step. `db:push` was never used, and no script for it exists.
- [x] **Hosting is gated** (Phases 4 and 7; provisioned in the review phase). The PR ships the
  Dockerfile and the runbook, and nothing was provisioned until the owner's explicit go-ahead
  (2026-11-10T21:34Z, relayed by the architect), which came after the local walk passed. The
  hosted in-browser check is open; see below.

### Local end-to-end walk (phase 7, 2026-11-10)

Run against a real Postgres and in a real browser (Chrome, through the claude-in-chrome
extension), as the plan's phase 7 sets out. Nothing was provisioned.

#### Setup

- Database: `createdb sacredtexts_review_dev` on the local Postgres (`localhost:5432`), then
  `pnpm -C apps/api migrate`, which created the 4 tables. This is the only database the walk
  created. To remove it: `dropdb sacredtexts_review_dev` (also in `apps/api/README.md`).
- Viewer: `pnpm -C apps/viewer build` (the plain build, with no runs baked in).
- Service: `pnpm -C apps/api start` with `SAMPLE_PATH` set to
  `review/samples/facct-2026-11-03-k10.json`, `VIEWER_DIST` set to `apps/viewer/dist`, and a
  local-only invite code. It logged the active sample `facct-2026-11-03-k10`, and
  `/api/health` returned `{"status":"ok","db":"up"}`.
- Accounts: two throwaway accounts, `reviewer-a@example.test` and `reviewer-b@example.test`,
  in the local database only.
- Screenshots and captured files are in the session scratchpad. None is committed.

#### Steps

| # | Step | Result |
|---|---|---|
| 1 | Sign up with the invite code | Pass. "Create a reviewer account" accepted the code and signed Reviewer A in. The page showed the sample header (`facct-2026-11-03-k10`, 1,423 cells, seed `spec-154`, 10 per stratum) and the 13 texts. |
| 2 | Pick the Qur'an (Uthmani), the Talmud (Aramaic) and the Sri Guru Granth Sahib | Pass. The pass became 339 cells (101 + 120 + 118), in sample order, with a progress bar per text. |
| 3 | Arabic, Hebrew and Gurmukhi render legibly and in the right direction | Pass. Hebrew prompts and answers render right-to-left and right-aligned. Arabic inside an English prompt is embedded right-to-left with its marks intact. Gurmukhi renders left-to-right with correct shaping. The Arabic note typed into the notes box runs right-to-left (`dir="auto"`). |
| 4 | Label 5 cells, with notes in Arabic and a defect flag | Pass, with 6 cells labelled: 3 Talmud, 1 Qur'an, 2 SGGS. The Qur'an `verify_source` cell has a refusal ("نعم" only at the end), labelled `refused` with an Arabic note. Both SGGS cells carry the defect flag: the first with a note, the second set while checking the dropped clicks (below). The server's draft held all 6 labels byte for byte, the Arabic note included. |
| 5 | Reload, and the labels persist | Pass. After a hard reload of a deep-linked cell and of `/review`, the outcome, the notes (Arabic included), the chosen texts and the progress (6 / 339; 1, 3 and 2 per text) all came back from the server. |
| 6 | Sign out, sign in as a second account, and it sees none of the first's labels | Pass. Reviewer B signed up in the same tab, without a reload (the cross-reviewer leak path). B saw no chosen texts and 0 labels. The cell A labelled showed no outcome and empty notes. |
| 7 | Sign back in, download the gold set twice, and the two files are identical | Pass. Signed back in as A: the 6 labels were back. The two downloads were byte-identical: 12,015 bytes, 6 rows, the same SHA-256. |
| 8 | `review-compare --version committed --version current` on it gives a report | Pass. 6 gold rows from 1 reviewer. It judged 4 and excluded the 2 defect-flagged rows. Both versions agreed 4 / 4, with no disagreements and no movers. |
| 9 | `/api/sample` is 401 when signed out | Pass. With curl before any sign-in, and from the browser after signing out: `401 {"error":"unauthorized"}`. |

#### How the downloads were captured

To keep the files out of the user's Downloads folder,
the page's `<a download>` click was hooked in the page. The hook read the very Blob the
**Download gold set** button produced and posted its bytes to a local receiver, which wrote
them to the scratchpad. The download code path (`buildGoldSet` → Blob → anchor) ran
unchanged.

#### What the walk turned up

- **Fixed: a `verify_source` "No" cell hid where its passage comes from.** The card shows only
  the expected Yes/No. On a "No" item (about a third of the sample's 389 `verify_source` cells
  have a blank citation) the reviewer couldn't see which text the passage really quotes, and
  needs that to use the question-defect flag (does the Talmud quote Judges 17:11?). The sample
  already carries it in `expected.true_*`. The cell page now shows "Passage source: <citation>
  · <version> · <tradition>" under the card (`ReviewCellPage.tsx`, with a test). The explorer is
  unchanged. After a rebuild and a service restart, the line showed in Chrome on the Talmud
  "No" cell that quotes Judges 17:11.
- **Documented: the service reads `index.html` once.** A viewer rebuilt while the service runs
  gives a blank page: the old shell points at bundles the rebuild deleted, and a missing
  `/assets/*` path gets the SPA shell with a 200. That is a local dev-loop issue only: a deploy
  builds before it starts. The local runbook now says to restart after a rebuild.
- **Not a defect: dropped clicks.** Two quick clicks in a row through the browser automation
  sometimes never reached the page. An event log showed no pointer events at all for the
  dropped clicks, and every click that arrived toggled the control correctly. Leaving a
  second between clicks fixed it.
- **Data note, not changed:** a `verify_source` cell's `true_tradition` is the generator's
  label, so the Masoretic Text shows as "Christianity". It's shown as recorded.

### Hosted deployment (review phase, 2026-11-10)

Provisioned on the owner's go-ahead. The conditions were: a new Railway project, one service plus
Postgres, the smallest tiers, a daily backup, and nothing ingested beyond the committed sample.

- **Project** `sacredtexts-review` (workspace Haadi), separate from multibench.
  - Service `review`: one replica.
  - Postgres: one instance, no HA or PITR.
  - A **daily** volume backup at 06:07 UTC, kept 6 days.
  - Nothing asked for payment or a plan change.
- **Build**: `apps/api/Dockerfile`, with the repo root as context.
  - Before deploying, it was built locally and run against a fresh local Postgres. The migrations
    ran twice (the second run was a no-op). The shell, the bundles, a missing-asset 404, the 401s,
    and a sample byte-identical to the committed file all checked out, as did a signup, a v1 save
    and the unknown-sample 404.
  - The Railway build produced the same bundle hash as the local one (`index-nRIXznEL.js`).
- **Variables**:
  - `DATABASE_URL` references Postgres's private URL, and Postgres has no public proxy.
  - `SAMPLE_PATH` is absolute.
  - `REVIEW_INVITE_CODE` was generated locally and set through stdin. It is held only in Railway
    and the gitignored root `.env`.
- **Checked over HTTPS without an account** (all pass):
  - the pre-deploy step logged `migrations applied`;
  - the database holds 4 tables and 0 rows;
  - `/api/health` reports the database up;
  - `/`, `/review` and the deep links serve the app;
  - the bundle is gzipped (145 of 486 KB);
  - a missing `/assets/*` returns 404;
  - `/api/sample` and `/api/auth/me` return 401;
  - the cookies are `Secure; SameSite=None`;
  - in Chrome, `/review` shows the sign-in and create-account forms;
  - the service did not log the "signup is CLOSED" line, so the invite code is set.
- **Open: the in-browser sign-up → label → reload → download check.** A builder agent doesn't create
  accounts or enter passwords or invite codes on a production host. The architect has been asked to
  have a human run it. It takes about 3 minutes with the code from `.env`.

## Deviations from Plan

- **Phase 1:** none of substance. From the consult nits, `texts[].cells` was renamed to
  `texts[].drawn` before the TS type pinned it, and `--out` is refused under `runs/`.
- **Phase 2:**
  - **The gold-set bytes are canonical**: compact JSON, keys sorted at every level, non-ASCII
    written raw. Integral floats are written as ints, and a float whose shortest form differs
    between Python and JS fails loudly. This is so the TS and Python writers agree byte for byte.
  - The fixture grew to 10 cells, adding judged `verify_source`, `refused` and false-premise rows.
- **Phase 3:**
  - The cookies are named `st_session`/`st_csrf` instead of `mb_*`. Cookies are scoped by host,
    not port, so a multibench API on `localhost` would otherwise clobber our session.
  - Beyond the plan's file list, an `api` job was added to `.github/workflows/tests.yml`.
- **Phase 4:**
  - Phase 3's consult asked for an **active-sample guard**, now in place: a PUT or submit for any
    other sample is 404. Reading, listing and deleting stay open.
  - `testTimeout` is 20 s, because the first cold PGlite boot timed out at 5 s.
  - Compression, `PORT` validation and fail-fast on a zero-cell sample came from consult notes.
- **Phase 5:**
  - Dropped from the multibench store: its `reviewer` info, JSON import/export, `evenSample`/`seededSample`
    and the submission client calls. Sampling is the committed Python draw, and the output is the
    gold-set download.
  - Added: an `"unavailable"` auth state, terminal (non-retried) saves and deletes on a permanent
    4xx, and the session counter.
- **Phase 6:**
  - A Spec 2 purge guard in `app.test.tsx` asserted that there was no "Review" link. That one
    assertion was dropped, because the plan's nav link reverses it on purpose.
  - `lang` on `QuestionCard` is optional.
  - HeroUI v3's `accent` replaces multibench's `primary`, a token v3 doesn't have.
- **Phase 7:** a "Passage source" line on `verify_source` cells, found by the walk. The service
  reads `index.html` once at startup; that is documented, not changed.
- **Review phase (hosting):**
  - **Provisioned**, where the plan had shipped config only. The owner's go-ahead superseded spec
    Open Question 2's "not approved", and the spec notes it.
  - **A Dockerfile instead of the Nixpacks `railway.json`.** The repo root has `requirements.txt`
    and no `package.json`, so auto-detection would build Python.
  - **`apps/api/railway.json` deleted.** Railway rejects a config-as-code path on a new service, so
    its settings are set on the service and documented in the README.
  - `migrate.ts` resolves `drizzle/` from its own file.
  - A missing `/assets/*` is now a 404 (deferred from Phase 7).
  - `.codev/checks/test.sh` maps `apps/api` changes to the viewer lane too, because the viewer
    pins the API's body cap.
  - The integration review's four fixes:
    - a body cap on the auth routes;
    - logout fails loudly, with a CSRF retry;
    - `current` needs the default graders;
    - the spec says "run directory".

    Two of these change behaviour inherited from multibench on purpose: the auth body cap and the
    logout check.

## Consultation Feedback

The reviewers were codex and claude throughout; `.codev/config.json` drops Gemini from the
per-phase consults. There were no `CONSULT_ERROR`s.

### Specify Phase (Round 1)

Both reviewers requested changes. Every point was taken (9a780cec). The owner's rulings at the spec
gate then superseded most of that design (not blind, an even stratified sample, texts not
languages, one reviewer, no stats), and the spec was rewritten.

#### Codex
- **Concern**: critical behaviour left unresolved (rubric, NRSV, assignment, allocation, topology) → **Addressed**: explicit defaults D1–D10.
- **Concern**: statistical estimands ambiguous → **Addressed**, then **N/A**: added, then dropped by the owner's "plain counts, no stats" ruling.
- **Concern**: a self-declared digest isn't a trust anchor → **Addressed**, then **N/A**: superseded, because the committed sample is pinned by a test, not ingested.
- **Concern**: sampling not deterministic → **Addressed**: sha256(seed‖cell id) order.
- **Concern**: privacy disclosure and pseudonyms → **Addressed**, then **N/A**: one-reviewer base case, and the gold set carries the account id only.

#### Claude
- **Concern**: the rubric contradicts Spec 48 / #23 → **Addressed**: the rubric follows class A/B, the leading stance, the #150 head and containment.
- **Concern**: the remaining design points → **Addressed** in the same revision.

### Plan Phase (Round 1)

#### Codex
- **Concern**: labels don't keep their rubric version or time → **Addressed**: each label is stamped on a real edit.
- **Concern**: the download reads the clock, so downloads differ → **Addressed**: it is clock-free and byte-identical.
- **Concern**: the 2 MB cap assumes single-byte notes → **Addressed**: an 8 MiB cap, plus a client byte guard.
- **Concern**: no font strategy and no Gurmukhi coverage → **Addressed**: a script-text font stack, plus a Gurmukhi test.
- **Concern**: the external version lookup isn't run-aware → **Addressed**.

#### Claude
- **Concern**: the committed sample sits outside the copyright audit → **Rebutted**: the owner ruled it fair use (counsel). Recorded in the arch docs.
- **Concern**: Phase 4 rebuilds an existing static host → **Addressed**: it ports `apps/viewer/server/index.mjs`.
- **Concern**: the store would retry a 413 forever → **Addressed**: a 413 is terminal.
- **Concern**: minor points (prompt arms, Phase 6 too big, an env inventory, `:` in route params, sample size) → **Addressed**: Phase 6 split into 6 and 7; `reviewLinks.ts`.

### Phase 1 (Round 1)

Both APPROVE.

#### Claude
- **Concern**: the `load_sample` shape is unvalidated; `--out` can land under `runs/`; untested error paths; `cells` → `drawn` → **Addressed** (feb19864).
- **Concern**: `_text_label` uses `.capitalize()` → **N/A**: cosmetic only. The one multi-work text renders as "Encyclicals — 26 works".

### Phase 2 (Rounds 1–3)

#### Codex
- **Round 1 concern**: the real `python -m sacredbench` entry point loads the providers module → **Addressed**: an offline entry-point test, with sockets refused and SDK imports blocked.
- **Round 1 concern**: make `cli.py`'s provider imports lazy → **Rebutted**: that touches collect/score/main and is out of the phase's scope, and the module loads no SDK.
- **Round 2 concern**: `runs/<run>//etc/passwd` escaped the run-directory lookup → **Addressed** (b0e0fa61): a canonical-path check plus a component-wise join, with a regression test.
- **Round 3**: APPROVE.

#### Claude
- **Rounds 1–2 notes** (a fixture gap, the `scores_path` check, README wording, an unsorted-rows hint, `excluded.both`, the expected-key check, a CLI smoke test) → **Addressed**.
- **Round 2 note**: directory versions are bound to `runs/<run>/` → **Rebutted**: that is as planned.
- **Round 2 note**: the AR_CITE mover is a rubric-vs-matcher divergence → **N/A**: a follow-up (below).
- **Round 3**: APPROVE. Follow-ups (a)–(d) → **N/A**: listed under Follow-up Items.

### Phase 3 (Round 1)

Both APPROVE.

#### Claude
- **Concern**: the stated worst-case size differs between files → **Addressed**: ~6.2 MB, measured.
- **Concern**: `sampleId` is unvalidated → **Addressed** in Phase 4 by the active-sample guard.
- **Concern**: the signup/login bodies have no `bodyLimit` → **N/A**: inherited from multibench. A follow-up.

### Phase 4 (Round 1)

Both APPROVE.

#### Claude
- **Concern**: no compression on the 2.8 MB sample → **Addressed**: `hono/compress`.
- **Concern**: `PORT=""` binds port 0 → **Addressed**: it exits.
- **Concern**: a zero-cell sample starts → **Addressed**: it fails fast.
- **Concern**: no ETag → **N/A**: compression covers most of the cost. A follow-up.

### Phase 5 (Rounds 1–2)

#### Codex
- **Round 1 concern**: requests in flight leak across a reviewer reset → **Addressed**: a session counter plus an enqueue gate, with 8 mutation-checked tests.
- **Round 2**: APPROVE.

#### Claude
- **Round 1 concern**: two new tests flaky in a full run → **Addressed**: it had reviewed a tree mid-edit. The tests park the PUT before the switch, and the suite was green 3/3.
- **Round 1 concern**: `persistDelete` lacked the terminal rule; a vacuous assertion → **Addressed**.
- **Round 1 concern**: `logout()` ignores `res.ok` → **Rebutted**: multibench parity. Recorded as a follow-up.
- **Round 2**: APPROVE, with informational notes → **N/A**:
  - the `ExplorerPage` flake (Flaky Tests);
  - `persistSample`'s early-return cleanup (a follow-up);
  - the queued-save test being characterization only.

### Phase 6 (Round 1)

Codex APPROVE. Claude COMMENT (HIGH).

#### Claude
- **Concern**: a cell page opened directly claims "not one of your chosen texts" before the draft loads → **Addressed**: the pass position, prev/next and that note wait for `draft.loaded`. Two tests cover it, and reverting the fix turns them red.

### Phase 7 (Round 1)

Both APPROVE.

#### Claude
- **Concern**: the defect-flag counts don't reconcile between walk steps 4 and 8; NRSV "29 distinct verses"; the `PassageSource` gate → **Addressed** (160c42ae).
- **Concern**: a missing `/assets/*` gets the shell with a 200 → **Addressed** in the review phase (dab6fbb8).

### PR review (Round 1) and the architect's integration review

Codex REQUEST_CHANGES. Claude APPROVE (HIGH, with notes). The architect's integration review drew
on its own consults (the Gemini lane was skipped, `agy` exit 3) and named four fixes (26956177).

#### Codex
- **Concern**: the signup and login bodies have no `bodyLimit` → **Addressed**: a 16 KiB cap (`AUTH_BODY_MAX_BYTES`) before parsing, with 413 tests. Removing the cap turns 3 tests red.
- **Concern**: the hosted sign-up → label → reload → download check isn't done → **N/A** for the builder: it needs a human account on the production host. The architect ruled that it doesn't block the merge, but it does gate inviting reviewers.
- **Concern**: the consult files for phases 2–7 are untracked, while those for the spec, the plan and phase 1 are committed → **Addressed**: on the architect's ruling, the consult, context and rebuttal files for phases 2–7 and the review round are committed, as other projects do.

#### Claude
- **Notes** (none blocking) → **N/A**, follow-ups:
  - `SameSite=None` → `Lax`;
  - re-affirm "no rate limiting" now that the service is public;
  - the submissions routes have no client caller;
  - the TS `canonicalJson` lacks the Python divergent-float guard;
  - the `load_gold` order check covers `cell_id` only.
- **Concern**: narrow the `review/` audit exemption to an NRSV allowlist → **Rebutted** by the architect: the owner ruled it fair use, with no copyright machinery.

#### Architect (integration review)
- **1. Unbounded bodies on the public auth routes** → **Addressed**, as in codex's point above.
- **2. Logout reports success when the server refused it** → **Addressed**:
  - `reviewApi.logout()` throws on a non-2xx.
  - `logoutReview()` refreshes a stale CSRF token and retries once. Any other refusal, or a second
    one, leaves the reviewer signed in, and the badge says "Couldn't sign out".
  - Tests: a stale-token retry signs out, and a persistent refusal stays signed in. Each half is
    mutation-checked.
- **3. `review-compare --version current` with a non-default evaluator** → **Addressed**:
  - `current` reads each row's run `summary.json` `evaluators`. It fails fast when they aren't the
    default `strict` + `containment` (in any order) or the summary is missing.
  - `committed` and run-directory versions read recorded verdicts and are unaffected.
- **4. Spec wording** → **Addressed**: a version is `committed`, `current`, or a run directory
  laid out like `runs/<run>/`.

## Lessons Learned

### What Went Well

- **Porting instead of rebuilding.** The multibench API, auth and store came over with their fixes.
  Most of the work went into the parts that really differed: the sample, the gold set and the
  version comparison.
- **The cross-language byte contract.** Deciding the canonical gold-set bytes in Phase 2, then
  pinning both writers to one fixture, made the TS download and the Python reader agree on the
  first try.
- **The real walk found a real gap.** The missing passage source on `verify_source` "No" cells
  was invisible to every test.
- **Verifying the image locally first.** The first Railway deploy passed on the first try because
  the same image had already run the migrations twice and served the app against a local Postgres.

### Challenges Encountered

- **The store's async edges.** The leak across a reviewer switch (requests in flight landing in
  the next session) came from codex, not from the ported fixes. It took a session counter and an
  enqueue gate, each guard mutation-checked.
- **Test races.** One store test, one page test, and the pre-existing explorer flake needed a
  deterministic park point or a `waitFor` before they were stable across full runs.
- **Railway's moving surface.** A config-as-code file path is rejected on new services, and the
  `Builder` enum has no DOCKERFILE. A `dockerfilePath` set on the service was enough, and the dead
  `railway.json` was removed.
- **The hosted check needs an account.** The agent can't create one on a production host, so the
  last check is a human step.

### What Would Be Done Differently

- Plan the hosted completion check as a human step from the start, and have the agent prepare
  everything around it.
- Prove the deploy mechanism (Dockerfile vs. auto-detect, whether a config file is read) in the
  plan's hosting phase, not at provision time.

### Methodology Improvements

- For a project that ends in a deploy, the plan's hosting phase should list which checks an agent
  can run and which need a human account.
- The per-builder dispatcher should be checked for **cross-lane reads** (one app's test reading
  another app's source) whenever an app is added. This project found one (`apps/api` →
  `apps/viewer`).

## Architecture Updates

- Routed: cold — `arch.md` gains a § **Review tool** (sample, service, UI, gold set, compare,
  hosting, copyright ruling), plus `apps/api/` and `review/` in Repository shape and the new lanes
  in Test gate. The viewer section's "`/review*` gone" now notes that `/review` is back.
- Routed: hot — `arch-critical.md`, with no new entry (it holds 10 facts):
  - `/review` and `apps/api` are folded into the existing viewer fact;
  - the owner's fair-use ruling (`review/` samples are outside the audit, NRSV included) is folded
    into the copyright-audit fact, so the two don't read as a contradiction;
  - the map gains the Review tool section.

## Lessons Learned Updates

- Routed: hot — `lessons-critical.md`'s dispatcher lesson now lists the `apps/api` and `review/`
  lanes, and states that a path read by two lanes must map to both.
- Routed: cold — `lessons-learned.md` § Process / SPIR gains three entries:
  - prove a hosting config is actually read (Railway's config-as-code rejection);
  - a hosted check that needs an account is a human step;
  - verify the container image locally against a real database before the first deploy.

## Flaky Tests

- `apps/viewer/src/routes/ExplorerPage.test.tsx`, the wrong-answer filter test (about line 98).
  It is a pre-existing flake, caused by a missing `waitFor`. It failed about once in 10 full viewer
  runs during phase 6, and claude saw it once in 4 in phase 5. It isn't in this project's files and
  wasn't changed or skipped.

## Follow-up Items

- **The hosted in-browser check** (sign-up → label → reload → download), by a human.
- **The deploy source.** Connect the `review` service to `main` for deploys on merge, which is the
  owner's call: `railway service source connect --repo faithfamilytechnologynetwork/sacredtexts --branch main --service review`.
  Until then, redeploy with the `git archive` + `railway up` recipe in `apps/api/README.md`.
- **The AR_CITE rubric-vs-matcher divergence.** The rubric discounts only a *disclaimed* echo of the
  form example, but #118 drops an undisclaimed one beside another citation (`34:46 أو 3:140` scores
  correct). The owner should decide which one moves.
- **Multi-reviewer agreement is per label.** A cell labelled by two reviewers counts twice in `n`.
- **`grader_path` is approximate** for a version scored with a non-default grader set. It is used
  for breakdowns only, never a verdict.
- **The NRSV figure** in `review/README.md` (105 cells, 28 distinct verses) is not pinned and can go
  stale if the sample is regenerated.
- **No ETag on `/api/sample`.**
- **The sign-in-while-signed-in residual window.** No UI path reaches it today.
- **`persistSample`'s early returns skip the `saving: false` cleanup.** This is unreachable today,
  because a delete always follows.
- **The router's `location.pathname` shows a decoded space.** The href and the matched cell are
  right.
- **The Review nav item is active only on `/review` exactly**, not on `/review/cell/…`.
- **The `true_tradition` label** comes from the generator and is shown as recorded: WLC shows as
  "Christianity".
- **Spec nice-to-knows:** `SameSite=None` → `Lax` now that everything is on one origin; pruning
  expired sessions; finer grader-path labels.
- **From the PR review:**
  - Tests for the two unpinned store guards: the in-flight edit on the LWW retry, and the CSRF
    refresh on the delete path.
  - The dead `dirty.size === 0` check.
  - Name the lost label when a double conflict discards it.
  - Re-affirm "no rate limiting" now that the service is public.
  - The unused submissions routes.
  - The TS `canonicalJson` divergent-float guard.
  - `load_gold`'s order check on the full sort key.

  All of these, plus the ETag, `SameSite=Lax`, session pruning and connecting the service to
  `main`, are tracked in **#156**.
