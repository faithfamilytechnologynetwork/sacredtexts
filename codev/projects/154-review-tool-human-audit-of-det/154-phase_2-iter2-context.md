### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Phase 2 is functionally complete, but its offline-import acceptance criterion is not actually met by the production CLI.
- claude: APPROVE — Phase 2 is complete and correct, with genuinely strong JS-parity and mover-invariant engineering; the only real gap is that `verify_source`/`refused` never reach a pinned comparison table in a fixture that Phase 5 will freeze.

### Builder Response to Iteration 1
# Phase 2, iteration 1: rebuttal and dispositions

Fixes are in commit `4d1d2f26`. 40 tests pass in `pipelines/tests/test_review_compare.py`.

## codex (REQUEST_CHANGES)

**Point:** `test_current_makes_no_network_calls_and_imports_no_provider` imports `review_compare`
directly, not through the real `python -m sacredbench review-compare` entry point. `sacredbench.cli`
imports `sacredbench.providers` (directly, and through `collect.py`). Make those imports lazy and
test the real entry point.

**Partly accepted.**

- **Accepted: test the real entry point.**
  `test_the_real_entrypoint_rescores_offline_without_a_provider_sdk` runs the actual
  `python -m sacredbench review-compare FIXTURE --version current` through `runpy`. It does so
  with `socket.socket.connect` and `socket.create_connection` refused, and with a `sys.meta_path`
  finder that raises on any import of `anthropic`, `openai`, `httpx`, `requests` or
  `google.genai`. The command exits 0 and prints the expected `current` report (6 / 8). So the
  real CLI path makes no network call and loads no provider SDK.
- **Declined: making `cli.py`'s provider imports lazy.**
  - **Those imports aren't new.** `from sacredbench.providers import is_quota_error` and the
    `collect` imports in `cli.py` predate this phase. They serve the `collect` and `score`
    commands, and `main()`'s exception tuple needs `CollectError`.
  - **Making them lazy is a refactor of unrelated commands.** `collect.py` itself imports
    `providers`, so `CollectError` would have to move to a provider-free module. That changes
    the `collect`, `score` and `main()` paths, which Phase 2 does not touch.
  - **Importing `sacredbench.providers` is inert.** Verified: after `import sacredbench.cli`, no
    `anthropic`, `openai`, `google`, `httpx` or `requests` module is loaded. The SDKs are imported
    lazily inside `providers`. Loading the module opens no connection and builds no client.
  - **The criterion's intent is met.** It is that the `current` re-score cannot reach a model.
    `review_compare` (the `current` path) imports no provider module, which the module-level test
    still pins. The real entry point makes no network call and loads no SDK, which the new test
    pins.

## claude (APPROVE): nits, all taken

1. **`verify_source` and `refused` never reach a pinned table.** Fixed. The fixture now has 10
   cells, built by the same `build_sample` at k=1.
   - Two new judged `verify_source` cells:
     - an `islam/native` refusal: Sonnet's real FAccT answer, which never opens with Yes/No.
       Scorer and human both say `refused`;
     - a `hinduism/english` false premise: an Aeterni Patris passage presented as Gita,
       answered "Yes.". Both say `incorrect`.
   - `by_task["verify_source"]` and `by_grader_path["verdict"]` are now asserted, and so are
     the new totals:
     - committed 6 / 8;
     - current 6 / 8;
     - the run-directory version 7 / 8.
   - The movers are unchanged: fixed 1, broken 1.
2. **`committed` reads `root / scores_path` with no containment check.** Fixed in the loader. A
   `scores_path` that is absolute or contains `..` is rejected, so neither `committed` nor a
   run-directory version can read outside its root. Two new loader cases cover it.
3. **README arm-count wording.** Fixed. The counts are described as covering "judged rows",
   with `(none)` for a run without arms, and the `--json` paragraph notes that `by_text` entries
   carry `arms`.
4. **The unsorted-rows error gives no hint.** Fixed. It now says to pass each downloaded gold set
   as its own argument rather than concatenating files.

The "working tree changed" warning on the claude lane was the builder adding the entry-point test
during the review. No consultant wrote to the tree.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
