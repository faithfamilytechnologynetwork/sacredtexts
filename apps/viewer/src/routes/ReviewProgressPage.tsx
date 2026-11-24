import { useEffect, useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ReviewAuthGate, ReviewerBadge } from "../components/ReviewAuthGate";
import { ReviewProgressBar } from "../components/ReviewProgress";
import { CenteredSpinner } from "../components/Loading";
import { ReviewSampleError } from "../components/ReviewSampleError";
import { useReviewSample } from "../lib/review";
import { getProgress, type ReviewerProgress } from "../lib/reviewApi";
import type { ReviewSample } from "../lib/reviewSample";
import { progressDashboard } from "../lib/reviewProgress";

// `/review/progress` (issue #161): who has reviewed what on the active sample, and how much. Any
// signed-in reviewer sees every reviewer's counts (by name), per text, and how much of each text
// anyone has labelled. Plain counts only (Spec 154). The counts are the reviewers' last saves.

export function ReviewProgressPage() {
  return (
    <ReviewAuthGate>
      <ReviewProgressInner />
    </ReviewAuthGate>
  );
}

function ReviewProgressInner() {
  const load = useReviewSample();
  if (load.state === "loading") return <CenteredSpinner label="Loading the sample…" />;
  if (load.state === "error") return <ReviewSampleError load={load} />;
  return <Dashboard sample={load.sample} />;
}

type ProgressLoad = { state: "loading" } | { state: "ok"; reviewers: ReviewerProgress[] } | { state: "error"; message: string };

function useProgress(sampleId: string): ProgressLoad & { retry: () => void } {
  const [load, setLoad] = useState<ProgressLoad>({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let alive = true;
    setLoad({ state: "loading" });
    getProgress().then(
      (p) => {
        if (!alive) return;
        if (p.sampleId !== sampleId) setLoad({ state: "error", message: `the progress is for sample ${p.sampleId}, not ${sampleId}` });
        else setLoad({ state: "ok", reviewers: p.reviewers });
      },
      (e: unknown) => {
        if (alive) setLoad({ state: "error", message: e instanceof Error ? e.message : "couldn't load the progress" });
      },
    );
    return () => {
      alive = false;
    };
  }, [sampleId, attempt]);
  return { ...load, retry: () => setAttempt((n) => n + 1) };
}

function Dashboard({ sample }: { sample: ReviewSample }) {
  const load = useProgress(sample.sample_id);
  const reviewers = load.state === "ok" ? load.reviewers : null;
  const dashboard = useMemo(() => reviewers && progressDashboard(sample, reviewers), [sample, reviewers]);

  let body;
  if (load.state === "loading") body = <CenteredSpinner label="Loading the progress…" />;
  else if (load.state === "error") {
    body = (
      <div role="alert" className="flex flex-col items-start gap-2">
        <p className="text-sm text-danger">Couldn&rsquo;t load the progress: {load.message}</p>
        <button type="button" onClick={load.retry} className="text-sm text-accent hover:underline">
          Try again
        </button>
      </div>
    );
  } else if (dashboard) {
    body = (
      <>
        <section className="flex flex-col gap-2" aria-labelledby="coverage-heading">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 id="coverage-heading" className="text-sm font-semibold">
              By text: labelled by anyone
            </h2>
            <ReviewProgressBar progress={dashboard.coverage.overall} label="Overall coverage" />
          </div>
          <ul className="flex flex-col gap-1" data-testid="coverage">
            {dashboard.coverage.texts.map((t) => (
              <li key={t.text} className="flex flex-wrap items-center justify-between gap-2 text-sm">
                <span className="text-default-700">{t.label}</span>
                <ReviewProgressBar progress={t} label={`${t.label} coverage`} />
              </li>
            ))}
          </ul>
        </section>

        <section className="flex flex-col gap-2" aria-labelledby="reviewers-heading">
          <h2 id="reviewers-heading" className="text-sm font-semibold">
            By reviewer ({dashboard.reviewers.length})
          </h2>
          {dashboard.reviewers.length === 0 ? (
            <p className="text-sm text-default-600" data-testid="no-reviewers">
              No one has started this sample yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="reviewers">
                <thead>
                  <tr className="border-b border-default-200 text-left text-xs text-default-500">
                    <th className="py-1 pr-4 font-medium">Reviewer</th>
                    <th className="py-1 pr-4 font-medium">Texts</th>
                    <th className="py-1 pr-4 text-right font-medium">Labelled</th>
                    <th className="py-1 font-medium">Last activity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-default-200">
                  {dashboard.reviewers.map((r, i) => (
                    <tr key={i} className="align-top" data-testid="reviewer-row">
                      <td className="py-2 pr-4 font-medium text-default-700">{r.name}</td>
                      <td className="py-2 pr-4">
                        {r.texts.length === 0 ? (
                          <span className="text-xs text-default-400">No texts chosen yet</span>
                        ) : (
                          <ul className="flex flex-col gap-1">
                            {r.texts.map((t) => (
                              <li key={t.text} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1" data-testid="reviewer-text">
                                <span className="text-default-700">
                                  {t.label}
                                  {!t.chosen && <span className="text-xs text-default-400"> (not chosen)</span>}
                                </span>
                                <ReviewProgressBar progress={t} label={`${r.name}: ${t.label} progress`} />
                              </li>
                            ))}
                          </ul>
                        )}
                      </td>
                      <td className="py-2 pr-4 text-right tabular-nums" data-testid="reviewer-labelled">
                        {r.labelled}
                      </td>
                      <td className="whitespace-nowrap py-2 tabular-nums text-default-600">
                        <time dateTime={r.updatedAt}>{r.updatedAt.slice(0, 10)}</time>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6" data-testid="review-progress-page">
      <header className="flex flex-col gap-3 border-b border-default-200 pb-4">
        <ReviewerBadge />
        <h1 className="text-xl font-semibold">Progress</h1>
        <p className="text-sm text-default-600">
          Who has labelled what on sample <span className="font-mono">{sample.sample_id}</span>, as{" "}
          <span className="font-mono">labelled / cells in the sample</span>. A cell counts once it has an outcome. The counts
          are each reviewer&rsquo;s last save; last activity is in UTC.
        </p>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <Link to="/review" className="text-sm text-accent hover:underline">
            ← Back to your pass
          </Link>
          {/* A plain link, not a router Link: the API answers with the file (#163). */}
          <a href="/api/labels.csv" className="text-sm text-accent hover:underline" data-testid="labels-csv-link">
            Download CSV
          </a>
        </div>
        <p className="text-xs text-default-500">
          The CSV has every reviewer&rsquo;s labels (name, email, outcome, defect, notes), one row per labelled cell, with
          each cell&rsquo;s text, task, model, prompt, expected text, answer and matcher outcome.
        </p>
      </header>
      {body}
    </div>
  );
}
