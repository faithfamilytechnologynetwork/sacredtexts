# Plan: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

**Specification**: [codev/specs/52-score-treat-uthmani-and-imla-i.md](../specs/52-score-treat-uthmani-and-imla-i.md)

## Executive Summary

Implements the spec's **Approach 1** (deterministic, position-aware Arabic orthography fold;
Jev out of scope). The spec's two Critical open questions are resolved with evidence gathered by
prototyping against the real code and the `exp-arabic-prompts-2026-10-29` run (recorded in
`codev/state/aspir-52_thread.md`); two plan-iter-1 consults (codex + claude, both
REQUEST_CHANGES, both confirming the strategy) added the blast-radius and gate decisions below.

**Fold rules (resolved).** Position-aware: the **medial** maqsura+dagger digraph `ىٰ` → ا (long
ā); the **word-final** digraph and bare alef-maqsura ى → ي. Lone dagger-alif → ا. Standalone
hamza ء → ا (makes `أَرَءَيْتُمْ↔أَرَأَيْتُمْ` equal; "drop" is asymmetric and fails it). Runs
**before** the Mn-mark deletion (the dagger U+0670 is itself a mark the current pass deletes).
Already-folded-today cases (madda آ, hamza-seats أ/إ/ؤ/ئ, wasl ٱ) are untouched.

**Word boundary** (`يَـٰبُنَىَّ` one word ↔ `يَا بُنَيَّ` two) is handled as a
whitespace-insensitive Arabic containment inside the containment predicate, **not** by stripping
whitespace in the normaliser — preserving the meaning of Arabic `exact`/`normalized`/`token_f1`
(Spec-15 four-submetric contract); the word-boundary cases are credited via `contains_reference`.

**Three decisions forced by the consults (all adopted):**

1. **Scoping — the fold lives in a new scoring-only `score_normalize()`, NOT the shared
   `normalize()`.** `generate.py` (`:70,232,248,418`) and `editions.py` import the shared
   `normalize()`; folding there would change verify_source negative-selection and move the
   committed question-set `ANCHOR_DIGEST` (`test_original_run_regression.py`), making the
   reference run non-reproducible, and would touch the copyright path (`audit.py` uses
   `strip_script_marks`). The spec mandates the pre-Mn ordering but **not** that the fold live in
   the shared normaliser. So: `normalize()` stays byte-identical; `score_normalize()` interleaves
   the fold **inside** the existing pipeline at the correct point — **NFKD → quote/dash folds →
   `fold_arabic_orthography` → `strip_script_marks` (mark deletion) → punctuation → whitespace** —
   NOT `fold(text)` wrapped around `normalize(text)` (that would run the fold before NFKD and let
   NFKD-decomposed Arabic presentation forms evade it). Generation, editions, and the audit gate
   are untouched and the digest stays stable.
2. **Containment contract — extend `bounded_contains` to be fold-aware (one contract), not a
   parallel function.** Its docstring makes it the single shared containment rule; its callers are
   `score_answer`, `outcomes.classify_refusal` (`:133`), `facct.py` (`:277`), `probes.py` (`:203`).
   A parallel Arabic-only function would let `facct` silently diverge while `test_facct.py:505`
   still passes. So `bounded_contains` uses `score_normalize` + whitespace-insensitive Arabic
   handling, and all four callers get the consistent folded contract.

