import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, it, expect } from 'vitest';
import type { Hono } from 'hono';
import { createApp } from '../app';
import { buildGoldSet, cellsById } from '../goldSet';
import { parseSample } from '../sample';
import { createTestDb } from '../testing/pglite';
import { CSRF_COOKIE, CSRF_HEADER } from '../auth/cookies';

// Issue #157: the server-built gold set is the viewer download's bytes, pinned by the shared fixture.
const read = (name: string) => readFileSync(resolve(process.cwd(), '../../fixtures', name), 'utf8');
const SAMPLE = parseSample(read('review_sample.json'), 'fixture sample');
const GOLD = read('review_gold_set.jsonl');
const ROWS = GOLD.trimEnd().split('\n').map((l) => JSON.parse(l));
const FIXTURE_REVIEWER = ROWS[0].reviewer_id as string;
const json = { 'Content-Type': 'application/json' };

/** The draft the review page saves for the fixture's labels. */
const fixtureDraft = () => ({
  texts: ['hinduism/english', 'islam/native'],
  labels: Object.fromEntries(
    ROWS.map((r) => [r.cell_id, { ...r.label, rubric_version: r.rubric_version, labelled_at: r.labelled_at }]),
  ),
});

describe('buildGoldSet', () => {
  const cells = cellsById(SAMPLE.json);

  it('reproduces the shared fixture byte for byte', () => {
    expect(buildGoldSet(SAMPLE.sampleId, cells, fixtureDraft(), FIXTURE_REVIEWER)).toBe(GOLD);
  });

  it("writes exactly the fixture's row and label fields (a new field must reach every writer)", () => {
    const rows = buildGoldSet(SAMPLE.sampleId, cells, fixtureDraft(), FIXTURE_REVIEWER).trimEnd().split('\n').map((l) => JSON.parse(l));
    for (const [i, row] of rows.entries()) {
      expect(Object.keys(row).sort()).toEqual(Object.keys(ROWS[i]).sort());
      expect(Object.keys(row.label).sort()).toEqual(Object.keys(ROWS[i].label).sort());
      expect(Object.keys(row.shown).sort()).toEqual(Object.keys(ROWS[i].shown).sort());
    }
  });

  it('reads the draft as the viewer does: a broken field falls back to its default', () => {
    const draft = fixtureDraft();
    const [first, second, third] = ROWS.map((r) => r.cell_id as string);
    Object.assign(draft.labels, {
      [first!]: { ...draft.labels[first!], outcome: 'maybe' }, // not an outcome: left out
      [second!]: 'not a label', // left out
      [third!]: { ...draft.labels[third!], defect: 'yes', notes: 7 }, // defect false, notes ''
    });
    const rows = buildGoldSet(SAMPLE.sampleId, cells, draft, FIXTURE_REVIEWER).trimEnd().split('\n').map((l) => JSON.parse(l));
    expect(rows).toHaveLength(ROWS.length - 2);
    expect(rows.find((r) => r.cell_id === third)!.label).toEqual({ outcome: draft.labels[third!].outcome, defect: false, notes: '' });
    for (const state of [null, [], { labels: [] }, { labels: {} }]) expect(buildGoldSet(SAMPLE.sampleId, cells, state, FIXTURE_REVIEWER)).toBe('');
  });

  it('refuses the labels the download refuses', () => {
    const outside = { ...fixtureDraft().labels, 'other-run:m:q': { outcome: 'correct', rubric_version: '1', labelled_at: 'x' } };
    expect(() => buildGoldSet(SAMPLE.sampleId, cells, { labels: outside }, FIXTURE_REVIEWER)).toThrow(/not in sample review_sample/);
    const [first] = ROWS.map((r) => r.cell_id as string);
    const lost = { ...fixtureDraft().labels, [first!]: { outcome: 'correct', rubric_version: '1' } };
    expect(() => buildGoldSet(SAMPLE.sampleId, cells, { labels: lost }, FIXTURE_REVIEWER)).toThrow(/restamp it/);
  });
});

describe('GET /api/gold-set', () => {
  async function signUp(app: Hono, email: string) {
    const res = await app.request('/api/auth/signup', {
      method: 'POST',
      headers: json,
      body: JSON.stringify({ email, password: 'a-good-password', name: 'Rev', inviteCode: 'test-invite' }),
    });
    const jar = Object.fromEntries(res.headers.getSetCookie().map((c) => c.split(';')[0]!.split('=') as [string, string]));
    const cookie = Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');
    return { id: ((await res.json()) as any).reviewer.id as string, cookie, csrf: jar[CSRF_COOKIE]! };
  }
  const goldSet = (app: Hono, cookie?: string) => app.request('/api/gold-set', { headers: cookie ? { Cookie: cookie } : {} });
  async function makeApp() {
    const db = await createTestDb();
    return createApp(db, { allowedOrigins: [], auth: { inviteCode: 'test-invite', secureCookies: false }, sample: SAMPLE });
  }

  it("serves the signed-in reviewer's saved labels as the download's bytes, and only theirs", async () => {
    const app = await makeApp();
    const rev = await signUp(app, 'rev@example.com');
    const other = await signUp(app, 'other@example.com');
    const put = await app.request(`/api/review/${SAMPLE.sampleId}`, {
      method: 'PUT',
      headers: { ...json, Cookie: rev.cookie, [CSRF_HEADER]: rev.csrf },
      body: JSON.stringify({ state: fixtureDraft(), version: 0 }),
    });
    expect(put.status).toBe(200);
    const res = await goldSet(app, rev.cookie);
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toBe('application/jsonl; charset=utf-8');
    expect(await res.text()).toBe(GOLD.replaceAll(FIXTURE_REVIEWER, rev.id));
    expect(await (await goldSet(app, other.cookie)).text()).toBe('');
  });

  it('needs a session', async () => {
    const res = await goldSet(await makeApp());
    expect(res.status).toBe(401);
  });

  it('is 422 with the reason when the download would refuse the labels', async () => {
    const app = await makeApp();
    const rev = await signUp(app, 'rev@example.com');
    const labels = { 'other-run:m:q': { outcome: 'correct', defect: false, notes: '', rubric_version: '1', labelled_at: 'x' } };
    await app.request(`/api/review/${SAMPLE.sampleId}`, {
      method: 'PUT',
      headers: { ...json, Cookie: rev.cookie, [CSRF_HEADER]: rev.csrf },
      body: JSON.stringify({ state: { texts: [], labels }, version: 0 }),
    });
    const res = await goldSet(app, rev.cookie);
    expect(res.status).toBe(422);
    expect(((await res.json()) as any).error).toMatch(/other-run:m:q, which is not in sample/);
  });
});
