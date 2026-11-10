import { useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ReviewAuthGate, ReviewerBadge, ReviewSaveStatus } from "../components/ReviewAuthGate";
import { ReviewProgress } from "../components/ReviewProgress";
import { OUTCOME_LABEL } from "../components/ReviewLabelControl";
import { CenteredSpinner } from "../components/Loading";
import { ReviewSampleError } from "../components/ReviewSampleError";
import {
  isLabelled,
  updateReviewState,
  useReviewSample,
  useReviewState,
  useReviewStatus,
  useSampleDraft,
  withTexts,
  type CellLabel,
} from "../lib/review";
import { passCells, progressByText, type ReviewSample } from "../lib/reviewSample";
import { buildGoldSet, goldSetFileName } from "../lib/goldSet";
import { cellLink } from "../lib/reviewLinks";

// `/review` (Spec 154): the reviewer's home. Behind the auth gate it loads the active sample and the
// reviewer's saved draft, then shows the text picker (the choice is saved in the draft), progress per
// text and overall, the pass (the sample's cells from the chosen texts, in sample order, each linking
// to its labelling page), and the gold-set download.

export function ReviewPage() {
  return (
    <ReviewAuthGate>
      <ReviewPageInner />
    </ReviewAuthGate>
  );
}

function ReviewPageInner() {
  const load = useReviewSample();
  if (load.state === "loading") return <CenteredSpinner label="Loading the sample…" />;
  if (load.state === "error") return <ReviewSampleError load={load} />;
  return <ReviewHome sample={load.sample} />;
}

const NO_LABELS: Readonly<Record<string, CellLabel>> = {};
const NO_TEXTS: readonly string[] = [];

