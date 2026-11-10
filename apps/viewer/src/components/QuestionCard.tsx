import { FAILURE_KIND_LABEL, failureSeverity } from "../lib/failureKind";
import { type QuestionResult } from "../lib/localResults";
import { formatMetric } from "../lib/explorer";

// One scored cell, as the error explorer shows it: the pass/fail state, then the four things the
// explorer spec lists side by side for each row: the prompt, the expected text, the model's actual
// answer, and the per-metric similarity scores (exact / normalized / token-F1). A metric reads
// "n/a" where the task emits none; a missing cell's metrics are all "n/a" (no answer was scored),
// so the card keeps a uniform shape while the "missing" badge + "no answer produced" marker make
// its nature unambiguous. The review pages (Spec 154) render cells with this same card.
//
// The prompt, expected and answer are scripture in many scripts (Arabic, Hebrew, Gurmukhi,
// Devanagari, Greek…). Each gets `dir="auto"` so a right-to-left text runs in its own direction,
// the `script-text` font stack, and `lang` when the caller knows the cell's language.

function StatusBadge({ r }: { r: QuestionResult }) {
  if (r.correct) {
    return <span className="rounded bg-success-100 px-2 py-0.5 text-xs font-medium text-success-700">correct</span>;
  }
  if (r.missing) {
    return <span className="rounded bg-warning-100 px-2 py-0.5 text-xs font-medium text-warning-700">missing</span>;
  }
  // Refused (answered but declined) is distinct from a wrong answer — neutral, not the red "wrong"
  // badge — because it is excluded from accuracy, not scored as incorrect (Spec 15 decision 2).
  if (r.refused) {
    return <span className="rounded bg-default-200 px-2 py-0.5 text-xs font-medium text-default-700">refused</span>;
  }
  return <span className="rounded bg-danger-100 px-2 py-0.5 text-xs font-medium text-danger-700">wrong</span>;
}

function Metric({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="rounded border border-default-200 px-2 py-1">
      <div className="text-[10px] uppercase tracking-wide text-default-400">{label}</div>
      <div className="font-mono text-sm">{formatMetric(value)}</div>
    </div>
  );
}

export function QuestionCard({ r, lang }: { r: QuestionResult; lang?: string }) {
  return (
    <div className="rounded-lg border border-default-200 p-4" data-testid="question-card">
      <div className="flex flex-wrap items-center gap-2 text-xs text-default-500">
        <StatusBadge r={r} />
        {r.failure && (
          <span
            className={
              failureSeverity(r.failure) === "major"
                ? "rounded border border-danger-300 bg-danger-50 px-2 py-0.5 text-xs font-medium text-danger-800"
                : "rounded border border-warning-300 bg-warning-50 px-2 py-0.5 text-xs font-medium text-warning-800"
            }
          >
            {failureSeverity(r.failure)} · {FAILURE_KIND_LABEL[r.failure]}
          </span>
        )}
        <span className="font-mono">{r.question_id}</span>
        <span>·</span>
        <span>{r.task}</span>
        {r.tradition.length > 0 && (
          <>
            <span>·</span>
            <span>{r.tradition.join(", ")}</span>
          </>
        )}
      </div>

      <dl className="mt-3 grid gap-3 text-sm">
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-default-400">prompt</dt>
          <dd className="script-text mt-0.5 whitespace-pre-wrap" dir="auto" lang={lang}>
            {r.prompt}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-default-400">expected</dt>
          <dd className="script-text mt-0.5 whitespace-pre-wrap" dir="auto" lang={lang}>
            {r.expected}
          </dd>
        </div>
        {r.missing ? (
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-default-400">answer</dt>
            <dd className="mt-0.5 italic text-warning-600">
              no answer produced (missing cell — the model returned no row for this question)
            </dd>
          </div>
        ) : (
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-default-400">answer</dt>
            <dd className="script-text mt-0.5 whitespace-pre-wrap" dir="auto" lang={lang}>
              {r.answer}
            </dd>
          </div>
        )}
      </dl>

      {/* Per-metric scores show for every failing row (spec AC6). A missing cell has no
          scored answer, so all three read "n/a" (formatMetric(null)); the badge and the
          "no answer produced" marker above distinguish it from a low-scoring answer. */}
      <div className="mt-3 flex flex-wrap gap-2">
        <Metric label="exact" value={r.exact} />
        <Metric label="normalized" value={r.normalized} />
        <Metric label="token-F1" value={r.token_f1} />
      </div>
    </div>
  );
}
