import type { PassProgress, ProgressCount } from "../lib/reviewSample";

// Progress through a reviewer's pass, ported from multibench's ReviewProgressBar: labelled / in pass,
// per chosen text and overall. A cell counts as labelled once it has an outcome.

export function ReviewProgressBar({ progress, label }: { progress: ProgressCount; label: string }) {
  const pct = progress.inPass > 0 ? Math.round((100 * progress.labelled) / progress.inPass) : 0;
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-1.5 w-28 shrink-0 overflow-hidden rounded-full bg-default-soft"
        role="progressbar"
        aria-valuenow={progress.labelled}
        aria-valuemin={0}
        aria-valuemax={progress.inPass}
        aria-label={label}
      >
        <div className="h-full rounded-full bg-accent transition-[width]" style={{ width: `${pct}%` }} />
      </div>
      <span className="whitespace-nowrap text-xs tabular-nums text-default-500">
        {progress.labelled} / {progress.inPass} labelled
      </span>
    </div>
  );
}

export function ReviewProgress({ progress }: { progress: PassProgress }) {
  return (
    <section className="flex flex-col gap-2" aria-label="Progress" data-testid="review-progress">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold">Progress</h2>
        <ReviewProgressBar progress={progress.overall} label="Overall progress" />
      </div>
      <ul className="flex flex-col gap-1">
        {progress.texts.map((t) => (
          <li key={t.text} className="flex flex-wrap items-center justify-between gap-2 text-sm" data-testid="text-progress">
            <span className="text-default-700">{t.label}</span>
            <ReviewProgressBar progress={t} label={`${t.label} progress`} />
          </li>
        ))}
      </ul>
    </section>
  );
}
