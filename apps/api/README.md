# `apps/api`: the review service

A small Postgres-backed service that holds the human review store for Spec 154: reviewer accounts,
one review draft per reviewer per sample, and immutable submissions. Reviewers label the cells of a
committed review sample (`review/samples/<sample_id>.json`); their labels live here and come out as
a gold-set file that `sacredbench review-compare` reads.

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

Responses are gzip- or deflate-compressed for a client that accepts it (`hono/compress`). That matters
for the sample (2.8 MB, about 0.5 MB gzipped) and the viewer bundle, because nothing sits in front of
the service.

**One active sample.** `SAMPLE_PATH` names it. Drafts and submissions are accepted for that sample
id only. A save or submit for any other id gets 404 `{error: "unknown sample"}`. Reading, listing and
discarding drafts still work for every id, so a draft from an earlier sample stays visible and can be
removed.

**What the review origin shows.** The deployment builds the viewer with `pnpm build`, not
`build:pages`, so it bakes in no runs. The browsing pages (`/`, `/errors`, `/standings`) on this
origin show their usual "no runs" empty state. That is expected: this origin is for review. The
public browsing viewer is the Cloudflare Pages build, which this service does not change.

**The viewer's own host is untouched.** `apps/viewer/server/index.mjs` (its `pnpm start`), its
smoke test and `apps/viewer/railway.json` are the pre-existing static-only host and stay as they are.
Whether any live service still uses that config is the owner's call. The **review** deployment uses
`apps/api/railway.json`, not the viewer's.

## Configuration

Copy `.env.example` to `.env`, or set the variables in the environment. Secrets (the database URL
and the invite code) come from the environment only. A relative path resolves against the directory
the service starts in, which is `apps/api` under `pnpm -C apps/api start`.

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
pnpm -C apps/viewer build      # not build:pages: the review origin bakes in no runs
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

> **Requires an explicit go-ahead. NOT approved.** Hosting costs money. Nothing below has been
> provisioned or run. Until a go-ahead, the review tool runs locally only.

The deployment is one Railway service plus a managed Postgres:

- **Service root:** the repo root, so the build can see `apps/viewer`, `apps/api` and
  `review/samples/`.
- **Config path:** `apps/api/railway.json` (config as code):
  - Build: `pnpm -C apps/viewer install --frozen-lockfile && pnpm -C apps/viewer build &&
    pnpm -C apps/api install --frozen-lockfile`.
  - Pre-deploy: `pnpm -C apps/api migrate`. It applies the committed, reviewed migrations on every
    deploy, before the new version goes live, and a failed migration fails the deploy. It is
    idempotent and never `db:push`.
  - Start: `pnpm -C apps/api start`. Health check: `/api/health` (503 when Postgres is unreachable,
    so a deploy that can't reach the database fails).

Provisioning steps, for when a go-ahead is given:

1. Create a Railway project with a managed **Postgres** and one empty service connected to this
   repository. Set the service's root directory to the repo root and its config path to
   `apps/api/railway.json`.
2. Set the service variables. The paths are relative to `apps/api`, where the start command runs:
   - `DATABASE_URL`: a reference to the Postgres service's URL.
   - `REVIEW_INVITE_CODE`: the shared code, given to reviewers out of band.
   - `SAMPLE_PATH=../../review/samples/facct-2026-11-03-k10.json`
   - `VIEWER_DIST=../viewer/dist`
   - Leave `ALLOWED_ORIGINS` empty: the UI and `/api` share the origin.
3. Deploy. Confirm the logs show the active sample id, `serving the viewer from …` and
   `api listening on :8080`, and that the four tables exist.
4. Generate the one public domain. The service needs no other domain.
5. **Completion check:** through that domain, in real Chrome and Safari, sign up with the invite
   code, pick texts, label a cell, reload to confirm it persists, and download the gold set.

**Unverified until then.** The repo root has no `package.json`, so check on the first deploy that
the builder detects Node and pnpm (Node 24, pnpm 10.30.2, as in `package.json`'s `engines` and
`packageManager`). If it does not, the build needs an explicit Node setup before this config can be
used.

To switch the active sample, commit the new sample file, point `SAMPLE_PATH` at it and redeploy.
Drafts for the old sample stay in the store and can be read or discarded, but no longer saved.
