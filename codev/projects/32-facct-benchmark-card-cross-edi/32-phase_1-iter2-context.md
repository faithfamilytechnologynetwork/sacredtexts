### Iteration 1 Reviews
- codex: APPROVE — Phase 1 implements the shared edition index, deterministic export and manifest, restricted-source filtering, CLI wiring, documentation, and focused tests as planned.
- claude: REQUEST_CHANGES — Schema, determinism, restricted filter and real-corpus output are all correct and verified, but the canonical-language guard has no covering test and the default export path drops a 17 MB derived file into a non-gitignored repo location.

### Builder Response to Iteration 1
# Phase 1 — Rebuttal to implement iteration-1 reviews

- **codex: APPROVE** (HIGH, no issues).
- **claude: REQUEST_CHANGES** (HIGH) — both named issues verified and fixed, plus the two
  worthwhile minors. All changes keep the full suite green (now **394 passed / 1 skipped**).

## claude issue 1 — canonical-language guard untested *(accepted, fixed)*

Correct: every fixture target was `en/en`, so deleting the `language == canonical_language` guard
left the suite green while letting the English Talmud and Papal Encyclicals into the in-process index
the card consumes. Fixed on both axes:
- Real-catalogue test now asserts `("Talmud Bavli", "William Davidson Edition - English")` and any
  `Papal Encyclicals` doc are **absent** from the index.
- The tmp fixture now includes a non-canonical edition (`Talmud Bavli / Davidson English`,
  `en` / canonical `he`) with its payload present, and the test asserts it never enters the index or
  the export — so the guard is covered even in CI where the real `texts/` tree is absent and the
  real-catalogue test skips.

Removing the guard now fails these assertions.

## claude issue 2 — default export path not gitignored *(accepted, fixed)*

Correct: `git check-ignore` confirmed `texts/edition_index.jsonl` was NOT ignored, against the repo's
convention for every other derived corpus artifact, and the README recipe points at that default.
Added `texts/edition_index.jsonl` and `texts/edition_index.jsonl.manifest.json` to `.gitignore`
(verified now ignored). The file stays derived-on-demand; the card reads the index in-process and #21
regenerates the file, so nothing is committed.

## claude minors *(two adopted, rest noted)*

- **`export_rows` silent first-wins on a conflicting duplicate** *(adopted)* — it now raises
  `EditionIndexError` when a second, *differing* wording appears for the same
  `(work, citation, version)`, honoring the project's fail-fast rule in a producer #21 consumes. This
  also gives `EditionIndexError` a real use (a new test covers it). Identical duplicates are still
  collapsed (no conflict).
- **`by_cite` omits `work`** *(adopted)* — added a NOTE at the `by_cite` field that a Bible consumer
  (Phase 2's counterfactual) must filter on `work == "The Bible"`, since LDS scriptures also use
  `Book chapter:verse` keys. Phase 2 will filter Bible-only explicitly and will source tradition from
  the catalogue, not from `Passage` (which collapses the tradition list to `[0]`).
- **Raw-citation vs normalized-cite-key grouping / vestigial `_BOOK_ALIAS`** *(noted, no change)* —
  empirically aligned today (all 31,102 citations match across the three editions; 0 alias hits). The
  alias is carried over from PR #30 and future-proofs a cross-converter book-name difference; left in
  place as harmless.

## Net

Both must-fix issues resolved with tests that fail if the fix is reverted; two fail-fast/safety minors
adopted; no open disagreement. codex approved outright.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
