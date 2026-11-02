import type { Cell } from "../lib/localResults";
import type { LeaderboardRow, TraditionRow } from "../lib/leaderboard";

const TASK_LABEL: Record<string, string> = {
  retrieve_quote: "Quote",
  complete_unit: "Complete",
  cite_passage: "Cite",
  verify_source: "Verify",
};

const TRADITION_ORDER = [
  "Christianity",
  "Judaism",
  "Islam",
  "Hinduism",
  "Sikhism",
  "Buddhism",
  "Book of Mormon",
  "Encyclicals",
];

function taskLabel(task: string): string {
  return TASK_LABEL[task] ?? task.replaceAll("_", " ");
}

function pct(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return `${Math.round(value * 100)}`;
}

function rate(cell: Cell | undefined, key: "accuracy" | "coverage" | "refused_rate"): number | null {
  if (!cell) return null;
  const direct = cell[key];
  if (typeof direct === "number") return direct;
  if (key === "refused_rate" && cell.n > 0 && typeof cell.refused === "number") return cell.refused / cell.n;
  return null;
}

function heat(value: number | null): { fill: string; ink: string } {
  if (value === null) return { fill: "#e7e5e4", ink: "#57534e" };
  const t = Math.max(0, Math.min(1, value));
  const mix = (a: number, b: number) => Math.round(a + (b - a) * t);
  const fill = `rgb(${mix(254, 30)}, ${mix(243, 64)}, ${mix(199, 175)})`;
  return { fill, ink: t > 0.62 ? "#fffaf3" : "#1c1917" };
}

function Heatmap({
  title,
  caption,
  rowLabels,
  colKeys,
  colLabels,
  values,
  aria,
  focusModel,
  focusCol,
  onPick,
}: {
  title: string;
  caption: string;
  rowLabels: string[];
  colKeys: string[];
  colLabels: string[];
  values: (number | null)[][];
  aria: string;
  focusModel?: string;
  focusCol?: string;
  onPick: (modelId: string, colKey: string) => void;
}) {
  const labelW = 132;
  const cellW = 78;
  const cellH = 28;
  const headH = 36;
  const width = labelW + colLabels.length * cellW;
  const height = headH + rowLabels.length * cellH;
  return (
    <figure className="min-w-0 rounded-xl border border-default-200 bg-default-50 p-4">
      <figcaption>
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="mt-0.5 text-xs text-default-500">{caption}</p>
      </figcaption>
      <svg
        role="img"
        aria-label={aria}
        viewBox={`0 0 ${width} ${height}`}
        className="mt-3 h-auto w-full"
      >
        {colLabels.map((label, c) => (
          <text
            key={colKeys[c] ?? label}
            x={labelW + c * cellW + cellW / 2}
            y={22}
            textAnchor="middle"
            fontSize="11"
            fontWeight={focusCol && focusCol === colKeys[c] ? 700 : 400}
            fill="currentColor"
            style={{ cursor: "pointer" }}
            onClick={() => rowLabels[0] && onPick(focusModel ?? rowLabels[0], colKeys[c] ?? label)}
          >
            {label}
          </text>
        ))}
        {rowLabels.map((row, r) => {
          const dim = !!focusModel && focusModel !== row;
          return (
          <g key={row} opacity={dim ? 0.28 : 1} style={{ cursor: "pointer" }} onClick={() => onPick(row, focusCol ?? colKeys[0] ?? "")}>
            <text x={0} y={headH + r * cellH + 18} fontSize="12" fontWeight={focusModel === row ? 700 : 400} fill="currentColor">
              {row.length > 18 ? `${row.slice(0, 17)}…` : row}
            </text>
            {colLabels.map((col, c) => {
              const value = values[r]?.[c] ?? null;
              const color = heat(value);
              const selected = focusModel === row && focusCol === colKeys[c];
              return (
                <g key={col} onClick={(e) => { e.stopPropagation(); onPick(row, colKeys[c] ?? col); }}>
                  <rect
                    x={labelW + c * cellW + 3}
                    y={headH + r * cellH + 2}
                    width={cellW - 6}
                    height={cellH - 4}
                    rx={4}
                    fill={color.fill}
                    stroke={selected ? "#b45309" : "transparent"}
                    strokeWidth={selected ? 2 : 0}
                  >
                    <title>{`${row} · ${col}: ${value === null ? "n/a" : `${Math.round(value * 100)}%`}`}</title>
                  </rect>
                  <text
                    x={labelW + c * cellW + cellW / 2}
                    y={headH + r * cellH + 18}
                    textAnchor="middle"
                    fontSize="11"
                    fontWeight={600}
                    fill={color.ink}
                  >
                    {pct(value)}
                  </text>
                </g>
              );
            })}
          </g>
          );
        })}
      </svg>
    </figure>
  );
}

