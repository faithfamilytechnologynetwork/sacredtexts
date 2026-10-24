# Spec 21 — Phase 1 (Jev judge pass + CLI) iteration 1 rebuttal

Two reviews, both **REQUEST_CHANGES**, both verified against the code and strongly convergent. All
substantive points accepted and fixed; the Phase 1 commit (authored by Jonathan Karr) was amended.
Full suite now **403 passed, 1 pre-existing skip**, and the required live smoke was run.

## Accepted and fixed

**1 — Total spend never surfaced (codex + claude).** `summarize()` now sums the API-returned
`usage.cost` into `total_cost_usd`, and the `judge` CLI prints `total Jev spend this file: $…`. New
test `test_summarize_is_a_noop_over_a_finished_file_and_sums_cost` asserts the sum.

**2 — Non-empty sidecar without a manifest → silent mixed-build (codex + claude).** New
`_require_manifest_if_rows(out)`, called at the top of both `estimate` and `judge`, raises if `out`
has rows but no `.manifest.json`. New test `test_nonempty_sidecar_without_manifest_fails_fast`.

**3 — Row schema deviated from the spec's pinned flat shape (claude).** `interpret` now emits flat
`kind` / `kind_probabilities` / `kind_confidence` when equivalence is evaluated, and the
`equivalence: "not_evaluated"` sentinel otherwise — matching the spec and the plan's Phase-2 grader
metric keys and Phase-4 agreement reader. `summarize` updated to read the flat field. The fixture
test asserts `parsed["kind"]` and `"equivalence" not in parsed`.

**4 — `interpret` fail-open on types (codex + claude).** It now fails loud on every authoritative
field: `_num()` rejects non-numbers (and bools); `_prob()` requires a probability in [0,1] for both
`noul` values; `decision_id`/`provider`/resolved build must be non-empty strings; `usage` must be a
dict with numeric `cost` and token counts; for equivalence, `probabilities` must be a dict and
`confidence` numeric. A silently tolerated `cost: None` (which would read as zero spend and defeat the
budget control) now raises. New test `test_interpret_fails_loud_on_mistyped_or_missing_fields`.

**5 — Phase-1 single-cell live smoke not actually run (claude).** Done: one real cell through the full
`judge`→`post_decision`→`interpret` path against the tutorial answers (`--limit 1 --yes`, written to a
scratch sidecar, committed evidence untouched). The tutorial's first cell (a refusal) was judged
refusal_p=0.97 / matches_requested_p=0.03 / equivalence not_evaluated; resolved build
`typesafe/jev-1.14-20261014`, manifest written, spend $0.000027. This validated that the request body
this code builds (`{model, state, questions}` from `build_questions`) hits the wire — the specify-phase
calls were scratch, not through this code. Total project live spend ≈ $0.00008, far under the $8 cap.

**6 — Test gaps (codex + claude).** Added: cost-sum assertion (#1); missing-manifest resume (#2);
mistyped-probability / missing-field tests (#4); a `--limit` test (`test_limit_caps_cells_judged`); a
genuinely concurrent build-conflict test (`test_concurrent_build_conflict_fails_fast`,
`concurrency=4`, alternating builds — whichever pins first, the differing in-flight build conflicts).

## Minors (claude) — all addressed

- Dropped the unused `from sacredbench.score import normalize` (was dead weight in Phase 1; re-added
  only where used, in Phase 3).
- `JevError` added to `cli.main()`'s handled tuple and imported at top level; the `judge` command no
  longer wraps runtime `JevError` in `BadParameter` (which added a spurious `Usage:` banner) — it
  bubbles to `main()` for a clean `error: …` + exit 2.
- The negative test `test_score_and_collect_do_not_invoke_the_judge` now asserts the judge *invocation*
  surfaces (`jev.judge`, `post_decision`, `alpha/decisions`, `build_questions`) are absent, instead of
  a bare `"jev"` substring — so Phase 2's `score --judgments` provenance read won't false-trip it.
- Manifest `question_set_digest` binding tightened to **exact equality** (codex #4): a manifest whose
  digest differs from the current answers' digest — including None-vs-present — fails fast. Because the
  digest is computed up front and written with the manifest on the first cell, it is never left
  unrecorded for a file that has one.

## Disagreements

None. Every point was a real fail-open or a real coverage gap.

## Note

The hardening above is substantial, but the module's origin is Karr's PR #30, so the amended Phase 1
commit keeps his authorship per the architect's instruction. (Also: I had been adding `Co-Authored-By`
trailers earlier in the project against the global CLAUDE.md and the architect's "no Co-Authored-By"
instruction; stopped as of Phase 1, and the earlier commits will be cleaned, message-only, before the
PR.)
