### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Core generation works and produces 476 default questions, but two Phase 2 contracts are not met.
- claude: REQUEST_CHANGES — Phase 2 hits every deliverable and I verified 476 questions / 17 texts / byte-exact prompts on the real corpus, but the manifest emits 202 excluded rows instead of 2, the containment-exclusion test is vacuous, and the false-premise negatives are 94% script-mismatched (spec-driven — needs an architect decision before Phase 6).

### Builder Response to Iteration 1
# Spec 26 Phase 2 — Rebuttal to per-phase consult (codex + claude, both REQUEST_CHANGES)

Both reviewers confirmed the core generation is correct (476 questions = 17 texts × 28, byte-exact
prompts, `display_citation` on real data, the `verify_source` identity flip, retired tasks gone,
pointer-guard updated, 340 tests). All findings accepted and fixed in `[Spec 26][Phase: implement] fix:
verify_source family/same-language negatives, target-aggregated exclusions, perf` (suite now 344).

## Blocking

### `cite_passage` required `quota + 1` entries (codex) — ACCEPTED
The exemplar may be another *target* entry (just not the same one), so only `max(quota, 2)` entries are
needed. Fixed; the test now covers exact-quota success and the `< 2`-entry failure, and the dead
`target_keys` set is removed.

### `excluded_texts` listed 202 document-groups, not the 2 targets (codex + claude) — ACCEPTED
`convert_encyclicals` re-stamps `work`/`version` per document, so each of the ~201 encyclicals became
its own excluded "text". Fixed by carrying the catalogue **target** identity through the channel:
`TextMeta` gains `target_key` (the target's `(work, version, language)`), set by both
`text_metadata` and `metadata_for_standardized_path`; `_build_texts` aggregates exclusions by
`target_key`, so encyclicals collapse to one `Papal Encyclicals` entry (Talmud English is the other).
A `test_excluded_aggregates_to_catalogue_target` test exercises the re-stamp case.

## Negative-quality design (claude #1) → architect decision (2026-10-20), implemented
claude flagged that `document_type` family exclusion left the 6 English texts with no same-language
cross-family partner, so ~48/51 negatives were cross-script (trivially rejectable). I surfaced it; the
architect chose **family = `hadith_collection` for the nine hadith collections, else the text's `work`**,
plus a **same-language preference** (fall back to cross-language only when no same-language
different-family partner exists, recording the per-text cross-language count in the manifest). Now
Qur'an↔hadith (both ar) and English-Bible↔LDS (both en) are same-script hard negatives; only Talmud
Aramaic (no `he` partner) goes cross-language, and that is flagged in
`manifest.verify_source_cross_language_negatives`. Spec/plan updated.

## Correctness & other findings

### `asked_norm` built only from the canonical pool (claude #4) — ACCEPTED
The containment exclusion now runs over **all** of the asked edition's entries (`_Text.all_norm`), not
just the ≥12-word canonical pool — so a passage present under a non-canonical/short citation can no
longer be a false "no". This is the Book-of-Mormon-quotes-KJV-Isaiah case the architect called out; a
deterministic test exercises it (shared passage under a non-canonical citation is excluded).

### Always-true assertion in the containment test (claude #3) — ACCEPTED
`test_verify_source_negative_excludes_contained_passage` is rewritten: it appends a shared passage to
both the asked edition (under a non-canonical citation) and a different-family text, then asserts
deterministically that **no** negative presents that passage. The `== -1 or True` tautology is gone.

### Performance: ~2.5M `normalize()` calls / 113 s (claude #5) — ACCEPTED
Per-entry normalized text is precomputed once per text (`entry_norms`, and `all_norm` for containment)
in `_build_texts`, instead of re-normalizing every cross-family candidate once per asked text. The
quadratic re-normalization is gone.

### Minors (claude #6) — ACCEPTED
- Dead `target_keys` removed (with the `cite_passage` fix).
- "Keep the full `requested_as` list in `source`" was my plan embellishment beyond the architect's
  instruction ("record the chosen name"); trimmed the plan to match the implementation (chosen name).
- Test fixtures now use `document_type == "hadith_collection"` so the family rule is exercised
  truthfully; docstrings corrected.

## Net
All findings fixed; the one genuine design question (negative quality) went to the architect and the
chosen family/same-language model is implemented and documented. The residual (near-verbatim but
non-identical shared passages) will be noted in the Phase-6 run README per the architect. Full pipeline
suite 344 passed.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