**Precise scorer wiring (iter-2 correction).** Of the four text-retrieval submetrics: `exact`
stays **raw** `answer.strip()==target.strip()` (no normaliser — unchanged); `normalized` uses
`score_normalize`; `token_f1` must be changed to call `score_normalize` internally (it calls
`normalize()` today, so without this edit Arabic `token_f1` would NOT move as the spec requires);
`contains_reference` goes through the fold-aware `bounded_contains`. For `cite_passage`, both the
candidate dedup (`_citation_candidates` / the boundary regex over the expected citation,
`score.py:247-276`) **and** the verdict (`bounded_contains`, `:281`) must move to `score_normalize`
together — folding only the verdict would make `n_candidates` disagree with the credit (the same
citation in two orthographies would count as two candidates → false hedge → 0).
3. **Consequence — the flip set is NOT refusal-independent; correct the #48 reasoning.** Because
   `outcomes.classify_refusal` uses `bounded_contains`, an Arabic cell with a leading decline cue
   that *did* deliver the verse in Imla'i flips `refused` → scored (correctly — it delivered). So
   the rebaseline moves some Arabic **refused** classifications too, and a rebase onto #48 is
   **not** automatically clean: the witness must be re-run after a #48 rebase. (The flip set is
   still defined on the text-match projection, so it does not *depend on #48's* decline-cue logic;
   but the two touch the same population — Arabic cells with decline cues.) **Mechanism nuance
   (iter-2):** under the default `strict`+`containment` graders — which all three committed runs
   use — the `classify_refusal` `bounded_contains` edit cannot *independently* move an outcome:
   `_with_outcome` gates `refused` on `not correct`, and a newly-contained cell already has
   `correct=1`, so its refused→scored change flows entirely through the headline flip (already in
   the flip set). The `classify_refusal` edit matters only under `--evaluator strict`. So the
   refused-set movement on the committed runs is a *consequence* of the flip set, which makes the
   delta easier to reason about — state this in the witness rationale. **Merge order
   (architect, 2026-10-29): #48 lands FIRST; this project rebases onto the post-#48 baseline and
   re-runs the orthography witness over it** — the witness is a mechanical projection-delta that
   re-runs cheaply over any baseline, whereas #48's hand-locked per-cell dispositions should not be
   re-validated against fold-moved refusal classifications.

Because this changes what `correct` means, it is a **sanctioned, oracle-witnessed rebaseline**:
committed scores and all derived artifacts for the four Arabic-bearing runs are regenerated once,
non-Arabic `(exact, normalized, token_f1)` projections are frozen against pre-change values, and
every Arabic cell that moves — headline flip **or** submetric change **or** refusal
reclassification — is pinned to a pre-registered, hand-verified set.

**Collision gate (spec-vs-feasibility, surfaced to architect).** The spec's SC "reject any rule
creating a distinct-word collision, even leaving residual cells" is, taken literally,
infeasible: the core maqsura→ya fold (needed for the largest class — `هدى↔هدي`,
`بُنَىَّ↔بُنَيَّ`) merges rare minimal pairs, and the one the prototype found (`نبى`/`نبّئ`) is
*mostly pre-existing* (`نبّئ`→`نبي` already today via the ئ seat-fold). The operative hard gate is
therefore at **scoring granularity**: every moved cell is hand-verified a true Uthmani↔Imla'i
equivalence before pre-registration, and the corpus vocab sweep is a diagnostic that must show
every introduced non-variant merge causes **no wrong credit** on any committed answer. This
refines the spec's intent (no wrong credit) while dropping an unachievable literal gate — flagged
to the architect, not decided silently.

Sequencing honors "rebaseline **once**": Phase 1 builds and tests the fold capability without
wiring it into the default path (committed evidence byte-identical, suite green); Phase 2 adopts
it and does the single atomic rebaseline; Phase 3 is governance, doc/number refresh, and the
architect moved-numbers packet.

## Phases (Machine Readable)

```json
{
  "phases": [
    {"id": "phase_1", "title": "score_normalize fold capability (logic + tests, unwired)"},
    {"id": "phase_2", "title": "Adopt fold as scoring contract + sanctioned rebaseline"},
    {"id": "phase_3", "title": "Governance docs, number refresh, architect moved-numbers packet"}
  ]
}
```

## Phase Breakdown

### Phase 1: `score_normalize` fold capability (logic + tests, unwired)

**Dependencies**: None

#### Objective

Add the position-aware Arabic fold and a fold-aware/whitespace-insensitive containment as **new,
fully-tested functions in `score.py`**, without yet calling them from the default scoring path.
Delivers the capability with exhaustive coverage while leaving every committed run's scores
byte-identical (suite green), so the hard logic is reviewed before the contract flips.

#### Files to Create / Modify

