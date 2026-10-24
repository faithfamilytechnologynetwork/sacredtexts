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

## Architect round 3 — item (1) reworked (fail-fast was over-broad)

The architect **rejected** the round-2 full-corpus fail-fast: failing `build_facct` unless the whole
current corpus hashes to the run manifest's value makes a historic card unbuildable after **any**
catalogue addition (arch invariant: a new tradition is a drop-in data change), breaking
`test_committed_facct_card_matches_the_run` for a reason unrelated to the run. *Reworked as directed:*
`build_facct` now records `selected_corpus_hash = gen.corpus_hash` over **only** the docs whose
`(work, version, language)` is in the run's `selected_texts`, beside `corpus_hash` (still the manifest
copy), and does **not** fail on a full-corpus mismatch. Editing a selected edition changes
`selected_corpus_hash` (the committed-card regression test fails with a clear diff; remedy =
regenerate), while an unrelated corpus addition leaves the card buildable and byte-identical. The
wording-mutation test now asserts `selected_corpus_hash` changes (not a `FacctError`), and a new test
asserts an unrelated addition leaves the whole card byte-identical. Contract documented in `facct.py`;
committed `facct.json` gains the one key (`facct.md` unchanged). Suite 444 passed / 1 skipped.

## Net

The counterfactual's edition *identity* is pinned via `selected_texts` and its *content* is tracked by
`selected_corpus_hash` (recorded, not enforced), without coupling a historic card to unrelated
catalogue growth. In-process index and exported file group identically for every work; no dead aliases
remain.
