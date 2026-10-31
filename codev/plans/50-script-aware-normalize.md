# Plan: Score Gurmukhi, Devanagari and romanized Pali correctly

**Spec:** `codev/specs/50-script-aware-normalize.md`. Stacks on `gita/1-corpus`.

## Phases

### Phase 1: Indic scripts and Pali in the scorer

- `score.py`: `INDIC_MARKS`, word edges, `fold_indic`, `compose_pali`, `is_pali`, and a `pali` flag
  on `normalize()`. `token_f1`, `bounded_contains` and the `normalized` metric pass it.
- `failure_kind.py`, `failureKind.ts`, `fixtures/failure_kind_cases.json`: the Indic rule and two new
  scripts for `other_script`.
- Tests: each letter and mark, the three real corpora, the Latin pins, open gates.

### Phase 2: Witness

- `test_script_normalize_rebaseline.py`: hash of every metric of every committed answer, pinned from
  the pre-fix scorer.

### Phase 3: Anchor

- Generate over the stacked corpus. If the digest moves, re-pin `ANCHOR_DIGEST`. `corpus_hash` does
  not depend on `normalize()`.

## Risks

| Risk | Mitigation |
|---|---|
| The stack below re-pins its anchor | Generate only after the Gita re-pin lands |
