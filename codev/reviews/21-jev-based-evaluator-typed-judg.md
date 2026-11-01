# Review: Jev-based evaluator — typed judge verdicts for containment, refusal, and passage equivalence

## Summary

Added the **Jev judge** (TypeSafe's System-One Decisions model, `jev-latest` → `typesafe/jev-1.14-20261014`)
as a paid, explicitly-invoked, resumable **separate-pass grader** over an already-collected answers
file: it asks a **containment** and a **refusal** diagnostic per text-retrieval cell, plus an optional
**passage-equivalence** question when an equivalence index is supplied. Verdicts land in a resumable
**sidecar** (never `scores.jsonl`); the deterministic headline is untouched and refusal stays an
outcome. Four phases, all passing 2-way (codex+claude) review — phases 2–4 reached a clean
APPROVE/APPROVE; phase 1 force-advanced at max_iterations with its findings verified fixed in-commit.
Validated live on the committed tutorial run (400 cells, $0.011705). Part 2 of 3 of PR #30; closes #21.

## Spec Compliance

- [x] Paid, explicitly-invoked, resumable judge over an answers file → resumable sidecar + header
      manifest; refuses to spend without `--yes`; pre-flight estimate; spend from `usage.cost` (Phase 1)
- [x] Sidecar row schema — `decision_id`, `judge_provider`, `rubric_id`, `question_set_digest`,
      `answer_digest`, `index_digest` (absent when no index), typed answers, `usage` (Phase 1)
- [x] Resolved build is grader identity — recorded per row + in the sidecar manifest + in
      `summary["judge"]`; build-mismatched resume fails fast (Phases 1, 2)
- [x] Resume is stale-safe — bound on `answer_digest` + `rubric_id` + `question_set_digest`; failed
      cells stay pending (Phase 1)
- [x] Task-type filter (only `retrieve_quote`/`complete_unit`) and a pre-send **restricted-target
      guard** independent of the commit-time audit (Phase 1; extended to index wordings in Phase 3)
- [x] Non-default seam — `jev` registered non-inline/verdict-less/`default=False`;
      `score --evaluator jev` fails fast; default `score` is byte-identical (Phase 2)
- [x] Resolved build surfaced in provenance — explicit `score --judgments <sidecar>` opt-in stamps
      `summary["judge"]`; `evaluators` stays `list[str]`; no cost field in the summary (Phase 2)
- [x] Passage equivalence OFF unless `--equivalence-index`; #32 schema consumed verbatim; fail-fast on
      missing manifest / `corpus_hash` mismatch; index `digest` per row + in the manifest + in the
      resume identity; no dependency on #32's branch (hand fixture) (Phase 3)
- [x] Validation on the committed tutorial run — live pass + agreement report + manual disagreement
      review; committed `scores.jsonl`/`answers.jsonl`/`summary.json` byte-identical; audit passes (Phase 4)
- [x] Public repo — no key material; no NABRE/TLG text in any committed artifact (all phases)
- [x] Carried code preserves a contributor's authorship on the Phase-1 `jev.py` commit (Phase 1)

## Validation on the committed tutorial run (Phase 4)

**Live pass.** 400 `retrieve_quote` cells on the **committed** `runs/tutorial-2026-10-11/answers.jsonl`,
`jev-latest` → `typesafe/jev-1.14-20261014`, 0 failures, **actual spend $0.011705** (pre-flight $0.0108;
project total ≈ $0.0118, cap $8). No equivalence index ⇒ every row records `equivalence:
"not_evaluated"`. Only new files were written (`judgments.jsonl` + `.manifest.json`,
`jev_agreement.{json,md}`); `git diff` on the committed `answers.jsonl`/`scores.jsonl`/`summary.json` is
empty, and the copyright audit passes.

**Agreement (threshold p ≥ 0.5), via the tested `jev_agreement` module:**

| Axis | Judge vs deterministic | Agreement | Split |
|---|---|---|---|
| Containment | `matches_requested_p` vs `contains_reference` | **93.25%** (373/400) | both 239, judge-only 27, deterministic-only **0**, neither 134 |
| Refusal | `refusal_p` vs `refused` outcome | **97.25%** (389/400) | both 116, judge-only **0**, deterministic-only 11, neither 273 |

Raw per-class probability means separate cleanly: containment `contains_reference=1` → **0.971**
(238/239 in [0.75,1.0]), `=0` → **0.180** (but 21 in [0.75,1.0] — the near-misses); refusal `refused` →
**0.900**, `not_refused` → **0.012**.

### Manual disagreement review (all 35 cells reviewed)

Disagreements: **24 containment-only + 8 refusal-only + 3 both** = 35 cells (27 containment + 11 refusal
axis-disagreements). Every one was inspected (`jev_agreement.md` carries each with its expected/answer
excerpt); they fall into three understood classes, **none a judge error**:

1. **Containment near-misses — orthographic / vocalization variance (27 cells, all judge-only; 0
   deterministic-only).** The designed diagnostic value. Two sub-kinds: Arabic **Uthmani digitization**
   differences (same verse, different mark/joiner code points — e.g. `إِنِّى` vs `إِنِّي`;
   `token_f1` 0.36–0.98, judge `matches_requested_p` 0.8–0.93) and English **archaic spelling** (KJV
   "recompence" vs expected "recompense", `token_f1` ≈ 0.98). Because deterministic-only = 0, the judge
   never contradicts a deterministic catch — it only **adds recall** on the near-misses.
2. **Refusal false-positives on hedged-but-delivering web-search answers (11 cells, all `*-search`
   arms).** The answer prefaces with a disclaimer ("I couldn't find the exact William Davidson Edition
   text…") then **delivers** the passage, often in a different vocalization. The deterministic cue-based
   refusal classifier flags the disclaimer as `refused`; the judge correctly scores low `refusal_p`
   (0.03–0.49) and, for the 3 both-axis cells, high `matches_requested_p` (0.63–0.93). A real finding →
   filed as **#48** (ties into the independent-rater work in #41).
3. **Refusal-boundary uncertainty (subset).** A few `opus-search` cells sit just under the 0.5 cut
   (`refusal_p` 0.45–0.49) — genuine declines where the judge is merely unconfident, visible in the raw
   distribution rather than the thresholded cut.

**Takeaway for the paper:** the judge is a high-value *recall* complement for containment in the RTL
orthographic-variance regime (27 near-miss catches, 0 deterministic regressions) and a sharp cross-check
that surfaced the refusal-classifier false-positives (#48).

## Deviations from Plan

- **None material.** Phase 4 added a `judge-agreement` **CLI subcommand** (not explicitly called for in
  the plan) so the committed agreement report is reproducible without a one-off script (per the repo's
  "no runner scripts" rule); the agreement logic lives in the tested `jev_agreement` module as planned.
- Phase 1 force-advanced at porch's `max_iterations=3` (codex still REQUEST_CHANGES); verified SAFE —
  codex's iter-3 findings are fixed in commit `d1d5031`, not buried (per the force-advance lesson).

## Consultation Feedback

Per-phase 2-way consultation (codex + claude; **gemini excluded by config** — it cannot see the
worktree, per the hot-tier lesson). 12 rounds total. No `CONSULT_ERROR`s.

### Phase 1 — Jev judge pass + CLI (3 rounds; force-advanced)
- **Spend never surfaced** (codex+claude) → **Addressed**: `summarize()` sums `usage.cost`; CLI prints it.
- **Manifest-less sidecar could go mixed-build** (codex+claude) → **Addressed**: `_require_manifest_if_rows`.
- **`interpret` fail-open on types** (codex+claude) → **Addressed**: every authoritative field validated.
- **Row schema vs the spec's flat shape** (claude) → **Addressed**: flat `kind`/`kind_probabilities`.
- **Mixed-build/mixed-qsd resume, negative `--limit`** (codex iter2/3) → **Addressed**: per-row build +
  qsd guards; `_check_limit`. **Live smoke not run** (claude) → **Addressed**: 1-cell smoke, $0.000027.
- Iter-3 codex REQUEST_CHANGES at max_iterations → **Addressed in `d1d5031`** (row qsd guard, negative
  limit, truncated-line wrap), verified before the force-advance; claude APPROVE.

### Phase 2 — Grader registration + provenance (3 rounds; clean APPROVE iter 3)
- **False provenance on an empty/skeletal sidecar** (codex iter1+iter2) → **Addressed**: `load_provenance`
  requires the sidecar to exist and carry ≥1 **complete** verdict row agreeing with the manifest
  (`require_verdict` + the build/qsd row guard).
- **"Merges into scores.jsonl" doc wording** (codex+claude) → **Addressed**: reworded to the
  sidecar-authoritative contract across docstring/comment/error/recipe.
- **Vacuous merge test; bare manifest `json.loads`; CODE_WALKTHROUGH pointer drift** (claude) →
  **Addressed**: test tied to `GRADERS["jev"].metric_keys`; JSON parse wrapped; pointers made exact.

### Phase 3 — Equivalence-index consumer (3 rounds; clean APPROVE iter 3)
- **Restricted text reachable via index wordings** (claude, blocking) → **Addressed**:
  `load_equivalence_index` guards every wording's `(work, version, language)` against `restricted_keys`,
  fail-fast (baked constraint, independent of the audit).
- **`index_digest` independently settable; per-row digest unvalidated** (codex) → **Addressed**: `judge`
  derives the digest from `index.digest`; `_load_existing` gains `pinned_index_digest`.
- **Exact-text wording exclusion is brittle for RTL** (claude) → **Addressed**: exclude by `version`.
- **`--questions` unbound to the run** (claude; codex iter2) → **Addressed**: bound on
  `question_set_digest` on **both** the answers and the manifest side.
- **`estimate(index_digest=)` untested** (claude) → **Addressed**: added. `_STATE_CHAR_LIMIT` + a huge
  index row (claude) → **N/A** (not reachable with #32's shape; recorded as a follow-up).

### Phase 4 — Validation on the tutorial run (2 rounds; clean APPROVE iter 2)
- **Phase files untracked / absent from PR scope** (codex iter1, sole blocker) → **Addressed**:
  committed the phase (`e98233e`) with the run artifacts + fixtures `git add`-ed explicitly.
- **`judge-agreement` undocumented; no CLI test; report not self-verifying; restricted reachability
  undocumented; docstring nit** (claude iter1) → **Addressed**: TUTORIAL + CODE_WALKTHROUGH recipe; CLI
  test; `answer_digest` cross-check in the join; reachability documented; docstring fixed.
- **Report lacks a `judge_model_resolved` header** (claude iter2) → **N/A** this spec (build is in the
  rows + sidecar manifest + score provenance); recorded as a follow-up.
- claude independently re-derived every agreement number from the committed data and confirmed
  byte-reproducibility + evidence integrity — both iter-2 verdicts APPROVE.

### Review Phase (PR #47, Round 1) — codex REQUEST_CHANGES / claude APPROVE; architect integration review
All folded in-PR; the committed sidecar/agreement files stayed byte-unchanged (no re-judge, no new spend):
- **Equivalence-index digest trusted, not verified** (codex) → **Addressed**: `load_equivalence_index`
  recomputes `sha256(file_bytes)[:16]` and fails on mismatch (test: same-row-count tampering).
- **`score --judgments` didn't bind judgments to the scored answers** (architect) → **Addressed**:
  `load_provenance` now requires every judged `(question_id, model_id, answer_digest)` to be among the
  answers being scored (test: a sidecar from different answers is refused).
- **`_single_question_set_digest` accepted a digest-less answers file** (architect) → **Addressed**:
  the judge now requires ≥1 non-empty digest (matching `collect`/`score`).
- **`interpret()` under-validated the typed choice** (codex) → **Addressed**: all `kind` labels present,
  every probability + the confidence in [0,1], usage cost/tokens non-negative (tests for each).
- **`jev_agreement` join not strict** (codex) → **Addressed**: every judgment needs a matching answer +
  `answer_digest`; duplicate `(qid, model_id)` fails.
- Minors → **Addressed**: import `JUDGED_TASKS` from `jev`; parenthesize the retry predicate; nudge
  `TYPICAL_COST_USD` to 3e-5 (conservative); `graders.py` note that `kind` is index-conditional for the
  merge pass; this review's stale test count fixed; the dropped manual disagreement review restored (below).
- Follow-ups filed: **#48** (refusal-classifier false positives, F1) and **#49** (merge pass / spend
  circuit-breaker / self-describing report, F2).

## Lessons Learned

### What Went Well
- **Carrying live-verified code paid off.** PR #30's `jev.py` was validated against the real Decisions
  wire during the specify phase; the only required change was the model id, and the fixture pinned the
  shape — the live smokes then confirmed the real path end-to-end.
- **The judge behaves as designed: a recall complement, not a headline.** On the tutorial run,
  containment agreement 93.25% with **0 deterministic-only** disagreements — the judge never contradicts
  a deterministic catch, it only adds the 27 orthographic near-misses the deterministic tier can't fold.
- **The refusal cross-check immediately earned its place**, surfacing that the cue-based refusal
  classifier false-positives on hedged-but-delivering web-search answers (11 cells, all search arms).

### Challenges Encountered
- **Provenance integrity took three tries to get airtight** (empty sidecar → skeletal row → the
  manifest/row both-sides binding). Each reviewer round found a narrower hole; the fix converged on
  "validate the rows, not just the manifest."
- **The equivalence path has many fail-fast seams** (corpus_hash, index digest, restricted wordings,
  question-set binding); keeping them decoupled (provenance must not bind index state) needed care.

### What Would Be Done Differently
- **Commit each phase at its boundary, not only at the end.** Phase 4's first review was a
  REQUEST_CHANGES purely because the files were untracked and thus invisible to the diff-based reviewer.
  Committing before the consult would have saved a round.
- **Write test fixtures that satisfy the real invariants from the start** — the phase-2 fixtures wrote
  empty/skeletal sidecars that masked the very provenance hole the reviewers then found.

### Methodology Improvements
- porch's per-phase refresh task repeatedly advanced to the next phase's implement task before the bound
  `afx self-refresh` could run, so the boundary refresh never fired across three boundaries. Worth
  checking whether the refresh task should gate `porch next` until consumed.

## Architecture Updates

Per the plan, this spec **flags** governance candidates rather than editing the capped hot-tier files
directly (the MAINTAIN arch-doc step owns `arch-critical.md`/`arch.md` and the displacement discipline).

- **Flagged for HOT (`arch-critical.md`), pending the arch-doc step:** "Jev (`jev.py`) is a paid,
  separate-pass, **sidecar-only** diagnostic grader — non-inline/verdict-less/`default=False` in
  `graders.py`; verdicts never enter `scores.jsonl`; `score --judgments` only stamps provenance;
  equivalence is off unless `--equivalence-index` (#32 schema verbatim, restricted-wording-guarded)."
- **Flagged for COLD (`arch.md`):** the sidecar schema + manifest identity (resolved build / rubric /
  qsd / index digest), the resume guards, and the `judge` / `judge-summary` / `judge-agreement` CLI.
- No direct edit made here (plan's division of responsibility).

## Lessons Learned Updates

Same flag-don't-edit disposition as above.

- **Flagged for HOT (`lessons-critical.md`):** "A System-One judge belongs in the diagnostic tier:
  validated on the tutorial run it added containment recall on RTL orthographic near-misses with **zero
  deterministic regressions**, and its refusal cross-check exposed refusal-classifier false-positives on
  web-search hedges — value it would not have as the headline."
- **Flagged for COLD (`lessons-learned.md`):** "Report the raw per-class probability distribution, not
  just the thresholded agreement — the 0.97/0.18 and 0.90/0.012 class means are what show the judge
  *separates* the classes, and they surface the boundary-uncertainty cases a 0.5 cut hides."
- No direct edit made here.

## Flaky Tests

No flaky tests encountered. The full suite is deterministic: **565 passed, 1 pre-existing skip**
(`test_original_run_regression` network skip) via `.codev/checks/test.sh`. Unit tests inject a fake
decider — no network, no key, no spend; the only live calls were the two budgeted smokes (Phase-1
single cell $0.000027; Phase-4 tutorial pass $0.011705).

## Follow-up Items

Filed as issues during the PR #47 review (architect-directed), referenced here:

- **#48 (F1) — refusal-classifier false positives** on hedged-but-delivering web-search answers: the 11
  enumerated phase-4 cells where the deterministic cue matcher over-calls `refused`, biasing accuracy
  denominators + coverage; fix path is adjudication against `outcomes.py` with those 11 as a
  pre-registered set (ties into the independent-rater issue #41).
- **#49 (F2) — Jev evaluator follow-ups**: the deferred per-row **merge-into-`scores.jsonl`** pass for
  new runs (treating `kind` as index-conditional); a **running-spend circuit breaker** (today's budget
  guard is pre-flight only); and a **self-describing agreement report** (`judge_model_resolved` /
  `rubric_id` header + `n_indexed_other_wordings` per row, so `neither` separates from "no index row").
- **`_STATE_CHAR_LIMIT` + a very large index row** makes that cell fail every retry; consider capping
  alternates (recoverable) vs. the current fail-fast. Not reachable with #32's current shape; rolls into
  #49 if pursued.

(The pre-PR trailer strip and the rebase onto main — earlier thread TODOs — are **done** on this branch:
the 10 pre-Phase-1 commits carry no trailers, and the branch is rebased onto current `main`.)
