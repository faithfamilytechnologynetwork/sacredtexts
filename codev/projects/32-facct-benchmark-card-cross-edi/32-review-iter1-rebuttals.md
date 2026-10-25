# PR #34 — Rebuttal to review consultation + architect integration review (round 1 / 1b)

Review consult: **codex REQUEST_CHANGES**, **claude APPROVE**. Architect integration review: **3
blocking + 2 non-blocking (round 1)** and **items 6–9 (round 1b)**. All folded; **not merged**.
Suite **442 passed / 1 skipped**; audit OK; the committed card is byte-identical except the item-9
language line; the edition-index export `corpus_hash` now equals the run manifest's.

## Blocking (architect round 1; codex overlaps on 2 & 3)

1. **Export `corpus_hash` ≠ run `corpus_hash`.** *Addressed.* `load_edition_documents` now returns
   `(indexed, all_nonrestricted, excluded)`; `build_manifest`'s `corpus_hash = gen.corpus_hash(all_nonrestricted)`
   — the full set `generate` hashes (translations included, before the language filter). Verified in
   the worktree: export now hashes `5ae493e7e249575c` == the run manifest. Module docstring states
   the semantics; test `test_real_catalogue_export_corpus_hash_equals_run_manifest`.
2. **Counterfactual not bound to the run.** *Addressed.* Candidates are now restricted to passages
   whose `(work, version, language)` is in the run manifest's `selected_texts`, and scoped to the
   question's language (structural via the `by_cite` key). A Bible edition added to the catalogue
   later cannot change a historic run's card. Tests: a 4th English Bible not in `selected_texts`
   does not match; a same-work different-language edition does not match. Committed card re-checked
   byte-identical (counterfactual unchanged: 32 / 3).
3. **`write_export` not both-or-neither.** *Addressed.* Factored one shared
   `edition_index.atomic_write_texts` (collision-safe `mkstemp`, stage-all, swap-all, rollback,
   cleanup) used by **both** `write_export` and `facct.write_card`. Test injects a second-swap
   failure and asserts both files are left byte-identical with no stray temp/backup.

## Non-blocking (architect round 1)

4. **`_bounded_equal` alias.** *Addressed.* Deleted; `score.py` and `outcomes.py` now call
   `bounded_contains` directly. No internal aliases remain.
5. **`by_cite` work/language-blind.** *Addressed.* Re-keyed on `(work, language, raw citation)` so
   the filter is structural (reconciled with item 8 below: raw citation, not normalized cite_key).

## Round 1b (claude lane, items 6–9)

6. **`_within` allowlist incomplete.** *Addressed.* Replaced with the inverse rule: an override may
   only be a NEW file or one of the card's own outputs (`facct.json` / `facct.md`) at that literal
   location; any other existing file in the run dir is rejected, and a symlink resolving onto another
   file is rejected. Tests: evidence alias, symlinked default, directory target, stale-card-survives.
7. **`by_norm` dead.** *Addressed.* Removed `EditionIndex.by_norm` and the `Passage.norm` field (and
   the per-passage `normalize` at index time); the counterfactual's empty-text guard now calls
   `score.normalize` on the few candidate passages.
8. **Two consumers could diverge.** *Addressed.* `by_cite` and `export_rows` now group on the **same**
   key — the raw citation within `(work, language)`; `cite_key`/`is_verse_citation` is only the
   is-a-Bible-verse predicate; `_BOOK_ALIAS` and the book normalization are deleted. Test asserts the
   in-process sibling sets equal the exported rows one-for-one.
9. **Census language asymmetry.** *Addressed.* Zero-question languages are now the union of target
   languages **and** canonical languages minus the pool, so Latin (the encyclicals' canonical
   language) appears alongside Greek. Committed card changes on that one line only; regenerated and
   re-pinned.

## Also folded (claude review lane, non-blocking)

- Run README no longer types the 32/3 figures (points at `facct.md`); the real-catalogue test pins
  both `NABRE` and `TLG`; `CODE_WALKTHROUGH.md` lists the two new modules.

## Not folded (architect to handle)

- Qur'an tradition `Sunni Islam` only — catalogue data → working-group thread (#27).
- `cli.py` textual conflict with #21 — merge-order resolution, architect to sequence.

## Review round 2 (consult re-run) — codex REQUEST_CHANGES, claude APPROVE; both folded

- **Counterfactual content not pinned to the run** (codex + claude): restricting to `selected_texts`
  pins edition *identity* but not *content* — editing a selected edition's wording could silently
  change a historic card. *Addressed.* `build_facct` now computes `generate.corpus_hash` over the
  full non-restricted set and **fails (`FacctError`) unless it equals the run manifest's
  `corpus_hash`**, so the card refuses to build from a drifted corpus. Test
  `test_build_fails_when_raw_edition_content_drifts` mutates a selected edition's wording and asserts
  the raise; the committed card is unchanged (corpus matches).
- **Index narrower than the export for non-Bible citations** (codex): `index_documents` bucketed only
  Bible-style citations while `export_rows` grouped every shared citation, so the one-for-one claim
  broke if a non-Bible work ever had sibling editions. *Addressed.* `index_documents` now buckets
  **every** `(work, language, citation)`; the Bible scope of the counterfactual lives in its consumer
  (`lookup_key`). The equality test now includes a non-Bible work with sibling editions.
- **Dead `cite_key` alias + stale comment** (claude): *Addressed.* Removed the alias; the predicate is
  `is_verse_citation`; the `EditionIndex` comment updated.
- **Review doc staleness** (claude): *Addressed.* AC6 and Deviations refreshed for the
  `is_verse_citation` predicate and the markdown-by-default / containment-promotion deviations.

Suite 443 passed / 1 skipped; audit OK; committed card byte-identical (no change from these fixes).
