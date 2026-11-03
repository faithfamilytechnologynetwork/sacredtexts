import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import { CenteredSpinner } from "../components/Loading";
import { RunSelector } from "../components/RunSelector";
import { fetchRunIndex, selectRunId, type RunRef } from "../lib/runIndex";
import { formatCell, formatCoverage, loadSummary, type Summary } from "../lib/localResults";
import { leaderboardRows } from "../lib/leaderboard";

// `/errors`: the picker in front of the error explorer. The explorer lives at
// `/run/$runId/model/$modelId` and needs a run and a model, so this page lists one run's models
// as links into it. The run is chosen exactly as on the leaderboard home: `?run=<id>` when it
// names a known run, else the same default (`selectRunId`); the selector writes `?run=`, so a
// pick is shareable and refresh-safe. Only `summary.json` is read — the headline accuracy and
// coverage beside each model come from it, the per-question join is the explorer's job.

type IndexState =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "failed"; message: string }
  | { status: "ready"; runs: RunRef[] };

// A settled load carries the run id it belongs to. `selectedId` changes during render, before the
// load effect resets the state, so a settled state is only shown when its `runId` matches — never
// the previous run's models (or error) under the newly selected id.
type RunState =
  | { status: "loading" }
  | { status: "error"; runId: string; message: string }
  | { status: "ready"; runId: string; summary: Summary };

export function ErrorsPage() {
  const { run } = useSearch({ from: "/errors" });
  const navigate = useNavigate();
  const [index, setIndex] = useState<IndexState>({ status: "loading" });
  const [runState, setRunState] = useState<RunState>({ status: "loading" });

  // (1) Enumerate the runs once.
  useEffect(() => {
    let live = true;
    (async () => {
      const result = await fetchRunIndex(fetch);
      if (!live) return;
      if (!result.ok) setIndex({ status: "failed", message: result.message });
      else if (result.runs.length === 0) setIndex({ status: "empty" });
      else setIndex({ status: "ready", runs: result.runs });
    })();
    return () => {
      live = false;
    };
  }, []);

  const runs = index.status === "ready" ? index.runs : [];
  const selectedId = useMemo(() => selectRunId(runs, run), [run, runs]);

  // (2) Load the selected run's summary; a `live` guard keeps a slow earlier load from
  // overwriting a newer selection.
  useEffect(() => {
    if (!selectedId) return;
    let live = true;
    setRunState({ status: "loading" });
    (async () => {
      const result = await loadSummary(`/runs/${encodeURIComponent(selectedId)}`, fetch);
      if (!live) return;
      setRunState(
        result.ok
          ? { status: "ready", runId: selectedId, summary: result.summary }
          : { status: "error", runId: selectedId, message: `${result.kind}: ${result.message}` },
      );
    })();
    return () => {
      live = false;
    };
  }, [selectedId]);

  if (index.status === "loading") return <CenteredSpinner label="Discovering runs…" />;
  if (index.status === "failed") {
    return (
      <div role="alert" className="mx-auto max-w-2xl py-16 text-center">
        <p className="font-semibold text-danger">Could not load the run index</p>
        <p className="mt-1 text-sm text-default-500">{index.message}</p>
      </div>
    );
  }
  if (index.status === "empty") {
    return (
      <div className="mx-auto max-w-2xl py-16 text-center">
        <h1 className="text-xl font-semibold">No runs yet</h1>
        <p className="mt-2 text-default-500">
          No benchmark run was found under <code>runs/</code>, so there are no answers to look at.
        </p>
      </div>
    );
  }

  // Only a state settled for the CURRENT selection counts; anything else is still loading.
  const current: RunState =
    runState.status !== "loading" && runState.runId === selectedId ? runState : { status: "loading" };

  return (
    <div>
      <div className="mx-auto max-w-5xl px-4 pt-8">
        <h1 className="text-2xl font-semibold">Verses</h1>
        <p className="mt-1 text-sm text-default-500">
          Pick a model to see every verse it was asked in this run: its answer, the expected text,
          and whether that answer was right, wrong, refused, or never saved. The page filters by task,
          tradition, and kind of mistake.
        </p>
      </div>
      <RunSelector
        runs={runs}
        selectedId={selectedId}
        onSelect={(id) => navigate({ to: "/errors", search: { run: id } })}
        error={current.status === "error" ? `Could not load run ${current.runId}: ${current.message}` : null}
      />
      {current.status === "loading" && <CenteredSpinner label={`Loading run ${selectedId}…`} />}
      {current.status === "ready" && <ModelPicker summary={current.summary} runId={current.runId} />}
    </div>
  );
}

function ModelPicker({ summary, runId }: { summary: Summary; runId: string }) {
  const { rows } = leaderboardRows(summary);
  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      {rows.length === 0 ? (
        <p className="text-sm">This run has no models.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <caption className="sr-only">Models in run {runId}</caption>
            <thead>
              <tr className="border-b text-left">
                <th className="py-1 pr-4">model</th>
                <th className="py-1 pr-4">accuracy</th>
                <th className="py-1 pr-4">coverage</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.modelId} className="border-b">
                  <td className="py-1 pr-4 font-medium">
                    <Link
                      to="/run/$runId/model/$modelId"
                      params={{ runId, modelId: row.modelId }}
                      className="text-default-700 underline"
                    >
                      {row.modelId}
                    </Link>
                  </td>
                  <td className="py-1 pr-4">{formatCell(row.overall)}</td>
                  <td className="py-1 pr-4">{formatCoverage(row.overall)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
