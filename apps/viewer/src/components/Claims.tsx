import { useState } from "react";
import type { Cell, Summary } from "../lib/localResults";
import type { LeaderboardRow } from "../lib/leaderboard";

type Mode = "quote-cite" | "answer-refuse" | "prompt" | "verify";

interface Point {
  modelId: string;
  x: number;
  y: number;
  n: number;
}

function rate(row: LeaderboardRow, task: string, key: "accuracy" | "coverage" | "refused_rate"): number | null {
  const cell = task === "_overall" ? row.overall : row.byTask[task];
  if (!cell || cell.n <= 0) return null;
  const direct = cell[key];
  if (typeof direct === "number") return direct;
  if (key === "refused_rate" && typeof cell.refused === "number") return cell.refused / cell.n;
  return null;
}

function cellRate(cell: Cell | undefined): number | null {
  if (!cell || cell.n <= 0 || typeof cell.accuracy !== "number") return null;
  return cell.accuracy;
}

function pointsFor(
  rows: LeaderboardRow[],
  mode: Mode,
  byPrompt: Summary["by_prompt"],
  verify: Summary["verify"],
): Point[] {
  const out: Point[] = [];
  for (const row of rows) {
    if (mode === "quote-cite") {
      const x = rate(row, "retrieve_quote", "accuracy");
      const y = rate(row, "cite_passage", "accuracy");
      const n = (row.byTask.retrieve_quote?.n ?? 0) + (row.byTask.cite_passage?.n ?? 0);
      if (x === null || y === null || n < 20) continue;
      out.push({ modelId: row.modelId, x, y, n });
    } else if (mode === "answer-refuse") {
      const x = rate(row, "_overall", "coverage");
      const y = rate(row, "_overall", "accuracy");
      const n = row.overall?.n ?? 0;
      if (x === null || y === null || n < 30) continue;
      out.push({ modelId: row.modelId, x, y, n });
    } else if (mode === "prompt") {
      const citeEn = byPrompt?.[row.modelId]?.["English prompt"]?.cite_passage;
      const citeNn = byPrompt?.[row.modelId]?.["Native prompt"]?.cite_passage;
      const x = cellRate(citeEn);
      const y = cellRate(citeNn);
      const n = (citeEn?.n ?? 0) + (citeNn?.n ?? 0);
      if (x === null || y === null || n < 20) continue;
      out.push({ modelId: row.modelId, x, y, n });
    } else {
      const yes = verify?.[row.modelId]?.yes;
      const no = verify?.[row.modelId]?.no;
      const x = cellRate(yes);
      const y = cellRate(no);
      const n = (yes?.n ?? 0) + (no?.n ?? 0);
      if (x === null || y === null || n < 20) continue;
      out.push({ modelId: row.modelId, x, y, n });
    }
  }
  return out;
}

function widest(points: Point[]): Point | undefined {
  return points.reduce<Point | undefined>((best, p) => {
    const gap = Math.abs(p.x - p.y);
    if (!best || gap > Math.abs(best.x - best.y)) return p;
    return best;
  }, undefined);
}

const NOTES: Record<Mode, { x: string; y: string; note: string }> = {
  "quote-cite": {
    x: "Quote accuracy",
    y: "Cite accuracy",
    note: "Above the diagonal, the model names the verse more often than it can quote it. Below, it quotes a verse it does not name.",
  },
  "answer-refuse": {
    x: "Coverage",
    y: "Accuracy when it answers",
    note: "A point high and far left answers rarely and is often right when it does. That rank is a refusal habit.",
  },
  prompt: {
    x: "Cite accuracy, English prompt",
    y: "Cite accuracy, native prompt",
    note: "Same task, split by the language of the prompt. Above the diagonal, the native prompt names the verse and the English prompt does not.",
  },
  verify: {
    x: "Accuracy on a real passage",
    y: "Accuracy rejecting a passage from somewhere else",
    note: "Above the diagonal, the model is surer that a passage is not from this edition than that a real passage is.",
  },
};

