import { describe, it, expect } from 'vitest';
import type { Hono } from 'hono';
import { eq, sql } from 'drizzle-orm';
import { createApp } from '../app';
import type { AppDb } from '../db';
import { createTestDb } from '../testing/pglite';
import { TEST_SAMPLE_ID, testSample } from '../testing/sample';
import { CSRF_COOKIE, CSRF_HEADER } from '../auth/cookies';
import { reviewers, reviews, sessions, submissions } from '../schema';
import { REVIEW_BODY_MAX_BYTES } from './review';

const auth = { inviteCode: 'test-invite', secureCookies: false };
const json = { 'Content-Type': 'application/json' };
const SAMPLE = TEST_SAMPLE_ID;
const OTHER_SAMPLE = 'fixture-sample';

function readCookies(res: Response): Record<string, string> {
  const out: Record<string, string> = {};
  for (const raw of res.headers.getSetCookie?.() ?? []) {
    const pair = raw.split(';')[0] ?? '';
    const eq = pair.indexOf('=');
    if (eq > 0) out[pair.slice(0, eq)] = pair.slice(eq + 1);
  }
  return out;
}
const cookieHeader = (jar: Record<string, string>) =>
  Object.entries(jar)
    .map(([k, v]) => `${k}=${v}`)
    .join('; ');

async function makeApp(): Promise<{ app: Hono; db: AppDb }> {
  const db = await createTestDb();
  return { app: createApp(db, { allowedOrigins: [], auth, sample: testSample() }), db };
}

async function signedIn(app: Hono, email = 'rev@example.com') {
  const res = await app.request('/api/auth/signup', {
    method: 'POST',
    headers: json,
    body: JSON.stringify({ email, password: 'a-good-password', name: 'Rev', inviteCode: 'test-invite' }),
  });
  return readCookies(res);
}
function authed(jar: Record<string, string>, extra: Record<string, string> = {}) {
  return { Cookie: cookieHeader(jar), [CSRF_HEADER]: jar[CSRF_COOKIE] ?? '', ...extra };
}
const put = (app: Hono, jar: Record<string, string>, sid: string, payload: unknown) =>
  app.request(`/api/review/${sid}`, {
    method: 'PUT',
    headers: authed(jar, json),
    body: JSON.stringify(payload),
  });
const get = async (app: Hono, jar: Record<string, string>, sid: string) =>
  (await (await app.request(`/api/review/${sid}`, { headers: { Cookie: cookieHeader(jar) } })).json()) as any;
const submit = (app: Hono, jar: Record<string, string>, sid: string, body: unknown) =>
  app.request(`/api/review/${sid}/submit`, { method: 'POST', headers: authed(jar, json), body: JSON.stringify(body) });
const listSubmissions = async (app: Hono, jar: Record<string, string>, sid: string) =>
  ((await (await app.request(`/api/review/${sid}/submissions`, { headers: { Cookie: cookieHeader(jar) } })).json()) as any)
    .submissions as any[];

/** A `SampleReview`-shaped draft: the chosen texts and per-cell labels. */
const sampleState = (note = '') => ({
  texts: ['quran-uthmani'],
  labels: {
    'facct-2026-11-03:astra:e84250807e983aef': {
      outcome: 'correct',
      defect: false,
      notes: note,
      rubric_version: '1',
      labelled_at: '2026-11-10T12:00:00.000Z',
    },
  },
});

/** A draft with `n` labels whose notes are each `noteChars` repetitions of `char`. */
function bigDraft(n: number, noteChars: number, chars: string[]) {
  const labels: Record<string, unknown> = {};
  for (let i = 0; i < n; i++) {
    const char = chars[i % chars.length]!;
    labels[`facct-2026-11-03:model-${String(i).padStart(4, '0')}:${i.toString(16).padStart(16, '0')}`] = {
      outcome: 'incorrect',
      defect: i % 2 === 0,
      notes: char.repeat(noteChars),
      rubric_version: '1',
      labelled_at: '2026-11-10T12:00:00.000+00:00',
    };
  }
  return { texts: ['quran-uthmani', 'sggs-gurmukhi'], labels };
}

