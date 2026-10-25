# Review: Jev-based evaluator — typed judge verdicts for containment, refusal, and passage equivalence

**Spec**: [codev/specs/21-jev-based-evaluator-typed-judg.md](../specs/21-jev-based-evaluator-typed-judg.md) ·
**Plan**: [codev/plans/21-jev-based-evaluator-typed-judg.md](../plans/21-jev-based-evaluator-typed-judg.md) ·
Protocol: ASPIR · Part 2 of 3 of Jonathan Karr's PR #30.

## Summary

Added the **Jev judge** (TypeSafe's System-One Decisions model, `jev-latest` → `typesafe/jev-1.14-20261014`)
as a paid, explicitly-invoked, resumable **separate-pass grader** over an already-collected answers
file. It asks two bounded questions per text-retrieval cell — **containment** (`matches_requested`) and
a **refusal** diagnostic — plus an optional **passage-equivalence** question when an equivalence index
is supplied. Verdicts land in a **sidecar** (`judgments.jsonl` + a header manifest) beside a run, never
in `scores.jsonl`; the deterministic headline in `score.py` is untouched and refusal stays an OUTCOME
in `outcomes.py`. The judge is registered in the Spec-15 grader seam (non-inline, verdict-less,
`default=False`), so the CLI / registry / recipe / summary provenance are mutually consistent.

Four phases, one PR ("Part 2 of 3 of #30", closes #21):
1. **Judge pass + CLI** — the core judge, resumable, resolved-build-as-identity, task filter,
   restricted-target guard, pre-flight estimate + `--limit`, spend from `usage.cost`.
2. **Grader registration + provenance** — `jev` in `graders.py`; `score --judgments <sidecar>` stamps
   the resolved build into `summary["judge"]`.
3. **Equivalence-index consumer** — `--equivalence-index` consuming #32's schema verbatim (off by
   default; corpus_hash/manifest/index-digest fail-fasts; restricted-wording guard).
4. **Validation on the committed tutorial run** (this phase) — the live pass + agreement report +
   manual disagreement review below.

## Spec Compliance

- **Diagnostic tier, never the headline.** `jev` is non-inline/verdict-less/`default=False`;
  `score --evaluator jev` fails fast; the default `score` is byte-identical (regression tests). ✓
- **Reproducibility.** Resolved build recorded per row + in the manifest + in `summary["judge"]`;
  build-mismatched / mixed-qsd / mixed-index / skeletal-row resume all fail fast. ✓
- **Explicit invocation + budget.** Paid pass refuses to spend without `--yes`; pre-flight estimate
  printed; spend summed from `usage.cost`. ✓
- **Equivalence off by default; #32 schema verbatim; no #32-branch dependency.** ✓ (hand-written fixture)
- **Restricted-target guard independent of the commit-time audit**, for both the judged cell and the
  index wordings sent to the API. ✓
- **Validation before trust** — this phase. ✓ (below)
- Public repo: no key material, no NABRE/TLG text committed. ✓

## Validation on the committed tutorial run (Phase 4)

**Live pass.** 400 `retrieve_quote` cells on the **committed** `runs/tutorial-2026-10-11/answers.jsonl`,
`jev-latest` → `typesafe/jev-1.14-20261014`, 0 failures. **Actual spend: $0.011705** (pre-flight
estimate $0.0108; project total ≈ $0.0118, cap $8). Pre-approved by the architect; pre-flight shown
before running. No equivalence index ⇒ every row records `equivalence: "not_evaluated"`.

**Evidence integrity.** Only new files were written: `judgments.jsonl` (+ `.manifest.json`),
`jev_agreement.{json,md}`. `git diff` on the committed `answers.jsonl` / `scores.jsonl` /
`summary.json` / `summary.md` is **empty** — the validation never re-ran `score`/`collect`. The
copyright audit passes on the whole run (origin-only; restricted payloads absent locally).

**Agreement (threshold p ≥ 0.5), via the tested `jev_agreement` module:**

| Axis | Judge vs deterministic | Agreement | Split |
|---|---|---|---|
| Containment | `matches_requested_p` vs `contains_reference` | **93.25%** (373/400) | both 239, judge-only 27, deterministic-only **0**, neither 134 |
| Refusal | `refusal_p` vs `refused` outcome | **97.25%** (389/400) | both 116, judge-only **0**, deterministic-only 11, neither 273 |

The judge's raw probabilities separate the deterministic classes cleanly:
- containment: `contains_reference=1` → mean `matches_requested_p` **0.971** (238/239 in [0.75,1.0]);
  `contains_reference=0` → mean **0.180**, but **21 cells in [0.75,1.0]** — the near-misses.
- refusal: `refused` → mean `refusal_p` **0.900** (114/127 in [0.75,1.0]); `not_refused` → mean **0.012**
  (all 273 in [0.0,0.25)).

### Manual disagreement review (all 35 cells accounted for)

Disagreements by axis: **24 containment-only, 8 refusal-only, 3 both** = 35 cells (27 containment +
11 refusal axis-disagreements). Every one was inspected (`jev_agreement.md` carries each with its
expected/answer excerpt); they fall into three understood categories, and **none is a judge error that
would argue against the diagnostic**:

1. **Containment near-misses — orthographic / vocalization variance (27 cells, all judge-only).**
   This is exactly the diagnostic value the spec names. Two sub-kinds:
   - **Arabic Uthmani digitization differences** (most): the answer is the same Qur'anic verse in a
     different mark/joiner digitization (e.g. `إِنِّى` vs `إِنِّي`, different hamza/sukūn code points),
     which `normalize()` cannot fully fold, so `contains_reference=0` and `token_f1` sits 0.36–0.98 —
     yet the judge correctly reads containment (`matches_requested_p` 0.8–0.93).
   - **English archaic spelling** (e.g. KJV "recompence" vs the expected "recompense"), `token_f1`
     0.86–0.98, judge `matches_requested_p` ≈ 0.69–0.73.
   Crucially, **deterministic-only = 0**: the judge never *failed* to see a containment the
   deterministic tier found, so it behaves as a superset in practice — it only *adds* recall on the
   near-misses, which is the intended role.

2. **Refusal false-positives on hedged-but-delivering web-search answers (the 11 refusal cells, all
   `*-search` arms).** The answer is prefaced with a disclaimer ("I couldn't find the exact William
   Davidson Edition text…", "I couldn't open the QUL page…") but then **delivers the passage**, often
   in a different vocalization. The deterministic cue-based refusal classifier flags the disclaimer as
   `refused`; the judge (correctly) scores low `refusal_p` (0.03–0.49) because content was delivered —
   and for the 3 "both" cells also high `matches_requested_p` (0.63–0.93), i.e. it sees the passage is
   present. This is a **genuine, useful finding**: the refusal heuristic over-triggers on search-arm
   hedges. It is a diagnostic observation, not a defect in this spec (refusal stays a deterministic
   outcome; the judge's refusal probability is explicitly a cross-check only).

3. **Refusal-boundary uncertainty (subset of the above).** A few `opus-search` cells sit just under
   the 0.5 cut (`refusal_p` 0.45–0.49) with low `matches_requested_p` — genuine declines where the
   judge is merely unconfident rather than wrong. The raw-distribution report (not just the 0.5 cut)
   makes this visible.

**Takeaway for the paper:** the judge is a high-value *recall* complement for containment in the
RTL orthographic-variance regime (adds 27 near-miss catches with zero deterministic regressions), and
a sharp cross-check that surfaces refusal-classifier false-positives on web-search answers.

## Deviations from Plan

- None material. Phase 4 adds a `judge-agreement` **CLI subcommand** (not called for explicitly in the
  plan) so the committed report is reproducible without a one-off script (per the repo's "no runner
  scripts" rule). The agreement logic lives in the tested `jev_agreement` module as planned.

## Consultation Feedback (9 impl iterations, codex + claude; gemini excluded — can't see the worktree)

- **Phase 1** (3 iters, force-advanced at max_iterations): spend reporting, manifest-less-sidecar
  fail-fast, flat `kind` schema, strict `interpret`, row-level qsd + negative-`--limit` guards. The
  force-advance was verified safe (findings fixed in `d1d5031`, not buried).
- **Phase 2** (3 iters, clean APPROVE/APPROVE at iter 3): false-provenance on empty/skeletal sidecar
  (now requires ≥1 complete verdict row agreeing with the manifest); "merges into scores.jsonl" doc
  wording corrected to the sidecar-authoritative contract.
- **Phase 3** (3 iters, clean APPROVE/APPROVE at iter 3): restricted-text-via-index-wordings guard
  (baked constraint); `index_digest` derived from the index; per-row index-digest resume validation;
  version-based (not exact-text) wording exclusion; `--questions` bound to the run by
  `question_set_digest` on both sides.

Rebuttals: `codev/projects/21-*/21-phase_{1,2,3}-iter{1,2,3}-rebuttals.md`.

## Lessons Learned

- **A System-One judge earns its place as a recall complement, not a headline.** The cleanest result
  here is *deterministic-only = 0* on containment: the judge never contradicts a deterministic catch,
  it only adds the orthographic near-misses — which is precisely why it is safe as a diagnostic tier
  and would be unsafe as the headline.
- **The refusal cross-check paid off immediately**: it surfaced that the cue-based deterministic
  refusal classifier false-positives on hedged-but-delivering web-search answers — a finding neither
  tier alone makes visible.
- **Report the raw distribution, not just the threshold.** The per-class probability split (means
  0.97/0.18 and 0.90/0.012) is what demonstrates the judge *separates* the classes; a bare 0.5-cut
  agreement number would hide both the separation and the boundary-uncertainty cases.

## Architecture / Lessons-doc update candidates (for the MAINTAIN arch-doc step)

- **HOT (arch-critical) candidate:** "Jev is a paid, separate-pass, sidecar-only diagnostic grader
  (`jev.py`): non-inline/verdict-less/`default=False` in `graders.py`; verdicts never enter
  `scores.jsonl`; `score --judgments` only stamps provenance. Equivalence is off unless
  `--equivalence-index` (#32 schema verbatim)."
- **HOT (lessons-critical) candidate:** "A System-One judge belongs in the diagnostic tier: validated
  on the tutorial run it added containment recall on RTL orthographic near-misses with zero
  deterministic regressions, and its refusal cross-check exposed refusal-classifier false-positives on
  web-search hedges."

(Per the plan, this review does not edit the hot/cold docs directly — it flags candidates.)

## Follow-up Items (out of this spec's scope)

- **`n_indexed_other_wordings` per judged row** (iter-3 claude): when an index is used, `neither`
  can't be distinguished from "no index row for this citation". Record the alternates count so a future
  equivalence-agreement report can separate them. (Not exercised here — Phase 4 used no index.)
- **Row-level `answer_digest` cross-check in `score --judgments`**: provenance currently binds on the
  question-set digest; a sidecar from a different collect run over the same question set would validate.
- **`_STATE_CHAR_LIMIT` + a very large index row** makes that cell fail every retry; consider capping
  alternates (recoverable) vs. the current fail-fast. Not reachable with #32's current shape.
- **Pre-PR history hygiene**: strip the `Co-Authored-By: Claude Opus 4.8` trailers from the early
  spec/plan/thread commits (message-only rewrite, tree unchanged) just before opening the PR.

## Flaky Tests

None. Full suite deterministic: **456 passed, 1 pre-existing skip** (`.codev/checks/test.sh`). Unit
tests inject a fake decider — no network, no key, no spend. The only live calls were the two budgeted
smokes (Phase 1 single cell; Phase 4 full tutorial pass).
