import { describe, it, expect } from 'vitest';
import { createApp } from '../app';
import type { AppDb } from '../db';
import { createTestDb } from '../testing/pglite';
import { testSample } from '../testing/sample';

const auth = { inviteCode: 'test-invite', secureCookies: false };

describe('GET /api/health', () => {
  it('returns 200 ok when the database responds (PGlite)', async () => {
    const app = createApp(await createTestDb(), { allowedOrigins: [], auth, sample: testSample() });
    const res = await app.request('/api/health');
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ status: 'ok', db: 'up' });
  });

  it('returns 503 when the database ping fails', async () => {
    const failing = {
      execute: async () => {
        throw new Error('unreachable');
      },
    } as unknown as AppDb;
    const app = createApp(failing, { allowedOrigins: [], auth, sample: testSample() });
    const res = await app.request('/api/health');
    expect(res.status).toBe(503);
    expect(await res.json()).toEqual({ status: 'error', db: 'down' });
  });
});
