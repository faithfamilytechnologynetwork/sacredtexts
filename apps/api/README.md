# `apps/api`: the review service

A small Postgres-backed service that holds the human review store for Spec 154: reviewer accounts,
one review draft per reviewer per sample, and immutable submissions. Reviewers label the cells of a
committed review sample (`review/samples/<sample_id>.json`); their labels live here and come out as
a gold set (`GET /api/gold-set`) that `sacredbench review-compare --from-service` reads.

The same service is the whole review deployment: it serves `/api`, the active sample, and the built
viewer from **one origin** (see [Topology](#topology)).

It is ported nearly verbatim from multibench's `apps/api` (its Spec 92), including the fixes in its
history. The changes from multibench:

- Drafts and submissions are keyed by **sample** (`sample_id`), not by tradition.
- The GitHub-issue publish column (`published_issue_url`) and its validation are removed.
- The draft and submit body cap is **8 MB** (bytes), up from 512 KB.
- The cookies are named `st_session` / `st_csrf`. Browsers scope cookies by host, not port, so
  multibench's `mb_*` names would collide with a multibench API running on `localhost` too.
- There is no edge proxy. multibench needed one so a separate SPA host and the API could share an
  origin; here this service serves the built viewer itself.

Run evidence under `runs/` is never read or written by this service.

## Stack

- **Hono**: the HTTP framework.
- **Drizzle**: the ORM and the **single schema authority**. Migrations are explicit:
  `drizzle-kit generate` → **review the SQL** → apply. **Never `db:push`.**
- **node-postgres** (`pg`) when it runs; **PGlite** (in-process Postgres) for tests, so
  `pnpm test` needs no external database.
- **tsx** runs the TypeScript directly (no emit step); `pnpm build` is a typecheck.

## Scripts

Run from `apps/api` (or `pnpm -C apps/api <script>` from the repo root). Install first with
`pnpm install --frozen-lockfile`.

| Command | What it does |
|---|---|
| `pnpm dev` | Run with reload (`tsx watch src/server.ts`). |
| `pnpm start` | Run the server (`tsx src/server.ts`). |
| `pnpm migrate` | Apply the committed migrations in `drizzle/` to `DATABASE_URL`. |
| `pnpm build` | Typecheck (`tsc --noEmit`). |
| `pnpm test` | Run the vitest suite (PGlite-backed). |

The suite is registered in the porch test gate (`.codev/checks/test.sh`), so it runs whenever a
branch touches `apps/api/`.

## Topology

One Hono process, one origin:

| Path | Served by |
|---|---|
| `/api/*` | The API routes below. An unmatched `/api` path is always a JSON 404 `{error: "not found"}`, never the viewer. |
| `GET /api/sample` | The active sample file, as committed (validated once at startup). |
| any other `GET`/`HEAD` | With `VIEWER_DIST` set: a file from the built viewer, else `index.html` (the SPA history fallback, so `/review/...` deep-links work). Without it: a JSON 404. |

The static serving ports the in-repo viewer host (`apps/viewer/server/index.mjs`: `serveStatic` plus
an `index.html` fallback). The differences are that `/api/*` is excluded from both, and only `GET`
and `HEAD` are served.

The run data a `build:pages` dist bakes under `dist/runs/` is served the way Cloudflare Pages serves
it, so the viewer behaves the same on both hosts:

- A found file gets the headers the dist's `_headers` file (the viewer's `public/_headers`) gives
  its path: every `/runs/*` file as `text/plain; charset=utf-8`, so it is compressed, and
  `/runs/_index` and `/runs/_gaps` as `no-cache`. The service reads `_headers` at startup and stops
  on a rule it can't read (only exact paths and a trailing `*` are supported).
- An encoded run id (`/runs/archive%2F<name>/summary.json`, as the client requests it) gets a
  **307** to the decoded path, as Pages' asset server answers it. Outside `/runs/` an encoded `/`
  is left alone, so a review cell id that holds one still deep-links.
- A missing run file gets the SPA shell, as on Pages. The client reads that as "absent".
- Every served file carries a validator: a weak `ETag` from its size and mtime, plus
  `Last-Modified`. A matching `If-None-Match` gets an empty **304**. A `/runs/*` file that `_headers`
  gives no `Cache-Control` gets `no-cache`. So a revisit revalidates instead of re-downloading
  about 70 MB of baked run files, and a redeploy's new runs show at once.

Responses are gzip- or deflate-compressed for a client that accepts it (`hono/compress`). That matters
for the sample (2.8 MB, about 0.5 MB gzipped) and the viewer bundle, because nothing sits in front of
the service.

**One active sample.** `SAMPLE_PATH` names it. Drafts and submissions are accepted for that sample
id only. A save or submit for any other id gets 404 `{error: "unknown sample"}`. Reading, listing and
discarding drafts still work for every id, so a draft from an earlier sample stays visible and can be
removed.

**What the review origin shows.** The full viewer, over **one run: `facct-2026-11-03`** (#159). The
image builds the viewer with `build:pages`, the Cloudflare Pages command, but copies in only the runs
the Dockerfile names (and `items/for-test/`), so `/`, `/errors`, `/standings` and `/gaps` see that
run alone and `/runs/_index` has one entry. The Pages deploy still bakes all of `runs/`; its build is
unchanged.

- **The list.** The viewer stage of `apps/api/Dockerfile` has one `COPY runs/<id> runs/<id>` line per
  hosted run, and that is the only place the hosted set is named. To host another run, add its line
  (an archive run is `runs/archive/<name>`) and redeploy. A named run that is missing fails the
  build, and no other directory under `runs/`, tracked or not, reaches the image. Untracked files
  inside a named run would reach a local `docker build`. The `git archive` deploy carries only
  tracked files.
- **The test.** `apps/viewer/vite/hostedBake.test.ts` reads the list, bakes exactly those runs, and
  checks the index, the artifacts, and that the review sample's `source_run` is among them. It also
  pins the list to `facct-2026-11-03`, so changing the hosted set means editing that line too.
- **Judge and Findings are empty here.** Both pages read `/runs/_judge`, built from the Jev
  `judgments-v5.jsonl` files. Those sit only under the top-level panel folders (`runs/<model>/`),
  not under `facct-2026-11-03`, so on this origin both pages show "No judgments-v5 files yet."

**The viewer's own host is untouched.** `apps/viewer/server/index.mjs` (its `pnpm start`), its
smoke test and `apps/viewer/railway.json` are the pre-existing static-only host and stay as they are.
Whether any live service still uses that config is the owner's call. The **review** deployment is
built from `apps/api/Dockerfile` (see [Hosting](#hosting)), not from the viewer's config.

## Configuration

Copy `.env.example` to `.env`, or set the variables in the environment. Secrets (the database URL
and the invite code) come from the environment only. A relative path resolves against the directory
the service starts in, which is `apps/api` under `pnpm -C apps/api start`. The hosted image uses
absolute paths (see [Hosting](#hosting)).

| Variable | Required | Behaviour |
|---|---|---|
| `DATABASE_URL` | yes | Postgres connection string. The server and the migrator exit if it is unset. |
| `SAMPLE_PATH` | yes | The committed review sample to serve. The server exits if it is unset, unreadable, not JSON, not `format: 1`, missing a required key, or has no cells. |
| `VIEWER_DIST` | no | The built viewer (`apps/viewer/dist`). When set, it is served beside `/api`, and the server exits if its `index.html` is missing. Unset ⇒ API only (local dev behind the Vite proxy). |
| `REVIEW_INVITE_CODE` | no | Shared signup code. **Fail-closed:** unset ⇒ signup is disabled (login still works). |
| `ALLOWED_ORIGINS` | no | Comma-separated CORS allow-list for credentialed requests. Empty is correct when the UI is same-origin; never `*`. |
| `PORT` | no | Listen port, default 8080. Set but not a port from 1 to 65535 (including empty) ⇒ exit. |

At startup the server logs the active sample id, whether it is serving the viewer, the CORS
allow-list, and whether signup is open.

## Endpoints

All live under `/api`.

| Method and path | Auth | What it does |
|---|---|---|
| `GET /api/health` | — | 200 `{status:"ok"}` when Postgres responds, 503 otherwise. |
| `POST /api/auth/signup` | invite code | Email + password + name (+ optional `background`). Sets the session and CSRF cookies; returns `{reviewer, csrfToken}`. JSON only. |
| `POST /api/auth/login` | — | Email + password. Same cookies and response. JSON only. |
| `GET /api/auth/csrf` | — | Returns the CSRF token paired with the CSRF cookie (minting one if absent), so a reloaded page can recover it. |
| `POST /api/auth/logout` | CSRF | Deletes the session row and clears both cookies. |
| `GET /api/auth/me` | session | The signed-in reviewer `{id, email, name, background}`. |
| `DELETE /api/account` | session + CSRF | Deletes the reviewer; the database cascades to their sessions, drafts and submissions. |
| `GET /api/sample` | session | The active sample, byte-for-byte as committed (`application/json`). |
| `GET /api/review` | session | All of the reviewer's drafts: `{drafts: [{sampleId, state, version}]}`. |
| `GET /api/review/:sampleId` | session | The reviewer's draft for a sample: `{state, version}`, or `{state: null, version: 0}`. |
| `PUT /api/review/:sampleId` | session + CSRF | Save `{state, version}` (below). Active sample only, else 404 `{error: "unknown sample"}`. |
| `DELETE /api/review/:sampleId` | session + CSRF | Discard the draft ("start over"). Idempotent. |
| `POST /api/review/:sampleId/submit` | session + CSRF | Freeze `{review}` as a new immutable submission. Returns `{submission: {id, submittedAt}}`. Active sample only, else 404 `{error: "unknown sample"}`. |
| `GET /api/review/:sampleId/submissions` | session | The reviewer's submissions for the sample, newest first (metadata only). |
| `GET /api/gold-set` | session | The reviewer's gold set for the active sample, as JSONL (`application/jsonl`), built from their saved draft. See [Gold set](#gold-set). |

**Drafts.** `state` is the viewer's per-sample review state (the chosen texts and the per-cell
labels). The API stores it opaquely as JSONB and does not validate its inner shape; it only requires
an object. JSONB does not keep object key order, so a client must not depend on it. Saves use
optimistic concurrency:

- `version: 0` creates the draft and returns `{version: 1}`.
- `version: N` updates only if the stored version is `N`, and returns `{version: N+1}`.
- Anything else (a stale version, or a second create) is **409** with
  `{error: "conflict", state, version}` holding the current draft, so the client can reconcile.

A reviewer only ever reads or writes their own rows: every query is keyed on the session's reviewer
id, so a conflict never leaks another reviewer's draft.

**Body cap.** `PUT /api/review/:sampleId` and `POST …/submit` reject bodies over **8 MB** (counted
in bytes) with **413**. The cap is sized from a maximal draft: 1,500 labels, each with a
1,000-character note of 4-byte UTF-8 characters plus ids and metadata, is about 6.2 MB. The client
caps notes at 1,000 characters and checks the byte size before sending.

### Gold set

`GET /api/gold-set` returns the bytes the review page's **Download gold set** saves for the same saved
labels. `review-compare --from-service` reads it, so a reviewer never passes a file around.
`src/goldSet.ts` ports the viewer's writer (`apps/viewer/src/lib/goldSet.ts`). It reads the draft the
way the viewer's tolerant loader does, and the tests pin it to `fixtures/review_gold_set.jsonl`.

- No labels: an empty body.
- Labels the download would refuse (one for a cell outside the sample, or one that lost its rubric
  version or time): **422** `{error}`, with the download's message.

The CLI signs in through `POST /api/auth/login`, fetches the gold set and signs out again
(`POST /api/auth/logout`), so its session row is deleted at once.

**Submissions** are insert-only: there is no update or delete route, so a submission never changes
once made. Account delete is the only thing that removes them.

## Auth model

Ported unchanged from multibench (test-tool scale): email + password (argon2id, passwords 8–1,024
characters), no email or magic link. Signup is gated by one shared `REVIEW_INVITE_CODE`, compared in
constant time, and fail-closed when unset. A duplicate email gets 409 (race-safe insert).

- **Sessions** are server-side rows holding only a SHA-256 of the token; revocation is a row delete.
  They last 30 days. Expired rows are rejected on use but not pruned (fine at this scale).
- **Cookies.** `st_session` is httpOnly; `st_csrf` is not. Both are `Secure; SameSite=None;
  Path=/`, and clearing them repeats those attributes. The review UI and `/api` share one origin, so
  the cookies are first-party. (Tightening to `SameSite=Lax` is a deferred clean-up.)
- **CSRF** is double-submit: every state-changing authenticated request, and logout, must send the
  `X-CSRF-Token` header matching the `st_csrf` cookie, or it gets 403 `{error: "csrf"}`. The token
  also comes back in the signup/login body and from `GET /api/auth/csrf`; the client keeps it in
  memory and refreshes it from `/csrf` after a 403.
- **Login CSRF.** Signup and login accept only an exact `application/json` MIME essence (415
  otherwise, including `text/plain;charset=application/json`). A cross-site form can only send a
  "simple" request, so it is refused, and a JSON one needs a CORS preflight that an unlisted origin
  fails.
- There is no rate limiting or email-enumeration hardening: reviewers are invited and trusted.

## Migrations

Drizzle is the single schema authority, and every change follows **generate → review → apply**:

1. Edit `src/schema/*`, then run `pnpm exec drizzle-kit generate --name <change>` to emit a new
   `drizzle/NNNN_<change>.sql` (plus `drizzle/meta/*`). Never hand-write these files.
2. **Review the generated SQL in the PR.** That review is the human gate on schema changes.
3. **Apply** with `pnpm migrate` (`src/migrate.ts`: drizzle-orm's programmatic migrator over the
   committed `drizzle/` files). It runs only committed SQL, never diffs the live schema the way
   `db:push` does, and is idempotent: applied migrations are recorded, so a re-run is a no-op.

`db:push` is never used, and there is no script for it. The tests apply the same migrations to
PGlite, so a broken migration fails `pnpm test`.

The current schema is `drizzle/0000_review_store.sql`: `reviewers`, `sessions`, `reviews` (unique
on reviewer + sample) and `submissions`, with `ON DELETE CASCADE` from each to `reviewers`.

## Local run

You need a Postgres you can create a database in. Run these from the repo root. They use absolute
paths, so they don't depend on where `pnpm -C` starts the process.

```bash
createdb sacredtexts_review_dev
export DATABASE_URL=postgres://localhost:5432/sacredtexts_review_dev
export REVIEW_INVITE_CODE=pick-a-code
export SAMPLE_PATH="$PWD/review/samples/facct-2026-11-03-k10.json"
export VIEWER_DIST="$PWD/apps/viewer/dist"

pnpm -C apps/api install --frozen-lockfile
pnpm -C apps/viewer install --frozen-lockfile
pnpm -C apps/api migrate
pnpm -C apps/viewer build:pages   # bakes all of runs/ into dist/runs/; the image bakes only its named runs
pnpm -C apps/api start         # api listening on :8080

curl -s localhost:8080/api/health    # {"status":"ok","db":"up"}
curl -s localhost:8080/api/sample    # {"error":"unauthorized"} until you sign in
```

Then open <http://localhost:8080/> in **Chrome**. The session cookies are `Secure; SameSite=None`;
Chrome treats `http://localhost` as secure and accepts them, but Safari does not.

The server reads `index.html` once, at startup. If you rebuild the viewer while it runs,
restart it. Otherwise it keeps serving the old shell, which points at bundles the rebuild
deleted, and the page is blank.

For viewer development with hot reload, leave `VIEWER_DIST` unset (API only) and run the viewer's
Vite dev server, which proxies `/api` to `:8080`.

To remove the local database afterwards: `dropdb sacredtexts_review_dev`.

## Hosting

> **Provisioned 2026-11-10** on the owner's go-ahead (relayed by the architect at 21:34Z):
> <https://review-production-8f474051.up.railway.app>. This is the Railway project
> `sacredtexts-review`, one service `review` plus a managed Postgres, in the Haadi workspace.
> It is separate from the multibench project.

**What runs**

- **Service `review`:** one replica, built from `apps/api/Dockerfile`.
- **Postgres:** Railway's managed Postgres, one instance, no HA or point-in-time recovery.
  - The volume is backed up **daily** (06:07 UTC) and each backup is kept for 6 days.
- **Domains:** `https://sacredtexts.iaser.ai`, the name reviewers use, and the generated Railway
  domain above. Both reach the same service on port 8080.

**The image** (`apps/api/Dockerfile`, built with the **repo root** as its context):

- One stage builds the viewer with `build:pages`, the Cloudflare Pages command: `vite build`, then
  `scripts/bake-runs.ts` bakes `runs/` into `dist/runs/` (reading `items/for-test/` for the panel's
  questions). That stage's `runs/` holds only the runs it names (see "What the review origin
  shows" under [Topology](#topology)).
- The service stage holds:
  - the API's production dependencies;
  - `apps/api/src` and `drizzle/`;
  - `review/samples/`;
  - the built viewer, with its baked `dist/runs/`.
- It runs as the `node` user with `tsx src/server.ts`.
- Every `COPY` names its paths, so no `node_modules`, `dist` or `texts/` reaches it. Run evidence
  reaches it only as the baked `dist/runs/` of the named runs.
- Build it locally with `docker build -f apps/api/Dockerfile -t sacredtexts-review .`.
- A Dockerfile is used, not Nixpacks or Railpack, because the repo root holds `requirements.txt`
  and no `package.json`, so auto-detection would build Python.

**Service settings** are set on the service itself. Railway rejects a config-as-code file path on a
new service ("Config as Code is deprecated"), so there is no `railway.json` for it. The settings are:

| Setting | Value |
|---|---|
| `dockerfilePath` | `apps/api/Dockerfile` |
| `preDeployCommand` | `tsx /app/apps/api/src/migrate.ts`: applies the committed, reviewed migrations before each new version goes live. A failed migration fails the deploy. It is idempotent and never `db:push`. |
| `healthcheckPath` | `/api/health`: 503 when Postgres is unreachable, so a deploy that can't reach the database fails. |
| `restartPolicyType` / `restartPolicyMaxRetries` | `ON_FAILURE` / `3` |

To read them back:
`railway api 'query($s: String!, $e: String!) { serviceInstance(serviceId: $s, environmentId: $e) { dockerfilePath preDeployCommand healthcheckPath restartPolicyType restartPolicyMaxRetries } }' --raw-var s=<service id> --raw-var e=<environment id>`.

**Variables** on the `review` service:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}`, a reference to the private `postgres.railway.internal` URL. Postgres has no public proxy. |
| `SAMPLE_PATH` | `/app/review/samples/facct-2026-11-03-k10.json` (an absolute path in the image) |
| `REVIEW_INVITE_CODE` | The shared signup code. It is kept only in Railway and the gitignored root `.env`, and given to reviewers out of band. It was set through stdin (`railway variable set --stdin`), so it is never on a command line. |

- `VIEWER_DIST` is set by the image (`/app/apps/viewer/dist`).
- `PORT` comes from Railway (8080).
- `ALLOWED_ORIGINS` is unset, because the UI and `/api` share the origin.

**Deploying.** The first deploy was a CLI upload of exactly the committed paths the image needs:

```bash
stage=$(mktemp -d)
git archive HEAD apps/api apps/viewer review/samples runs items/for-test | tar -x -C "$stage"
railway up "$stage" --path-as-root --service review --detach
```

That uploads about 165 MB (17 MB gzipped), almost all of it `runs/`, where the whole repo is about
345 MB. The upload still carries all of `runs/`, but the image keeps only the runs the Dockerfile
names. With all the runs baked (2026-11-11), the image was about 118 MB compressed (614 MB
unpacked; 105 MB and 463 MB without them). With only `facct-2026-11-03` baked (#159), its
`dist/runs/` is 69 MB, and a local build is 541 MB unpacked, 111 MB as a gzipped `docker save`.
A cold container answers `/api/health` in under a second, because the baked files are read from
disk only when they are requested. To deploy on every merge instead,
connect the service to the repository's `main` branch. That is the owner's call:
`railway service source connect --repo faithfamilytechnologynetwork/sacredtexts --branch main --service review`.

**Checked on the first deploy (2026-11-10), over HTTPS, without an account:**

- The pre-deploy step logged `migrations applied`.
- At startup the service logged the active sample, `serving the viewer from /app/apps/viewer/dist`
  and `api listening on :8080`. It did not log the "signup is CLOSED" line, so the invite code is set.
- The database holds the four tables plus drizzle's migration record, with no rows.
- `/api/health` returned `{"status":"ok","db":"up"}`.
- `/`, `/review` and a `/review/cell/…` deep link serve the app.
- The JS bundle is served gzipped: 145 KB of 486 KB.
- A missing `/assets/*` file returns 404.
- `/api/sample` and `/api/auth/me` return 401 when signed out.
- The cookies are `Secure; SameSite=None`.
- In Chrome, `/review` shows the sign-in and create-account forms.

**Completion check (a human, in a real browser).** Through the domain, sign up with the invite code,
pick texts, label a cell, reload to confirm it persists, open Results, and run
`review-compare --from-service <domain>`. A builder agent
doesn't create accounts or enter the invite code on the production host, so a person runs this.

To switch the active sample, commit the new sample file, point `SAMPLE_PATH` at it and redeploy.
Drafts for the old sample stay in the store and can be read or discarded, but no longer saved.
