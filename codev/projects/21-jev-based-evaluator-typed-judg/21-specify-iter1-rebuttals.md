# Spec 21 — Specify iteration 1 rebuttal

Two reviews: **codex REQUEST_CHANGES** (5 issues), **claude COMMENT** (8 issues). They converge.
Both verified the spec against the actual tree; every factual claim they checked held. I accepted
substantially all feedback — no redesign was required. Below, each point, what changed, and where.

## codex (REQUEST_CHANGES)

**C1 — Edition-index question must be resolved; option (a) can't satisfy passage-equivalence.**
Accepted. The spec no longer leaves this open-ended. A new **Scope decision** paragraph (Desired
State / top of spec) provisionally takes option (a): ship **containment + refusal-diagnostic now**,
with equivalence's alternates empty so `other_indexed_wording` cannot fire, and says so plainly. The
title's "passage equivalence" is now explicitly caveated as deferred coverage. The decision is
flagged as the architect's to confirm before plan (it is a baked-scope call, and ASPIR has no human
gate, so I resolved it internally for consistency while surfacing it for redirection).

**C2 — Output contract is internally inconsistent (merge vs sidecar).** Accepted — this was the
sharpest issue. Desired State now states registration is **selection/discovery-only** for Part 2 and
the verdicts are written to a **sidecar** whose **authoritative schema is named field-by-field**
(`refusal_p`, `matches_requested_p`, `kind`/`kind_probabilities`/`kind_confidence`, plus provenance).
The `scores.jsonl` merge is explicitly **not built here** and deferred for new runs. I also noted the
`submetrics_for`/`_CANONICAL_ORDER` detail (claude I1): a non-inline grader's `metric_keys` wouldn't
reach `scores.jsonl` from `score` anyway, so the sidecar is unambiguously the home of its fields.

**C3 — Resume identity insufficient.** Accepted. Success criteria + schema now bind the resume key to
**`answer_digest`** (exact answer content), **`rubric_id`** (prompt/schema version), and the
**question-set digest** — a changed answer/prompt/question-set re-judges or fails loud. The floating
`jev-latest` build-roll case (also claude I4) is covered by a separate criterion: a multi-build file
is flagged by `summarize`.

**C4 — Judgment scope ambiguous.** Accepted. New criterion + Desired State line: only
`retrieve_quote`/`complete_unit` are judged; `verify_source`/`cite_passage` are **skipped and reported
as skipped**, because containment/passage-wording questions are meaningless for a Yes/No source check
or a citation.

**C5 — Agreement criteria not testable.** Accepted. The agreement report is now defined to use a
**fixed `p ≥ 0.5`** threshold **and** tabulate the **raw per-outcome-class distribution**, so the
disagreement set is stable and not a threshold artefact. The refusal-threshold open question was
promoted out of "Nice-to-know" and marked resolved.

## claude (COMMENT)

**I1 — Meaning of `graders.py` registration.** Accepted — same fix as C2. Resolved as
selection/discovery-only + named sidecar fields; merge deferred.

**I2 — Title/Desired State overstate equivalence under option (a).** Accepted — same as C1. Added the
scope caveat and an explicit fallback: with empty alternates `kind ∈ {refusal, requested_wording,
neither}`, equivalence coverage deferred.

**I3 — "Surfaced the way collect's is" is factually wrong.** Accepted and corrected. Desired State now
says Jev spend is surfaced from the **Decisions API's returned `usage.cost`** (summed + per-cell), and
explicitly contrasts with `score`'s price-config/UNPRICED model. Good catch — `collect` records
per-row usage but surfaces no cost.

**I4 — `jev-latest` floating alias as resume key.** Accepted — covered under C3; multi-build files are
flagged, pinning a build is allowed. Risk table updated.

**I5 — Restricted-text *transmission* uncovered.** Accepted — strong catch. New constraint + success
criterion + risk row: the pass refuses/skips any cell whose source `(work, version, language)` maps to
a `restricted` target **before** sending its reference text to the API, independent of the commit-time
audit gate. Noted as latent today (neither committed run has a restricted source) but required before
pointing the pass at an arbitrary run.

**I6 — $8 cap has no mechanism.** Accepted. New criterion + constraint: a **pre-flight cost estimate**
(pending cells × typical per-cell cost) prints before any call, and a **`--limit`** bounds cells per
invocation, making the cap enforceable rather than aspirational.

**I7 — Refusal-probability threshold mis-prioritized.** Accepted — promoted to Important and resolved
(see C5).

**I8 — Commit the live response as the test fixture.** Accepted. New criterion: a **redacted
live-verified Decisions response is committed as the fixture** `interpret()`'s fail-fast tests run
against, per the project's "mocking the provider seam hides live-only failures" lesson.

**Also noted (claude, not an issue):** the `cross_translation` import in the contributor's `jev.py` is top-level
and non-optional, so option (a) requires an actual code edit (make the import optional), not just
`index=None`. Captured in Approach 1's "Required edits" list.

## Disagreements

None substantive. The only judgment call is **C1/I2**: both reviewers wanted the edition-index
scope *decided*. I decided it (option (a)) for internal consistency and testability, but — because it
is a scope decision the architect flagged as baked — I left it explicitly subject to the architect's
confirmation before the plan phase rather than treating my choice as final. If the architect prefers
(b) (vendor a minimal index now) the equivalence criteria tighten accordingly; the rest of the spec is
unaffected.

## Net

All 13 points actioned in the spec (commit `[Spec 21] Specification with multi-agent review`). The
spec is now internally consistent (one output surface, named schema), testable (fixed thresholds,
defined skip behaviour), reproducible (strengthened resume identity), and safe (restricted-text
transmission guard, enforceable budget).
