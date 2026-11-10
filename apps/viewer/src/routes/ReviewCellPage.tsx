import { useMemo } from "react";
import { getRouteApi, Link } from "@tanstack/react-router";
import { ReviewAuthGate, ReviewSaveStatus } from "../components/ReviewAuthGate";
import { ReviewLabelControl } from "../components/ReviewLabelControl";
import { ReviewSampleError } from "../components/ReviewSampleError";
import { QuestionCard } from "../components/QuestionCard";
import { CenteredSpinner } from "../components/Loading";
import {
  emptyLabel,
  updateReviewState,
  useReviewSample,
  useReviewState,
  useSampleDraft,
  withLabel,
  type LabelPatch,
} from "../lib/review";
import { passCells, toQuestionResult, type ReviewSample, type SampleCell, type SampleTask } from "../lib/reviewSample";
import { CANT_JUDGE_GUIDANCE, RUBRIC, RUBRIC_VERSION } from "../lib/rubric";
import { cellIdFromParam, cellLink } from "../lib/reviewLinks";

const route = getRouteApi("/review/cell/$cellId");

// `/review/cell/$cellId` (Spec 154): label one cell. The cell is rendered with the explorer's card
// (prompt, expected, answer, per-metric scores), next to the matcher's verdict, all its submetrics and
// its grader path, the task's rubric with its version, and the label control. Previous / next walk the
// reviewer's pass. Editing stays off until the reviewer's saved labels have loaded (the ported gate).

export function ReviewCellPage() {
  return (
    <ReviewAuthGate>
      <ReviewCellPageInner />
    </ReviewAuthGate>
  );
}

function ReviewCellPageInner() {
  const { cellId: param } = route.useParams();
  const cellId = cellIdFromParam(param);
  const load = useReviewSample();
  if (load.state === "loading") return <CenteredSpinner label="Loading the sample…" />;
  if (load.state === "error") return <ReviewSampleError load={load} />;
  const cell = load.sample.cells.find((c) => c.cell_id === cellId);
  if (!cell) return <CellNotFound cellId={cellId} sampleId={load.sample.sample_id} />;
  return <ReviewCell sample={load.sample} cell={cell} />;
}

function CellNotFound({ cellId, sampleId }: { cellId: string; sampleId: string }) {
  return (
    <div role="alert" className="mx-auto max-w-xl py-12 text-center" data-testid="cell-not-found">
      <h1 className="text-xl font-semibold">Cell not found</h1>
      <p className="mt-2 text-sm text-default-500">
        <span className="font-mono">{cellId}</span> isn&rsquo;t in the review sample{" "}
        <span className="font-mono">{sampleId}</span>.
      </p>
      <Link to="/review" className="mt-4 inline-block text-sm text-accent hover:underline">
        ← Back to your pass
      </Link>
    </div>
  );
}

