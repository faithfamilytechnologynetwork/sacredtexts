import { describe, it, expect } from 'vitest';
import type { Hono } from 'hono';
import { eq } from 'drizzle-orm';
import { createApp } from '../app';
import { createTestDb } from '../testing/pglite';
import { testSample } from '../testing/sample';
import { CSRF_COOKIE, SESSION_COOKIE, CSRF_HEADER } from '../auth/cookies';
import { createSession, SESSION_TTL_MS } from '../auth/session';
import { reviewers, sessions } from '../schema';
import { AUTH_BODY_MAX_BYTES } from './auth';

const auth = { inviteCode: 'test-invite', secureCookies: false };
const jsonHeaders = { 'Content-Type': 'application/json' };

async function makeApp(): Promise<Hono> {
  return createApp(await createTestDb(), { allowedOrigins: [], auth, sample: testSample() });
}

function readCookies(res: Response): Record<string, string> {
  const out: Record<string, string> = {};
  for (const raw of res.headers.getSetCookie?.() ?? []) {
    const pair = raw.split(';')[0] ?? '';
    const eq = pair.indexOf('=');
    if (eq > 0) out[pair.slice(0, eq)] = pair.slice(eq + 1);
  }
  return out;
}
const cookieHeader = (jar: Record<string, string>): string =>
  Object.entries(jar)
    .map(([k, v]) => `${k}=${v}`)
    .join('; ');

const signupBody = (over: Record<string, unknown> = {}) => ({
  email: 'reviewer@example.com',
  password: 'a-good-password',
  name: 'Rev Iewer',
  inviteCode: 'test-invite',
  ...over,
});

async function signup(app: Hono, over: Record<string, unknown> = {}): Promise<Response> {
  return app.request('/api/auth/signup', {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(signupBody(over)),
  });
}

describe('signup (invite-gated)', () => {
  it('creates a reviewer and sets session + csrf cookies', async () => {
    const app = await makeApp();
    const res = await signup(app);
    expect(res.status).toBe(201);
    const body = (await res.json()) as any;
    expect(body.reviewer.email).toBe('reviewer@example.com');
    expect(body.reviewer.id).toMatch(/[0-9a-f-]{36}/);
    const jar = readCookies(res);
    expect(jar[SESSION_COOKIE]).toBeTruthy();
    expect(jar[CSRF_COOKIE]).toBeTruthy();
    // The CSRF token is also returned in the BODY so the cross-site SPA (which cannot read the
    // API-origin cookie via JS) can hold it in memory and echo it in the X-CSRF-Token header.
    expect(body.csrfToken).toBe(jar[CSRF_COOKIE]);
  });

  it('exposes a csrf token via GET /api/auth/csrf', async () => {
    const app = await makeApp();
    const res = await app.request('/api/auth/csrf');
    expect(res.status).toBe(200);
    const jar = readCookies(res);
    const csrfToken = ((await res.json()) as any).csrfToken;
    expect(csrfToken).toBeTruthy();
    expect(csrfToken).toBe(jar[CSRF_COOKIE]); // body token matches the paired cookie
  });

  it('rejects a wrong or missing invite code (fail-closed)', async () => {
    const app = await makeApp();
    expect((await signup(app, { inviteCode: 'nope' })).status).toBe(403);
    expect((await signup(app, { inviteCode: undefined })).status).toBe(403);
  });

  it('refuses every signup while REVIEW_INVITE_CODE is unset (fail-closed), whatever code is supplied', async () => {
    for (const inviteCode of [undefined, '']) {
      const app = createApp(await createTestDb(), {
        allowedOrigins: [],
        auth: { inviteCode, secureCookies: false },
        sample: testSample(),
      });
      for (const supplied of ['test-invite', 'anything', '', undefined]) {
        const res = await signup(app, { inviteCode: supplied });
        expect(res.status).toBe(403);
        expect(readCookies(res)[SESSION_COOKIE]).toBeUndefined();
      }
    }
  });

  it('rejects a signup sent as a non-JSON request', async () => {
    const app = await makeApp();
    const res = await app.request('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify(signupBody()),
    });
    expect(res.status).toBe(415);
  });

  it('rejects a short password and a duplicate email', async () => {
    const app = await makeApp();
    expect((await signup(app, { password: 'short' })).status).toBe(400);
    expect((await signup(app)).status).toBe(201);
    expect((await signup(app)).status).toBe(409); // same email again
  });

  it('rejects an over-long password and a malformed email', async () => {
    const app = await makeApp();
    expect((await signup(app, { password: 'x'.repeat(1025) })).status).toBe(400);
    expect((await signup(app, { email: 'not-an-email' })).status).toBe(400);
  });
});

