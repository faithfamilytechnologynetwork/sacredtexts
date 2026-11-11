import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import type { Hono } from 'hono';
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { createApp } from './app';
import { createTestDb } from './testing/pglite';
import { testSample } from './testing/sample';
import { isApiPath, isAssetPath, loadViewerDist, parseHeaders } from './static';

const auth = { inviteCode: 'test-invite', secureCookies: false };
const SHELL = '<!doctype html><html><body><div id="root"></div><!-- spa-shell --></body></html>';
const ASSET = 'console.log("asset a");';
// Above hono/compress's 1 KiB threshold.
const BIG_ASSET = `export const words = ${JSON.stringify('בראשית ברא אלהים '.repeat(200))};`;

describe('the built viewer beside /api', () => {
  let dist: string;
  let app: Hono;

  beforeAll(async () => {
    dist = mkdtempSync(join(tmpdir(), 'api-dist-'));
    writeFileSync(join(dist, 'index.html'), SHELL);
    mkdirSync(join(dist, 'assets'));
    writeFileSync(join(dist, 'assets', 'a.js'), ASSET);
    writeFileSync(join(dist, 'assets', 'big.js'), BIG_ASSET);
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

  it('gzips a file for a client that accepts it, and only then', async () => {
    const gz = await app.request('/assets/big.js', { headers: { 'Accept-Encoding': 'gzip' } });
    expect(gz.status).toBe(200);
    expect(gz.headers.get('content-encoding')).toBe('gzip');
    expect(gz.headers.get('vary')).toMatch(/Accept-Encoding/i);
    const packed = Buffer.from(await gz.arrayBuffer());
    expect(packed.length).toBeLessThan(Buffer.byteLength(BIG_ASSET));
    expect(gunzipSync(packed).toString('utf8')).toBe(BIG_ASSET);

    const plain = await app.request('/assets/big.js');
    expect(plain.headers.get('content-encoding')).toBeNull();
    expect(await plain.text()).toBe(BIG_ASSET);
  });

  it('gives a missing /assets file a JSON 404, never the shell', async () => {
    for (const path of ['/assets/index-STALE.js', '/assets/', '/assets/deep/missing.css']) {
      const res = await app.request(path);
      expect(res.status, path).toBe(404);
      expect(await res.json(), path).toEqual({ error: 'not found' });
    }
    // Only the assets directory: a look-alike client route still gets the shell.
    const route = await app.request('/assetsfoo');
    expect(route.status).toBe(200);
    expect(await route.text()).toBe(SHELL);
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

describe('isAssetPath', () => {
  it('matches paths under /assets/ only', () => {
    expect(isAssetPath('/assets/index-abc.js')).toBe(true);
    expect(isAssetPath('/assets/')).toBe(true);
    expect(isAssetPath('/assets')).toBe(false);
    expect(isAssetPath('/assetsfoo')).toBe(false);
    expect(isAssetPath('/review/assets/x.js')).toBe(false);
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

// Issue #157: the hosted image builds the viewer with `build:pages`, so the dist carries the baked
// run data under runs/ and the Pages `_headers` file. This dist uses the viewer's real `_headers`.
describe('the run data a build:pages dist bakes', () => {
  let dist: string;
  let app: Hono;
  const INDEX = '[{"id":"facct-2026-11-03"}]';
  const SUMMARY = '{"run":"archive/first-run"}';
  const SCORES = `${'{"question_id":"q","metrics":{"outcome":"correct"}}\n'.repeat(100)}`;

  beforeAll(async () => {
    dist = mkdtempSync(join(tmpdir(), 'api-dist-runs-'));
    writeFileSync(join(dist, 'index.html'), SHELL);
    copyFileSync(join(process.cwd(), '../viewer/public/_headers'), join(dist, '_headers'));
    mkdirSync(join(dist, 'runs', 'archive', 'first-run'), { recursive: true });
    writeFileSync(join(dist, 'runs', '_index'), INDEX);
    writeFileSync(join(dist, 'runs', 'archive', 'first-run', 'summary.json'), SUMMARY);
    writeFileSync(join(dist, 'runs', 'archive', 'first-run', 'scores.jsonl'), SCORES);
    app = createApp(await createTestDb(), { allowedOrigins: [], auth, sample: testSample(), viewer: loadViewerDist(dist) });
  });
  afterAll(() => rmSync(dist, { recursive: true, force: true }));

  it('serves the extension-less run index as text, never cached', async () => {
    const res = await app.request('/runs/_index');
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toBe('text/plain; charset=utf-8');
    expect(res.headers.get('cache-control')).toBe('no-cache');
    expect(await res.text()).toBe(INDEX);
  });

  it('serves every run file as text/plain, so it is gzipped', async () => {
    const res = await app.request('/runs/archive/first-run/scores.jsonl', { headers: { 'Accept-Encoding': 'gzip' } });
    expect(res.headers.get('content-type')).toBe('text/plain; charset=utf-8');
    expect(res.headers.get('content-encoding')).toBe('gzip');
    expect(res.headers.get('cache-control')).toBe('no-cache'); // the service's default for /runs/*
    expect(gunzipSync(Buffer.from(await res.arrayBuffer())).toString('utf8')).toBe(SCORES);
  });

  it('revalidates run files: an ETag, no-cache, and a 304 with no body for a matching If-None-Match', async () => {
    const path = '/runs/archive/first-run/scores.jsonl';
    const first = await app.request(path);
    const etag = first.headers.get('etag');
    expect(etag).toMatch(/^W\/"[0-9a-f]+-[0-9a-f]+"$/);
    expect(first.headers.get('last-modified')).toBeTruthy();
    expect(first.headers.get('cache-control')).toBe('no-cache');
    const again = await app.request(path, { headers: { 'If-None-Match': etag!, 'Accept-Encoding': 'gzip' } });
    expect(again.status).toBe(304);
    expect(again.headers.get('etag')).toBe(etag);
    expect(await again.text()).toBe('');
    // the run index keeps its own Cache-Control from _headers; a changed file gets a new ETag
    const index = await app.request('/runs/_index');
    expect(index.headers.get('cache-control')).toBe('no-cache');
    writeFileSync(join(dist, 'runs', 'archive', 'first-run', 'scores.jsonl'), `${SCORES}{}\n`);
    const changed = await app.request(path, { headers: { 'If-None-Match': etag! } });
    expect(changed.status).toBe(200);
    expect(changed.headers.get('etag')).not.toBe(etag);
    writeFileSync(join(dist, 'runs', 'archive', 'first-run', 'scores.jsonl'), SCORES);
  });

  it('answers an encoded run id with a 307 to the decoded path, as Pages does', async () => {
    const res = await app.request('/runs/archive%2Ffirst-run/summary.json');
    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toBe('/runs/archive/first-run/summary.json');
    expect(await (await app.request(res.headers.get('location')!)).text()).toBe(SUMMARY);
  });

  it('leaves the shell and the cell route alone (an encoded slash outside /runs is not decoded)', async () => {
    for (const path of ['/', '/review/cell/run%3Avendor%2Fmodel%3Aq']) {
      const res = await app.request(path);
      expect(res.status, path).toBe(200);
      expect(await res.text(), path).toBe(SHELL);
    }
  });

  it('reads _headers as Pages writes it, and refuses a rule it would misread', () => {
    expect(parseHeaders('# c\n/runs/*\n  Content-Type: text/plain\n\n/runs/_index\n  Cache-Control: no-cache\n')).toEqual([
      { path: '/runs/*', headers: [['Content-Type', 'text/plain']] },
      { path: '/runs/_index', headers: [['Cache-Control', 'no-cache']] },
    ]);
    expect(() => parseHeaders('/runs/:id/x\n  A: b\n')).toThrow(/unsupported path/);
    expect(() => parseHeaders('  A: b\n')).toThrow(/under a path/);
  });
});