- `pipelines/sacredbench/score.py` — add `fold_arabic_orthography(text)`, `score_normalize(text)`
  (the fold interleaved into the pipeline: NFKD → quote/dash → fold → mark deletion → punct → ws),
  and the whitespace-insensitive Arabic containment helper. Do **not** yet call any of them from
  `normalize()`, `score_answer`, `token_f1`, or `bounded_contains` (those wirings happen in Phase 2
  — this keeps the default path, and therefore every committed score, byte-identical). The
  word-final detector inside the fold must **skip Mn marks + `_SCRIPT_EDITORIAL`** to find the next
  real letter, because the fold runs pre-mark-deletion (verified: 2,972 corpus words have a final
  maqsura followed only by marks, e.g. `وَعَلَىٰٓ` = ى + U+0670 + U+0653; a naive adjacency check
  mis-folds it to `وعلا`).
- `pipelines/tests/test_arabic_orthography_fold.py` (new) — the unit/invariant suite (Latin
  invariance kept consistent with `test_normalize_nonlatin.py`).

#### Deliverables

- [ ] `fold_arabic_orthography` folding each in-scope pair (dagger→ا, medial digraph→ا, final
      digraph/bare maqsura→ي, standalone hamza ء→ا), direction-independent.
- [ ] `score_normalize` interleaving the fold at the right pipeline point (NFKD → fold → marks),
      with a test on an Arabic **presentation/compatibility form** that NFKD decomposes, proving the
      fold still applies after decomposition (guards against the fold-before-NFKD ordering bug).
- [ ] Per-pair unit tests; already-folded cases (madda/seats/wasl) still fold.
- [ ] Context-dependence negatives: `أَتَىٰكُمْ↔أَتَاكُمْ` fold equal AND `عَلَىٰ↔على` stay equal,
      **plus a stacked-mark case `وَعَلَىٰٓ`** (final maqsura behind a dagger+madda) stays `وعلي`,
      not `وعلا`.
- [ ] Word-collision tests: `قَالَ`≠`قِيلَ`, `بَيْت`≠`بَات`. **Disposition note**: `سَأَلَ`≠`سَالَ`
      from the spec's Test Scenarios is **unsatisfiable and pre-existing** (both already normalise
      to `سال` today via hamza-seat decomposition) — recorded here as out of scope, not silently
      skipped.
- [ ] Corpus before/after collision **diagnostic** over
      `texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json`: enumerate introduced merges, assert
      they are dominated by same-word Uthmani↔plene reunions (the current dagger-deletion artifact),
      and list any genuine distinct-word merges for Phase-2 hand-verification. (Not a
      zero-collision assertion — zero is unachievable because the dagger fix itself "introduces"
      correct merges.)
- [ ] Latin byte-invariance of `score_normalize`; Hebrew/other-RTL untouched.
- [ ] Tests for this phase.

#### Acceptance Criteria

- [ ] All new tests pass; the full suite (`.codev/checks/test.sh`) stays green because
      `normalize()`, `bounded_contains`, and the default scoring path are unchanged.
- [ ] Re-scoring the committed runs still reproduces their `scores.jsonl` byte-for-byte, and the
      `ANCHOR_DIGEST` is unchanged (`test_first_run_regression.py`, `test_tutorial_run.py`,
      `test_original_run_regression.py`, `test_contains_reference_rebaseline.py` all still pass
      unmodified).
- [ ] Copyright audit gate passes.

#### Test Plan

Unit: per-pair, context-dependence (incl. stacked-mark), collision, Latin-invariance,
Hebrew-untouched, run via `uv --project pipelines run pytest`. Integration: the unchanged
committed-run guards confirm zero default-path drift.

### Phase 2: Adopt fold as scoring contract + sanctioned rebaseline

**Dependencies**: Phase 1

#### Objective

Flip the default contract and perform the single atomic rebaseline: route scoring through
`score_normalize`, make `bounded_contains` fold-aware (one shared containment contract across
scoring/refusal/facct/probes), regenerate committed scores and every derived artifact for the four
Arabic-bearing runs, freeze non-Arabic projections, and pin every Arabic change to a
pre-registered, hand-verified set.

#### Files to Create / Modify

