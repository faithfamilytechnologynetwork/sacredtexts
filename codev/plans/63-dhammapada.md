# Plan: Add the Dhammapada (Pali)

**Specification**: [codev/specs/63-dhammapada.md](../specs/63-dhammapada.md)

## Executive Summary

Four phases, each one commit, each green on its own. The payload comes first, because nothing reads
it until a catalogue entry exists. The canary comes next, so no state of the branch has Pali in
the pool without a gate. No live run.

## Phases (Machine Readable)

<!-- REQUIRED: porch parses this JSON to track phase progress. Keep it in sync when you add or remove phases; at least two phases. -->

```json
{
  "phases": [
    {"id": "phase_1", "title": "Raw payload: VRI's romanized Dhammapada"},
    {"id": "phase_2", "title": "Canary gates cover Pali"},
    {"id": "phase_3", "title": "Converter and catalogue entry"},
    {"id": "phase_4", "title": "Pool test, docs, re-pinned anchor"}
  ]
}
```

## Phase Breakdown

### Phase 1: Raw payload

- `texts/raw/Buddhism/s0502m.mul.xml`, byte for byte from `2d134ff`.
- **Done when:** its SHA-256 matches; the suite passes unchanged.

### Phase 2: Canary gates cover Pali

- `score.py`: `pali_scoring_unaware()`, `SCORING_GATES` and `gated_languages()`.
- `cli.py`: `collect` and `score` use `gated_languages()`.
- `test_catalogue.py`: the canary test runs for `pa` and `pi`.
- **Done when:** the test passes, and fails with the `pi` gate removed.

### Phase 3: Converter and catalogue entry

- `convert.py`: `clean_vri_gatha`, `convert_vri_dhammapada`, registry line `vri_dhammapada`.
- `texts/raw/Buddhism/source.yaml`: the target from the spec.
- Tests: synthetic cases for notes, page markers, parentheses, closing matter and each failure, and
  a per-verse property test over all 423 verses.
- `test_catalogue.py`: 23 targets, 19 texts in the pool.
- **Done when:** the property test fails on one dropped letter, on leaked notes, and on leaked
  closing matter.

### Phase 4: Pool test, docs, re-pinned anchor

- `test_generate.py`: 228 verses ≥12 words, 43 ≥16.
- `facct.py`: `"pi": "Pali"`.
- `pipelines/README.md`, `texts/README.md`.
- `test_original_run_regression.py`: re-pin both anchor constants from a fresh `generate`.
- **Done when:** the full suite passes with `texts/standardized/` rebuilt; the committed card is
  unchanged; the audit passes.

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| A fresh `generate` changes every text's questions | Expected for any new text; the re-pin records it; committed runs untouched |
| The Gita PR also re-pins the anchor | The two PRs go in sequence |
