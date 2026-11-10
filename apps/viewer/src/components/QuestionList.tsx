import { type QuestionResult } from "../lib/localResults";
import { QuestionCard } from "./QuestionCard";

// The per-question list for one model under the error explorer. Presentational: it takes
// the (already filtered) QuestionResult[] and renders each question with its pass/fail
// state, one QuestionCard per row (the card holds the side-by-side rendering).

export function QuestionList({ results }: { results: QuestionResult[] }) {
  if (results.length === 0) {
    return (
      <p className="mt-6 text-sm text-default-500">No questions match the current filters.</p>
    );
  }

  return (
    <ul className="mt-4 flex flex-col gap-4">
      {results.map((r) => (
        <li key={r.question_id}>
          <QuestionCard r={r} />
        </li>
      ))}
    </ul>
  );
}