describe('review drafts', () => {
  it('requires auth', async () => {
    const { app } = await makeApp();
    expect((await app.request(`/api/review/${SAMPLE}`)).status).toBe(401);
    expect((await app.request('/api/review')).status).toBe(401);
  });

  it('creates a draft (version 0 → 1), then reads it back', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const created = await put(app, jar, SAMPLE, { state: sampleState('hi'), version: 0 });
    expect(created.status).toBe(200);
    expect(((await created.json()) as any).version).toBe(1);

    const body = await get(app, jar, SAMPLE);
    expect(body.version).toBe(1);
    expect(body.state).toEqual(sampleState('hi'));
  });

  it('reads an absent draft as the empty version-0 sentinel', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    expect(await get(app, jar, SAMPLE)).toEqual({ state: null, version: 0 });
  });

  it('updates on a matching version and rejects a stale one with 409 + current', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    await put(app, jar, SAMPLE, { state: sampleState('v1'), version: 0 }); // → v1

    const ok = await put(app, jar, SAMPLE, { state: sampleState('v2'), version: 1 }); // → v2
    expect(ok.status).toBe(200);
    expect(((await ok.json()) as any).version).toBe(2);

    // A save that still thinks it's on v1 is stale → 409 with the current state/version to reconcile.
    const stale = await put(app, jar, SAMPLE, { state: sampleState('v1-again'), version: 1 });
    expect(stale.status).toBe(409);
    const conflict = (await stale.json()) as any;
    expect(conflict.error).toBe('conflict');
    expect(conflict.version).toBe(2);
    expect(conflict.state).toEqual(sampleState('v2'));
  });

  it('rejects a second version-0 insert (the other device created it first) with 409 + current', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    await put(app, jar, SAMPLE, { state: sampleState('device-1'), version: 0 });
    const second = await put(app, jar, SAMPLE, { state: sampleState('device-2'), version: 0 });
    expect(second.status).toBe(409);
    const conflict = (await second.json()) as any;
    expect(conflict.version).toBe(1);
    expect(conflict.state).toEqual(sampleState('device-1'));
  });

  it('rejects a mutating save without the CSRF header', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const res = await app.request(`/api/review/${SAMPLE}`, {
      method: 'PUT',
      headers: { Cookie: cookieHeader(jar), ...json }, // no X-CSRF-Token
      body: JSON.stringify({ state: sampleState(), version: 0 }),
    });
    expect(res.status).toBe(403);
  });

  it('recovers from a CSRF 403: GET /api/auth/csrf returns the paired token and the retry succeeds', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    // The client lost its in-memory token (e.g. a reload) and sends a stale one.
    const stale = await app.request(`/api/review/${SAMPLE}`, {
      method: 'PUT',
      headers: { Cookie: cookieHeader(jar), [CSRF_HEADER]: 'stale-token', ...json },
      body: JSON.stringify({ state: sampleState('retry'), version: 0 }),
    });
    expect(stale.status).toBe(403);
    expect(((await stale.json()) as any).error).toBe('csrf');

    const refreshed = await app.request('/api/auth/csrf', { headers: { Cookie: cookieHeader(jar) } });
    const csrfToken = ((await refreshed.json()) as any).csrfToken;
    expect(csrfToken).toBe(jar[CSRF_COOKIE]); // the existing cookie's token, not a new one

    const retry = await app.request(`/api/review/${SAMPLE}`, {
      method: 'PUT',
      headers: { Cookie: cookieHeader(jar), [CSRF_HEADER]: csrfToken, ...json },
      body: JSON.stringify({ state: sampleState('retry'), version: 0 }),
    });
    expect(retry.status).toBe(200);
    expect((await get(app, jar, SAMPLE)).state).toEqual(sampleState('retry'));
  });

  it('lists all of the reviewer\'s drafts, keyed by sample id', async () => {
    const { app, db } = await makeApp();
    const jar = await signedIn(app);
    await put(app, jar, SAMPLE, { state: sampleState('a'), version: 0 });
    // A draft left from an earlier active sample (the API no longer accepts saves for it).
    const reviewerId = (await db.select({ id: reviewers.id }).from(reviewers))[0]!.id;
    await db.insert(reviews).values({ reviewerId, sampleId: OTHER_SAMPLE, state: sampleState('b'), version: 1 });
    const res = await app.request('/api/review', { headers: { Cookie: cookieHeader(jar) } });
    const body = (await res.json()) as any;
    expect(body.drafts.map((d: any) => d.sampleId).sort()).toEqual([SAMPLE, OTHER_SAMPLE].sort());
    expect(body.drafts.every((d: any) => d.version === 1)).toBe(true);
  });

  it('saves and submits only for the active sample; other ids stay readable and removable', async () => {
    const { app, db } = await makeApp();
    const jar = await signedIn(app);
    const saved = await put(app, jar, OTHER_SAMPLE, { state: sampleState('stray'), version: 0 });
    expect(saved.status).toBe(404);
    expect(await saved.json()).toEqual({ error: 'unknown sample' });
    const submitted = await submit(app, jar, OTHER_SAMPLE, { review: sampleState('stray') });
    expect(submitted.status).toBe(404);
    expect(await submitted.json()).toEqual({ error: 'unknown sample' });
    expect(await db.select().from(reviews)).toHaveLength(0);
    expect(await db.select().from(submissions)).toHaveLength(0);

    // The guard sits behind auth and CSRF: signed out is still 401, a missing CSRF header still 403.
    const signedOut = await app.request(`/api/review/${OTHER_SAMPLE}`, {
      method: 'PUT',
      headers: json,
      body: JSON.stringify({ state: sampleState(), version: 0 }),
    });
    expect(signedOut.status).toBe(401);
    const noCsrf = await app.request(`/api/review/${OTHER_SAMPLE}`, {
      method: 'PUT',
      headers: { Cookie: cookieHeader(jar), ...json },
      body: JSON.stringify({ state: sampleState(), version: 0 }),
    });
    expect(noCsrf.status).toBe(403);

    // A draft from an earlier active sample can still be read and discarded.
    const reviewerId = (await db.select({ id: reviewers.id }).from(reviewers))[0]!.id;
    await db.insert(reviews).values({ reviewerId, sampleId: OTHER_SAMPLE, state: sampleState('old'), version: 3 });
    expect(await get(app, jar, OTHER_SAMPLE)).toEqual({ state: sampleState('old'), version: 3 });
    const del = await app.request(`/api/review/${OTHER_SAMPLE}`, { method: 'DELETE', headers: authed(jar) });
    expect(del.status).toBe(200);
    expect(await get(app, jar, OTHER_SAMPLE)).toEqual({ state: null, version: 0 });
  });

  it('deletes a draft (start over), idempotently', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    await put(app, jar, SAMPLE, { state: sampleState('x'), version: 0 });
    const del = await app.request(`/api/review/${SAMPLE}`, { method: 'DELETE', headers: authed(jar) });
    expect(del.status).toBe(200);
    expect((await get(app, jar, SAMPLE)).version).toBe(0); // discarded
    // Deleting again is still a no-op 200.
    expect((await app.request(`/api/review/${SAMPLE}`, { method: 'DELETE', headers: authed(jar) })).status).toBe(200);
  });

  it('rejects a draft DELETE without the CSRF header', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    await put(app, jar, SAMPLE, { state: sampleState('keep'), version: 0 });
    const res = await app.request(`/api/review/${SAMPLE}`, {
      method: 'DELETE',
      headers: { Cookie: cookieHeader(jar) },
    });
    expect(res.status).toBe(403);
    expect((await get(app, jar, SAMPLE)).version).toBe(1);
  });

  it('rejects an array state, a null state and a missing version (only objects are valid drafts)', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    expect((await put(app, jar, SAMPLE, { state: [1, 2, 3], version: 0 })).status).toBe(400);
    expect((await put(app, jar, SAMPLE, { state: null, version: 0 })).status).toBe(400);
    expect((await put(app, jar, SAMPLE, { state: sampleState() })).status).toBe(400);
  });
});

