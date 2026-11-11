import { LABEL_OUTCOMES, NOTES_MAX_CHARS, type CellLabel, type LabelOutcome, type LabelPatch } from "../lib/review";

// The intake widget of the review workflow, adapted from multibench's ReviewCheckControl: the true
// outcome as a four-way choice (click the chosen one again to clear it), the question-defect flag,
// and notes capped at NOTES_MAX_CHARS with a counter. Only a label with an outcome is a judgement:
// a flag or a note alone isn't counted in progress or written to the gold set.

export const OUTCOME_LABEL: Record<LabelOutcome, string> = {
  correct: "Correct",
  incorrect: "Incorrect",
  refused: "Refused",
  cant_judge: "Can't judge",
};

const ACTIVE_CLASS: Record<LabelOutcome, string> = {
  correct: "border-success bg-success-soft text-success-soft-foreground",
  incorrect: "border-danger bg-danger-soft text-danger-soft-foreground",
  refused: "border-default-500 bg-default-soft text-default-soft-foreground",
  cant_judge: "border-warning bg-warning-soft text-warning-soft-foreground",
};

export function ReviewLabelControl({
  label,
  onChange,
  disabled = false,
}: {
  label: CellLabel;
  onChange: (patch: LabelPatch) => void;
  /** While the saved labels are loading (or their load failed), the inputs are inert: an edit on a
   * blank base would be dropped when the saved draft is adopted. Gate until the load succeeds. */
  disabled?: boolean;
}) {
  return (
    <div
      className="flex flex-col gap-3 rounded-lg border border-default-200 bg-surface-secondary p-3"
      data-testid="review-label-control"
    >
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="True outcome">
        <span className="text-xs font-semibold uppercase tracking-wide text-default-500">True outcome</span>
        {LABEL_OUTCOMES.map((outcome) => {
          const active = label.outcome === outcome;
          return (
            <button
              key={outcome}
              type="button"
              aria-pressed={active}
              disabled={disabled}
              onClick={() => onChange({ outcome: active ? null : outcome })}
              className={
                "rounded-full border px-3 py-1 text-sm transition-colors disabled:opacity-50 " +
                (active ? ACTIVE_CLASS[outcome] : "border-default-200 bg-background text-default-600 hover:border-default-300")
              }
            >
              {OUTCOME_LABEL[outcome]}
            </button>
          );
        })}
      </div>

      <label className="flex items-start gap-2 text-sm text-default-700">
        <input
          type="checkbox"
          className="mt-1"
          checked={label.defect}
          disabled={disabled}
          onChange={(e) => onChange({ defect: e.target.checked })}
        />
        <span>
          Question defect <span className="text-default-500">— the expected text or the prompt is itself wrong</span>
        </span>
      </label>

      <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
        <span className="flex items-baseline justify-between gap-2">
          Notes
          <span className="font-normal tabular-nums" data-testid="notes-counter">
            {label.notes.length} / {NOTES_MAX_CHARS}
          </span>
        </span>
        <textarea
          value={label.notes}
          maxLength={NOTES_MAX_CHARS}
          onChange={(e) => onChange({ notes: e.target.value.slice(0, NOTES_MAX_CHARS) })}
          placeholder="What did you see? Edge cases, a rubric question, a defect…"
          rows={3}
          dir="auto"
          disabled={disabled}
          className="script-text rounded border border-default-200 bg-background px-2 py-1 text-sm text-default-800 disabled:opacity-50"
        />
      </label>

      {label.outcome === null && (label.defect || label.notes !== "") && (
        <p className="text-xs text-warning-700" data-testid="label-needs-outcome">
          Pick an outcome: a flag or a note alone isn&rsquo;t counted or downloaded.
        </p>
      )}
    </div>
  );
}
