# Phase 3 — Rebuttal to implement iteration-1 reviews

Both **REQUEST_CHANGES** (codex HIGH, claude MEDIUM); the findings converge and all are accepted
and fixed. Suite now **426 passed / 1 skipped**. The real card was re-rendered and read against the
docs bar. Fix commit authored by me (review-response).

## Prose unification — "one editable place" (codex #4, claude #1)

*Fixed.* Removed the `_COUNTERFACTUAL_SCOPE` constant from the analysis section and moved **all**
reader-facing wording into `CARD_PROSE`: the scope template, the census count sentence, the
zero-languages and excluded labels, the table **column headers**, and the section intros. The
renderer now contains only structure (markdown pipes) + interpolation; every word a reader reads is
in the one block Jonathan edits.

## No typed figures in the prose (codex #1, claude #2)

*Fixed.*
- `claims[0]` no longer says all accuracy figures measure "requested wording of a citation" — it now
  names what each of the four tasks is scored on (quote / complete / cite / judge), covering the
  whole table.
- The counterfactual intro and scope are now **templates** interpolated with the Bible edition count
  and version list derived from `census["selected_texts"]` (`"3 … (ASV (1901), KJV, WEB)"`), and
  `non_conclusions` no longer says "the three English Bibles". Adding a fourth public-domain English
  Bible now changes the prose automatically. A test asserts the literal "three" is absent.

## Human card now carries the 17 texts (claude #3) and drops the confusing table (claude #4)

*Fixed.* `facct.md` now renders a per-text table — work/version, language, tradition, document type,
license — for every selected text, so a reader can see which license governs each slice (the spec
criterion `facct.json` satisfied but the markdown did not). The three-breakdowns-side-by-side table
that implied a false per-row relationship is gone; a simple by-tradition table plus the per-text
table replace it.

## Task names glossed (claude #5)

*Fixed.* A new "The four tasks" section glosses `retrieve_quote` / `complete_unit` / `cite_passage` /
`verify_source` in one line each, from `CARD_PROSE`.

## Output safety (codex #2, codex #3, claude minors)

*Fixed.* The `facct` command now: validates **both** destinations including the defaults through
`_within` (so a symlink at `run_dir/facct.json` pointing outside is rejected); rejects `_within`
resolving to the run directory itself (`--md .` now errors cleanly); rejects `--json` and `--md`
resolving to the same path; and stages both files to temp paths and `os.replace`s them into place, so
a failure leaves neither JSON nor Markdown touched (true both-or-neither, matching
`edition_index.write_export`).

## Systematic drift guard (codex #5, claude minor)

*Fixed.* Added a test that asserts **every** model×task and overall count, accuracy and coverage, and
**every** counterfactual numerator/denominator, appears in the rendered card — not just one cell. The
original single-cell mutation test (20.0% → 40.0%) stays.

## Net

All prose is in one place, no figure is typed into it, the human card carries the per-text census the
spec names, the four tasks are explained, the writes are atomic and path-safe, and the drift guard
now covers the whole card.