describe('review body cap (8 MB, in bytes)', () => {
  it('is 8 MiB', () => {
    expect(REVIEW_BODY_MAX_BYTES).toBe(8 * 1024 * 1024);
  });

  it('accepts a maximal multilingual draft: 1,500 labels × 1,000-character Gurmukhi/Arabic notes', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const state = bigDraft(1500, 1000, ['ਗ', 'ع']);
    const res = await put(app, jar, SAMPLE, { state, version: 0 });
    expect(res.status).toBe(200);
    const back = await get(app, jar, SAMPLE);
    expect(Object.keys(back.state.labels)).toHaveLength(1500);
    expect(back.state).toEqual(state);
  });

  it('accepts the worst case the cap is sized from: 1,500 notes of 1,000 four-byte characters', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const state = bigDraft(1500, 1000, ['𝔄', '𐌰']); // U+1D504, U+10330: 4 bytes each in UTF-8
    const body = JSON.stringify({ state, version: 0 });
    const bytes = Buffer.byteLength(body, 'utf8');
    expect(bytes).toBeGreaterThan(6_000_000); // genuinely near the sizing estimate (~6.2 MB)
    expect(bytes).toBeLessThan(REVIEW_BODY_MAX_BYTES);
    const res = await app.request(`/api/review/${SAMPLE}`, { method: 'PUT', headers: authed(jar, json), body });
    expect(res.status).toBe(200);
    expect((await get(app, jar, SAMPLE)).state).toEqual(state);
  });

  it('rejects a draft body over 8 MB with 413 and stores nothing', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const big = { state: { blob: 'x'.repeat(REVIEW_BODY_MAX_BYTES) }, version: 0 };
    const res = await put(app, jar, SAMPLE, big);
    expect(res.status).toBe(413);
    expect((await get(app, jar, SAMPLE)).version).toBe(0);
  });

  it('counts bytes, not characters: 3-byte characters over the cap are rejected', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    // ~2.8M characters (under 8M chars) but ~8.4 MB of UTF-8.
    const big = { state: { blob: 'ਗ'.repeat(Math.ceil(REVIEW_BODY_MAX_BYTES / 3) + 1024) }, version: 0 };
    expect(JSON.stringify(big).length).toBeLessThan(REVIEW_BODY_MAX_BYTES);
    expect((await put(app, jar, SAMPLE, big)).status).toBe(413);
  });

  it('rejects a submit body over 8 MB with 413 and records no submission', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    const res = await submit(app, jar, SAMPLE, { review: { blob: 'x'.repeat(REVIEW_BODY_MAX_BYTES) } });
    expect(res.status).toBe(413);
    expect(await listSubmissions(app, jar, SAMPLE)).toHaveLength(0);
  });
});