- `pipelines/sacredbench/score.py` — wire per the "Precise scorer wiring" note above: `normalized`
  → `score_normalize`; `token_f1` → change its internal `normalize()` calls to `score_normalize`
  (else Arabic `token_f1` does not move); `exact` stays **raw** (unchanged); `bounded_contains` →
  `score_normalize` + whitespace-insensitive Arabic containment; `cite_passage`'s
  `_citation_candidates` + boundary regex **and** verdict both move to `score_normalize` together.
  `normalize()` is left unchanged. Update the module docstring (the `score_normalize` vs `normalize`
  split, ordering, the Arabic contract).
- `pipelines/sacredbench/probes.py` — `probes.py:18-40` already holds a **looser, context-free**
  Arabic fold (`fold_arabic_letters`: `ى→ي`, `ئ→ي`, `ة→ه` after `normalize()`) used by
  `clustered_accuracy`. That is the exact fork the containment decision closes, in the analysis
  layer. **Decision: re-express it over `score_normalize`** (so a probe cannot assert an
  equivalence the scorer denies); update `test_probes.py`. Nothing committed depends on it (no probe
  artifact in any `runs/`), so if re-expression proves non-trivial the fallback is to document the
  divergence explicitly — but default to reconciling.
- Regenerate, for `first-run-2026-10-11`, `tutorial-2026-10-11`, `original-2026-10-21`:
  `scores.jsonl`, `summary.json`/`summary.md`; `original-2026-10-21/facct.json`/`.md`;
  `tutorial-2026-10-11/jev_agreement.json`/`.md`. (Panel/usage fed back verbatim; never re-run
  `collect`/`generate`.)
- `runs/exp-arabic-prompts-2026-10-29/analyze.py` — **fix the hard-coded `sys.path.insert(0, "/Users/
  …/sacredtexts/pipelines")` (`:14`) to a repo-relative path first.** As written it imports the
  **main checkout's** scorer, so re-running it from this worktree would regenerate `scores-{en,ar}.jsonl`
  with the UNFOLDED scorer — a silent non-rebaseline. Then re-run it to refresh both conditions.
  Keep `answers-ar-normalized.jsonl` as provenance (the hand-normalisation the fold now supersedes —
  note in the run README); preserve the README's pre-fold headline (82.1/78.6 vs 71.4/71.4) as
  *pre-fold* evidence rather than overwriting it. Use the README's own prototype re-score
  (`:67-87`, en 52/56 / ar 52/56) as a free independent cross-check on the Phase-2 numbers. Do not
  invent a generic `scores.jsonl`/`summary.*` for this run.
- `apps/viewer/src/local/tutorialRun.test.ts` — re-pin the rebaselined tutorial numbers it reads off
  disk (leaderboard order + non-increasing assert, `opus≈1.0`/`haiku≈0.7121`, the
  `haiku-search` correct/refused/wrong counts incl. the Sunni-Islam/Arabic subset). **The test
  dispatcher `.codev/checks/test.sh` maps `runs/**`→the pipelines (pytest) lane only**, so a
  pipelines+runs PR would NOT run vitest and "full suite green" could hide a red viewer suite —
  Phase 2 must run `pnpm -C apps/viewer test` explicitly AND map `runs` to **both** lanes in the
  dispatcher (the treatment `fixtures/` already gets), so this can't silently regress again.
- `pipelines/tests/test_contains_reference_rebaseline.py` — rescope its projection oracle to
  **non-Arabic cells only** (the rescoped non-Arabic SHA computed from **pre-change `git show HEAD:`**
  scores filtered to non-Arabic — NOT recomputed from the regenerated file, which would be
  circular); re-pin `FLIP_SET` + `test_headline_flips_exactly_the_registered_cells` (the predicate
  `correct==1 and normalized==0` now admits Arabic containment-credited cells — first-run's 2 Arabic
  cells are under `gemma-3-4b`/`llama-3.1-8b`, outside the current claude-haiku-only set, so check
  them); the `test_contains_reference_invariants` "`correct==normalized` except flipped" invariant;
  `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE` for tutorial `retrieve_quote` (all four models carry Arabic
  cells); and the **refused** sets/counts for any Arabic cells that reclassify.