describe('body cap on the public auth routes', () => {
  const post = (app: Hono, path: string, body: unknown) =>
    app.request(path, { method: 'POST', headers: jsonHeaders, body: JSON.stringify(body) });

  it('rejects a signup body over the cap with 413 and creates no reviewer', async () => {
    const db = await createTestDb();
    const app = createApp(db, { allowedOrigins: [], auth, sample: testSample() });
    const res = await post(app, '/api/auth/signup', signupBody({ background: 'x'.repeat(AUTH_BODY_MAX_BYTES) }));
    expect(res.status).toBe(413);
    expect(await db.select().from(reviewers)).toHaveLength(0);
  });

  it('rejects a login body over the cap with 413', async () => {
    const app = await makeApp();
    expect((await signup(app)).status).toBe(201);
    const res = await post(app, '/api/auth/login', {
      email: 'reviewer@example.com',
      password: 'a-good-password',
      pad: 'x'.repeat(AUTH_BODY_MAX_BYTES),
    });
    expect(res.status).toBe(413);
  });

  it('counts bytes, not characters: 4-byte characters over the cap are rejected', async () => {
    const app = await makeApp();
    const emoji = '\u{1F600}'; // 4 bytes in UTF-8, 2 UTF-16 code units
    const chars = Math.ceil(AUTH_BODY_MAX_BYTES / 4) + 1;
    expect(emoji.repeat(chars).length * 2).toBeLessThan(AUTH_BODY_MAX_BYTES * 4); // sanity: chars, not bytes, would pass
    const res = await post(app, '/api/auth/signup', signupBody({ background: emoji.repeat(chars) }));
    expect(res.status).toBe(413);
  });

  it('still accepts the longest legal password at its widest in bytes, with a background', async () => {
    // The password cap counts UTF-16 units, so its widest UTF-8 form is 1,024 three-byte characters.
    const app = await makeApp();
    const res = await signup(app, {
      password: '\u0A15'.repeat(1024), // Gurmukhi ka: 3 bytes in UTF-8
      background: 'reads Quranic Arabic; hafiz. '.repeat(20),
    });
    expect(res.status).toBe(201);
  });
});

describe('login / me / logout', () => {
  it('logs in with correct credentials, rejects wrong ones, and gates /me on a session', async () => {
    const app = await makeApp();
    await signup(app);

    expect(
      (
        await app.request('/api/auth/login', {
          method: 'POST',
          headers: jsonHeaders,
          body: JSON.stringify({ email: 'reviewer@example.com', password: 'wrong' }),
        })
      ).status,
    ).toBe(401);

    const login = await app.request('/api/auth/login', {
      method: 'POST',
      headers: jsonHeaders,
      body: JSON.stringify({ email: 'reviewer@example.com', password: 'a-good-password' }),
    });
    expect(login.status).toBe(200);
    const jar = readCookies(login);

    // /me without a cookie → 401; with the session cookie → 200.
    expect((await app.request('/api/auth/me')).status).toBe(401);
    const me = await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jar) } });
    expect(me.status).toBe(200);
    expect(((await me.json()) as any).reviewer.email).toBe('reviewer@example.com');

    // Logout revokes the session (delete row) → /me now 401 with the same cookie. Logout is
    // CSRF-checked, so the token must accompany it.
    const logout = await app.request('/api/auth/logout', {
      method: 'POST',
      headers: { Cookie: cookieHeader(jar), [CSRF_HEADER]: jar[CSRF_COOKIE] ?? '' },
    });
    expect(logout.status).toBe(200);
    expect(
      (await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jar) } })).status,
    ).toBe(401);
  });
});

