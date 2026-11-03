# task-15kS — kimi at temperature 0.6

2026-11-03. OpenRouter's route for `moonshotai/kimi-k3.1-pro` began rejecting every call
at temperature 0 with 400 "invalid temperature: only 0.6 is allowed for this model" (all 50
of kimi's new Sikh retrieve_quote calls failed ~12:27 PT; temp 0 was accepted two hours
earlier). Owner decided: run kimi at 0.6.

Change: `items/for-test/models/openrouter.yaml` kimi line now carries `temperature: 0.6`
(explicit key wins over the `<<: *openrouter` merge); header comment notes the exception.
`pipelines/tests/test_phase2_tools.py::test_items_for_test_panel_is_search_off` asserted every
panel model at 0 — now asserts kimi is the only non-zero, at 0.6.

Verified: `load_config(PANEL)` loads 16 models; the other 15 fingerprints are unchanged
(`|t=0.0`), kimi's becomes `...|t=0.6` — a new panel identity. `collect()` raises CollectError
when resuming an answers file that holds kimi rows under the old fingerprint, and
`carry_forward` skips them, so kimi's re-collect needs fresh answer files. runs/ untouched.

Left alone, flagged to the architect (kept to the scoped change): `check_models.py` probes at a
hardcoded temperature 0 (will now 400 on kimi); README.md / cost.py→COST.md / join_run.py
docstring still say "temperature 0" for the whole panel.

Direction log: 20:40Z the owner briefly redirected to "no temperature for kimi" (would be
`temperature: null` overriding the merge → unset, request omits it, fingerprint loses `|t=`;
no committed kimi row would collide — all 3978 in runs/facct-2026-11-03 are `|t=0.0`). 20:41Z
reversed: 0.6 stands (OpenRouter's current default for this model). Full suites green with the
0.6 edit: pipelines 1338 passed / 35 skipped, items/for-test 25 passed.

PR opened and HELD. Caveat from the architect: kimi's 50 failed cells are being retried at
temperature 0 first; if the route has flipped back, this PR closes unmerged. Merge only on relay.
