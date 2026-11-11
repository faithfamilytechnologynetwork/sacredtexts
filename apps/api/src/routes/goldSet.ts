import { Hono } from 'hono';
import type { AppDb } from '../db';
import { buildGoldSet, cellsById, GoldSetError } from '../goldSet';
import { requireAuth } from '../middleware/auth';
import type { AppEnv } from '../middleware/auth';
import type { ActiveSample } from '../sample';
import { currentDraft } from './review';

/**
 * `GET /api/gold-set` (issue #157): the signed-in reviewer's gold set for the active sample, as JSONL,
 * built from their saved draft. The bytes are the review page's "Download gold set" file, so
 * `review-compare --from-service` reads the labels without a file being passed around. No labels ⇒ an
 * empty body. Labels the download would refuse (one naming a cell outside the sample, or one that lost
 * its stamp) ⇒ 422 with the same message.
 */
export function goldSetRoute(db: AppDb, sample: ActiveSample): Hono<AppEnv> {
  const cells = cellsById(sample.json);
  const route = new Hono<AppEnv>();
  route.use('*', requireAuth(db));
  route.get('/', async (c) => {
    const reviewerId = c.get('reviewerId');
    const { state } = await currentDraft(db, reviewerId, sample.sampleId);
    try {
      const text = buildGoldSet(sample.sampleId, cells, state, reviewerId);
      return c.body(text, 200, { 'Content-Type': 'application/jsonl; charset=utf-8' });
    } catch (err) {
      if (err instanceof GoldSetError) return c.json({ error: err.message }, 422);
      throw err;
    }
  });
  return route;
}
