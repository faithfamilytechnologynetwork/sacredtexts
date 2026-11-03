# task-Anwe — FAccT rerun landing zone

2026-11-02. One PR, two coupled changes, nothing under runs/ touched.

- `items/for-test/join_run.py --run-dir <path>` (default today's `runs/`). `run_dir` is threaded
  through `out_dir`, `_card_path`, `reconcile_usage`, `add_usage` as a parameter (no module-global
  mutation). The score subprocess still writes beside the answers. A `--run-dir` run refuses
  `runs/` itself, any path inside a committed model folder (`runs/<id>/` with base/ or model.json),
  and the viewer-reserved names panel/paper/archive. The usage card is seeded from the committed
  `runs/<model>/model.json` (prices only, `collected` dropped) so rerun cost tracking works;
  runs/ is only read. Tests: `items/for-test/test_join_run.py` (not in the porch gate; run with
  `uv run --project pipelines --with tqdm pytest items/for-test/test_join_run.py`).
- Viewer: a top-level `runs/<name>/` with no summary.json and no base/ of its own, whose
  children have `<model>/base/**/summary.json`, is a virtual panel run `<name>`. The default
  `panel` now skips such folders (otherwise a rerun would have been merged into it — the old
  code rolled up ANY summary-less top-level folder). Index `mtimeMs` for virtual panels is the
  newest summary FILE mtime (was the dir mtime; only a last-resort recency fallback, since
  generated_at wins). Gaps report the model as the segment before `base`.
- Surprise worth knowing: standings for virtual panels key on bare model_id (per-file summaries
  carry no `panel` block), so `panel` vs `rerun-…` dedupe on model id, newest wins.
- Verified: `/panel/*` and `/_gaps` over the real runs/ are byte-identical to origin/main (sha
  compare of both endpoint versions); viewer check-types + 222 vitest pass.
- Left alone: LeaderboardTable's "Combined from every finished file…" note still shows only for
  id `panel` (cosmetic; the client has no virtual-panel marker).
