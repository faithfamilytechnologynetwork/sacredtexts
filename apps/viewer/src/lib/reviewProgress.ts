// The review progress dashboard's counts (issue #161): every reviewer's labels from `GET /api/progress`
// joined with the active sample, per reviewer and per text. Plain counts only (the owner's ruling,
// Spec 154). `inPass` here is the text's cell count in the whole sample, which is a reviewer's pass
// for that text.

import type { ReviewerProgress } from "./reviewApi";
import type { PassProgress, ReviewSample, TextProgress } from "./reviewSample";

export interface ReviewerTextProgress extends TextProgress {
  /** False for a text the reviewer labelled in but no longer has chosen. */
  chosen: boolean;
}

export interface ReviewerRow {
  name: string;
  /** Every text they chose or labelled in, in the sample's text order. */
  texts: ReviewerTextProgress[];
  /** Sample cells they have labelled. */
  labelled: number;
  updatedAt: string;
}

export interface ProgressDashboard {
  reviewers: ReviewerRow[];
  /** Per text and overall: the cells labelled by anyone / the cells in the sample. */
  coverage: PassProgress;
}

export function progressDashboard(sample: ReviewSample, reviewers: readonly ReviewerProgress[]): ProgressDashboard {
  const textOf = new Map(sample.cells.map((c) => [c.cell_id, c.text]));
  const cellsIn = new Map<string, number>();
  for (const cell of sample.cells) cellsIn.set(cell.text, (cellsIn.get(cell.text) ?? 0) + 1);
  const perText = (cellIds: Iterable<string>) => {
    const counts = new Map<string, number>();
    for (const id of cellIds) {
      const text = textOf.get(id);
      if (text !== undefined) counts.set(text, (counts.get(text) ?? 0) + 1);
    }
    return counts;
  };
  const sum = (counts: Map<string, number>) => [...counts.values()].reduce((n, k) => n + k, 0);

  const rows = reviewers.map((r) => {
    const labelled = perText(r.labelledCellIds);
    return {
      name: r.name,
      texts: sample.texts
        .filter((t) => r.texts.includes(t.id) || labelled.has(t.id))
        .map((t) => ({
          text: t.id,
          label: t.label,
          labelled: labelled.get(t.id) ?? 0,
          inPass: cellsIn.get(t.id) ?? 0,
          chosen: r.texts.includes(t.id),
        })),
      labelled: sum(labelled),
      updatedAt: r.updatedAt,
    };
  });

  const byAnyone = perText(new Set(reviewers.flatMap((r) => r.labelledCellIds)));
  return {
    reviewers: rows,
    coverage: {
      texts: sample.texts.map((t) => ({ text: t.id, label: t.label, labelled: byAnyone.get(t.id) ?? 0, inPass: cellsIn.get(t.id) ?? 0 })),
      overall: { labelled: sum(byAnyone), inPass: sample.cells.length },
    },
  };
}
