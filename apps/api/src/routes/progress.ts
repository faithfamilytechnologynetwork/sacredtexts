import { Hono } from 'hono';
import { asc, eq, sql } from 'drizzle-orm';
import type { AppDb } from '../db';
import { cellsById, LABEL_OUTCOMES } from '../goldSet';
import { requireAuth } from '../middleware/auth';
import type { AppEnv } from '../middleware/auth';
import type { ActiveSample } from '../sample';
import { reviewers, reviews, submissions } from '../schema';

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

/**
 * `GET /api/progress` (issue #161): every reviewer's progress on the active sample, for any signed-in
 * reviewer. One entry per reviewer with a draft for it: their name (never the email), the texts they
 * chose, the ids of the sample cells they have labelled (in sample order), their submission count and
 * the draft's last save. The draft is read as the viewer's tolerant loader reads it: a label counts once
 * its outcome is one of the label outcomes, and `texts` is kept only when it is a list of strings. The
 * viewer joins the cell ids with the sample for the per-text counts.
 */
export function progressRoute(db: AppDb, sample: ActiveSample): Hono<AppEnv> {
  const cellIds = [...cellsById(sample.json).keys()];
  const route = new Hono<AppEnv>();
  route.use('*', requireAuth(db));
  route.get('/', async (c) => {
    const drafts = await db
      .select({ reviewerId: reviews.reviewerId, name: reviewers.name, state: reviews.state, updatedAt: reviews.updatedAt })
      .from(reviews)
      .innerJoin(reviewers, eq(reviewers.id, reviews.reviewerId))
      .where(eq(reviews.sampleId, sample.sampleId))
      .orderBy(asc(reviewers.name), asc(reviewers.id)); // one draft per reviewer; the id only breaks a name tie
    const counts = await db
      .select({ reviewerId: submissions.reviewerId, n: sql<number>`count(*)::int` })
      .from(submissions)
      .where(eq(submissions.sampleId, sample.sampleId))
      .groupBy(submissions.reviewerId);
    const submitted = new Map(counts.map((r) => [r.reviewerId, r.n]));
    return c.json({
      sampleId: sample.sampleId,
      reviewers: drafts.map((d) => {
        const state = isRecord(d.state) ? d.state : {};
        const labels = isRecord(state.labels) ? state.labels : {};
        const texts = Array.isArray(state.texts) && state.texts.every((t) => typeof t === 'string') ? state.texts : [];
        return {
          name: d.name,
          texts,
          labelledCellIds: cellIds.filter((id) => {
            const label = labels[id];
            return isRecord(label) && LABEL_OUTCOMES.includes(label.outcome as string);
          }),
          submissions: submitted.get(d.reviewerId) ?? 0,
          updatedAt: d.updatedAt.toISOString(),
        };
      }),
    });
  });
  return route;
}
