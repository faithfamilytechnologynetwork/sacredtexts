# Spec 21 — Plan iteration 1 rebuttal

Two reviews, both **REQUEST_CHANGES**, both verified against the code in the worktree and highly
complementary. I accepted every substantive point; the plan was revised in commit `[Spec 21] Plan
with multi-agent review`. (Both reviews carried a "repository moved during review" banner — I checked
`git log`/`reflog`: HEAD moved only because of porch's `build-complete` commit and my thread commit;
the **plan file was untouched** after its `Initial implementation plan` commit, so both reviewed the
correct content.)

## codex (REQUEST_CHANGES)

**X1 — Phase 2 provenance interface undefined; implicit discovery risks default scoring.** Accepted.
Phase 2 now adds an **explicit `score --judgments <path>`** opt-in with manifest validation +
question-set binding; the judge build goes in a **new sibling summary key**, `evaluators` stays a
`list[str]`, and no `cost` field enters the summary. No implicit co-location discovery.

**X2 — Grader metric keys inconsistent / omit equivalence.** Accepted. Descriptor is now
`("matches_requested_p", "refusal_p", "kind")` — matching the sidecar contract — and the `graders.py`
docstring note is updated on registration.

**X3 — Index identity not in resume validation.** Accepted. `index_digest` is added to the sidecar
manifest identity; a resume whose recorded `index_digest` differs fails fast even when `corpus_hash`
is unchanged. New mixed-index test in Phase 3.

**X4 — Phase 1 exposes `--equivalence-index` but leaves it unwired.** Accepted. The flag is **removed
from Phase 1** and added only in Phase 3; Phase 1 does not accept it.

**X5 — `generated_at` defeats byte-identical summary.** Accepted. Phase 2 requires byte-identity for
`scores.jsonl` and compares the summary **excluding `generated_at`**. (Phase 4 avoids the issue
entirely: it never re-runs `score`, so committed summaries are not rewritten — `git diff` must be
empty.)

**X6 — Agreement report has no test plan.** Accepted. The report is now a **tested module**
(`jev_agreement.py` + `test_jev_agreement.py`) with fixture-based tests for the answers×scores×
judgments join, the `p ≥ 0.5` boundary, raw per-outcome distributions, and exhaustive disagreement
enumeration.

**X7 — Resolved-build concurrency + missing-credentials tests.** Accepted. Phase 1 test plan now
includes a concurrency/manifest-identity test (first response establishes identity; later/in-flight
responses must match before being written) and a missing-`OPENROUTER_API_KEY` fail-fast test.

## claude (REQUEST_CHANGES)

**I1 — `test_graders.py` deletes the real registration.** Accepted — sharp catch. The file
(`:80-96`, `del GRADERS["jev"]` in `finally`) is now in Phase 2's modify list, with the fixture fixed
and an assertion that the suite passes in file-order.

**I2 — `summary["evaluators"]` shape / `cost` guard.** Accepted — same resolution as X1: `evaluators`
stays `list[str]` (consumed by `LeaderboardTable.tsx:48`, pinned by `test_score.py:256`); build goes
in a new sibling key; no `cost` field (`test_tutorial_run.py:66` guards it).

**I3 — Implicit sidecar discovery erodes reproducibility silently.** Accepted — same as X1; explicit
`--judgments`. The specific failure (a re-score of the tutorial run ceasing to reproduce committed
`summary.json` after Phase 4, with no test catching it) is exactly why the opt-in is explicit.

**I4 — Phase 3 `corpus_hash` has no defined input.** Accepted. Answer rows carry
`question_set_digest` but not `corpus_hash`; the latter lives only in
`runs/<id>/questions.jsonl.manifest.json`. Phase 3 adds an explicit `--questions`/run-manifest option
to locate it — no co-location guessing.

**I5 — No step to retrieve PR #30's code.** Accepted. Phase 1 now names the retrieval path
(`gh pr diff 30` / `gh api …/contents/…?ref=the fork branch`) and the `--author` mechanics,
and records that only `cross_translation` (`EditionIndex`, `cite_key`) and `score.normalize` are
imported — so **`cite_key` is re-implemented locally** since the `cross_translation` import is dropped,
and nothing from PR #30's `providers.py`/`config.py`/`collect.py` is carried.

**I6 — `summarize()` unplanned.** Accepted. Phase 1 keeps the contributor's `summarize(path)`, exposes it as a
`judge-summary` surface, and tests the spec's "no-op on a fully-judged file" scenario.

**I7 — Missing test items.** Accepted — credential fail-fast (also X7) and an explicit negative that
`score`/`collect` never import/invoke the judge are both in Phase 1's test plan.

**I8 — Defer all live contact to Phase 4 vs the hot-tier lesson.** Accepted. Phase 1 ends with a
**single-cell live smoke (≈ $0.00003)** to catch model-id/auth/shape drift before later phases build
on the HTTP/parse code; Phase 4's full pass + architect pre-flight ping is unchanged. (I had already
done the equivalent live verification during Specify; this bakes it into the phase as a standing
guard.)

**I9 — Metric-key skew (minor) + docstring.** Accepted — same as X2; names aligned to the sidecar,
docstring updated.

**Useful facts folded (not issues):** audit safety confirmed (judgment rows have no `source`/text, so
`audit.py` skips them; the committed run dirs are un-ignored, so sidecars are committable); the viewer
only fetches the four canonical files; the ~$0.011 / 400-cell tutorial pre-flight figure is now stated
in Phase 4.

## Disagreements

None. Every point was a real gap or a real code-level tripwire; all are actioned.

## Net

All 16 points folded. The plan now has: an explicit, test-guarded provenance interface; a consistent
sidecar/grader naming contract; resume identity that binds build + index digest; a defined
`corpus_hash` source; a named code-retrieval + authorship path; a tested agreement module; and the
missing credential/concurrency/no-judge-in-score/`summarize` tests — plus an early live smoke that
honours the project's "mocking the provider seam hides live-only failures" lesson.
