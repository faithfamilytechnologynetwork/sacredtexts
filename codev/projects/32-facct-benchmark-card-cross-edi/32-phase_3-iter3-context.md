### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Markdown rendering is largely complete, but the card contains a misleading benchmark claim and the CLI does not fully satisfy its output-safety guarantees.
- claude: REQUEST_CHANGES — Renderer, CLI and tests are sound and the numbers are genuinely derived, but card prose is split across two places, carries typed counts the spec forbids, and the human card omits the per-text census it is supposed to carry.

### Builder Response to Iteration 1
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


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — Markdown content is substantially improved, but output handling still violates the phase’s safety guarantees and some prose remains outside the designated block.
- claude: COMMENT — Phase-3 card is complete, prose is genuinely unified, numbers are derived and drift-guarded; the rendered card omits the panel identity and the containment rule it claims to rest on, and the new path/atomicity guards are untested.

### Builder Response to Iteration 2
# Phase 3 — Rebuttal to implement iteration-2 reviews

codex **REQUEST_CHANGES** (HIGH), claude **COMMENT** (HIGH, non-blocking). All points accepted and
fixed. Suite now **430 passed / 1 skipped**; the real card re-rendered and re-read. Fix commit
authored by me (review-response).

## codex (blocking)

1. **Two-file write not genuinely both-or-neither** (second-stage `os.replace` could leave stale MD).
   *Fixed.* New `write_card(report, json_path, md_path)`: both files are rendered in memory, each is
   staged to a **collision-safe** temp (`tempfile.mkstemp` in the validated parent), then swapped in;
   if the second swap fails, the first is **rolled back** to its prior bytes (or removed if it did not
   exist), and all temp/backup files are cleaned in `finally`. A test monkeypatches `os.replace` to
   fail on the second call and asserts both files are byte-identical to their prior contents with no
   stray `*.tmp`/`*.bak.*` left behind.
2. **Predictable `.tmp` paths (collision + symlink bugs).** *Fixed.* `mkstemp` gives unique names in
   the (already `_within`-validated) directory, so `--json a.tmp --md a` can no longer collide and a
   planted `*.tmp` symlink can't redirect a write.
3. **Prose still outside `CARD_PROSE`** (`FAccT benchmark card`, `overall`, `Scope:`). *Fixed.* Moved
   to `title_template`, `overall_label`, `counterfactual_scope_label` in `CARD_PROSE`; the renderer
   now interpolates them.

## claude (non-blocking, adopted)

1. **Card claimed "For this panel" but never showed the panel.** *Fixed.* Added a panel table
   (model / provider / model ID / tools / endpoint) from `report["panel"]`, with a note that tool use
   is part of a model's identity — so a search-on vs search-off run no longer renders an identical
   card.
2. **Correctness rule never stated.** *Fixed.* The outcomes section now states that correct =
   *contains* the reference wording (naming the evaluators from `report["evaluators"]`), the same
   containment the counterfactual uses, so a reader does not assume exact match.
3. **"English" hardcoded while counts derived.** *Fixed.* Dropped the "English" adjective from the
   counterfactual templates (the count and version list stay derived); a non-English Bible in the
   pool can no longer make the prose false.
4. **"The four tasks" typed and not derived.** *Fixed.* The section is now "The tasks" and glosses
   only the tasks actually present in `report["outcomes"]`, in table order; a `--tasks` subset run
   glosses exactly what it asked.

## claude minors

- New guards now tested (atomic rollback, stale-card-survives-failure via the CLI, `--json == --md`,
  default-path validation).
- Temp cleanup on a failed second stage is handled by `write_card`'s `finally`/rollback.
- `_pct(None)` path is Phase-2 and untriggered here; left as is.

## Net

The write is atomic with rollback and collision-safe, all card wording is in `CARD_PROSE`, and the
paper-facing card now names the panel (with tools) and the correctness rule it rests on.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
