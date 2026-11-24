import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, it, expect } from 'vitest';
import type { Hono } from 'hono';
import { createApp } from '../app';
import type { AppDb } from '../db';
import { parseSample } from '../sample';
import { reviews } from '../schema';
import { createTestDb } from '../testing/pglite';
import { CSRF_COOKIE, CSRF_HEADER } from '../auth/cookies';
import { LABELS_CSV_COLUMNS } from './labelsCsv';

// Issue #163: every reviewer's labels as CSV, for any signed-in reviewer.
const SAMPLE = parseSample(readFileSync(resolve(process.cwd(), '../../fixtures/review_sample.json'), 'utf8'), 'fixture sample');
type Cell = Record<'cell_id' | 'question_id' | 'run' | 'text' | 'task' | 'model_id' | 'prompt' | 'answer' | 'outcome', string> & {
  expected: Record<string, string>;
};
const CELLS = (JSON.parse(SAMPLE.json) as { cells: Cell[] }).cells;
const json = { 'Content-Type': 'application/json' };
const label = (outcome: unknown, extra: Record<string, unknown> = {}) => ({
  outcome,
  defect: false,
  notes: '',
  rubric_version: '1',
  labelled_at: '2026-11-18T00:00:00.000Z',
  ...extra,
});

async function makeApp(): Promise<{ app: Hono; db: AppDb }> {
  const db = await createTestDb();
  return { app: createApp(db, { allowedOrigins: [], auth: { inviteCode: 'test-invite', secureCookies: false }, sample: SAMPLE }), db };
}

async function signUp(app: Hono, email: string, name: string) {
  const res = await app.request('/api/auth/signup', {
    method: 'POST',
    headers: json,
    body: JSON.stringify({ email, password: 'a-good-password', name, inviteCode: 'test-invite' }),
  });
  const jar = Object.fromEntries(res.headers.getSetCookie().map((c) => c.split(';')[0]!.split('=') as [string, string]));
  const cookie = Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');
  const headers = { ...json, Cookie: cookie, [CSRF_HEADER]: jar[CSRF_COOKIE]! };
  return {
    id: ((await res.json()) as any).reviewer.id as string,
    cookie,
    save: (state: unknown) => app.request(`/api/review/${SAMPLE.sampleId}`, { method: 'PUT', headers, body: JSON.stringify({ state, version: 0 }) }),
  };
}

const download = (app: Hono, cookie?: string) => app.request('/api/labels.csv', { headers: cookie ? { Cookie: cookie } : {} });

/** Parse RFC 4180 CSV (CRLF records, quoted fields with doubled quotes) into records. */
function parseCsv(body: string): string[][] {
  const records: string[][] = [];
  let record: string[] = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < body.length; i++) {
    const ch = body[i]!;
    if (quoted) {
      if (ch === '"' && body[i + 1] === '"') (field += '"'), i++;
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') record.push(field), (field = '');
    else if (ch === '\r' && body[i + 1] === '\n') record.push(field), records.push(record), (record = []), (field = ''), i++;
    else field += ch;
  }
  expect(record).toEqual([]); // the body ends with a full record
  return records;
}

/** The CSV's rows as objects keyed by column, after checking the BOM and the header. */
async function rowsOf(res: Response): Promise<Array<Record<string, string>>> {
  const bytes = new Uint8Array(await res.arrayBuffer());
  expect([...bytes.slice(0, 3)]).toEqual([0xef, 0xbb, 0xbf]); // read as bytes: decoding strips the BOM
  const [header, ...rows] = parseCsv(new TextDecoder('utf-8', { ignoreBOM: true }).decode(bytes.slice(3)));
  // Literal, so a reordered or renamed column fails here, not only in the generator's own constant.
  expect(header!.join(',')).toBe(
    'reviewer_name,reviewer_email,sample_id,cell_id,question_id,run,text,task,model_id,prompt,expected,answer,' +
      'matcher_outcome,human_outcome,defect,notes,rubric_version,labelled_at,draft_updated_at',
  );
  return rows.map((r) => Object.fromEntries(LABELS_CSV_COLUMNS.map((k, i) => [k, r[i]!])));
}

