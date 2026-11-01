# air-31 — Panel temperature (PR #30 carve-out 1 of 3)

## Task
Cherry-pick the **temperature** slice of a contributor's PR #30 (commit `ea08f17`) onto
current main, preserving his authorship. PR #30 is huge (7991 insertions: jev, facct,
cross_translation, viewer); carve-outs 2 & 3 (Jev → #21, FAccT card → separate issue) are
explicitly out of scope.

## What I did
A literal `git cherry-pick` won't work — I'm taking only the temperature subset of a
36-file commit, and current main has diverged (Spec 8 tools, Spec 26 verify_source). So I
hand-applied the temperature-only changes and set `--author` to a contributor.

In scope, applied:
- `config.py`: `ModelSpec.temperature: float | None`, validated (numeric, bool rejected,
  0..2, fail-fast), threaded into `load_config`.
- `providers.py`: `sampling_kwargs(model)` helper; merged into all three providers
  (anthropic/openai/gemini) — omitted when unset so the host default stands.
- `collect.py`: temperature appended to `_panel_fingerprint` **only when set** (current fp
  already ends in `|tools`, so unset temp = unchanged fp → committed runs' fps intact);
  `max_tokens` + `temperature` recorded on every answer row.
- `cli.py score` panel block + `score.py` summary panel dict and markdown table gain
  `max_tokens` / `temperature` columns (`—` when unset).
- `configs/models.example.yaml` (4 entries) + `configs/models.openrouter.yaml` (3 entries):
  `temperature: 0` with a one-line comment each.
- `.env.example` (key NAMES only) + `.gitignore` `!.env.example`; TUTORIAL "Before you
  start" points at it.
- Tests: new `test_temperature.py` (config validation, fingerprint behaviour, provider
  kwargs via faked SDKs); `test_collect.py` max_tokens/temperature assertion.

### Adaptations from the PR (to stay in scope)
- Dropped the PR's `.env.example` Jev line and its `cross_translation.py` docstring sentence
  in `score.py` (both reference carve-outs 2/3).
- Current `_panel_fingerprint` already includes tools; appended `|t=` after tools rather
  than the PR's pre-tools position. Net effect (append-when-set) is identical.
- Updated 3 existing `test_phase2_tools.py` exact panel key-set assertions (feature
  intentionally widens the panel shape).

## Status
PR #33 opened (commit 189c9e2, a contributor's authorship). Reached pr gate. 384 tests pass.
Per global CLAUDE.md: no Co-Authored-By / "Generated with" trailers.

## PR #33 review — architect blocker (2026-10-23)
Architect (main) found: adding `temperature: 0` to `configs/models.openrouter.yaml` breaks
reproducibility of the committed `runs/original-2026-10-21` run (fingerprint gains `|t=0.0`,
no longer matches the answers' stored `...|` fingerprints → `score --config` fails). Correct.

Fix requested: revert openrouter.yaml temp lines (keep one commented example), keep temp:0 in
example.yaml, add a regression test (committed run's config fingerprints == run's answer
fingerprints), re-gate, push, DO NOT merge.

### I found the SAME break also hits example.yaml (flagged, holding for decision)
`runs/tutorial-2026-10-11/answers.jsonl` fingerprints are byte-identical to the
`models.example.yaml` panel (opus-search/opus/haiku-search/haiku, same models+tools, NO temp).
Verified: `score --config configs/models.example.yaml runs/tutorial-2026-10-11/answers.jsonl`
SUCCEEDS without temp, FAILS with temp:0. So example.yaml is the de-facto committed config for
tutorial-2026-10-11, contradicting the architect's "no committed run depends on it."

Done: reverted openrouter.yaml temperature (working tree only, not committed).
Open question sent to architect: is example.yaml a committed reproduction config (→ also revert
temp:0, generic test over BOTH pairs) or just a template (→ keep temp:0, test only
original↔openrouter)? Recommended: revert example.yaml too + generic test.

### Resolution (architect approved recommendation, 2026-10-23)
Both committed configs treated as reproduction configs. Applied:
- Reverted `temperature: 0` from `configs/models.example.yaml` (tutorial-2026-10-11) AND
  `configs/models.openrouter.yaml` (original-2026-10-21); each keeps ONE commented example line
  explaining why temperature is unset (it would drift the committed run's fingerprint).
- New `pipelines/tests/test_committed_config_reproducibility.py`: generic guard over all
  committed-run↔config pairs — config fingerprints must equal the fingerprints stored on the
  run's answers. Verified it catches drift (a stray `temperature: 0` → `|t=0.0` fails it).
- **DEVIATION from issue #31**: the issue's literal "temperature: 0 in example.yaml" is
  SUPERSEDED (architect decision) — a committed panel config must not drift from the finished
  run it reproduces. `temperature: 0` stays documented as a commented example in both configs.

All 386 pipeline tests pass (1 skipped). Re-gating, pushing. DO NOT merge (architect holds).
