# Plan: Add Sri Guru Granth Sahib (Gurmukhi)

**Specification**: [codev/specs/50-sri-guru-granth-sahib.md](../specs/50-sri-guru-granth-sahib.md)

## Executive Summary

Four phases, each one commit, each green on its own. The order follows the data: the raw payload
first, because nothing reads it until a catalogue entry exists; then the FAccT fix, because adding
the catalogue entry would otherwise change the committed card; then the converter and catalogue
entry together, because the catalogue requires its converter; last, the pool tests, docs and the
re-pinned regeneration anchor.

No live run. Part 2 (Gurmukhi-aware `normalize()`) must land before any panel runs on Sri Guru
Granth Sahib.

## Phases (Machine Readable)

<!-- REQUIRED: porch parses this JSON to track phase progress. Keep it in sync when you add or remove phases; at least two phases. -->

```json
{
  "phases": [
    {"id": "phase_1", "title": "Raw payload: Shabad OS extract and build script"},
    {"id": "phase_2", "title": "FAccT card ignores texts added after the run"},
    {"id": "phase_3", "title": "Converter and catalogue entry"},
    {"id": "phase_4", "title": "Pool tests, docs, re-pinned anchor"}
  ]
}
```

## Phase Breakdown

### Phase 1: Raw payload — Shabad OS extract and build script

- `texts/raw/Sikhism/build_extract.py`: stdlib only. Reads a sparse checkout of
  `shabados/shabados` (`database/collections/{lines,line-groups,sections}`), keeps SSA2 primary
  lines, orders them `sections → lineGroups → lines`, and writes one JSON record per line with the
  upstream commit in the header. Fails fast on a line in no section, a line group in two sections,
  or overlapping sections.
- `texts/raw/Sikhism/sggs_shabados.json`: its output at `7e36a29` (60,555 lines, 51 sections).
- **Done when:** the script rebuilds the file byte for byte; the suite and audit pass unchanged
  (nothing reads the file yet).

### Phase 2: FAccT card ignores texts added after the run

- `facct.py`: `post_run_filter(targets, manifest)` keeps restricted targets (never in a manifest)
  and those the run's manifest lists as selected or excluded. Any other target came after the run.
  The census uses it.
- **Done when:** a unit test adds a text after a run and the card does not change; it fails
  without the filter.

### Phase 3: Converter and catalogue entry

- `convert.py`: `clean_sggs_line` removes the declared apparatus; `convert_shabados_sggs` numbers
  panktis per Ang in reading order (`Ang N:k`), applies `_SGGS_ANG_ERRATA` (failing on a stale
  one), and fails on a decreasing Ang. Registry line `"shabados_sggs"`.
- `texts/raw/Sikhism/source.yaml`: the target from the spec's Desired State.
- Tests: fixtures for two panktis on one physical line, the bindi + ZWJ + vowel order, a subscript
  heading, `॥੧॥ ਰਹਾਉ ॥`, a decreasing Ang and a stale erratum; and a property test over the real
  payload that raw minus apparatus equals entry text for all 60,555 lines.
- `test_catalogue.py`: the default pool is 18 texts.
- **Done when:** convert yields 60,555 unique citations; the property test fails if one vowel sign
  is dropped from one line.

### Phase 4: Pool tests, docs, re-pinned anchor

- `test_generate.py`: Sri Guru Granth Sahib's eligible pools through generate's own selection
  (1,452 entries ≥12 words, 100 ≥16).
- `facct.py`: `"pa": "Punjabi"` in the language names.
- `pipelines/README.md`, `texts/README.md`: the new converter and payload.
- `test_original_run_regression.py`: re-pin `ANCHOR_CORPUS_HASH` and `ANCHOR_DIGEST` from a fresh
  `generate` with the run manifest's params, per the 2026-10-28 procedure.
- **Done when:** the full suite passes with `texts/standardized/` rebuilt, so the anchor test runs
  instead of skipping; the committed card is unchanged; the audit passes.

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| A fresh `generate` changes every text's questions (one RNG across texts; negatives draw from the whole pool) | Expected for any new text; the anchor re-pin records it; committed runs untouched |
| A panel runs before part 2 | Stated in the spec, the PR and the issue |
| Generate takes ~40 min, so the anchor test is slow | Unchanged from today; it skips without `texts/standardized/` |

## Documentation Updates

- `pipelines/README.md`: the `shabados_sggs` converter.
- `texts/README.md`: the extract and how to rebuild it.
