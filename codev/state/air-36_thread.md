# air-36 — Integrate PR #35 (failure kinds + manuscript breakdowns)

## Goal
Carry a contributor's PR #35 (`the fork branch`, 3 commits from 849fb5c) onto current
main and fix the five review items from the PR comment. AIR protocol, strict mode.

## Architect brief (2026-10-25)
- Cherry-pick his 3 commits (preserve authorship), don't rewrite. Only expected conflict: cli.py.
- Parity fixture (item 1) is the most important: ONE JSON fixture asserted by BOTH pytest and
  viewer vitest.
- Analysis commands stay read-only over runs/ (print only).
- Zero live API spend; nothing here calls a model.
- Public repo: no NABRE/TLG text in fixtures; audit must pass; no .DS_Store/texput.log/todo.md.
- todo.md items → GitHub issues (dedupe #29, #27), reference from PR.
- Heads-up: builder-aspir-21 mid-flight also touches cli.py (judge command) — keep cli.py
  additions minimal/append-style to ease their rebase.
- PR: "Supersedes #35" + "Closes #36"; NO Generated-with/Co-Authored-By lines. pr gate is
  human-approved — ping at PR time, don't merge.

## Investigation notes
- His base 849fb5c predates #34. Overlapping files (both main & PR changed since base):
  `.gitignore`, `cli.py`, `outcomes.py`. `.gitignore`/`outcomes.py` edits are non-overlapping
  (should auto-merge); cli.py import block + command insertion will conflict.
- `edition_index.py` (from #34) exposes `load_edition_documents()` → `(indexed_docs,
  all_nonrestricted_docs, excluded_restricted)` via `convert_target` + licence gate. English
  Bibles (Protestant Christian: KJV/ASV(1901)/WEB) have `language==canonical_language==en`, so
  they land in `indexed_docs`. editions.py will build its agreement table from those instead of
  reading `texts/raw/*.json`.
- failure_kind.py (`classify_failure`) and failureKind.ts (`classifyFailure`) are parallel; the
  fixture covers every classify branch so they can't drift. Fixture at repo-root
  `fixtures/failure_kind_cases.json`, read by pytest (`parents[2]`) and vitest (import.meta.url).

## Progress
- Cherry-picked all 3 of the contributor's commits with `-x`, authorship preserved. Only cli.py
  conflicted (commit 1): main's `edition-index`/`facct` commands vs his `failures` command share
  an insertion point — kept both. Commits 2 & 3 auto-merged cli.py.
- Item 3 (reconcile): the rebase surfaced main's `score._bounded_equal`→`bounded_contains` rename
  (pure rename, identical body). His probes.py imported the old name → ImportError cascaded
  through cli.py into 6 test modules. Fixed probes.py import+call. Commit 65f2324.
- Item 1 (parity fixture): `fixtures/failure_kind_cases.json` (21 cases, every classifier branch)
  + `fixtures/README.md`. pytest splats each case into `classify_failure`; vitest maps
  snake→camel and calls `classifyFailure`. vitest resolves the fixture from `process.cwd()`
  (=apps/viewer) — `import.meta.url` is NOT a file: URL under vitest. Commit cd16008.
- Item 2 (editions): rewired `editions.py` onto `edition_index.load_edition_documents()` (converter
  + licence gate); dropped kjv/asv/web path options from the `editions` CLI for `--raw-root`.
  Real run: 31095 shared verses across KJV/ASV(1901)/WEB. test_editions.py added. Commit dc68841.
- Item 4 (stray files): removed .DS_Store/texput.log/todo.md, gitignored the first two. todo.md
  open items filed as #37-#43 (deduped vs #27 canonical-language, #29 refusal/verify_source
  caveat); `[x]` done items already shipped by splits/probes. Commit 4d3ad06.
- Item 5 (README): added English-only refusal-cue limitation bullet to
  runs/original-2026-10-21/README.md limitations (prose only, no numbers). Commit 6c0a06c.
- Verified: analysis commands (failures/breakdown/probes/splits/editions) all run read-only over
  runs/ (runs/ stays clean). Full dispatcher green: pipelines 483 passed/1 skipped, viewer 185
  passed, tsc clean.

## PR #44 opened; porch at pr gate (human-approved). Round-1 review folded (2026-10-25)
Architect r1: both consult lanes REQUEST_CHANGES — 7 blocking, item 8 decided, cleanups, gate
item 10, 2 follow-ups. All folded (commits 0324204 → bae23df):
- B1 tradition: breakdown_run counts a shared text once per LISTED tradition (not tradition[0]);
  multi-tradition regression test.
- B2 parity gaps: Python `_normalize` strips `_` to match TS; Greek added to `_script` +
  primaryScript (grc); severity added to the fixture + asserted in BOTH suites; +2 fixture cases.
- B3: fixtures/ now gated on BOTH test lanes in .codev/checks/test.sh (was zero-tested).
- B4: viewer no-roster join emits failure:null (was classifying from ""); expectedText fallback
  "" to match Python.
- B5: format_splits prints "—" for an all-refused model (was TypeError); regression test.
- B6: replaced the vacuous cite_passage assertion with `not in tests`.
- B7: probes/splits payload loaders fail loud on a missing passed/defaulted path (+ CLI validates).
- Item 8: finished SacredBench rename (README/TUTORIAL/viewer README/index.html/pyproject);
  RootLayout already had it. LeaderboardTable copy rewrite + rename declared in PR body.
- Item 9 cleanups: paraphrase_f1 param so splits._quote_kind delegates the cascade; promoted
  expected_text/tokens/load_rows; dropped unused Counter import + stale noqa; outcomes docstring
  indentation; CODE_WALKTHROUGH module tree + &kind= in viewer README.
- **Item 10 GATE**: re-ran failures/breakdown/probes/splits/editions over runs/original-2026-10-21;
  ALL FIVE byte-identical pre vs post-fix. No manuscript number moved (no underscores/Greek in this
  run flip a class; every text single-tradition; _quote_kind refactor behavior-preserving). Reported
  to architect.
- Follow-ups filed: #45 (route remaining raw reads via edition_index, unify the join, --json),
  #46 (localResults no-roster sample-path honesty).
Gate state: pr (human-approved). Do NOT merge; waiting on architect approval.
