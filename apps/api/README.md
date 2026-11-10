# `apps/api`: the review service

A small Postgres-backed service that holds the human review store for Spec 154: reviewer accounts,
one review draft per reviewer per sample, and immutable submissions. Reviewers label the cells of a
committed review sample (`review/samples/<sample_id>.json`); their labels live here and come out as
a gold-set file that `sacredbench review-compare` reads.

It is ported nearly verbatim from multibench's `apps/api` (its Spec 92), including the fixes in its
history. The changes from multibench:

- Drafts and submissions are keyed by **sample** (`sample_id`), not by tradition.
- The GitHub-issue publish column (`published_issue_url`) and its validation are removed.
- The draft and submit body cap is **8 MB** (bytes), up from 512 KB.
- The cookies are named `st_session` / `st_csrf`. Browsers scope cookies by host, not port, so
  multibench's `mb_*` names would collide with a multibench API running on `localhost` too.

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

## Configuration

Copy `.env.example` to `.env`, or set the variables in the environment. Secrets (the database URL
and the invite code) come from the environment only.

| Variable | Required | Meaning |
|---|---|---|
| `DATABASE_URL` | yes | Postgres connection string. The server and the migrator exit if it is unset. |
| `REVIEW_INVITE_CODE` | no | Shared signup code. **Fail-closed:** unset ⇒ signup is disabled (login still works). |
| `ALLOWED_ORIGINS` | no | Comma-separated CORS allow-list for credentialed requests. Empty is correct when the UI is same-origin; never `*`. |
| `PORT` | no | Listen port, default 8080. |

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
| `GET /api/review` | session | All of the reviewer's drafts: `{drafts: [{sampleId, state, version}]}`. |
| `GET /api/review/:sampleId` | session | The reviewer's draft for a sample: `{state, version}`, or `{state: null, version: 0}`. |
| `PUT /api/review/:sampleId` | session + CSRF | Save `{state, version}` (below). |
| `DELETE /api/review/:sampleId` | session + CSRF | Discard the draft ("start over"). Idempotent. |
| `POST /api/review/:sampleId/submit` | session + CSRF | Freeze `{review}` as a new immutable submission. Returns `{submission: {id, submittedAt}}`. |
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

You need a Postgres you can create a database in.

```bash
cd apps/api
pnpm install --frozen-lockfile
createdb sacredtexts_review
export DATABASE_URL=postgres://localhost:5432/sacredtexts_review
export REVIEW_INVITE_CODE=pick-a-code
pnpm migrate
pnpm start          # api listening on :8080
curl -s localhost:8080/api/health    # {"status":"ok","db":"up"}
```

The session cookies are `Secure`. Chrome treats `http://localhost` as secure and accepts them;
Safari does not, so use Chrome for a local walk.

## Hosting

Not provisioned. Hosting needs an explicit go-ahead because it costs money.