describe('GET /api/labels.csv', () => {
  it("exports every reviewer's labels, one row per labelled cell, with the cell's context from the sample", async () => {
    const { app, db } = await makeApp();
    const zara = await signUp(app, 'zara@example.com', 'Zara');
    const amir = await signUp(app, 'amir@example.com', 'Amir');
    const idle = await signUp(app, 'idle@example.com', 'Idle'); // no draft: no rows
    const [c0, c1, c2, c3] = CELLS as [Cell, Cell, Cell, Cell];
    const note = 'Says "verse 12", then,\nstops — قرآن';
    expect((await zara.save({ texts: ['islam/native'], labels: { [c3.cell_id]: label('incorrect'), [c2.cell_id]: label('correct'), [c0.cell_id]: label('cant_judge') } })).status).toBe(200);
    const amirLabels = {
      'other-run:m:q': label('maybe'), // not in the sample: still a row, with no context; outcome as stored
      [c3.cell_id]: label(null), // picked no outcome yet: no row
      [c2.cell_id]: 'not a label', // no row
      [c1.cell_id]: label('incorrect', { defect: true, notes: note, rubric_version: '2' }),
      'another-run:m:a': label('correct', { notes: '=1+1' }), // two cells outside the sample go by id; notes stay verbatim
    };
    expect((await amir.save({ texts: ['hinduism/english'], labels: amirLabels })).status).toBe(200);
    // A draft from an earlier sample is exported too, under its own sample id.
    await db.insert(reviews).values({ reviewerId: zara.id, sampleId: 'earlier-sample', state: { labels: { [c0.cell_id]: label('refused') } } });

    const res = await download(app, idle.cookie);
    expect(res.status).toBe(200);
    expect(res.headers.get('Content-Type')).toBe('text/csv; charset=utf-8');
    expect(res.headers.get('Content-Disposition')).toMatch(/^attachment; filename="review-labels-\d{4}-\d{2}-\d{2}\.csv"$/);
    const rows = await rowsOf(res);
    // `expected` is the task's ground truth: the scored continuation (not `full_text`), the citation, or yes/no.
    expect([c0, c1, c2, c3].map((c) => c.task)).toEqual(['complete_unit', 'complete_unit', 'cite_passage', 'verify_source']);
    const expected = new Map([c0, c1, c2, c3].map((c) => [c, c.expected.text ?? c.expected.citation ?? c.expected.answer]));
    expect(expected.get(c3)).toMatch(/^(yes|no)$/);
    const context = (c: Cell) => ({
      ...{ question_id: c.question_id, run: c.run, text: c.text, task: c.task, model_id: c.model_id },
      ...{ prompt: c.prompt, expected: expected.get(c), answer: c.answer, matcher_outcome: c.outcome },
    });
    const noContext = Object.fromEntries(Object.keys(context(c0)).map((k) => [k, '']));
    const stamp = { rubric_version: '1', labelled_at: '2026-11-18T00:00:00.000Z' };
    const amirRow = { reviewer_name: 'Amir', reviewer_email: 'amir@example.com', sample_id: SAMPLE.sampleId };
    const zaraRow = { reviewer_name: 'Zara', reviewer_email: 'zara@example.com' };
    expect(rows.map(({ draft_updated_at, ...r }) => r)).toEqual([
      { ...amirRow, cell_id: c1.cell_id, ...context(c1), human_outcome: 'incorrect', defect: 'true', notes: note, rubric_version: '2', labelled_at: stamp.labelled_at },
      { ...amirRow, cell_id: 'another-run:m:a', ...noContext, human_outcome: 'correct', defect: 'false', notes: '=1+1', ...stamp },
      { ...amirRow, cell_id: 'other-run:m:q', ...noContext, human_outcome: 'maybe', defect: 'false', notes: '', ...stamp },
      { ...zaraRow, sample_id: 'earlier-sample', cell_id: c0.cell_id, ...context(c0), human_outcome: 'refused', defect: 'false', notes: '', ...stamp },
      { ...zaraRow, sample_id: SAMPLE.sampleId, cell_id: c0.cell_id, ...context(c0), human_outcome: 'cant_judge', defect: 'false', notes: '', ...stamp },
      { ...zaraRow, sample_id: SAMPLE.sampleId, cell_id: c2.cell_id, ...context(c2), human_outcome: 'correct', defect: 'false', notes: '', ...stamp },
      { ...zaraRow, sample_id: SAMPLE.sampleId, cell_id: c3.cell_id, ...context(c3), human_outcome: 'incorrect', defect: 'false', notes: '', ...stamp },
    ]);
    expect(rows.every((r) => !Number.isNaN(Date.parse(r.draft_updated_at!)))).toBe(true);
  });

  it('is the header alone when no one has labelled anything', async () => {
    const { app } = await makeApp();
    const rev = await signUp(app, 'rev@example.com', 'Rev');
    await rev.save({ labels: [] });
    const res = await download(app, rev.cookie);
    expect(res.status).toBe(200);
    expect(await rowsOf(res)).toEqual([]);
  });

  it('needs a session', async () => {
    const { app } = await makeApp();
    expect((await download(app)).status).toBe(401);
  });
});
