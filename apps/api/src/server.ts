import { resolve } from 'node:path';
import { serve } from '@hono/node-server';
import { createApp } from './app';
import { parseAllowedOrigins } from './cors';
import { nodePgDatabase } from './db';
import { loadSample } from './sample';
import type { ActiveSample } from './sample';
import { loadViewerDist } from './static';
import type { ViewerDist } from './static';

// Fail fast on missing config rather than starting a half-working service (no silent fallbacks).
const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  console.error('DATABASE_URL is required');
  process.exit(1);
}

const allowedOrigins = parseAllowedOrigins(process.env.ALLOWED_ORIGINS);
// Log the parsed allow-list at startup: an empty list is the correct default (never a wildcard),
// but it also produces opaque browser CORS failures, so surfacing it saves real debugging time.
console.log(
  allowedOrigins.length > 0
    ? `CORS allow-list: ${allowedOrigins.join(', ')}`
    : 'CORS allow-list is EMPTY — no cross-site origin is allowed (set ALLOWED_ORIGINS).',
);

const inviteCode = process.env.REVIEW_INVITE_CODE;
if (!inviteCode) {
  // Fail-closed, not fatal: the service still serves reads/login, but signup is closed until the
  // shared invite code is set. Surface it so it isn't a silent mystery.
  console.log('REVIEW_INVITE_CODE is unset — signup is CLOSED until it is configured.');
}

// Unset ⇒ 8080. Set but not a TCP port (including empty, which Number() reads as 0) ⇒ exit.
const port = process.env.PORT === undefined ? 8080 : Number(process.env.PORT);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error(`PORT is not a valid port: ${JSON.stringify(process.env.PORT)}`);
  process.exit(1);
}

// The one active review sample. Required: without it there is nothing to review.
const samplePath = process.env.SAMPLE_PATH;
if (!samplePath) {
  console.error('SAMPLE_PATH is required (the committed review sample, e.g. review/samples/<id>.json)');
  process.exit(1);
}
let sample: ActiveSample;
try {
  sample = loadSample(resolve(samplePath));
} catch (err) {
  console.error((err as Error).message);
  process.exit(1);
}
console.log(`active sample: ${sample.sampleId} (${resolve(samplePath)})`);

// The built viewer. Optional: unset ⇒ API-only, for local dev behind the Vite proxy.
let viewer: ViewerDist | undefined;
const viewerDist = process.env.VIEWER_DIST;
if (viewerDist) {
  try {
    viewer = loadViewerDist(viewerDist);
  } catch (err) {
    console.error((err as Error).message);
    process.exit(1);
  }
  console.log(`serving the viewer from ${viewer.root}`);
} else {
  console.log('VIEWER_DIST is unset — API only (no viewer is served).');
}

const app = createApp(nodePgDatabase(databaseUrl), {
  allowedOrigins,
  auth: { inviteCode, secureCookies: true },
  sample,
  viewer,
});

serve({ fetch: app.fetch, port }, (info) => {
  console.log(`api listening on :${info.port}`);
});
