# air-31 — Panel temperature (PR #30 carve-out 1 of 3)

## Task
Cherry-pick the **temperature** slice of Jonathan Karr's PR #30 (commit `ea08f17`) onto
current main, preserving his authorship. PR #30 is huge (7991 insertions: jev, facct,
cross_translation, viewer); carve-outs 2 & 3 (Jev → #21, FAccT card → separate issue) are
explicitly out of scope.

## What I did
A literal `git cherry-pick` won't work — I'm taking only the temperature subset of a
36-file commit, and current main has diverged (Spec 8 tools, Spec 26 verify_source). So I
hand-applied the temperature-only changes and set `--author` to Jonathan Karr.

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
All pipeline tests pass (384 passed, 1 skipped), including the copyright audit. ~63 LOC +
new test file. Within AIR scope. Committed with Jonathan Karr's authorship; opening PR.
Per global CLAUDE.md: no Co-Authored-By / "Generated with" trailers.
