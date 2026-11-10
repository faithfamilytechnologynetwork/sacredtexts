import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import type { Hono } from 'hono';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createApp } from './app';
import { createTestDb } from './testing/pglite';
import { testSample } from './testing/sample';
import { isApiPath, loadViewerDist } from './static';

const auth = { inviteCode: 'test-invite', secureCookies: false };
const SHELL = '<!doctype html><html><body><div id="root"></div><!-- spa-shell --></body></html>';
const ASSET = 'console.log("asset a");';

describe('the built viewer beside /api', () => {
  let dist: string;
  let app: Hono;

  beforeAll(async () => {
    dist = mkdtempSync(join(tmpdir(), 'api-dist-'));
    writeFileSync(join(dist, 'index.html'), SHELL);
    mkdirSync(join(dist, 'assets'));
    writeFileSync(join(dist, 'assets', 'a.js'), ASSET);
    // A dist folder named `api` must never shadow or leak through /api.
    mkdirSync(join(dist, 'api'));
    writeFileSync(join(dist, 'api', 'secret.txt'), 'not for /api');
    app = createApp(await createTestDb(), {
      allowedOrigins: [],
      auth,
      sample: testSample(),
      viewer: loadViewerDist(dist),
    });
  });
  afterAll(() => rmSync(dist, { recursive: true, force: true }));

  it('serves index.html at / and for an unmatched client route', async () => {
    for (const path of ['/', '/review/cell/x', '/errors', '/runs/_index']) {
      const res = await app.request(path);
      expect(res.status, path).toBe(200);
      expect(res.headers.get('content-type'), path).toMatch(/text\/html/);
      expect(await res.text(), path).toBe(SHELL);
    }
  });

  it('serves a real file from the dist with its own content type', async () => {
    const res = await app.request('/assets/a.js');
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toMatch(/javascript/);
    expect(await res.text()).toBe(ASSET);
  });

  it('answers HEAD for the shell and for a file', async () => {
    expect((await app.request('/review/cell/x', { method: 'HEAD' })).status).toBe(200);
    expect((await app.request('/assets/a.js', { method: 'HEAD' })).status).toBe(200);
  });

  it('gives an unmatched /api path a JSON 404, never the shell or a dist file', async () => {
    for (const path of ['/api/nope', '/api', '/api/secret.txt', '/api/unknown/deep/path']) {
      const res = await app.request(path);
      expect(res.status, path).toBe(404);
      expect(await res.json(), path).toEqual({ error: 'not found' });
    }
  });

  it('keeps the real API routes working with the viewer mounted', async () => {
    expect((await app.request('/api/health')).status).toBe(200);
    expect((await app.request('/api/sample')).status).toBe(401);
  });

  it('serves neither files nor the shell to a non-read method', async () => {
    for (const path of ['/review/cell/x', '/assets/a.js']) {
      const res = await app.request(path, { method: 'POST' });
      expect(res.status, path).toBe(404);
      expect(await res.json(), path).toEqual({ error: 'not found' });
    }
  });
});

describe('API-only (no VIEWER_DIST)', () => {
  it('answers every unmatched path with a JSON 404', async () => {
    const app = createApp(await createTestDb(), { allowedOrigins: [], auth, sample: testSample() });
    for (const path of ['/', '/review/cell/x', '/api/nope']) {
      const res = await app.request(path);
      expect(res.status, path).toBe(404);
      expect(await res.json(), path).toEqual({ error: 'not found' });
    }
  });
});

describe('loadViewerDist', () => {
  it('fails when the directory has no index.html', () => {
    const empty = mkdtempSync(join(tmpdir(), 'api-dist-empty-'));
    try {
      expect(() => loadViewerDist(empty)).toThrow(/no readable index\.html/);
      expect(() => loadViewerDist(join(empty, 'missing'))).toThrow(/no readable index\.html/);
    } finally {
      rmSync(empty, { recursive: true, force: true });
    }
  });
});

describe('isApiPath', () => {
  it('matches /api and paths under it, not look-alikes', () => {
    expect(isApiPath('/api')).toBe(true);
    expect(isApiPath('/api/')).toBe(true);
    expect(isApiPath('/api/health')).toBe(true);
    expect(isApiPath('/apis')).toBe(false);
    expect(isApiPath('/api-docs')).toBe(false);
    expect(isApiPath('/review/api')).toBe(false);
  });
});
