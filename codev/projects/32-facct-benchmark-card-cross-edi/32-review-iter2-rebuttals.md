# PR #34 — Rebuttal to review iteration 2

**codex REQUEST_CHANGES**, **claude APPROVE** (both HIGH). Both folded. Suite **443 passed / 1
skipped**; audit OK; the committed card is byte-identical (these fixes are validation/indexing
internals, not output changes). Not merged.

## codex (blocking)

1. **Counterfactual content not pinned to the run.** *Addressed.* Restricting candidates to
   `selected_texts` pins edition *identity* but not *content* — editing a selected edition's wording
   in `texts/raw` could still silently change a historic card. `build_facct` now computes
   `generate.corpus_hash` over the full non-restricted converted set and raises `FacctError` unless it
   equals the run manifest's `corpus_hash`, so the card refuses to build from a drifted corpus.
   `load_edition_documents` is called once and the index is passed to `_counterfactual` (no second
   load). Test `test_build_fails_when_raw_edition_content_drifts` mutates a selected edition's wording
   and asserts the raise; on the committed run the hashes match (`5ae493e7e249575c`).

2. **Index narrower than the export for non-Bible citations.** *Addressed.* `index_documents` now
   buckets **every** `(work, language, citation)` (not only Bible-style ones), so `by_cite` is
   one-for-one with `export_rows` for every work; the Bible-only scope of the counterfactual lives in
   its consumer (`lookup_key`, which returns None for a non-verse citation). The equality test now
   includes a non-Bible work (`The Qur'an`) with two editions sharing a citation.

3. **442-passed not independently rerun (read-only review env).** Noted — rerun here: 443 passed / 1
   skipped after the round-2 fixes.

## claude (APPROVE, non-blocking)

- **`build_facct` didn't compare corpus_hash to the catalogue** — same as codex #1, now fixed.
- **Dead `cite_key` alias + stale comment.** *Addressed.* Alias removed; the predicate is
  `is_verse_citation`; the `EditionIndex` comment updated.
- **Review doc staleness (Deviations, AC6).** *Addressed.* Both refreshed for the `is_verse_citation`
  predicate, the alias removal, and the raw-citation key.

## Net

Edition identity *and* content are now pinned to the run (a drifted corpus fails fast), the in-process
index and the exported file group identically for every work, and no dead aliases remain. No open
disagreements.
