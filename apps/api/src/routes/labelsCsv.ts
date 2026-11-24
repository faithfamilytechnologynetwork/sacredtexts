import { Hono } from 'hono';
import { asc, eq } from 'drizzle-orm';
import type { AppDb } from '../db';
import { cellsById } from '../goldSet';
import { requireAuth } from '../middleware/auth';
import type { AppEnv } from '../middleware/auth';
import type { ActiveSample } from '../sample';
import { reviewers, reviews } from '../schema';

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

/** The export's columns, in order. */
export const LABELS_CSV_COLUMNS = [
  'reviewer_name',
  'reviewer_email',
  'sample_id',
  'cell_id',
  'question_id',
  'run',
  'text',
  'task',
  'model_id',
  'prompt',
  'expected',
  'answer',
  'matcher_outcome',
  'human_outcome',
  'defect',
  'notes',
  'rubric_version',
  'labelled_at',
  'draft_updated_at',
] as const;

/** A stored value as CSV text: a string verbatim, nothing as empty, anything else as its JSON. */
const text = (v: unknown) => (v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v));

/**
 * The expected dict's human-readable ground truth: the text for retrieve_quote/complete_unit, the
 * citation for cite_passage, yes/no for verify_source. The pipeline's `failure_kind.expected_text` and
 * the viewer's `localResults.expectedText` read it the same way.
 */
const expectedText = (expected: unknown) => {
  if (!isRecord(expected)) return undefined;
  for (const k of ['text', 'citation', 'answer']) if (typeof expected[k] === 'string') return expected[k];
  return '';
};

/** One RFC 4180 field: quoted (with doubled quotes) when it holds a comma, quote or line break. */
const csvField = (s: string) => (/[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s);

/**
 * `GET /api/labels.csv` (issue #163): every reviewer's labels, as CSV, for any signed-in reviewer. One
 * row per labelled cell per draft (a label counts once its outcome is non-null), for drafts of every
 * sample, so nothing stored is left out. The cell's context (question, run, text, task, model, prompt,
 * expected text, answer, the matcher's outcome) comes from the active sample by cell id, and is empty
 * for a cell not in it. Rows go by reviewer, then sample, then cell (sample order, then any cell outside
 * the sample by id). UTF-8 with a byte-order mark, so a spreadsheet reads non-Latin text correctly; CRLF
 * line ends.
 */
export function labelsCsvRoute(db: AppDb, sample: ActiveSample): Hono<AppEnv> {
  const cells = cellsById(sample.json);
  const order = new Map([...cells.keys()].map((id, i) => [id, i]));
  const rank = (cellId: string) => order.get(cellId) ?? cells.size; // a cell outside the sample goes last
  const route = new Hono<AppEnv>();
  route.use('*', requireAuth(db));
  route.get('/', async (c) => {
    const drafts = await db
      .select({ name: reviewers.name, email: reviewers.email, sampleId: reviews.sampleId, state: reviews.state, updatedAt: reviews.updatedAt })
      .from(reviews)
      .innerJoin(reviewers, eq(reviewers.id, reviews.reviewerId))
      .orderBy(asc(reviewers.name), asc(reviewers.id), asc(reviews.sampleId));
    const lines = [LABELS_CSV_COLUMNS.join(',')];
    for (const d of drafts) {
      const labels = isRecord(d.state) && isRecord(d.state.labels) ? d.state.labels : {};
      const cellIds = Object.keys(labels)
        .filter((id) => isRecord(labels[id]) && labels[id].outcome != null)
        .sort((a, b) => rank(a) - rank(b) || (a < b ? -1 : a > b ? 1 : 0));
      for (const cellId of cellIds) {
        const label = labels[cellId] as Record<string, unknown>;
        const cell = cells.get(cellId) ?? {};
        const row = [
          d.name,
          d.email,
          d.sampleId,
          cellId,
          cell.question_id,
          cell.run,
          cell.text,
          cell.task,
          cell.model_id,
          cell.prompt,
          expectedText(cell.expected),
          cell.answer,
          cell.outcome,
          label.outcome,
          label.defect,
          label.notes,
          label.rubric_version,
          label.labelled_at,
          d.updatedAt.toISOString(),
        ];
        lines.push(row.map((v) => csvField(text(v))).join(','));
      }
    }
    const filename = `review-labels-${new Date().toISOString().slice(0, 10)}.csv`;
    return c.body(`\uFEFF${lines.map((l) => `${l}\r\n`).join('')}`, 200, {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${filename}"`,
    });
  });
  return route;
}
