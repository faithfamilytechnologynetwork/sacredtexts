# Phase 3 — Rebuttal to implement iteration-3 reviews

Both **REQUEST_CHANGES** (HIGH), converging on one blocking correctness-prose bug and one
output-safety hole; claude added polish for the paper-facing card. All accepted and fixed. Suite now
**434 passed / 1 skipped**; the real card re-rendered and re-read. Fix commit authored by me.

## Blocking (both reviewers)

1. **Correctness note claimed containment for all four tasks.** The real run has `cite_passage`
   (single correct citation) and `verify_source` (leading Yes/No), which are not scored by
   containment — so the note contradicted the contract on a paper-facing card. *Fixed.* The note is
   now **per task**, driven off the `present_tasks` list: retrieve_quote/complete_unit → *contain* the
   reference wording; cite_passage → name the one correct citation; verify_source → the correct
   leading Yes/No. Containment is now explicitly scoped to "the two text-retrieval tasks" (with the
   evaluator names). A real-run test asserts the cite_passage and verify_source wording and that
   containment is not claimed table-wide.

2. **`_within` allowed a card path that aliases run evidence** (`--json summary.json`, or a default
   `facct.json` symlinked onto `scores.jsonl`), letting `write_card` overwrite authoritative evidence
   after reading it (codex #2). *Fixed.* `_within` now rejects any output path that resolves onto one
   of the run's evidence files (`scores.jsonl`, `answers.jsonl`, `summary.json`,
   `questions.jsonl.manifest.json`), direct or symlink-resolved, and rejects an existing-directory
   target. Tests cover the direct alias, the symlinked default, and the directory target — each leaves
   evidence byte-untouched and writes no card.

## claude non-blocking (adopted)

- **`write_facct_json` was dead, non-atomic production code.** *Deleted*; the two tests that used it
  now call `write_card`, so nothing can bypass the both-or-neither path.
- **`write_card` could raise a bare `OSError`/`FileNotFoundError`** past `main()` (directory target or
  missing parent). *Fixed.* `_within` rejects directory targets, and `write_card` now
  `mkdir(parents=True)`s each parent (a `--json out/facct.json` with `out/` absent now works; a test
  covers it).
- **`0 / 0` counterfactual row was ambiguous.** *Fixed.* A note below the table explains a `0 / 0`
  model had no incorrect Bible retrieve_quote answers to reconsider.
- **Bare ISO language codes.** *Fixed.* `grc`/`he`/… now render as `Greek (grc)` / `Hebrew (he)` via a
  name map in `CARD_PROSE`.
- **"A tradition's column" stale after the table rework.** *Fixed* → "row".
- **`by_tradition` can exceed `n_texts` for a multi-tradition text.** *Fixed* with a note under the
  table ("a text shared by more than one tradition is counted under each").

## Net

The card's correctness rule now matches the scoring contract task by task, a card output path can
never overwrite run evidence, the only writer is the atomic `write_card`, and the paper-facing card
reads cleanly (language names, the 0/0 clarification, accurate tradition note).
