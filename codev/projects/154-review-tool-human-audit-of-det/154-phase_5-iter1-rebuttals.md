# Phase 5, iteration 1 — rebuttals

Both reviewers asked for changes. I took every blocking point and two of claude's three minor notes;
the third is recorded as a deliberate parity choice. Everything is in one follow-up commit on top of
1c7a5e40.

## codex — stale in-flight requests leak across reviewers (KEY ISSUE) — **fixed**

Agreed, and it was a real leak. `resetReviewStore()` cleared the maps, but a request already in flight
still wrote to the global state when it resolved. Reviewer A's slow draft GET could land in B's session
and be saved under B's account, and A's stale 401 could wipe B's session.

Fix (`apps/viewer/src/lib/review.ts`):

- **A session counter.** `resetReviewStore()` bumps `session`. Every async path captures the session it
  started in and drops its result if the session has moved on. That covers `ensureSampleLoaded`,
  `prefetchDrafts`, `persistSample` (after the load, after each PUT including the LWW retry, in the
  catch before `handleAuthError`, and after the CSRF refresh), `persistDelete` and `initReview`.
- **The queue.** `enqueue` won't run an op queued in an earlier session. Without that, A's queued
  "start over" ran as B and deleted B's server draft. A queued *save* already bailed on its own, because
  B's state is empty after a reset; the delete is the case that needed the gate.
- **The load map.** A settling load removes only its own `loadPromises` entry, so it can't unhook B's
  newer load for the same sample.
- **Init.** `initInFlight` became the per-session `initFor`, so a reset re-arms init at once.

Regression tests (`reviewStore.test.ts`, "requests in flight when the session changes"). Each parks one
of A's requests, switches to B, then releases it:

- A's draft GET, and whether B's own concurrent load survives it;
- A's draft LIST;
- A's PUT answering 409: no LWW retry and no adoption;
- a save queued behind an in-flight PUT;
- a start-over queued behind an in-flight PUT;
- A's stale 401: B's session is intact;
- a stale init, and a reset re-arming init.

Each guard was mutation-checked by removing it: the session bump, the enqueue gate, the load-map
identity check and the per-session init each turn at least one test red.

## claude — two new tests fail in a full-suite run (BLOCKER) — **fixed (it reviewed a tree mid-edit)**

Claude reviewed the working tree while I was writing the fix above. Its blocker was already fixed by
the time it reported: the "WORKING TREE CHANGED" warning on its review names exactly my two files.
Its diagnosis was right. The fake switches accounts when the login *request* is sent, and `enqueue`
starts ops a few microtasks later, so A's PUT sometimes went out tagged as B.

I used its suggested fix: both tests now drain to a macrotask (`settle()`), so A's PUT is parked on the
wire before B signs in. Once the PUT is parked, the caller tag is deterministic, so I kept the
assertion on it: it is the stronger check, proving the one PUT that went out was A's. The full viewer
suite is green three runs in a row (358/358).

## claude — minor notes

- **`persistDelete` lacked the terminal rule — taken.** A DELETE refused with a non-retryable 4xx is now
  `rejected` and not retried, the same as a save. Two tests cover it: a terminal 400 isn't retried, and
  a transient failure still is. The first test fails if the rule is removed.
- **The vacuous `server` assertion — taken.** The "does NOT overwrite a saved server draft when the
  initial load fails" fake now writes through a versioned `server` map, as multibench's did. A blind
  version-0 save would 409, and its LWW retry would then overwrite the saved work, so the server-state
  assertions now bite. Mutation-checked: disabling the load guard turns the test red.
- **`reviewApi.logout()` ignores `res.ok` — not changed, by design.** This is multibench parity, and
  claude flagged it for awareness only. Fixing it would mean a CSRF refresh and retry on logout, which
  belongs with the ported auth flow if a later phase wants it. It's recorded in the thread.
- **Uncommitted changes — committed** in the follow-up commit.

## Residual window (recorded, not changed)

One case is left on purpose. If a sign-in ever happened while another reviewer was still signed in,
A's not-yet-sent edit could go out between B's login response setting the cookie and the store
resetting. No UI path reaches it: the sign-in form only shows while signed out, and every signed-out
state follows a reset or a fresh page load. The thread records it.
