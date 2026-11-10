import { pgTable, uuid, text, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { reviewers } from './reviewers';

/**
 * An immutable submission: a frozen copy of a review draft for one sample at submit time. There is
 * no update path; immutability is by construction (insert-only; the API exposes no mutation). FK
 * cascades on reviewer delete.
 */
export const submissions = pgTable('submissions', {
  id: uuid('id').primaryKey().defaultRandom(),
  reviewerId: uuid('reviewer_id')
    .notNull()
    .references(() => reviewers.id, { onDelete: 'cascade' }),
  sampleId: text('sample_id').notNull(),
  review: jsonb('review').notNull(),
  submittedAt: timestamp('submitted_at', { withTimezone: true }).notNull().defaultNow(),
});
