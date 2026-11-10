import { describe, it, expect } from 'vitest';
import { gunzipSync } from 'node:zlib';
import { createApp } from '../app';
import { createTestDb } from '../testing/pglite';
import { testSample } from '../testing/sample';

const auth = { inviteCode: 'test-invite', secureCookies: false };

function cookieHeader(res: Response): string {
  return (res.headers.getSetCookie?.() ?? []).map((raw) => raw.split(';')[0]).join('; ');
}

describe('GET /api/sample', () => {
  it('is 401 signed out and returns the active sample verbatim signed in', async () => {
    const sample = testSample('sample-under-test');
    const app = createApp(await createTestDb(), { allowedOrigins: [], auth, sample });

    const signedOut = await app.request('/api/sample');
    expect(signedOut.status).toBe(401);
    expect(await signedOut.json()).toEqual({ error: 'unauthorized' });

    const signup = await app.request('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'rev@example.com', password: 'a-good-password', name: 'Rev', inviteCode: 'test-invite' }),
    });
    expect(signup.status).toBe(201);

    const res = await app.request('/api/sample', { headers: { Cookie: cookieHeader(signup) } });
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toBe('application/json; charset=utf-8');
    const body = await res.text();
    expect(body).toBe(sample.json);
    expect(JSON.parse(body).sample_id).toBe('sample-under-test');

    // The real sample is ~2.8 MB; a client that accepts gzip gets it compressed, byte-identical inside.
    const gz = await app.request('/api/sample', {
      headers: { Cookie: cookieHeader(signup), 'Accept-Encoding': 'gzip' },
    });
    expect(gz.headers.get('content-encoding')).toBe('gzip');
    expect(gunzipSync(Buffer.from(await gz.arrayBuffer())).toString('utf8')).toBe(sample.json);
  });
});
