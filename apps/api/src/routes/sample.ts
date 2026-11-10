import { Hono } from 'hono';
import type { AppDb } from '../db';
import { requireAuth } from '../middleware/auth';
import type { AppEnv } from '../middleware/auth';
import type { ActiveSample } from '../sample';

/**
 * `GET /api/sample`: the active review sample, for signed-in reviewers only. The body is the
 * committed file's exact bytes (validated once at startup), so nothing is re-serialized per request.
 */
export function sampleRoute(db: AppDb, sample: ActiveSample): Hono<AppEnv> {
  const route = new Hono<AppEnv>();
  route.use('*', requireAuth(db));
  route.get('/', (c) => c.body(sample.json, 200, { 'Content-Type': 'application/json; charset=utf-8' }));
  return route;
}
