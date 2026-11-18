import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, it, expect } from 'vitest';
import type { Hono } from 'hono';
import { createApp } from '../app';
import type { AppDb } from '../db';
import { parseSample } from '../sample';
import { reviews, submissions } from '../schema';
import { createTestDb } from '../testing/pglite';
import { CSRF_COOKIE, CSRF_HEADER } from '../auth/cookies';

// Issue #161: every reviewer's progress on the active sample, by name, for any signed-in reviewer.
const SAMPLE = parseSample(readFileSync(resolve(process.cwd(), '../../fixtures/review_sample.json'), 'utf8'), 'fixture sample');
const CELL_IDS = (JSON.parse(SAMPLE.json).cells as Array<{ cell_id: string }>).map((c) => c.cell_id);
const json = { 'Content-Type': 'application/json' };
const label = (outcome: unknown) => ({ outcome, defect: false, notes: '', rubric_version: '1', labelled_at: '2026-11-18T00:00:00.000Z' });

async function makeApp(): Promise<{ app: Hono; db: AppDb }> {
  const db = await createTestDb();
  return { app: createApp(db, { allowedOrigins: [], auth: { inviteCode: 'test-invite', secureCookies: false }, sample: SAMPLE }), db };
}

async function signUp(app: Hono, email: string, name: string) {
  const res = await app.request('/api/auth/signup', {
    method: 'POST',
    headers: json,
    body: JSON.stringify({ email, password: 'a-good-password', name, inviteCode: 'test-invite' }),
  });
  const jar = Object.fromEntries(res.headers.getSetCookie().map((c) => c.split(';')[0]!.split('=') as [string, string]));
  const cookie = Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');
  const headers = { ...json, Cookie: cookie, [CSRF_HEADER]: jar[CSRF_COOKIE]! };
  return {
    id: ((await res.json()) as any).reviewer.id as string,
    cookie,
    save: (state: unknown) => app.request(`/api/review/${SAMPLE.sampleId}`, { method: 'PUT', headers, body: JSON.stringify({ state, version: 0 }) }),
    submit: () => app.request(`/api/review/${SAMPLE.sampleId}/submit`, { method: 'POST', headers, body: JSON.stringify({ review: {} }) }),
  };
}

const progress = async (app: Hono, cookie?: string) => app.request('/api/progress', { headers: cookie ? { Cookie: cookie } : {} });

describe('GET /api/progress', () => {
  it("lists every reviewer's draft on the active sample by name, with the cells they labelled", async () => {
    const { app, db } = await makeApp();
    const zara = await signUp(app, 'zara@example.com', 'Zara');
    const amir = await signUp(app, 'amir@example.com', 'Amir');
    const idle = await signUp(app, 'idle@example.com', 'Idle'); // no draft: not listed
    const [c0, c1, c2, c3] = CELL_IDS as [string, string, string, string];
    expect((await zara.save({ texts: ['islam/native'], labels: { [c2]: label('correct'), [c0]: label('cant_judge') } })).status).toBe(200);
    expect((await zara.submit()).status).toBe(201);
    expect((await zara.submit()).status).toBe(201);
    const amirLabels = {
      [c1]: label('incorrect'),
      [c3]: label(null), // picked no outcome yet
      [c0]: label('maybe'), // not an outcome
      [c2]: 'not a label',
      'other-run:m:q': label('correct'), // not in the sample
    };
    expect((await amir.save({ texts: ['hinduism/english', 7], labels: amirLabels })).status).toBe(200);
    // A draft or a submission from an earlier active sample is not counted.
    await db.insert(reviews).values({ reviewerId: idle.id, sampleId: 'earlier-sample', state: { texts: ['islam/native'], labels: { [c0]: label('correct') } } });
    await db.insert(submissions).values({ reviewerId: amir.id, sampleId: 'earlier-sample', review: {} });

    const res = await progress(app, idle.cookie);
    expect(res.status).toBe(200);
    const body = (await res.json()) as any;
    expect(body.sampleId).toBe(SAMPLE.sampleId);
    expect(body.reviewers.map((r: any) => ({ ...r, updatedAt: typeof r.updatedAt }))).toEqual([
      { name: 'Amir', texts: [], labelledCellIds: [c1], submissions: 0, updatedAt: 'string' },
      { name: 'Zara', texts: ['islam/native'], labelledCellIds: [c0, c2], submissions: 2, updatedAt: 'string' },
    ]);
    expect(Number.isNaN(Date.parse(body.reviewers[0].updatedAt))).toBe(false);
    expect(JSON.stringify(body)).not.toMatch(/@example\.com/);
  });

  it('reads a draft with no usable state as nothing labelled', async () => {
    const { app } = await makeApp();
    const rev = await signUp(app, 'rev@example.com', 'Rev');
    await rev.save({ labels: [] });
    const body = (await (await progress(app, rev.cookie)).json()) as any;
    expect(body.reviewers).toMatchObject([{ name: 'Rev', texts: [], labelledCellIds: [], submissions: 0 }]);
  });

  it('needs a session', async () => {
    const { app } = await makeApp();
    expect((await progress(app)).status).toBe(401);
  });
});
