import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  formatCell,
  formatCoverage,
  type Cell,
  type Summary,
} from "../lib/localResults";
import {
  formatTokens,
  hasTraditionData,
  leaderboardRows,
  searchContrast,
  traditionRows,
} from "../lib/leaderboard";
import { Claims } from "./Claims";
import { ResultsCharts } from "./ResultsCharts";
import { spotlights } from "../lib/spotlights";

/** Accuracy as a whole-percent, or "n/a" (null = every answered cell refused / no data). */
function NegativeItems({ cells }: { cells: Record<string, Cell> }) {
  const rows = Object.entries(cells)
    .filter(([, cell]) => cell.n > 0 && typeof cell.accuracy === "number")
    .sort((a, b) => (a[1].accuracy ?? 1) - (b[1].accuracy ?? 1));
  if (rows.length < 2) return null;
  return (
    <section className="mt-6 rounded-2xl border border-default-200 bg-default-50 p-4" aria-label="Negative items">
      <h2 className="text-xl font-semibold">A correct no is not one test</h2>
      <p className="mt-1 max-w-3xl text-sm text-default-600">
        A different script is an alphabet check. The Talmud shown the Bible, and the Book of Mormon
        shown an encyclical, are canon checks. The bar is accuracy among answers. Refusals stay out of it.
      </p>
      <div className="mt-4 space-y-2">
        {rows.map(([name, cell]) => (
          <div key={name} className="grid grid-cols-[16rem_1fr_3rem] items-center gap-3 text-sm">
            <span>{name}</span>
            <span className="h-2.5 rounded-full bg-default-200">
              <span
                className="block h-2.5 rounded-full bg-foreground"
                style={{ width: `${Math.round((cell.accuracy ?? 0) * 100)}%` }}
              />
            </span>
            <span className="text-right">{Math.round((cell.accuracy ?? 0) * 100)}%</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function pct(accuracy: number | null | undefined): string {
  return accuracy === null || accuracy === undefined ? "n/a" : `${Math.round(accuracy * 100)}%`;
}

/** Signed whole-point accuracy delta between two overall cells, or "—" when either is null. */
function accuracyDelta(on: Cell | undefined, off: Cell | undefined): string {
  if (!on || !off || on.accuracy === null || off.accuracy === null) return "—";
  const d = Math.round((on.accuracy - off.accuracy) * 100);
  return `${d > 0 ? "+" : ""}${d} pt`;
}

// The benchmark leaderboard for a single run: one row per model ranked by overall
// accuracy, a column per task, an overall column, per-model token totals, and a
// per-tradition breakdown below. Pure/presentational — it takes a parsed Summary and the
// run id (so model rows and task cells link into the error explorer); data loading and run
// selection live in LeaderboardPage.

export function LeaderboardTable({ summary, runId }: { summary: Summary; runId: string }) {
  const { tasks, rows } = leaderboardRows(summary);
  const showTraditions = hasTraditionData(summary);
  const tRows = showTraditions ? traditionRows(summary, tasks) : [];
  const contrast = searchContrast(summary);
  const cards = spotlights(rows, tasks, tRows);
  const [focus, setFocus] = useState<{ modelId?: string; task?: string; tradition?: string }>({});
  const [view, setView] = useState<"both" | "charts" | "table">("both");
  const showCharts = view !== "table";
  const showTables = view !== "charts";
  const rowClass = (modelId: string) =>
    focus.modelId && focus.modelId !== modelId ? "border-b opacity-40" : "border-b";
  const cellMark = (task: string) =>
    focus.task === task ? "bg-warning-50" : undefined;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">Scores</h1>
        <Link to="/errors" search={{ run: runId }} className="text-sm text-default-700 underline">
          Open the verses
        </Link>
      </div>
      <p className="mt-1 text-sm text-default-500">
        Accuracy is how often a model is right when it answers. Coverage is how often it answers.
        Refusals stay out of accuracy, so a model that declines the hard verse can outrank one that
        tries and misses. Quoting a verse and naming it are scored apart. Traditions are not averaged
        into one score.
      </p>
      {runId === "panel" && (
        <p className="mt-1 text-xs text-default-400">
          Combined from every finished file under each model. A file still being collected stays
          out until it has a summary. Book of Mormon and encyclicals are their own traditions.
        </p>
      )}
      {summary.evaluators && summary.evaluators.length > 0 && (
        <p className="mt-1 text-xs text-default-400">
          Scored by evaluator{summary.evaluators.length === 1 ? "" : "s"}:{" "}
          <span className="font-medium">{summary.evaluators.join(" + ")}</span>
        </p>
      )}

      {cards.length > 0 && (
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {cards.map((card) => {
            const on = focus.modelId === card.modelId && focus.task === card.task && focus.tradition === card.tradition
              && (card.modelId || card.task);
            return (
              <button
                key={card.id}
                type="button"
                onClick={() => setFocus(on ? {} : { modelId: card.modelId, task: card.task, tradition: card.tradition })}
                className={`rounded-xl border px-3 py-3 text-left ${on ? "border-warning-500 bg-warning-50" : "border-default-200 bg-default-50"}`}
              >
                <div className="text-xs font-medium uppercase tracking-wide text-default-500">{card.kicker}</div>
                <div className="mt-1 text-lg font-semibold">{card.title}</div>
                <p className="mt-1 text-sm text-default-600">{card.detail}</p>
              </button>
            );
          })}
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-2" role="group" aria-label="View">
        {(["both", "charts", "table"] as const).map((mode) => (
          <button
            key={mode}
            type="button"
            aria-pressed={view === mode}
            onClick={() => setView(mode)}
            className={`rounded-full px-3 py-1 text-sm ${view === mode ? "bg-foreground text-background" : "bg-default-100 text-default-700"}`}
          >
            {mode === "both" ? "Charts and table" : mode === "charts" ? "Charts" : "Table"}
          </button>
        ))}
        {focus.modelId && (
          <button type="button" className="text-sm text-default-500 underline" onClick={() => setFocus({})}>
            Clear highlight
          </button>
        )}
      </div>

      {showCharts && summary.verify_negative && (
        <NegativeItems cells={summary.verify_negative} />
      )}

      {showCharts && (
        <Claims
          rows={rows}
          byPrompt={summary.by_prompt}
          verify={summary.verify}
          focusModel={focus.modelId}
          onPick={(modelId) => setFocus({ modelId })}
        />
      )}

      {showCharts && (
        <ResultsCharts
          tasks={tasks}
          rows={rows}
          traditions={tRows}
          focusModel={focus.modelId}
          focusTask={focus.task}
          focusTradition={focus.tradition}
          onPickModel={(modelId) => setFocus({ modelId })}
          onPickTask={(modelId, task) => setFocus({ modelId, task })}
          onPickTradition={(modelId, tradition) => setFocus({ modelId, tradition })}
        />
      )}

      {showTables && <h2 className="mt-8 text-lg font-semibold">Numbers</h2>}
      {showTables && <div className="mt-2 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-1 pr-4">model</th>
              {tasks.map((t) => (
                <th key={t} className={`py-1 pr-4 ${cellMark(t) ?? ""}`}>{t}</th>
              ))}
              <th className="py-1 pr-4">overall</th>
              <th className="py-1 pr-4">coverage</th>
              <th className="py-1 pr-4">tokens</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.modelId} className={rowClass(row.modelId)}>
                <td className="py-1 pr-4 font-medium">
                  <Link
                    to="/run/$runId/model/$modelId"
                    params={{ runId, modelId: row.modelId }}
                    className="text-default-700 underline"
                  >
                    {row.modelId}
                  </Link>
                </td>
                {tasks.map((t) => (
                  <td key={t} className={`py-1 pr-4 ${cellMark(t) ?? ""}`}>
                    <Link
                      to="/run/$runId/model/$modelId"
                      params={{ runId, modelId: row.modelId }}
                      search={{ task: t }}
                      className="underline decoration-dotted"
                    >
                      {formatCell(row.byTask[t])}
                    </Link>
                  </td>
                ))}
                <td className="py-1 pr-4 font-semibold">{formatCell(row.overall)}</td>
                <td className="py-1 pr-4 font-semibold">{formatCoverage(row.overall)}</td>
                <td className="py-1 pr-4 text-default-500">{formatTokens(row.tokens)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}

      {showTables && contrast.length > 0 && (
        <>
          <h2 className="mt-8 text-lg font-semibold">Search on vs off</h2>
          <p className="text-xs text-default-400">
            same base model with web search enabled vs disabled — accuracy and coverage side by side
          </p>
          <div className="mt-2 overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-1 pr-4">model</th>
                  <th className="py-1 pr-4">search off</th>
                  <th className="py-1 pr-4">search on</th>
                  <th className="py-1 pr-4">Δ accuracy</th>
                </tr>
              </thead>
              <tbody>
                {contrast.map((p) => (
                  <tr key={p.base} className="border-b">
                    <td className="py-1 pr-4 font-medium">{p.base}</td>
                    <td className="py-1 pr-4">
                      {pct(p.off.overall?.accuracy)} acc · {formatCoverage(p.off.overall)} cov
                    </td>
                    <td className="py-1 pr-4">
                      {pct(p.on.overall?.accuracy)} acc · {formatCoverage(p.on.overall)} cov
                    </td>
                    <td className="py-1 pr-4 font-semibold">{accuracyDelta(p.on.overall, p.off.overall)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showTables && showTraditions && (
        <>
          <h2 className="mt-8 text-lg font-semibold">By tradition</h2>
          <p className="text-xs text-default-400">each observation counts once per listed tradition</p>
          <div className="mt-2 overflow-x-auto">
            <table data-testid="tradition-table" className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-1 pr-4">model</th>
                  <th className="py-1 pr-4">tradition</th>
                  {tasks.map((t) => (<th key={t} className="py-1 pr-4">{t}</th>))}
                  <th className="py-1 pr-4">overall</th>
                </tr>
              </thead>
              <tbody>
                {tRows.map((row) => (
                  <tr
                    key={`${row.modelId}:${row.tradition}`}
                    className={
                      (focus.modelId && focus.modelId !== row.modelId) ||
                      (focus.tradition && focus.tradition !== row.tradition)
                        ? "border-b opacity-40"
                        : "border-b"
                    }
                  >
                    <td className="py-1 pr-4 font-medium">{row.modelId}</td>
                    <td className="py-1 pr-4">{row.tradition}</td>
                    {tasks.map((t) => (
                      <td key={t} className="py-1 pr-4">
                        <Link
                          to="/run/$runId/model/$modelId"
                          params={{ runId, modelId: row.modelId }}
                          search={{ task: t, tradition: row.tradition }}
                          className="underline decoration-dotted"
                        >
                          {formatCell(row.byTask[t])}
                        </Link>
                      </td>
                    ))}
                    <td className="py-1 pr-4 font-semibold">{formatCell(row.overall)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
