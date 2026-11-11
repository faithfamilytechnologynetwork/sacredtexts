# Review phase, iteration 1: rebuttals

Codex requested changes and claude approved. The architect's integration review of PR #155 named four
fixes, one of which overlaps codex's. All four are in 26956177, and CI is green on 01b11e0f.

## codex (REQUEST_CHANGES)

1. **Unbounded bodies on the public auth routes: fixed.** `POST /api/auth/signup` and `/login` now
   apply `bodyLimit({ maxSize: AUTH_BODY_MAX_BYTES })` (16 KiB) before the JSON is parsed. Over the cap
   is a 413. The cap leaves room for the widest legal password (1,024 UTF-16 units, at most 3 KiB in
   UTF-8) plus a name, a background note, an email and the invite code.
   - Four tests:
     - an over-cap signup gives 413 and creates no reviewer;
     - an over-cap login gives 413;
     - the cap counts bytes, not characters;
     - the widest legal password still signs up.
   - Removing the cap turns three of them red.
   - Checked live after the redeploy: a 20 KB body to either route gets 413.

2. **The hosted sign-up → label → reload → download check: not a builder action.** The host is
   production. A builder agent doesn't create accounts or enter passwords or the invite code there.
   - Every account-free check passed on the live service (`codev/reviews/154-…md` § Hosted
     deployment).
   - The architect ruled that the human check doesn't block the merge, but it does gate inviting
     reviewers. It is waiting on a human.

3. **Untracked consult files for phases 2–7: committed on the architect's ruling** (2026-11-11T00:07Z),
   matching the other projects. The original note follows. Keeping
   `codev/projects/*` consult files untracked was this builder's standing order. The repo's other
   projects commit theirs, and so do this project's spec, plan and phase 1, as codex says. I asked the
   architect whether to commit them before the merge.

## claude (APPROVE)

None of claude's notes blocks the merge. Each one is tracked in follow-up issue #156:

- `SameSite=Lax`;
- re-affirming "no rate limiting" now that the service is public;
- the submissions routes, which have no client caller;
- the TS `canonicalJson` float guard;
- `load_gold`'s order check on the full sort key.

## The architect's integration review (PR #155 comment): all fixed in 26956177

1. **The auth body cap**: as codex 1 above.
2. **Logout ignores a refused response.**
   - `reviewApi.logout()` throws on a non-2xx.
   - `logoutReview()` refreshes a stale CSRF token and retries once, as saves and deletes do. Any
     other refusal, or a second one, rejects and leaves the reviewer signed in, and the badge shows
     "Couldn't sign out".
   - The tests cover a stale token followed by a successful sign-out (tokens `stale`, then `fresh`),
     and a refusal that persists (two POSTs, still signed in).
   - Removing the `res.ok` check turns 3 tests red; removing the retry turns 2 red.
3. **`review-compare --version current` with a non-default evaluator.** `current` now reads the
   `evaluators` in each row's run `summary.json`. It fails fast if they aren't the default `strict` +
   `containment` (in any order), or if the summary is missing. `committed` and run-directory versions
   are unaffected. Three tests cover it, and removing the guard turns 2 red.
4. **Spec wording.** A version is now `committed`, `current`, or a run directory laid out like
   `runs/<run>/`.

**Declined, per the owner's ruling:** narrowing the `review/` audit exemption to an NRSV allowlist.
