import { ReviewUnavailable } from "./ReviewAuthGate";
import type { SampleLoad } from "../lib/review";

/** A failed sample load: "review service unavailable" when there's no API, else the error and a retry. */
export function ReviewSampleError({ load }: { load: Extract<SampleLoad, { state: "error" }> & { retry: () => void } }) {
  if (load.unavailable) return <ReviewUnavailable />;
  return (
    <div role="alert" className="mx-auto max-w-xl py-12 text-center" data-testid="sample-error">
      <h1 className="text-xl font-semibold">Couldn&rsquo;t load the review sample</h1>
      <p className="mt-2 text-sm text-danger">{load.message}</p>
      <button type="button" onClick={load.retry} className="mt-4 text-sm text-accent hover:underline">
        Try again
      </button>
    </div>
  );
}
