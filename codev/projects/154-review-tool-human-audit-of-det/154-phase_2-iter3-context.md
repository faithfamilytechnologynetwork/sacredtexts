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


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Phase 2 is otherwise complete, but directory-version lookup can escape the selected run directory.
- claude: APPROVE — Phase 2 is complete, tested, and the iteration-1 concerns are genuinely fixed — including a real offline entry-point test and a verified-inert provider import that justifies the one declination.

### Builder Response to Iteration 2
# Phase 2, iteration 2: dispositions

Fixes are in commit `b0e0fa61`. 44 tests pass in
`pipelines/tests/test_review_compare.py`.

## codex (REQUEST_CHANGES): accepted and fixed

**Point:** `scores_path="runs/fixture-run//etc/passwd"` passed validation. The raw prefix slice
then produced `/etc/passwd`, and joining that to `run_dir` discarded `run_dir`.

**Fixed, both ways codex suggested:**

- **The loader rejects non-canonical paths.** `scores_path` must equal
  `str(PurePosixPath(scores_path))`, so a doubled slash, a `.` segment or a trailing `/` is
  rejected. Absolute paths and `..` were already rejected. There are new loader cases for
  `doubled_slash` and `dot`.
- **The run-directory lookup is structural.** `_run_dir_paths` matches the first two path
  components against `("runs", <run>)`, rejects `..`, and builds the path with
  `run_dir.joinpath(*parts[2:])`. It never slices a string. The regression test
  `test_a_run_directory_lookup_never_leaves_the_directory` passes `runs/fixture-run//etc/passwd`
  straight to `compare` (bypassing the loader). It resolves to `<run_dir>/etc/passwd`, inside the
  directory, and fails as "not found". A `..` row is refused.

## claude (APPROVE): notes

1. **`excluded` sub-counts overlap.** Taken. The report now has `excluded.both`, and the text
   line reads `excluded 3 (cant_judge 2, defect 2, both 1)`.
2. **A malformed `expected` raises a raw `KeyError`.** Taken. The loader checks the key
   `score_answer` reads for the row's task (`text` / `citation` / `answer`) and fails with a
   `ReviewCompareError`, which the CLI prints as `error: …` with exit 2.
3. **Directory versions are bound to `runs/<run>/`.** No change; this is as planned. It is
   documented in `review/README.md`.
4. **The `AR_CITE` broken mover is a rubric-vs-matcher divergence.** Acknowledged, and it will be
   raised with the architect.
   - The approved rubric discounts only a *disclaimed* echo of the form example.
   - The matcher (#118) drops an undisclaimed echo too, when another citation is beside it.
   - The fixture label follows the rubric. This is a real divergence for #41-style
     adjudication, not a fixture error.
5. **The smoke test called `compare()`, not the CLI.** Taken. It now runs `review-compare`
   through the CLI from the repo root (with `--json`) on the first 20 committed sample cells.
   Committed and current each show 20 / 20, and there are no movers.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