function ReviewHome({ sample }: { sample: ReviewSample }) {
  const sid = sample.sample_id;
  const draft = useSampleDraft(sid);
  const review = useReviewState();
  const status = useReviewStatus();
  const texts = review.samples[sid]?.texts ?? NO_TEXTS;
  const labels = review.samples[sid]?.labels ?? NO_LABELS;

  const pass = useMemo(() => passCells(sample, texts), [sample, texts]);
  const progress = useMemo(() => progressByText(sample, texts, labels), [sample, texts, labels]);
  const textLabel = useMemo(() => new Map(sample.texts.map((t) => [t.id, t.label])), [sample]);
  const nextUnlabelled = pass.find((c) => !isLabelled(labels[c.cell_id]));
  const labelledCount = Object.values(labels).filter(isLabelled).length;

  const [downloadError, setDownloadError] = useState<string | null>(null);

  function toggleText(id: string, chosen: boolean) {
    // Keep the sample's text order, so the saved choice doesn't depend on click order.
    const next = sample.texts.map((t) => t.id).filter((t) => (t === id ? chosen : texts.includes(t)));
    updateReviewState((s) => withTexts(s, sid, next));
  }

  function downloadGoldSet() {
    setDownloadError(null);
    try {
      const text = buildGoldSet(sample, labels, status.reviewer?.id ?? "");
      saveTextFile(goldSetFileName(sid), text);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "couldn't build the gold set");
    }
  }

  return (
    <div className="flex flex-col gap-6" data-testid="review-page">
      <header className="flex flex-col gap-3 border-b border-default-200 pb-4">
        <ReviewerBadge />
        <h1 className="text-xl font-semibold">Review</h1>
        <p className="text-sm text-default-600">
          Record the true outcome of each cell in your pass, guided by the rubric beside it. Your labels
          save as you go; download them as a gold set to compare matcher versions.
        </p>
        <p className="text-xs text-default-500" data-testid="sample-meta">
          Sample <span className="font-mono">{sid}</span> · {sample.cells.length} cells from{" "}
          <span className="font-mono">{sample.source_run}</span> · seed{" "}
          <span className="font-mono">{sample.seed}</span> · {sample.per_stratum} per stratum
        </p>
        <ReviewSaveStatus />
        {draft.failed && (
          <button type="button" onClick={draft.retry} className="self-start text-xs text-accent hover:underline">
            Try loading your labels again
          </button>
        )}
      </header>

      <section className="flex flex-col gap-2" aria-labelledby="texts-heading">
        <h2 id="texts-heading" className="text-sm font-semibold">
          Your texts
        </h2>
        <p className="text-xs text-default-500">Choose the texts you know well. Your pass is the sample&rsquo;s cells from them.</p>
        <fieldset className="grid gap-1 sm:grid-cols-2" disabled={!draft.loaded} aria-label="Texts">
          {sample.texts.map((t) => (
            <label key={t.id} className="flex items-center gap-2 text-sm text-default-700">
              <input type="checkbox" checked={texts.includes(t.id)} onChange={(e) => toggleText(t.id, e.target.checked)} />
              <span>
                {t.label} <span className="text-default-400">({t.drawn} cells)</span>
              </span>
            </label>
          ))}
        </fieldset>
      </section>

      {texts.length === 0 ? (
        <p className="rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800" data-testid="choose-texts">
          Choose at least one text above to start your pass.
        </p>
      ) : (
        <>
          <ReviewProgress progress={progress} />

          <section className="flex flex-col gap-2" aria-labelledby="pass-heading">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="pass-heading" className="text-sm font-semibold">
                Your pass ({pass.length} cells)
              </h2>
              {nextUnlabelled ? (
                <Link {...cellLink(nextUnlabelled.cell_id)} className="text-sm text-accent hover:underline" data-testid="continue-link">
                  Continue with the next unlabelled cell →
                </Link>
              ) : (
                <span className="text-sm text-success-700">Every cell in your pass is labelled.</span>
              )}
            </div>
            <ol className="flex flex-col divide-y divide-default-200 rounded-lg border border-default-200" data-testid="pass-list">
              {pass.map((cell, i) => {
                const label = labels[cell.cell_id];
                return (
                  <li key={cell.cell_id}>
                    <Link
                      {...cellLink(cell.cell_id)}
                      className="flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2 text-sm hover:bg-default-50"
                      data-testid="pass-item"
                    >
                      <span className="w-10 shrink-0 tabular-nums text-default-400">{i + 1}</span>
                      <span className="text-default-700">{textLabel.get(cell.text)}</span>
                      <span className="font-mono text-xs text-default-500">{cell.source.citation}</span>
                      <span className="text-xs text-default-500">{cell.task}</span>
                      <span className="text-xs text-default-500">{cell.model_id}</span>
                      <span className="text-xs text-default-400">matcher: {cell.outcome}</span>
                      <LabelState label={label} />
                    </Link>
                  </li>
                );
              })}
            </ol>
          </section>
        </>
      )}

      <section className="flex flex-col gap-2 border-t border-default-200 pt-4" aria-labelledby="gold-heading">
        <h2 id="gold-heading" className="text-sm font-semibold">
          Gold set
        </h2>
        <p className="text-xs text-default-500">
          Every cell you&rsquo;ve given an outcome, with everything needed to re-score it, as JSONL for{" "}
          <span className="font-mono">review-compare</span>. You have {labelledCount} labelled{" "}
          {labelledCount === 1 ? "cell" : "cells"}.
        </p>
        <button
          type="button"
          onClick={downloadGoldSet}
          disabled={!draft.loaded || labelledCount === 0}
          className="self-start rounded bg-accent px-3 py-1.5 text-sm font-medium text-accent-foreground disabled:opacity-50"
        >
          Download gold set
        </button>
        {downloadError && (
          <p className="text-sm text-danger" role="alert" data-testid="download-error">
            {downloadError}
          </p>
        )}
      </section>
    </div>
  );
}

function LabelState({ label }: { label: CellLabel | undefined }) {
  if (!label || label.outcome === null) {
    return (
      <span className="ml-auto text-xs text-default-400" data-testid="label-state">
        not labelled
      </span>
    );
  }
  return (
    <span className="ml-auto text-xs font-medium text-default-700" data-testid="label-state">
      {OUTCOME_LABEL[label.outcome]}
      {label.defect && <span className="text-warning-700"> · defect</span>}
    </span>
  );
}

/** Hand the browser a text file to save. */
function saveTextFile(name: string, text: string): void {
  const url = URL.createObjectURL(new Blob([text], { type: "application/jsonl" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // Revoke after the click has handed the file over; some browsers drop a download revoked at once.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
