# bugfix-97 thread — _DaemonPool private-attr break on Python 3.14

## Investigate (2026-11-02)
- Reproduced on uv-resolved CPython 3.14.0: `AttributeError: '_DaemonPool' object has no attribute '_initializer'`
  at `pipelines/sacredbench/collect.py:57` (`test_dead_cell_stays_pending_then_refilled_once` et al.).
- Root cause: `_DaemonPool._adjust_thread_count` is a verbatim copy of CPython 3.11's body. It reads the
  private `self._initializer` / `self._initargs` and calls the private `concurrent.futures.thread._worker`
  with the 3.11 signature `(ref, work_queue, initializer, initargs)`. 3.14 refactored ThreadPoolExecutor
  (`prepare_context` → `_create_worker_context`; `_worker(ref, ctx, work_queue)`), so both are gone/changed.
- CI stayed green only because `.github/workflows/tests.yml` pins 3.11; no `.python-version` exists, so local
  uv picks the newest interpreter (3.14).
- Fix (architect: smallest correct, keep daemon threads, no other changes): delegate to
  `super()._adjust_thread_count()` from a short-lived daemon thread — `Thread.daemon` is documented as
  inherited from the creating thread, so stdlib-created workers come out daemonic on every version without
  reading any private state. Plus `pipelines/.python-version` = 3.11.

## Fix (2026-11-02)
- `_DaemonPool._adjust_thread_count` now runs `super()._adjust_thread_count()` on a short-lived daemon
  spawner thread (workers inherit daemon=True) and re-raises any spawn failure on the submitting thread
  (otherwise a queued cell would never run). Dropped the `concurrent.futures.thread` / `weakref` imports.
- `pipelines/.python-version` = `3.11`; verified `uv --project pipelines run` now resolves 3.11.15.
- Regression tests in `test_collect.py`: daemon-worker behaviour (fails on 3.14 w/o fix), spawn-failure
  surfacing, and an AST guard against the private worker wiring (fails on 3.11 too, so CI pins it).
- Full suite: 877 passed / 2 skipped on 3.11.15 AND 3.14.0 (3.14 via UV_PROJECT_ENVIRONMENT scratch venv).
- Not done (architect: no other changes): tightening `requires-python`, adding 3.14 to the CI matrix.