function ReviewCell({ sample, cell }: { sample: ReviewSample; cell: SampleCell }) {
  const sid = sample.sample_id;
  const draft = useSampleDraft(sid);
  const review = useReviewState();
  const texts = review.samples[sid]?.texts;
  const label = review.samples[sid]?.labels[cell.cell_id] ?? emptyLabel();

  const pass = useMemo(() => passCells(sample, texts ?? []), [sample, texts]);
  const pos = pass.findIndex((c) => c.cell_id === cell.cell_id);
  const prev = pos > 0 ? pass[pos - 1] : undefined;
  const next = pos >= 0 && pos < pass.length - 1 ? pass[pos + 1] : undefined;
  const result = useMemo(() => toQuestionResult(cell), [cell]);
  const textLabel = sample.texts.find((t) => t.id === cell.text)?.label ?? cell.text;

  const onChange = (patch: LabelPatch) =>
    updateReviewState((s) => withLabel(s, sid, cell.cell_id, patch, new Date()));

  return (
    <div className="flex flex-col gap-5" data-testid="review-cell-page">
      <header className="flex flex-col gap-2 border-b border-default-200 pb-4">
        <nav className="flex flex-wrap items-center justify-between gap-3 text-sm" aria-label="Pass">
          <Link to="/review" className="text-accent hover:underline">
            ← Your pass
          </Link>
          {pos >= 0 && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-default-400" data-testid="pass-position">
                cell {pos + 1} of {pass.length} in your pass
              </span>
              {prev ? (
                <Link {...cellLink(prev.cell_id)} className="text-default-600 hover:text-foreground" aria-label="Previous cell">
                  ← Previous
                </Link>
              ) : (
                <span className="text-default-300">← Previous</span>
              )}
              {next ? (
                <Link {...cellLink(next.cell_id)} className="text-default-600 hover:text-foreground" aria-label="Next cell">
                  Next →
                </Link>
              ) : (
                <span className="text-default-300">Next →</span>
              )}
            </div>
          )}
        </nav>
        {pos < 0 && (
          <p className="text-xs text-warning-700" data-testid="outside-pass">
            This cell&rsquo;s text isn&rsquo;t one of your chosen texts. You can still label it; the label is
            downloaded with the rest.
          </p>
        )}
        <ReviewSaveStatus />
        {draft.failed && (
          <button type="button" onClick={draft.retry} className="self-start text-xs text-accent hover:underline">
            Try loading your labels again
          </button>
        )}
        <h1 className="text-xl font-semibold">
          {textLabel} <span className="font-mono font-normal text-default-600">{cell.source.citation}</span>
        </h1>
        <p className="flex flex-wrap gap-x-3 text-xs text-default-500">
          <span>{cell.task}</span>
          <span>
            model <span className="font-mono">{cell.model_id}</span>
          </span>
          <span className="font-mono">{cell.cell_id}</span>
        </p>
      </header>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <div className="flex flex-col gap-4">
          <QuestionCard r={result} lang={cell.source.language} />
          <MatcherVerdict cell={cell} />
        </div>
        <div className="flex flex-col gap-4">
          <RubricPanel task={cell.task} />
          <ReviewLabelControl label={label} onChange={onChange} disabled={!draft.loaded} />
          {next && (
            <Link {...cellLink(next.cell_id)} className="self-end text-sm text-accent hover:underline">
              Next cell →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

const VERDICT_CLASS: Record<SampleCell["outcome"], string> = {
  correct: "bg-success-100 text-success-700",
  incorrect: "bg-danger-100 text-danger-700",
  refused: "bg-default-200 text-default-700",
};

function metricText(value: unknown): string {
  if (typeof value === "string") return value;
  return JSON.stringify(value) ?? String(value);
}

/** The matcher's verdict as recorded in the run: outcome, grader path and every submetric. */
function MatcherVerdict({ cell }: { cell: SampleCell }) {
  const metrics = Object.entries(cell.metrics).filter(([k]) => k !== "outcome");
  return (
    <section className="flex flex-col gap-2 rounded-lg border border-default-200 p-4" aria-labelledby="matcher-heading" data-testid="matcher-verdict">
      <div className="flex flex-wrap items-center gap-2">
        <h2 id="matcher-heading" className="text-sm font-semibold">
          Matcher verdict
        </h2>
        <span className={`rounded px-2 py-0.5 text-xs font-medium ${VERDICT_CLASS[cell.outcome]}`} data-testid="matcher-outcome">
          {cell.outcome}
        </span>
        <span className="text-xs text-default-500">
          grader path <span className="font-mono text-default-700" data-testid="grader-path">{cell.grader_path}</span>
        </span>
      </div>
      <dl className="flex flex-wrap gap-2">
        {metrics.map(([k, v]) => (
          <div key={k} className="rounded border border-default-200 px-2 py-1">
            <dt className="text-[10px] uppercase tracking-wide text-default-400">{k}</dt>
            <dd className="font-mono text-sm">{metricText(v)}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

/** The task's rubric, with its version (each label records the version it was made under). */
function RubricPanel({ task }: { task: SampleTask }) {
  const rubric = RUBRIC[task];
  return (
    <section className="flex flex-col gap-2 rounded-lg border border-default-200 p-4 text-sm" aria-labelledby="rubric-heading" data-testid="rubric">
      <h2 id="rubric-heading" className="flex flex-wrap items-baseline justify-between gap-2 text-sm font-semibold">
        <span>
          Rubric: <span className="font-mono font-normal">{task}</span>
        </span>
        <span className="text-xs font-normal text-default-500" data-testid="rubric-version">
          version {RUBRIC_VERSION}
        </span>
      </h2>
      <ul className="flex flex-col gap-1.5">
        {rubric.rules.map((rule) => (
          <li key={rule.outcome}>
            <strong>{rule.outcome}:</strong> {rule.text}
          </li>
        ))}
      </ul>
      {rubric.tolerances && (
        <div>
          <p className="text-default-700">Ignore:</p>
          <ul className="ml-5 list-disc text-default-700">
            {rubric.tolerances.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      )}
      <p className="text-default-600">{CANT_JUDGE_GUIDANCE}</p>
    </section>
  );
}
