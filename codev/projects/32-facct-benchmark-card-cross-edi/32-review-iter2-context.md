### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Core card logic is strong, but the edition export is not actually transactional and the counterfactual is not bound to the run’s corpus.
- claude: APPROVE — Spec-complete and independently verified — card numbers reproduce exactly from the run evidence, single scoring contract held, copyright gate extended correctly; findings are an untested index-side guard and minor cleanliness items.

### Builder Response to Iteration 1
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


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
