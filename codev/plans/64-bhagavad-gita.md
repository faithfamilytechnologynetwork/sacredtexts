# Plan: Add the Bhagavad Gita (Sanskrit)

**Specification**: [codev/specs/64-bhagavad-gita.md](../specs/64-bhagavad-gita.md)

## Executive Summary

Four phases, each one commit, each green on its own. Payload first, because nothing reads it until
a catalogue entry exists. Then the canary, so `sa` rows are refused before any `sa` text can reach
them. Then the converter and catalogue entry together. Last, the pools, docs and re-pinned anchor.

No live run. Issue #50 part 2 must land first.

## Phases (Machine Readable)

<!-- REQUIRED: porch parses this JSON to track phase progress. Keep it in sync when you add or remove phases; at least two phases. -->

```json
{
  "phases": [
    {"id": "phase_1", "title": "Raw payload: Stotra Samhita extract and build script"},
    {"id": "phase_2", "title": "Canary gates Sanskrit"},
    {"id": "phase_3", "title": "Converter and catalogue entry"},
    {"id": "phase_4", "title": "Pool tests, docs, re-pinned anchor"}
  ]
}
```

## Phase Breakdown

### Phase 1: Raw payload

- `texts/raw/Hinduism/build_extract.py`: stdlib only. Parses `gita.tex`, checks its SHA-256 and writes
  one record per verse. Fails on an unknown line, a numbering gap or a wrong chapter count.
- `texts/raw/Hinduism/gita_stotrasamhita.json`: its output at `b89199c`.
- **Done when:** the script rebuilds the file byte for byte; the suite and audit pass unchanged.

### Phase 2: Canary gates Sanskrit

- `score.py`: `devanagari_scoring_unaware()`, and a `SCORING_GATES` table the gates read.
- `cli.py`: collect and score refuse every gated language.
- `test_catalogue.py`: the canary test covers `pa` and `sa`.
- **Done when:** the test fails with the `sa` line removed.

### Phase 3: Converter and catalogue entry

- `convert.py`: `clean_gita_line`, `convert_stotrasamhita_gita`, a registry line. Chapter 13 is
  renumbered from upstream's 2..35 to 1..34.
- `texts/raw/Hinduism/source.yaml`: the target from the spec.
- Tests: fixtures, plus a property test over all 700 verses.
- **Done when:** convert yields 700 unique citations; the property test fails if one vowel sign drops.

### Phase 4: Pool tests, docs, re-pinned anchor

- `test_generate.py`: 152 entries ≥12 words, 16 ≥16.
- `facct.py`: `"sa": "Sanskrit"`.
- `pipelines/README.md`, `texts/README.md`.
- `test_original_run_regression.py`: re-pin both anchors from a fresh `generate`.
- **Done when:** the full suite passes with `texts/standardized/` rebuilt; the card is unchanged; the
  audit passes.

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Dhammapada lands first and moves the same lines | Rebase, then re-pin the anchor again |
| Generate takes ~40 min | Run in the background; the anchor test skips without `texts/standardized/` |