- `pipelines/tests/test_orthography_rebaseline.py` (new) — the durable witness: (1) a SHA over the
  **non-Arabic** projection frozen from pre-change committed scores (`git show HEAD:…`), proving
  nothing non-Arabic moved; (2) the **full Arabic before/after delta** — every Arabic cell whose
  `normalized`, `token_f1`, `contains_reference`, `correct`, **or** `outcome` changes is
  pre-registered (not only headline flips); (3) pinned rebaselined headline accuracies/coverages;
  (4) derived-artifact self-consistency (`summary` agrees with `scores.jsonl`).
- `pipelines/tests/test_first_run_regression.py`, `test_tutorial_run.py` — re-pin the byte-for-byte
  re-score asserts to the regenerated scores.
- `pipelines/tests/test_original_run_regression.py` — re-pin the **re-score** assert and the
  **facct-card** assert to the regenerated artifacts; the **`ANCHOR_DIGEST`** assert stays
  unchanged (generation is untouched) — confirm it still passes; the cite_passage decline survey
  pin is unaffected (regex over the raw answer).

#### Deliverables

- [ ] Scoring routed through `score_normalize`; `bounded_contains` fold-aware; `normalize()`
      unchanged; the four submetrics keep their defined meaning.
- [ ] All four runs regenerated (scores + summary + facct + jev_agreement / analyze outputs) and
      internally consistent.
- [ ] "Arabic cell" defined precisely (a cell whose **answer or expected text** contains
      Arabic-script code points) and the resulting count **pinned** so a partition drift is visible
      (a prototype count by that definition gives ≈2 / 132 / 452 movable cells for
      first-run / tutorial / original; this differs from the spec's 840 figure, which counted any
      answer row with Arabic codepoints incl. verify_source cells whose expected is an English
      yes/no — pin whichever the chosen definition yields, and note the hand-verification budget is
      bounded by *moved* cells, not by the partition size). Covers cite_passage Arabic cells, which
      can also move.
- [ ] New `test_orthography_rebaseline.py`; `test_contains_reference_rebaseline.py` rescoped +
      refused-sets re-pinned; first-run/tutorial/original guards re-pinned; `ANCHOR_DIGEST`
      confirmed stable.
- [ ] Every moved Arabic cell hand-verified a true orthographic equivalence before freezing; the
      hand-verification method recorded for the review doc.

#### Acceptance Criteria

- [ ] Full suite green; copyright audit gate passes; no artifact derived from a `restricted`
      source committed or altered; `ANCHOR_DIGEST` unchanged.
- [ ] Non-Arabic projection SHA identical to pre-change; every Arabic change matches the
      pre-registered delta; the experiment run converges its two conditions.
- [ ] No `summary.md`/`facct.md`/`jev_agreement.md` disagrees with its source scores.

#### Test Plan

Unit/integration: the new witness + rescoped oracle + re-pinned guards + experiment replay.
Manual: hand-inspect every moved Arabic cell (flip, submetric, or refusal reclassification) against
the verse before pre-registration — the collision gate at scoring granularity.

### Phase 3: Governance docs, number refresh, architect moved-numbers packet

**Dependencies**: Phase 2

#### Objective

Record the contract change where contributors will see it, refresh every hard-coded number that a
rebaselined run rotted, and hand the architect the moved-numbers packet required before merge.

#### Files to Create / Modify

- `codev/resources/arch-critical.md` — the scoring fact now states Arabic-orthography folding (the
  `score_normalize` vs `normalize` split, position-aware ى/ىٰ, dagger-alif, standalone hamza,
  fold-aware `bounded_contains`, refusal reclassification) and names `test_orthography_rebaseline.py`.
- `codev/resources/lessons-critical.md` — one line: context-free Arabic folds are provably
  insufficient; fold must be position-aware + hand-verified at scoring granularity, and belongs in a
  scoring-only normaliser to avoid generator drift.
- `pipelines/TUTORIAL.md` (`:275-278`, hard-coded `original-2026-10-21` accuracies) and
  `pipelines/CODE_WALKTHROUGH.md` (prose describing the Arabic pass) — refresh to the rebaselined
  numbers / new split (`test_code_walkthrough.py` guards only symbol names, so these rot silently).
- `runs/*/README.md` (the four runs) — rebaseline note with moved per-task numbers; the experiment
  README's `answers-ar-normalized.jsonl` provenance note.