export function Claims({
  rows,
  byPrompt,
  verify,
  focusModel,
  onPick,
}: {
  rows: LeaderboardRow[];
  byPrompt?: Summary["by_prompt"];
  verify?: Summary["verify"];
  focusModel?: string;
  onPick: (modelId: string) => void;
}) {
  const available = (["quote-cite", "answer-refuse", "prompt", "verify"] as const).filter(
    (mode) => pointsFor(rows, mode, byPrompt, verify).length >= 2,
  );
  const [mode, setMode] = useState<Mode>(available[0] ?? "quote-cite");
  const active = available.includes(mode) ? mode : available[0];
  const points = active ? pointsFor(rows, active, byPrompt, verify) : [];
  if (points.length < 2) return null;
  const standout = widest(points);
  const w = 560;
  const h = 420;
  const padL = 52;
  const padB = 46;
  const padT = 16;
  const padR = 16;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;
  const px = (v: number) => padL + v * plotW;
  const py = (v: number) => padT + (1 - v) * plotH;

  if (!active) return null;
  const xLabel = NOTES[active].x;
  const yLabel = NOTES[active].y;
  const note = NOTES[active].note;
  const buttons: [Mode, string][] = [
    ["quote-cite", "Quote against cite"],
    ["answer-refuse", "Accuracy against coverage"],
    ["prompt", "English prompt against native"],
    ["verify", "Real passage against a fake"],
  ];

  return (
    <section className="mt-6 rounded-2xl border border-default-200 bg-default-50 p-4" aria-label="Core claim">
      <p className="text-xs font-medium uppercase tracking-wide text-default-500">The claim</p>
      <h2 className="mt-1 text-xl font-semibold">One accuracy number ranks the wrong thing.</h2>
      <p className="mt-1 max-w-3xl text-sm text-default-600">{note}</p>
      <div className="mt-3 flex flex-wrap gap-2" role="group" aria-label="Claim chart">
        {buttons.filter(([id]) => available.includes(id)).map(([id, label]) => (
          <button
            key={id}
            type="button"
            aria-pressed={active === id}
            onClick={() => setMode(id)}
            className={`rounded-full px-3 py-1 text-sm ${active === id ? "bg-foreground text-background" : "bg-background text-default-700"}`}
          >
            {label}
          </button>
        ))}
      </div>
      {standout && (
        <button
          type="button"
          onClick={() => onPick(standout.modelId)}
          className="mt-3 block text-left text-sm text-default-700 underline decoration-dotted"
        >
          Widest split: {standout.modelId}, {Math.round(standout.x * 100)}% {xLabel.toLowerCase()} and {Math.round(standout.y * 100)}% {yLabel.toLowerCase()}.
        </button>
      )}
      <svg role="img" aria-label={`${yLabel} against ${xLabel} for each model`} viewBox={`0 0 ${w} ${h}`} className="mt-2 h-auto w-full">
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <g key={t}>
            <line x1={px(t)} y1={padT} x2={px(t)} y2={padT + plotH} stroke="#e7e5e4" />
            <line x1={padL} y1={py(t)} x2={padL + plotW} y2={py(t)} stroke="#e7e5e4" />
            <text x={px(t)} y={h - 18} textAnchor="middle" fontSize="11" fill="currentColor">{Math.round(t * 100)}</text>
            <text x={14} y={py(t) + 4} fontSize="11" fill="currentColor">{Math.round(t * 100)}</text>
          </g>
        ))}
        <line x1={px(0)} y1={py(0)} x2={px(1)} y2={py(1)} stroke="#a8a29e" strokeDasharray="4 4" />
        <text x={w / 2} y={h - 2} textAnchor="middle" fontSize="12" fill="currentColor">{xLabel}</text>
        <text x={14} y={12} fontSize="12" fill="currentColor">{yLabel}</text>
        {points.map((p) => {
          const dim = !!focusModel && focusModel !== p.modelId;
          const on = focusModel === p.modelId;
          return (
            <g key={p.modelId} opacity={dim ? 0.3 : 1} style={{ cursor: "pointer" }} onClick={() => onPick(p.modelId)}>
              <circle cx={px(p.x)} cy={py(p.y)} r={on ? 9 : 6} fill={on ? "#b45309" : "#1d4ed8"}>
                <title>{`${p.modelId}: ${Math.round(p.x * 100)}% by ${Math.round(p.y * 100)}%, n=${p.n}`}</title>
              </circle>
              <text x={px(p.x) + 8} y={py(p.y) - 8} fontSize="11" fontWeight={on ? 700 : 500} fill="currentColor">
                {p.modelId}
              </text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}
