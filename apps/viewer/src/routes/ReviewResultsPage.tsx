import { useMemo } from "react";
import { Link } from "@tanstack/react-router";
import { ReviewAuthGate, ReviewerBadge } from "../components/ReviewAuthGate";
import { CenteredSpinner } from "../components/Loading";
import { ReviewSampleError } from "../components/ReviewSampleError";
import { useReviewSample, useReviewState, useReviewStatus, useSampleDraft, type CellLabel } from "../lib/review";
import type { ReviewSample } from "../lib/reviewSample";
import { goldRows } from "../lib/goldSet";
import { agreementReport, formatTally, type AgreementReport, type Tally } from "../lib/reviewResults";
import { cellLink } from "../lib/reviewLinks";

// `/review/results` (issue #157): how the matcher's shown verdict agrees with the signed-in reviewer's
// labels, computed here from the sample and the loaded draft (lib/reviewResults), so it follows every
// edit. The numbers are review-compare's `--version committed` numbers for the same labels.

export function ReviewResultsPage() {
  return (
    <ReviewAuthGate>
      <ReviewResultsInner />
    </ReviewAuthGate>
  );
}

function ReviewResultsInner() {
  const load = useReviewSample();
  if (load.state === "loading") return <CenteredSpinner label="Loading the sample…" />;
  if (load.state === "error") return <ReviewSampleError load={load} />;
  return <Results sample={load.sample} />;
}

const NO_LABELS: Readonly<Record<string, CellLabel>> = {};

function Results({ sample }: { sample: ReviewSample }) {
  const draft = useSampleDraft(sample.sample_id);
  const labels = useReviewState().samples[sample.sample_id]?.labels ?? NO_LABELS;
  const reviewerId = useReviewStatus().reviewer?.id ?? "";
  const textLabel = useMemo(() => new Map(sample.texts.map((t) => [t.id, t.label])), [sample]);
  const cells = useMemo(() => new Map(sample.cells.map((c) => [c.cell_id, c])), [sample]);
  const result = useMemo((): { report: AgreementReport } | { error: string } => {
    try {
      return { report: agreementReport(goldRows(sample, labels, reviewerId)) };
    } catch (e) {
      return { error: e instanceof Error ? e.message : "couldn't count your labels" };
    }
  }, [sample, labels, reviewerId]);

  let body;
  if (!draft.loaded) body = draft.failed ? <p className="text-sm text-danger">Couldn&rsquo;t load your labels.</p> : <CenteredSpinner label="Loading your labels…" />;
  else if ("error" in result) body = <p className="text-sm text-danger" role="alert">{result.error}</p>;
  else if (result.report.rows === 0) body = <p className="text-sm text-default-600" data-testid="no-results">You haven&rsquo;t labelled any cells yet.</p>;
  else {
    const r = result.report;
    body = (
      <>
        <p className="text-sm" data-testid="results-overall">
          Overall: <span className="font-semibold tabular-nums">{formatTally(r.overall)}</span>
        </p>
        <p className="text-xs text-default-500" data-testid="results-excluded">
          {r.rows} labelled; {r.overall.n} judged. Not counted: {r.excluded.total} (can&rsquo;t judge {r.excluded.cant_judge},
          question defect {r.excluded.defect}, both {r.excluded.both}).
        </p>
        <TallyTable title="By task" tallies={r.by_task} />
        <TallyTable title="By text" tallies={r.by_text} name={(t) => textLabel.get(t) ?? t} />
        <TallyTable title="By grader path" tallies={r.by_grader_path} />
        <section className="flex flex-col gap-2" aria-labelledby="disagreements-heading">
          <h2 id="disagreements-heading" className="text-sm font-semibold">
            Disagreements ({r.disagreements.length})
          </h2>
          <ul className="flex flex-col divide-y divide-default-200 rounded-lg border border-default-200" data-testid="disagreements">
            {r.disagreements.map((d) => (
              <li key={d.cell_id}>
                <Link {...cellLink(d.cell_id)} className="flex flex-wrap gap-x-3 gap-y-1 px-3 py-2 text-sm hover:bg-default-50">
                  <span className="text-default-700">{textLabel.get(d.text) ?? d.text}</span>
                  <span className="font-mono text-xs text-default-500">{cells.get(d.cell_id)?.source.citation}</span>
                  <span className="text-xs text-default-500">{d.task}</span>
                  <span className="text-xs text-default-500">{cells.get(d.cell_id)?.model_id}</span>
                  <span className="ml-auto text-xs">
                    you: {d.human} · matcher: {d.version}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6" data-testid="review-results-page">
      <header className="flex flex-col gap-3 border-b border-default-200 pb-4">
        <ReviewerBadge />
        <h1 className="text-xl font-semibold">Results</h1>
        <p className="text-sm text-default-600">
          How often the matcher&rsquo;s verdict matches your labels on sample <span className="font-mono">{sample.sample_id}</span>,
          as <span className="font-mono">agree / n</span>. Can&rsquo;t-judge and question-defect labels are counted apart, not in{" "}
          <span className="font-mono">n</span>.
        </p>
        <Link to="/review" className="self-start text-sm text-accent hover:underline">
          ← Back to your pass
        </Link>
      </header>
      {body}
    </div>
  );
}

function TallyTable({ title, tallies, name = (k) => k }: { title: string; tallies: Record<string, Tally>; name?: (key: string) => string }) {
  return (
    <section className="flex flex-col gap-1" aria-label={title}>
      <h2 className="text-sm font-semibold">{title}</h2>
      <table className="self-start text-sm">
        <tbody>
          {Object.entries(tallies).map(([key, t]) => (
            <tr key={key}>
              <td className="min-w-72 py-0.5 pr-4 text-default-700">{name(key)}</td>
              <td className="py-0.5 tabular-nums">{formatTally(t)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
