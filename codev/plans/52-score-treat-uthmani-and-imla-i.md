# Plan: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

**Specification**: [codev/specs/52-score-treat-uthmani-and-imla-i.md](../specs/52-score-treat-uthmani-and-imla-i.md)

## Executive Summary

Implements the spec's **Approach 1** (deterministic, position-aware Arabic orthography fold in
the scorer; Jev adjudication out of scope per "either, not both"). The spec left two Critical
open questions; both are resolved here with evidence gathered by prototyping against the real
code and the `exp-arabic-prompts-2026-10-29` run (recorded in `codev/state/aspir-52_thread.md`):

1. **The ى / ىٰ rule is position-aware.** No context-free character map can fold
   `أَتَىٰكُمْ↔أَتَاكُمْ` while preserving `عَلَىٰ↔على`, and the full-collapse map that covers all
   pairs provably merges distinct words (`قَالَ≡قِيلَ`, `بَيْت≡بَات`). The resolved rule: the
   **medial** maqsura+dagger digraph `ىٰ` → ا (it spells long ā); the **word-final** digraph and
   bare alef-maqsura ى → ي. Lone dagger-alif → ا (always long ā). Standalone hamza ء → ا (makes
   `أَرَءَيْتُمْ↔أَرَأَيْتُمْ` equal — "drop" is asymmetric and fails this pair). All of this runs
   **before** the existing Mn-mark deletion, because the dagger (U+0670) is itself a mark the
   current pass deletes. (Already-folded-today cases — madda آ, hamza-seats أ/إ/ؤ/ئ, wasl ٱ — are
   untouched.)
2. **The word boundary (`يَـٰبُنَىَّ` one word ↔ `يَا بُنَيَّ` two words) is handled in the
   containment predicate only**, as a whitespace-insensitive Arabic containment, **not** by
   stripping whitespace inside `normalize()`. This preserves the meaning of Arabic `exact`,
   `normalized`, and `token_f1` (which would degenerate if `normalize()` deleted Arabic spaces),
   honoring the Spec-15 four-submetric contract; the word-boundary cases are caught via
   `contains_reference`, which is exactly its "correct-but-wrapped retrieval" role.

Because this changes what `correct` means, it is a **sanctioned, oracle-witnessed rebaseline**:
committed scores and all derived artifacts for the four Arabic-bearing runs are regenerated
once, non-Arabic `(exact, normalized, token_f1)` projections are frozen against the pre-change
values, and the Arabic cells that move are pinned to a pre-registered, hand-verified flip set.

