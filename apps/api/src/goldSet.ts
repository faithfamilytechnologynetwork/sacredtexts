// The gold set built server-side (issue #157), for `GET /api/gold-set` and `review-compare
// --from-service`. A port of the viewer's download (`apps/viewer/src/lib/goldSet.ts`) over a stored
// draft: the draft is read as the viewer's tolerant loader reads it (`parseSampleReview`: each label
// field falls back to its default on its own), so this writes exactly the bytes the download would.
// All three writers (this, the viewer, `review_compare.dumps_gold_rows`) are pinned to
// fixtures/review_gold_set.jsonl. A new row or label field means editing every writer (and
// `review_compare.GOLD_KEYS` / `LABEL_KEYS`); the tests pin each writer's key sets to the fixture's.

/** Labels that can't be written as a gold set (the viewer's download refuses the same labels). */
export class GoldSetError extends Error {
  override name = 'GoldSetError';
}

const LABEL_OUTCOMES = ['correct', 'incorrect', 'refused', 'cant_judge'];

type Cell = Record<string, unknown>;

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);
const str = (v: unknown) => (typeof v === 'string' ? v : '');

/** Order strings by Unicode code point, as Python's `sorted` does (JS `<` compares UTF-16 units). */
function compareCodePoints(a: string, b: string): number {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    const x = a.codePointAt(i)!;
    const y = b.codePointAt(i)!;
    if (x !== y) return x - y;
    if (x > 0xffff) i++;
  }
  return a.length - b.length;
}

/** JSON with object keys sorted by code point at every level (Python's `sort_keys=True`). */
function canonicalJson(value: unknown): string {
  if (typeof value === 'number' && !Number.isFinite(value)) {
    throw new GoldSetError(`cannot write the number ${value} to a gold set`);
  }
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (isRecord(value)) {
    const keys = Object.keys(value).sort(compareCodePoints);
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(value[k])}`).join(',')}}`;
  }
  const text = JSON.stringify(value);
  if (text === undefined) throw new GoldSetError(`cannot write a ${typeof value} to a gold set`);
  return text;
}

/** The active sample's cells by id. */
export function cellsById(sampleJson: string): Map<string, Cell> {
  const cells = (JSON.parse(sampleJson) as { cells: Cell[] }).cells;
  return new Map(cells.map((c) => [str(c.cell_id), c]));
}

/** The gold-set file's text for a reviewer's stored draft `state` on the active sample. */
export function buildGoldSet(sampleId: string, cells: Map<string, Cell>, state: unknown, reviewerId: string): string {
  const labels = isRecord(state) && isRecord(state.labels) ? state.labels : {};
  const rows: Array<{ cellId: string; json: string }> = [];
  for (const [cellId, raw] of Object.entries(labels)) {
    const label = isRecord(raw) ? raw : {};
    if (!LABEL_OUTCOMES.includes(label.outcome as string)) continue;
    const cell = cells.get(cellId);
    if (!cell) throw new GoldSetError(`a label names cell ${cellId}, which is not in sample ${sampleId}`);
    const [rubricVersion, labelledAt] = [str(label.rubric_version), str(label.labelled_at)];
    if (rubricVersion === '' || labelledAt === '') {
      throw new GoldSetError(`the label on ${cellId} has lost its rubric version or time; edit it to restamp it`);
    }
    const row = {
      format: 1,
      sample_id: sampleId,
      ...Object.fromEntries(
        ['cell_id', 'run', 'model_id', 'question_id', 'scores_path', 'task', 'text', 'prompt', 'expected', 'answer', 'source']
          .map((k) => [k, cell[k]]),
      ),
      shown: { outcome: cell.outcome, metrics: cell.metrics, grader_path: cell.grader_path },
      label: { outcome: label.outcome, defect: typeof label.defect === 'boolean' ? label.defect : false, notes: str(label.notes) },
      rubric_version: rubricVersion,
      reviewer_id: reviewerId,
      labelled_at: labelledAt,
    };
    rows.push({ cellId, json: canonicalJson(row) });
  }
  return rows
    .sort((a, b) => compareCodePoints(a.cellId, b.cellId))
    .map((r) => `${r.json}\n`)
    .join('');
}
