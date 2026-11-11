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