Sequencing honors "rebaseline **once**": Phase 1 builds and unit-tests the fold capability
without touching the default scoring path (committed evidence stays byte-identical, suite green);
Phase 2 adopts it as the contract and does the single atomic rebaseline; Phase 3 is governance,
run-README notes, and the architect moved-numbers packet.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "Arabic orthography fold capability (logic + tests, unwired)"},
    {"id": "phase_2", "title": "Adopt fold as scoring contract + sanctioned rebaseline"},
    {"id": "phase_3", "title": "Governance docs, run-README notes, architect moved-numbers packet"}
  ]
}
```

## Phase Breakdown

### Phase 1: Arabic orthography fold capability (logic + tests, unwired)

**Dependencies**: None

#### Objective

Add the position-aware Arabic orthography fold and a whitespace-insensitive Arabic containment
helper as **new, fully-tested functions in `score.py`**, without calling them from the default
`normalize()` / scoring path. This delivers the capability with exhaustive unit and invariant
coverage while leaving every committed run's scores byte-identical, so the suite stays green and
the capability can be reviewed in isolation before the contract flips.

#### Files to Create / Modify

- `pipelines/sacredbench/score.py` — add `fold_arabic_orthography(text)` (the pre-mark
  position-aware fold: medial `ىٰ`→ا, final `ىٰ`/`ى`→ي, lone dagger→ا, standalone hamza ء→ا) and
  `arabic_whitespace_insensitive_contains(answer, expected)`. Do **not** yet invoke them from
  `normalize()` / `score_answer`.
- `pipelines/tests/test_normalize_nonlatin.py` — extend with the new per-pair and invariant tests
  (or a new `test_arabic_orthography_fold.py`; keep the Latin-invariance home consistent with the
  existing file).

#### Deliverables

- [ ] `fold_arabic_orthography` folding each in-scope pair to a single skeleton, applied
      direction-independently.
- [ ] `arabic_whitespace_insensitive_contains` for the word-boundary cases.
- [ ] Unit tests: one minimal pair per rule (dagger-alif, medial digraph, final digraph,
      bare maqsura ى→ي, standalone hamza, word boundary) folds/matches equal.
- [ ] Context-dependence negative tests: `أَتَىٰكُمْ↔أَتَاكُمْ` fold equal **and** `عَلَىٰ↔على`
      stay equal (not broken), i.e. the medial-vs-final predicate is exercised both ways.
- [ ] Word-collision tests: `قَالَ`≠`قِيلَ`, `بَيْت`≠`بَات` do not collide after folding.
- [ ] A corpus before/after collision **diagnostic** over
      `texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json`: assert that introduced merges are
      dominated by same-word Uthmani↔plene variants (the dagger-deletion artifact the current
      scorer has) and that any genuine distinct-word merges are enumerated and bounded — this is
      the input to the Phase-2 hand-verification, not a zero-collision assertion (zero is
      unachievable because the dagger fix itself "introduces" correct merges).
- [ ] Latin byte-invariance test for the helper (Latin in → Latin unchanged).
- [ ] Hebrew/other-RTL untouched by the new Arabic rules.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] All new unit/invariant tests pass; the full existing suite (`.codev/checks/test.sh`) stays
      green because `normalize()` and the default scoring path are unchanged.
- [ ] Re-scoring the committed runs still reproduces their `scores.jsonl` byte-for-byte
      (`test_first_run_regression.py`, `test_tutorial_run.py`, `test_contains_reference_rebaseline.py`
      all still pass unmodified).
- [ ] Copyright audit gate passes.

#### Test Plan

Unit: the per-pair, context-dependence, collision, Latin-invariance, Hebrew-untouched tests
above, run via `uv --project pipelines run pytest`. Integration: the unchanged committed-run
regression guards confirm no default-path drift.

### Phase 2: Adopt fold as scoring contract + sanctioned rebaseline

**Dependencies**: Phase 1

#### Objective

Flip the default contract: wire the fold into `normalize()` (ordered before the Mn-mark
deletion) and the containment predicate into `score_answer`, then perform the single atomic
rebaseline — regenerate committed scores and every derived artifact for the four Arabic-bearing
runs, freeze non-Arabic projections, and pin the Arabic flips to a pre-registered, hand-verified
set via a new durable witness test.

#### Files to Create / Modify

- `pipelines/sacredbench/score.py` — call `fold_arabic_orthography` inside `normalize()` **before**
  `strip_script_marks`'s mark deletion (so the dagger-alif survives as a letter); route
  `contains_reference` through the whitespace-insensitive Arabic containment. Update the module
  docstring to state the new Arabic-orthography contract and ordering.
- `runs/first-run-2026-10-11/`, `runs/tutorial-2026-10-11/`, `runs/original-2026-10-21/`,
  `runs/exp-arabic-prompts-2026-10-29/` — regenerate `scores.jsonl`, `summary.json`/`summary.md`;
  regenerate `original-2026-10-21/facct.json`/`.md` and `tutorial-2026-10-11/jev_agreement.json`/`.md`.
  (Panel/usage fed back verbatim; never re-run `collect`/`generate`.)
- `pipelines/tests/test_contains_reference_rebaseline.py` — make its projection oracle
  **non-Arabic-scoped** (freeze `(exact, normalized, token_f1)` over non-Arabic cells only; Arabic
  cells are expected to move).
- `pipelines/tests/test_orthography_rebaseline.py` (new) — the durable witness for THIS rebaseline:
  (1) a SHA over the **non-Arabic** projection, frozen from the pre-change committed scores via
  `git show HEAD:…`, proving nothing non-Arabic moved; (2) the exact pre-registered
  **orthography flip set** (the `(model_id, question_id)` cells whose headline flips, defined on
  the text-match projection — refusal-independent, so a rebase onto #48 stays clean); (3) pinned
  rebaselined headline accuracies/coverages; (4) derived-artifact self-consistency
  (`summary` agrees with `scores.jsonl`).
- `pipelines/tests/test_first_run_regression.py`, `pipelines/tests/test_tutorial_run.py` — re-pin
  to the regenerated `scores.jsonl` (these become byte-for-byte guards over the new baseline).

#### Deliverables

- [ ] `normalize()` folds Arabic orthography before mark deletion; containment is
      whitespace-insensitive for Arabic; the four submetrics keep their defined meaning.
- [ ] All four runs regenerated (scores + summary + facct + jev_agreement) and internally
      consistent.
- [ ] "Arabic cell" defined by answer-script (answer or expected contains Arabic code points) and
      used to partition frozen vs movable cells.
- [ ] New `test_orthography_rebaseline.py` witness; `test_contains_reference_rebaseline.py`
      rescoped; first-run/tutorial guards re-pinned.
- [ ] The pre-registered orthography flip set is hand-verified (every flipped cell is a true
      Uthmani↔Imla'i equivalence of the same verse, not a spurious word-merge) before freezing;
      the hand-verification method is recorded in the review doc.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] Full suite green under `.codev/checks/test.sh`; copyright audit gate passes; no artifact
      derived from a `restricted` source is committed or altered.
- [ ] Non-Arabic projection SHA identical to the pre-change value (nothing non-Arabic moved).
- [ ] Headline `correct` flips exactly on the pre-registered orthography cells; the experiment run
      converges its two conditions.
- [ ] No `summary.md` disagrees with its `scores.jsonl`.

#### Test Plan

Unit/integration: the new witness + rescoped oracle + re-pinned regression guards, plus an
experiment-run replay asserting convergence and the exact flip set. Manual: hand-inspect every
flipped cell against the verse before pre-registration (the collision gate at scoring
granularity).

### Phase 3: Governance docs, run-README notes, architect moved-numbers packet

**Dependencies**: Phase 2

#### Objective

Record the contract change where future contributors will see it, note the rebaseline in the
affected runs, and hand the architect the moved-numbers packet required before merge.

#### Files to Create / Modify

- `codev/resources/arch-critical.md` — the scoring fact now states Arabic-orthography folding
  (Uthmani↔Imla'i: position-aware ى/ىٰ, dagger-alif, standalone hamza; whitespace-insensitive
  Arabic containment) and names `test_orthography_rebaseline.py` as its witness.
- `codev/resources/lessons-critical.md` — a one-line lesson (context-free Arabic folds are
  provably insufficient; fold must be position-aware + hand-verified at scoring granularity).
- `runs/*/README.md` (the four runs) or a short rebaseline note — record that scores were
  rebaselined under #52 and the moved per-task numbers.
- `codev/reviews/52-score-treat-uthmani-and-imla-i.md` — the review/lessons doc (created at the
  Review phase; the moved-numbers table + hand-verification method live here).

#### Deliverables

- [ ] arch-critical / lessons-critical updated (via the `update-arch-docs` discipline: respect the
      hot-tier caps, demote if full).
- [ ] Run-README rebaseline notes.
- [ ] A moved-numbers summary sent to the architect (`afx send architect`) before the PR merges.
- [ ] Tests for this phase: N/A — documentation only; the suite from Phase 2 must stay green.

#### Acceptance Criteria

- [ ] Hot-tier docs remain within their caps and their maps stay accurate.
- [ ] The architect has the moved-numbers packet and has not flagged a surprise before merge.
- [ ] Full suite still green.

#### Test Plan

Manual: re-read the hot-tier docs against the `update-arch-docs` rules; confirm the architect
acknowledgement. No code.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A fold rule merges two genuinely distinct words (false "correct") | Medium | High | Phase-1 corpus diagnostic + Phase-2 hand-verification of every flipped cell before pre-registration; non-collision beats convergence |
| Dagger fold ordered after mark deletion (silently no-ops) | Medium | High | Ordering is a stated contract; Phase-1 dagger-pair unit test fails if mis-ordered |
| Whitespace-insensitive containment over-matches a short reference | Low | Medium | Confined to the containment predicate over verse-length references; covered by non-collision tests |
| Rebaseline misses a run or derived artifact | Medium | Medium | Phase-2 enumerates all four runs + summary/facct/jev_agreement; witness asserts self-consistency |
| Latin/Hebrew accidentally affected | Low | High | Script-scoped fold; Latin-invariance + Hebrew-untouched tests; non-Arabic projection SHA frozen |
| #48 merges first → rebase + oracle re-run | Medium | Low–Medium | Flip set defined on the text-match projection (refusal-independent); re-run the witness after rebase; merge order is the architect's call |
| Two rebaselines by accident (churn) | Low | Medium | Phase 1 is deliberately unwired; the rebaseline happens exactly once in Phase 2 |

## Documentation Updates

`codev/resources/arch-critical.md` and `lessons-critical.md` (Phase 3, via `update-arch-docs`);
run-README rebaseline notes (Phase 3); the module docstring in `score.py` (Phase 2);
`codev/reviews/52-*.md` at the Review phase. No external API docs.
