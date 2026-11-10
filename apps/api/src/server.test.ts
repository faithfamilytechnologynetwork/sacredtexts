import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { sampleObject } from './testing/sample';

// Startup is tested on the REAL entry point (`tsx src/server.ts`), because the fail-fast exits live
// there. No database is needed: the pool connects lazily, so a dead DATABASE_URL only makes
// /api/health report 503.
const DEAD_DB = 'postgres://127.0.0.1:1/none';

async function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const probe = createServer();
    probe.once('error', reject);
    probe.listen(0, '127.0.0.1', () => {
      const addr = probe.address();
      const port = typeof addr === 'object' && addr ? addr.port : 0;
      probe.close(() => (port ? resolve(port) : reject(new Error('no free port'))));
    });
  });
}

function startServer(env: Record<string, string | undefined>) {
  const child = spawn('node_modules/.bin/tsx', ['src/server.ts'], {
    env: { PATH: process.env.PATH, DATABASE_URL: DEAD_DB, ...env },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let output = '';
  child.stdout.on('data', (d) => (output += d));
  child.stderr.on('data', (d) => (output += d));
  const exited = new Promise<number | null>((resolve) => child.on('exit', (code) => resolve(code)));
  return { child, exited, output: () => output };
}

describe('server startup', () => {
  let dir: string;
  let goodSample: string;

  beforeAll(() => {
    dir = mkdtempSync(join(tmpdir(), 'api-server-'));
    goodSample = join(dir, 'sample.json');
    writeFileSync(goodSample, JSON.stringify(sampleObject('startup-sample')));
    writeFileSync(join(dir, 'format2.json'), JSON.stringify({ ...sampleObject(), format: 2 }));
  });
  afterAll(() => rmSync(dir, { recursive: true, force: true }));

  it('exits 1 when SAMPLE_PATH is unset', async () => {
    const s = startServer({ SAMPLE_PATH: undefined });
    expect(await s.exited).toBe(1);
    expect(s.output()).toMatch(/SAMPLE_PATH is required/);
  }, 20_000);

  it('exits 1 when SAMPLE_PATH is missing or invalid', async () => {
    const missing = startServer({ SAMPLE_PATH: join(dir, 'nope.json') });
    expect(await missing.exited).toBe(1);
    expect(missing.output()).toMatch(/cannot read sample/);

    const wrongFormat = startServer({ SAMPLE_PATH: join(dir, 'format2.json') });
    expect(await wrongFormat.exited).toBe(1);
    expect(wrongFormat.output()).toMatch(/unsupported sample format 2/);
  }, 20_000);

  it('exits 1 when VIEWER_DIST has no index.html', async () => {
    const empty = mkdtempSync(join(dir, 'dist-empty-'));
    const s = startServer({ SAMPLE_PATH: goodSample, VIEWER_DIST: empty });
    expect(await s.exited).toBe(1);
    expect(s.output()).toMatch(/no readable index\.html/);
  }, 20_000);

  it('serves /api, the sample guard and the viewer from one origin when configured', async () => {
    const viewer = mkdtempSync(join(dir, 'dist-'));
    writeFileSync(join(viewer, 'index.html'), '<div id="root"></div>');
    const port = await freePort();
    const s = startServer({ SAMPLE_PATH: goodSample, VIEWER_DIST: viewer, PORT: String(port) });
    try {
      let up = false;
      for (let i = 0; i < 80 && !up; i++) {
        try {
          await fetch(`http://127.0.0.1:${port}/api/health`);
          up = true;
        } catch {
          await new Promise((r) => setTimeout(r, 250));
        }
      }
      expect(up, s.output()).toBe(true);
      expect(s.output()).toMatch(/active sample: startup-sample/);
      expect(s.output()).toMatch(/serving the viewer from/);

      const shell = await fetch(`http://127.0.0.1:${port}/review/cell/x`);
      expect(shell.status).toBe(200);
      expect(await shell.text()).toBe('<div id="root"></div>');
      expect((await fetch(`http://127.0.0.1:${port}/api/health`)).status).toBe(503); // dead DB
      const notFound = await fetch(`http://127.0.0.1:${port}/api/nope`);
      expect(notFound.status).toBe(404);
      expect(await notFound.json()).toEqual({ error: 'not found' });
    } finally {
      s.child.kill('SIGTERM');
      await s.exited;
    }
  }, 30_000);
});