describe('review submissions (immutable)', () => {
  it('requires auth + CSRF to submit', async () => {
    const { app } = await makeApp();
    // unauthenticated
    expect(
      (await app.request(`/api/review/${SAMPLE}/submit`, { method: 'POST', headers: json, body: '{}' })).status,
    ).toBe(401);
    // authed but no CSRF header
    const jar = await signedIn(app);
    const noCsrf = await app.request(`/api/review/${SAMPLE}/submit`, {
      method: 'POST',
      headers: { Cookie: cookieHeader(jar), ...json },
      body: JSON.stringify({ review: sampleState() }),
    });
    expect(noCsrf.status).toBe(403);
  });

  it('rejects a submit whose review is not an object', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    expect((await submit(app, jar, SAMPLE, { review: [1] })).status).toBe(400);
    expect((await submit(app, jar, SAMPLE, { review: null })).status).toBe(400);
    expect((await submit(app, jar, SAMPLE, {})).status).toBe(400);
  });

  it('creates an immutable snapshot; a second submit adds a new one', async () => {
    const { app, db } = await makeApp();
    const jar = await signedIn(app);
    const first = await submit(app, jar, SAMPLE, { review: sampleState('v1') });
    expect(first.status).toBe(201);
    const meta = ((await first.json()) as any).submission;
    expect(meta.id).toBeTruthy();
    expect(meta.submittedAt).toBeTruthy();

    // Submit again (the draft evolved) → a SEPARATE immutable row (no update path).
    await submit(app, jar, SAMPLE, { review: sampleState('v2') });
    const rows = await listSubmissions(app, jar, SAMPLE);
    expect(rows).toHaveLength(2);
    // Metadata only: no publish field (multibench's GitHub-issue column is removed).
    expect(rows.every((r: any) => Object.keys(r).sort().join() === 'id,submittedAt')).toBe(true);
    // The frozen snapshots are stored verbatim, keyed by sample.
    const stored = await db.select().from(submissions).where(eq(submissions.sampleId, SAMPLE));
    const notesOf = (review: any) => review.labels['facct-2026-11-03:astra:e84250807e983aef'].notes;
    expect(stored.map((r) => notesOf(r.review)).sort()).toEqual(['v1', 'v2']);
    expect(stored.find((r) => notesOf(r.review) === 'v1')!.review).toEqual(sampleState('v1'));
  });

  it('keeps submissions per sample', async () => {
    const { app } = await makeApp();
    const jar = await signedIn(app);
    await submit(app, jar, SAMPLE, { review: sampleState('a') });
    expect(await listSubmissions(app, jar, SAMPLE)).toHaveLength(1);
    expect(await listSubmissions(app, jar, OTHER_SAMPLE)).toHaveLength(0);
  });

  it('has no publish column in the submissions table', async () => {
    const { db } = await makeApp();
    const result = await db.execute(
      sql`select column_name from information_schema.columns where table_name = 'submissions' order by column_name`,
    );
    const columns = (result as unknown as { rows: { column_name: string }[] }).rows.map((r) => r.column_name);
    expect(columns).toEqual(['id', 'review', 'reviewer_id', 'sample_id', 'submitted_at']);
  });

  it('keys drafts by sample_id (no tradition_id column survives the port)', async () => {
    const { db } = await makeApp();
    const result = await db.execute(
      sql`select column_name from information_schema.columns where table_name = 'reviews' order by column_name`,
    );
    const columns = (result as unknown as { rows: { column_name: string }[] }).rows.map((r) => r.column_name);
    expect(columns).toEqual(['id', 'reviewer_id', 'sample_id', 'state', 'updated_at', 'version']);
  });
});