function GroupedBars({
  rows,
  focusModel,
  onPick,
}: {
  rows: LeaderboardRow[];
  focusModel?: string;
  onPick: (modelId: string) => void;
}) {
  const labelW = 128;
  const track = 420;
  const rowH = 34;
  const width = labelW + track + 36;
  const height = 28 + rows.length * rowH;
  const series = [
    { key: "accuracy" as const, label: "Accuracy", color: "#1d4ed8" },
    { key: "coverage" as const, label: "Coverage", color: "#0f766e" },
    { key: "refused_rate" as const, label: "Refusal", color: "#c2410c" },
  ];
  return (
    <figure className="rounded-xl border border-default-200 bg-default-50 p-4">
      <figcaption>
        <h3 className="text-base font-semibold">Accuracy, coverage, refusal</h3>
        <p className="mt-0.5 text-xs text-default-500">
          Accuracy ignores refusals. Coverage is the share that answered. Refusal is the share that declined.
        </p>
        <div className="mt-2 flex flex-wrap gap-3 text-xs">
          {series.map((s) => (
            <span key={s.key} className="inline-flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: s.color }} />
              {s.label}
            </span>
          ))}
        </div>
      </figcaption>
      <svg
        role="img"
        aria-label="Grouped bars of accuracy, coverage, and refusal for each model"
        viewBox={`0 0 ${width} ${height}`}
        className="mt-3 h-auto w-full"
      >
        {rows.map((row, i) => {
          const y = 16 + i * rowH;
          const dim = !!focusModel && focusModel !== row.modelId;
          return (
            <g key={row.modelId} opacity={dim ? 0.28 : 1} style={{ cursor: "pointer" }} onClick={() => onPick(row.modelId)}>
              <text x={0} y={y + 16} fontSize="12" fontWeight={focusModel === row.modelId ? 700 : 400} fill="currentColor">
                {row.modelId}
              </text>
              {series.map((s, k) => {
                const value = rate(row.overall, s.key);
                const w = value === null ? 0 : Math.max(0, Math.min(1, value)) * track;
                const by = y + k * 8;
                return (
                  <g key={s.key}>
                    <rect x={labelW} y={by} width={track} height={6} rx={3} fill="#e7e5e4" />
                    <rect x={labelW} y={by} width={w} height={6} rx={3} fill={s.color}>
                      <title>{`${row.modelId} ${s.label}: ${value === null ? "n/a" : `${Math.round(value * 100)}%`}`}</title>
                    </rect>
                  </g>
                );
              })}
              <text x={labelW + track + 8} y={y + 16} fontSize="11" fill="currentColor">
                {pct(rate(row.overall, "accuracy"))}
              </text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}

export function ResultsCharts({
  tasks,
  rows,
  traditions,
  focusModel,
  focusTask,
  focusTradition,
  onPickModel,
  onPickTask,
  onPickTradition,
}: {
  tasks: string[];
  rows: LeaderboardRow[];
  traditions: TraditionRow[];
  focusModel?: string;
  focusTask?: string;
  focusTradition?: string;
  onPickModel: (modelId: string) => void;
  onPickTask: (modelId: string, task: string) => void;
  onPickTradition: (modelId: string, tradition: string) => void;
}) {
  if (rows.length === 0) return null;
  const taskCols = tasks.map(taskLabel);
  const taskValues = rows.map((row) => tasks.map((t) => rate(row.byTask[t], "accuracy")));
  const traditionNames = [
    ...TRADITION_ORDER.filter((name) => traditions.some((row) => row.tradition === name)),
    ...[...new Set(traditions.map((row) => row.tradition))]
      .filter((name) => !TRADITION_ORDER.includes(name))
      .sort(),
  ];
  const byModelTradition = new Map<string, Map<string, Cell | undefined>>();
  for (const row of traditions) {
    const per = byModelTradition.get(row.modelId) ?? new Map<string, Cell | undefined>();
    per.set(row.tradition, row.overall);
    byModelTradition.set(row.modelId, per);
  }
  const traditionValues = rows.map((row) =>
    traditionNames.map((name) => rate(byModelTradition.get(row.modelId)?.get(name), "accuracy")),
  );

  return (
    <section className="mt-6 space-y-4" aria-label="Charts">
      <GroupedBars rows={rows} focusModel={focusModel} onPick={onPickModel} />
      {tasks.length > 0 && (
        <Heatmap
          title="Accuracy by task"
          caption="Click a cell to highlight that model and task in the table. Whole percent."
          rowLabels={rows.map((r) => r.modelId)}
          colKeys={tasks}
          colLabels={taskCols}
          values={taskValues}
          aria="Heatmap of accuracy by model and task"
          focusModel={focusModel}
          focusCol={focusTask}
          onPick={onPickTask}
        />
      )}
      {traditionNames.length > 0 && (
        <Heatmap
          title="Accuracy by tradition"
          caption="Click a cell to follow that tradition into the table. Deeper blue is higher accuracy."
          rowLabels={rows.map((r) => r.modelId)}
          colKeys={traditionNames}
          colLabels={traditionNames.map((name) => (name.length > 14 ? `${name.slice(0, 13)}…` : name))}
          values={traditionValues}
          aria="Heatmap of accuracy by model and tradition"
          focusModel={focusModel}
          focusCol={focusTradition}
          onPick={onPickTradition}
        />
      )}
    </section>
  );
}