describe('session validity', () => {
  it('rejects an expired session and a revoked one', async () => {
    const db = await createTestDb();
    const app = createApp(db, { allowedOrigins: [], auth, sample: testSample() });
    await signup(app);
    const reviewerId = (await db.select({ id: reviewers.id }).from(reviewers))[0]!.id;
    const me = (token: string) =>
      app.request('/api/auth/me', { headers: { Cookie: `${SESSION_COOKIE}=${token}` } });

    const fresh = await createSession(db, reviewerId);
    expect((await me(fresh.token)).status).toBe(200);

    // Minted one TTL (plus a minute) ago, so it expired a minute ago.
    const expired = await createSession(db, reviewerId, new Date(Date.now() - SESSION_TTL_MS - 60_000));
    expect(expired.expiresAt.getTime()).toBeLessThan(Date.now());
    expect((await me(expired.token)).status).toBe(401);

    // Soft-revoked rows are rejected too: a session is valid only while revoked_at is null.
    await db.update(sessions).set({ revokedAt: new Date() }).where(eq(sessions.reviewerId, reviewerId));
    expect((await me(fresh.token)).status).toBe(401);
  });
});

describe('cross-site request rejection (login/logout CSRF)', () => {
  it('rejects a login sent as a simple (non-JSON) request — the cross-site fixation payload', async () => {
    const app = await makeApp();
    await signup(app);
    // A cross-site attacker can only send a "simple" request without a CORS preflight; a text/plain
    // body is exactly that. Requiring application/json forces a preflight (CORS-gated), so this is
    // rejected at the contract level.
    const res = await app.request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify({ email: 'reviewer@example.com', password: 'a-good-password' }),
    });
    expect(res.status).toBe(415);
  });

  it('rejects the parameter-smuggling bypass (text/plain;charset=application/json)', async () => {
    const app = await makeApp();
    await signup(app);
    // MIME essence is the CORS-safelisted `text/plain` (no preflight), so it must be rejected even
    // though the string contains "application/json". An essence-exact check catches it.
    const res = await app.request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=application/json' },
      body: JSON.stringify({ email: 'reviewer@example.com', password: 'a-good-password' }),
    });
    expect(res.status).toBe(415);
  });

  it('rejects a logout without the CSRF token (forced-logout)', async () => {
    const app = await makeApp();
    const jar = readCookies(await signup(app));
    const res = await app.request('/api/auth/logout', {
      method: 'POST',
      headers: { Cookie: cookieHeader(jar) }, // no X-CSRF-Token
    });
    expect(res.status).toBe(403);
  });
});

describe('reviewer isolation', () => {
  it('keeps each reviewer to their own record, and deleting one leaves the other intact', async () => {
    const app = await makeApp();
    const jarA = readCookies(await signup(app, { email: 'a@example.com' }));
    const jarB = readCookies(await signup(app, { email: 'b@example.com' }));

    // Each session resolves to its own reviewer.
    const meA = (await (
      await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jarA) } })
    ).json()) as any;
    const meB = (await (
      await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jarB) } })
    ).json()) as any;
    expect(meA.reviewer.email).toBe('a@example.com');
    expect(meB.reviewer.email).toBe('b@example.com');
    expect(meA.reviewer.id).not.toBe(meB.reviewer.id);

    // A deletes A's own account (CSRF). B is untouched: still authenticated and able to log in.
    const delA = await app.request('/api/account', {
      method: 'DELETE',
      headers: { Cookie: cookieHeader(jarA), [CSRF_HEADER]: jarA[CSRF_COOKIE] ?? '' },
    });
    expect(delA.status).toBe(200);
    expect(
      (await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jarA) } })).status,
    ).toBe(401);
    expect(
      (await app.request('/api/auth/me', { headers: { Cookie: cookieHeader(jarB) } })).status,
    ).toBe(200);
  });
});

describe('account deletion (CSRF-protected)', () => {
  it('requires the CSRF header, then deletes the account (cascade)', async () => {
    const app = await makeApp();
    const jar = readCookies(await signup(app));

    // DELETE without the CSRF header → 403 (session valid, but double-submit fails).
    const noCsrf = await app.request('/api/account', {
      method: 'DELETE',
      headers: { Cookie: cookieHeader(jar) },
    });
    expect(noCsrf.status).toBe(403);

    // With the CSRF header echoing the csrf cookie → 200.
    const del = await app.request('/api/account', {
      method: 'DELETE',
      headers: { Cookie: cookieHeader(jar), [CSRF_HEADER]: jar[CSRF_COOKIE] ?? '' },
    });
    expect(del.status).toBe(200);

    // Account is gone: login now fails.
    const login = await app.request('/api/auth/login', {
      method: 'POST',
      headers: jsonHeaders,
      body: JSON.stringify({ email: 'reviewer@example.com', password: 'a-good-password' }),
    });
    expect(login.status).toBe(401);
  });
});