describe('reviewer isolation (drafts and submissions)', () => {
  it('B cannot read A\'s draft or see it in the list', async () => {
    const { app } = await makeApp();
    const jarA = await signedIn(app, 'a@example.com');
    const jarB = await signedIn(app, 'b@example.com');
    await put(app, jarA, SAMPLE, { state: sampleState('A-only'), version: 0 });

    expect(await get(app, jarB, SAMPLE)).toEqual({ state: null, version: 0 });
    const bList = (await (await app.request('/api/review', { headers: { Cookie: cookieHeader(jarB) } })).json()) as any;
    expect(bList.drafts).toEqual([]);
  });

  it('B cannot overwrite or delete A\'s draft, and a B conflict never leaks A\'s state', async () => {
    const { app } = await makeApp();
    const jarA = await signedIn(app, 'a@example.com');
    const jarB = await signedIn(app, 'b@example.com');
    await put(app, jarA, SAMPLE, { state: sampleState('A-only'), version: 0 }); // A at v1

    // B updating "version 1" of the same sample matches no row of B's → 409 with B's own (empty) state.
    const bStale = await put(app, jarB, SAMPLE, { state: sampleState('B-overwrite'), version: 1 });
    expect(bStale.status).toBe(409);
    const conflict = (await bStale.json()) as any;
    expect(conflict.state).toBeNull();
    expect(conflict.version).toBe(0);

    // B creating its own draft for the same sample is a separate row.
    expect((await put(app, jarB, SAMPLE, { state: sampleState('B-own'), version: 0 })).status).toBe(200);
    // B deleting the sample's draft deletes only B's.
    expect((await app.request(`/api/review/${SAMPLE}`, { method: 'DELETE', headers: authed(jarB) })).status).toBe(200);

    const a = await get(app, jarA, SAMPLE);
    expect(a.version).toBe(1);
    expect(a.state).toEqual(sampleState('A-only'));
    expect((await get(app, jarB, SAMPLE)).version).toBe(0);
  });

  it('B cannot see A\'s submissions', async () => {
    const { app } = await makeApp();
    const jarA = await signedIn(app, 'a@example.com');
    const jarB = await signedIn(app, 'b@example.com');
    await submit(app, jarA, SAMPLE, { review: sampleState('A') });
    expect(await listSubmissions(app, jarB, SAMPLE)).toHaveLength(0);
    expect(await listSubmissions(app, jarA, SAMPLE)).toHaveLength(1);
  });
});

describe('account delete cascades', () => {
  it('removes the reviewer\'s sessions, drafts and submissions, and leaves another reviewer\'s intact', async () => {
    const { app, db } = await makeApp();
    const jarA = await signedIn(app, 'a@example.com');
    const jarB = await signedIn(app, 'b@example.com');
    const idOf = async (email: string) =>
      (await db.select({ id: reviewers.id }).from(reviewers).where(eq(reviewers.email, email)))[0]!.id;
    const idA = await idOf('a@example.com');
    const idB = await idOf('b@example.com');
    for (const [jar, reviewerId] of [[jarA, idA], [jarB, idB]] as const) {
      await put(app, jar, SAMPLE, { state: sampleState('draft'), version: 0 });
      // A draft from an earlier active sample (saves for it are no longer accepted).
      await db.insert(reviews).values({ reviewerId, sampleId: OTHER_SAMPLE, state: sampleState('draft'), version: 1 });
      await submit(app, jar, SAMPLE, { review: sampleState('submitted') });
    }
    const counts = async (reviewerId: string) => ({
      sessions: (await db.select().from(sessions).where(eq(sessions.reviewerId, reviewerId))).length,
      reviews: (await db.select().from(reviews).where(eq(reviews.reviewerId, reviewerId))).length,
      submissions: (await db.select().from(submissions).where(eq(submissions.reviewerId, reviewerId))).length,
    });
    expect(await counts(idA)).toEqual({ sessions: 1, reviews: 2, submissions: 1 });

    const del = await app.request('/api/account', { method: 'DELETE', headers: authed(jarA) });
    expect(del.status).toBe(200);

    expect(await counts(idA)).toEqual({ sessions: 0, reviews: 0, submissions: 0 });
    expect(await counts(idB)).toEqual({ sessions: 1, reviews: 2, submissions: 1 });
    expect((await app.request(`/api/review/${SAMPLE}`, { headers: { Cookie: cookieHeader(jarA) } })).status).toBe(401);
    expect((await get(app, jarB, SAMPLE)).state).toEqual(sampleState('draft'));
  });
});
