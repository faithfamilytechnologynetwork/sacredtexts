import type { Cell } from "./localResults";
import type { LeaderboardRow, TraditionRow } from "./leaderboard";

export interface Spotlight {
  id: string;
  kicker: string;
  title: string;
  detail: string;
  modelId?: string;
  task?: string;
  tradition?: string;
}

function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function scored(cell: Cell | undefined, minN: number): cell is Cell & { accuracy: number } {
  return !!cell && cell.n >= minN && typeof cell.accuracy === "number";
}

const TASK_LABEL: Record<string, string> = {
  retrieve_quote: "quoting",
  complete_unit: "completion",
  cite_passage: "citation",
  verify_source: "verification",
};

/** A few findings computed from the cells already on the page. Clicking one focuses
 * the charts and the tables on that model, task, or tradition. */
export function spotlights(
  rows: LeaderboardRow[],
  tasks: string[],
  traditions: TraditionRow[],
): Spotlight[] {
  const out: Spotlight[] = [];
  const ranked = rows.filter((r) => scored(r.overall, 30));
  if (ranked.length > 0) {
    const best = ranked.reduce((a, b) => (a.overall!.accuracy! >= b.overall!.accuracy! ? a : b));
    const worst = ranked.reduce((a, b) => (a.overall!.accuracy! <= b.overall!.accuracy! ? a : b));
    out.push({
      id: "best",
      kicker: "Highest accuracy",
      title: best.modelId,
      detail: `${pct(best.overall!.accuracy!)} when it answers${typeof best.overall!.coverage === "number" ? ` · ${pct(best.overall!.coverage)} coverage` : ""} · n=${best.overall!.n}`,
      modelId: best.modelId,
    });
    if (worst.modelId !== best.modelId) {
      out.push({
        id: "worst",
        kicker: "Lowest accuracy",
        title: worst.modelId,
        detail: `${pct(worst.overall!.accuracy!)} when it answers · n=${worst.overall!.n}`,
        modelId: worst.modelId,
      });
    }
    const refusals = ranked
      .map((r) => {
        const rate = r.overall?.refused_rate ?? (r.overall && r.overall.n > 0 && typeof r.overall.refused === "number" ? r.overall.refused / r.overall.n : null);
        return { row: r, rate };
      })
      .filter((x): x is { row: LeaderboardRow; rate: number } => typeof x.rate === "number");
    if (refusals.length > 0) {
      const top = refusals.reduce((a, b) => (a.rate >= b.rate ? a : b));
      if (top.rate >= 0.15) {
        out.push({
          id: "refusal",
          kicker: "Refuses most",
          title: top.row.modelId,
          detail: `${pct(top.rate)} of its cells are refusals, so they stay out of the accuracy score.`,
          modelId: top.row.modelId,
        });
      }
    }
  }

  const taskPool = tasks.map((task) => {
    let correct = 0;
    let incorrect = 0;
    for (const row of rows) {
      const cell = row.byTask[task];
      if (!cell) continue;
      correct += cell.correct ?? 0;
      incorrect += cell.incorrect ?? 0;
    }
    const answered = correct + incorrect;
    return { task, accuracy: answered > 0 ? correct / answered : null, answered };
  }).filter((t) => t.accuracy !== null && t.answered >= 30);
  if (taskPool.length >= 2) {
    const easiest = taskPool.reduce((a, b) => (a.accuracy! >= b.accuracy! ? a : b));
    const hardest = taskPool.reduce((a, b) => (a.accuracy! <= b.accuracy! ? a : b));
    if (easiest.task !== hardest.task) {
      out.push({
        id: "task-easy",
        kicker: "Easiest task",
        title: TASK_LABEL[easiest.task] ?? easiest.task,
        detail: `${pct(easiest.accuracy!)} across models that answered.`,
        task: easiest.task,
      });
      out.push({
        id: "task-hard",
        kicker: "Hardest task",
        title: TASK_LABEL[hardest.task] ?? hardest.task,
        detail: `${pct(hardest.accuracy!)} across models that answered.`,
        task: hardest.task,
      });
    }
  }

  let widest: { modelId: string; high: string; low: string; gap: number } | null = null;
  const byModel = new Map<string, TraditionRow[]>();
  for (const row of traditions) {
    const list = byModel.get(row.modelId) ?? [];
    list.push(row);
    byModel.set(row.modelId, list);
  }
  for (const [modelId, list] of byModel) {
    const usable = list.filter((r) => scored(r.overall, 20));
    if (usable.length < 2) continue;
    const high = usable.reduce((a, b) => (a.overall!.accuracy! >= b.overall!.accuracy! ? a : b));
    const low = usable.reduce((a, b) => (a.overall!.accuracy! <= b.overall!.accuracy! ? a : b));
    const gap = high.overall!.accuracy! - low.overall!.accuracy!;
    if (!widest || gap > widest.gap) {
      widest = { modelId, high: high.tradition, low: low.tradition, gap };
    }
  }
  if (widest && widest.gap >= 0.15) {
    out.push({
      id: "spread",
      kicker: "Widest tradition gap",
      title: widest.modelId,
      detail: `${pct(widest.gap)} between ${widest.high} and ${widest.low}.`,
      modelId: widest.modelId,
      tradition: widest.low,
    });
  }
  return out.slice(0, 6);
}
