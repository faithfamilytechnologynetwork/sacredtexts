import { pgTable, uuid, text, jsonb, integer, timestamp, unique } from 'drizzle-orm/pg-core';
import { reviewers } from './reviewers';

/**
 * A reviewer's in-progress DRAFT for one review sample (`sample_id` is the committed sample's id,
 * e.g. `facct-2026-11-03-k10`). `state` is the viewer's `SampleReview` shape (the chosen texts
 * and the per-cell labels), stored verbatim as JSONB; the API persists it opaquely and does not
 * re-implement the shape. `version` drives optimistic concurrency: a stale save is rejected (409)
 * and the client reconciles. One draft per (reviewer, sample).
 */
export const reviews = pgTable(
  'reviews',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    reviewerId: uuid('reviewer_id')
      .notNull()
      .references(() => reviewers.id, { onDelete: 'cascade' }),
    sampleId: text('sample_id').notNull(),
    state: jsonb('state').notNull(),
    version: integer('version').notNull().default(1),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [unique('reviews_reviewer_sample_unique').on(t.reviewerId, t.sampleId)],
);
