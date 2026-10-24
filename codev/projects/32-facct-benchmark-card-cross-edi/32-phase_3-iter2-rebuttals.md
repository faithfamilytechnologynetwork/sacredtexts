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
