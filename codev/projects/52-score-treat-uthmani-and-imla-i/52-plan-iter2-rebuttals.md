# Plan 52 — Rebuttal to iteration-2 plan consults

Both reviewers again returned **REQUEST_CHANGES** (HIGH) while confirming the strategy, scoping,
and sequencing hold. iter-2 found correctness/wiring errors and two verified traps that would
silently corrupt the rebaseline. All accepted; verified against the code before revising.

## claude (REQUEST_CHANGES) — two high traps + wiring/completeness

1. **Viewer suite pins moved tutorial numbers; dispatcher runs only pytest (false green).**
   ACCEPTED, verified: `.codev/checks/test.sh` maps `runs/**`→the pipelines lane only, and
   `apps/viewer/src/local/tutorialRun.test.ts` reads the committed tutorial run off disk and pins
   accuracies/counts the rebaseline moves. Phase 2 now: re-pin that test, run `pnpm -C apps/viewer
   test` explicitly, and map `runs`→**both** lanes in the dispatcher. Added as a risk row.
2. **`analyze.py` imports the main checkout's scorer (`:14` `sys.path.insert(0, "…/sacredtexts/
   pipelines")`).** ACCEPTED, verified — re-running from the worktree would regenerate
   `scores-{en,ar}.jsonl` with the UNFOLDED scorer (silent non-rebaseline). Phase 2 fixes the path
   to repo-relative *first*, and cross-checks against the README's prototype re-score. Risk row added.
3. **`test_contains_reference_rebaseline.py` re-pin list incomplete.** ACCEPTED — Phase 2 now also
   re-pins `FLIP_SET`/`test_headline_flips_exactly_the_registered_cells` (the `correct==1 and
   normalized==0` predicate admits Arabic containment-credited cells; first-run's 2 Arabic cells are
   `gemma-3-4b`/`llama-3.1-8b`, outside the current claude-haiku-only set — flagged to check), the
   "`correct==normalized` except flipped" invariant, and `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`.
   The rescoped non-Arabic SHA is explicitly computed from **pre-change `git show HEAD:`** data (not
   the regenerated file) to avoid the circular-oracle trap codex raised in iter-1.
4. **`token_f1`/`exact` wiring wrong.** ACCEPTED — corrected: `exact` stays raw; `token_f1`'s
   internal `normalize()` calls must change to `score_normalize` (else Arabic `token_f1` does not
   move); `normalized`→`score_normalize`; `contains`→fold-aware `bounded_contains`.
5. **cite_passage dedup does not share `bounded_contains`.** ACCEPTED — `_citation_candidates` and
   the boundary regex call `normalize` directly; Phase 2 moves both the candidate dedup and the
   verdict to `score_normalize` together so `n_candidates` and the credit agree.
6. **`probes.py:18-40` already holds a looser context-free Arabic fold** used by
   `clustered_accuracy`. ACCEPTED — the exact fork the containment decision closes. Decision:
   re-express it over `score_normalize` (update `test_probes.py`); nothing committed depends on it,
   so documenting the divergence is the fallback. Added to Phase 2 files.
7. **Smaller notes.** ACCEPTED — generation/scoring divergence stated as harmless at verse length
   (risk row); the README's pre-fold headline preserved as *pre-fold* and its prototype re-score
   used as a cross-check; "Arabic cell" count pinned to the chosen definition (≈2/132/452), noting
   the 840 discrepancy and that the hand-verify budget is bounded by *moved* cells.
8. **Refusal mechanism nuance.** ACCEPTED and folded into the decision-3 text + witness rationale:
   under the default `strict`+`containment` graders (all committed runs), the `classify_refusal`
   edit cannot independently move an outcome — a newly-contained cell already has `correct=1`, so
   the refused→scored change flows through the headline flip; the edit matters only under
   `--evaluator strict`.

## codex (REQUEST_CHANGES)

1. **Word-boundary submetric test through `score_answer` still absent; Phase-1/2 containment
   sequencing inconsistent.** ACCEPTED — Phase 1 adds the whitespace-insensitive containment helper
   and tests it in isolation but does NOT wire `bounded_contains` until Phase 2 (made explicit); the
   end-to-end `score_answer` submetric assertion (spacing diff ⇒ `exact=0`, `normalized=0`,
   `token_f1` boundaries preserved, only `contains_reference` supplies the match) is a Phase-2
   deliverable.
2. **`exact` must remain raw.** ACCEPTED — corrected throughout (see claude #4).
3. **Ordering: NFKD → fold → mark deletion.** ACCEPTED — `score_normalize` is specified as the fold
   *interleaved* into the pipeline after NFKD/quote-dash and before mark deletion, NOT `fold()`
   wrapped around `normalize()`; a compatibility-form test guards it. (My prototype already ordered
   it this way; the plan prose was wrong and is fixed.)

## Net

No disputes. Strategy and all three iter-1 decisions stand. iter-2 closed two silent-corruption
traps (viewer false-green, `analyze.py` import path), completed the rebaseline re-pin surface,
corrected the submetric wiring (`exact` raw, `token_f1` must change, cite_passage call sites,
NFKD-first ordering), reconciled the `probes.py` fork, and refined the refusal mechanism and the
Arabic-cell count. Fixes are additive precision, not a redesign.
