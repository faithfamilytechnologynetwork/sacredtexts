import { Hono } from 'hono';
import { bodyLimit } from 'hono/body-limit';
import { and, desc, eq, sql } from 'drizzle-orm';
import type { AppDb } from '../db';
import { reviews, submissions } from '../schema';
import { requireAuth } from '../middleware/auth';
import type { AppEnv } from '../middleware/auth';

/**
 * Byte cap on a draft save or a submit body. Sized from a maximal serialized draft: 1,500 labels,
 * each with a 1,000-character note of 4-byte UTF-8 characters plus ids and metadata, measures about
 * 6.2 MB (pinned by a test). The client enforces the 1,000-character note limit and checks this cap
 * before sending.
 */
export const REVIEW_BODY_MAX_BYTES = 8 * 1024 * 1024;

/** The reviewer's current draft for one sample, or the empty (version 0) sentinel. */
export async function currentDraft(
  db: AppDb,
  reviewerId: string,
  sampleId: string,
): Promise<{ state: unknown; version: number }> {
  const rows = await db
    .select({ state: reviews.state, version: reviews.version })
    .from(reviews)
    .where(and(eq(reviews.reviewerId, reviewerId), eq(reviews.sampleId, sampleId)))
    .limit(1);
  const row = rows[0];
  return row ? { state: row.state, version: row.version } : { state: null, version: 0 };
}

/**
 * Per-sample review DRAFT persistence with optimistic concurrency. `state` is the viewer's
 * `SampleReview` shape (chosen texts + per-cell labels), stored opaquely as JSONB (the viewer's
 * tolerant parser owns the shape; the API does not re-implement it). `version` guards cross-device
 * conflicts: a save carrying a stale version is rejected 409 with the current `{state, version}` so
 * the client can reconcile. All routes require auth (and, being non-GET, the PUT/POST/DELETE also
 * pass the CSRF check inside `requireAuth`).
 *
 * Only the active sample (`activeSampleId`) can gain a draft or a submission: a save or submit for
 * any other id is 404 `{error: "unknown sample"}`, so the store never holds rows for a sample this
 * service does not serve. Reads, the list and discard stay open for every id, so drafts from an
 * earlier active sample remain visible and removable.
 */
export function reviewRoutes(db: AppDb, activeSampleId: string): Hono<AppEnv> {
  const route = new Hono<AppEnv>();
  route.use('*', requireAuth(db));
  const unknownSample = (sampleId: string) => sampleId !== activeSampleId;

  // List all of this reviewer's drafts (so a landing page can show real cross-device progress
  // without opening each sample). Returns [{sampleId, state, version}].
  route.get('/', async (c) => {
    const reviewerId = c.get('reviewerId');
    const rows = await db
      .select({ sampleId: reviews.sampleId, state: reviews.state, version: reviews.version })
      .from(reviews)
      .where(eq(reviews.reviewerId, reviewerId));
    return c.json({ drafts: rows });
  });

  // Load this reviewer's draft for a sample. Absent → {state: null, version: 0}.
  route.get('/:sampleId', async (c) => {
    const draft = await currentDraft(db, c.get('reviewerId'), c.req.param('sampleId'));
    return c.json(draft);
  });

  // Save (create or update) with optimistic concurrency. Body: {state: object, version: number}.
  // version 0 = "new draft" (insert); >0 = update only if it matches the stored version. The body
  // is byte-capped so an authenticated reviewer can't store arbitrarily large JSONB.
  route.put('/:sampleId', bodyLimit({ maxSize: REVIEW_BODY_MAX_BYTES }), async (c) => {
    const reviewerId = c.get('reviewerId');
    const sampleId = c.req.param('sampleId');
    if (unknownSample(sampleId)) return c.json({ error: 'unknown sample' }, 404);
    const body = await c.req.json().catch(() => null);
    if (
      !body ||
      typeof body !== 'object' ||
      typeof body.version !== 'number' ||
      typeof body.state !== 'object' ||
      body.state === null ||
      Array.isArray(body.state)
    ) {
      return c.json({ error: 'invalid body' }, 400);
    }
    const { state, version } = body as { state: unknown; version: number };

    if (version === 0) {
      const inserted = await db
        .insert(reviews)
        .values({ reviewerId, sampleId, state, version: 1 })
        .onConflictDoNothing({ target: [reviews.reviewerId, reviews.sampleId] })
        .returning({ version: reviews.version });
      if (inserted.length === 0) {
        return c.json({ error: 'conflict', ...(await currentDraft(db, reviewerId, sampleId)) }, 409);
      }
      return c.json({ version: inserted[0]!.version });
    }

    const updated = await db
      .update(reviews)
      .set({ state, version: sql`${reviews.version} + 1`, updatedAt: new Date() })
      .where(
        and(
          eq(reviews.reviewerId, reviewerId),
          eq(reviews.sampleId, sampleId),
          eq(reviews.version, version),
        ),
      )
      .returning({ version: reviews.version });
    if (updated.length === 0) {
      return c.json({ error: 'conflict', ...(await currentDraft(db, reviewerId, sampleId)) }, 409);
    }
    return c.json({ version: updated[0]!.version });
  });

  // Submit a review: freeze a snapshot into the immutable `submissions` table. There is NO update or
  // delete path — immutability is by construction (insert-only).
  route.post('/:sampleId/submit', bodyLimit({ maxSize: REVIEW_BODY_MAX_BYTES }), async (c) => {
    const reviewerId = c.get('reviewerId');
    const sampleId = c.req.param('sampleId');
    if (unknownSample(sampleId)) return c.json({ error: 'unknown sample' }, 404);
    const body = await c.req.json().catch(() => null);
    if (
      !body ||
      typeof body.review !== 'object' ||
      body.review === null ||
      Array.isArray(body.review)
    ) {
      return c.json({ error: 'invalid body' }, 400);
    }
    const inserted = await db
      .insert(submissions)
      .values({ reviewerId, sampleId, review: body.review })
      .returning({ id: submissions.id, submittedAt: submissions.submittedAt });
    return c.json({ submission: inserted[0] }, 201);
  });

  // List this reviewer's submissions for a sample (newest first) — metadata only, so the UI can
  // show "submitted at …".
  route.get('/:sampleId/submissions', async (c) => {
    const reviewerId = c.get('reviewerId');
    const sampleId = c.req.param('sampleId');
    const rows = await db
      .select({ id: submissions.id, submittedAt: submissions.submittedAt })
      .from(submissions)
      .where(and(eq(submissions.reviewerId, reviewerId), eq(submissions.sampleId, sampleId)))
      .orderBy(desc(submissions.submittedAt));
    return c.json({ submissions: rows });
  });

  // Discard this reviewer's draft for a sample ("start over"). Idempotent — deleting a
  // non-existent draft is a no-op 200.
  route.delete('/:sampleId', async (c) => {
    const reviewerId = c.get('reviewerId');
    const sampleId = c.req.param('sampleId');
    await db
      .delete(reviews)
      .where(and(eq(reviews.reviewerId, reviewerId), eq(reviews.sampleId, sampleId)));
    return c.json({ ok: true });
  });

  return route;
}