- `codev/reviews/52-score-treat-uthmani-and-imla-i.md` — review/lessons (created at Review; the
  moved-numbers table + hand-verification method live here).

#### Deliverables

- [ ] arch-critical / lessons-critical updated via the `update-arch-docs` discipline (hot-tier caps,
      demote if full, maps accurate).
- [ ] `TUTORIAL.md` + `CODE_WALKTHROUGH.md` numbers/prose refreshed; run-README rebaseline notes.
- [ ] Moved-numbers packet sent to the architect (`afx send architect`) before the PR merges.
- [ ] Tests for this phase: N/A — documentation only; the Phase-2 suite must stay green.

#### Acceptance Criteria

- [ ] Hot-tier docs within caps and maps accurate; no stale hard-coded numbers remain in the named
      docs.
- [ ] Architect has the moved-numbers packet and has not flagged a surprise before merge.
- [ ] Full suite still green.

#### Test Plan

Manual: re-read hot-tier docs against `update-arch-docs`; grep the named docs for stale numbers;
confirm the architect acknowledgement. No code.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A fold rule causes a wrong credit (false "correct") | Medium | High | Phase-1 corpus diagnostic + Phase-2 hand-verification of every moved cell; scoring-granularity gate; non-collision beats convergence |
| Changing shared `normalize()` moves the question-set digest (generator drift) | — | — | **Avoided by design**: fold lives in `score_normalize`; `normalize()` untouched; `ANCHOR_DIGEST` stays pinned |
| Word-final detection folds a mark-trailed maqsura (`وَعَلَىٰٓ`→`وعلا`) | Medium | High | Boundary predicate skips Mn + `_SCRIPT_EDITORIAL`; stacked-mark unit test (2,972 corpus words affected) |
| Containment fork lets facct/refusal silently diverge | Medium | Medium | Extend the single `bounded_contains` (not a parallel fn); all four callers share the contract |
| Flip set assumed refusal-independent; #48 rebase assumed clean | Medium | Medium | **Corrected**: refusal reclassifies for Arabic; **decided order: #48 first, then rebase + re-run the orthography witness over the post-#48 baseline** (architect 2026-10-29) |
| `test_original_run_regression.py` (the Arabic guard, 840 cells) left red | Medium | Medium | Phase-2 re-pins its re-score + facct asserts; digest assert confirmed stable |
| Dagger fold ordered after mark deletion (silently no-ops) | Medium | High | Ordering is a stated contract; dagger-pair unit test fails if mis-ordered |
| Rebaseline misses a run or derived artifact | Medium | Medium | Phase-2 enumerates all four runs + summary/facct/jev_agreement/analyze; witness asserts self-consistency |
| Latin/Hebrew accidentally affected | Low | High | Script-scoped fold; Latin-invariance + Hebrew-untouched tests; non-Arabic projection SHA frozen |
| Viewer suite pins moved tutorial numbers but dispatcher runs only pytest (false green) | Medium | High | Re-pin `tutorialRun.test.ts`; run `pnpm -C apps/viewer test` explicitly; map `runs`→both lanes in `.codev/checks/test.sh` |
| `analyze.py` imports the main checkout's scorer → silent non-rebaseline from the worktree | Medium | High | Fix its `sys.path.insert` to repo-relative before re-running; cross-check against the README's prototype re-score (52/56) |
| Generation (unfolded `normalize`) vs scoring (folded) treat negatives differently | Low | Low | Harmless at verse length across different works (negatives are whole other-work entries); stated explicitly, not left implicit |
| Hard-coded numbers in TUTORIAL/CODE_WALKTHROUGH rot | Medium | Low | Phase-3 refresh + grep gate |
| Two rebaselines by accident (churn) | Low | Medium | Phase 1 deliberately unwired; rebaseline happens exactly once in Phase 2 |

## Documentation Updates

`codev/resources/arch-critical.md` + `lessons-critical.md`, `pipelines/TUTORIAL.md`,
`pipelines/CODE_WALKTHROUGH.md`, the four run READMEs (Phase 3); the `score.py` module docstring
(Phase 2); `codev/reviews/52-*.md` at the Review phase. No external API docs.
