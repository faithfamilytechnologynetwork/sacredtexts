# Plan 154 — iteration 1 rebuttal

Both reviewers returned REQUEST_CHANGES. I accepted every point except one: claude's
copyright point, which conflicts with an explicit owner ruling. The plan was revised in
place.

## codex

1. **Labels don't keep their rubric version or time.** Accepted.
   - `CellLabel` is now `{outcome, defect, notes, rubric_version, labelled_at}`.
   - `withLabel` stamps both values **only on a real change** to the outcome, defect or
     notes, so an old label keeps the rubric version it was made under.
   - There is a regression test for "a no-op edit keeps the old stamp".

2. **The download reads the clock, so repeated downloads aren't identical.** Accepted.
   - The gold-set builder now reads no clock: `labelled_at` comes from each stored label.
   - Phase 5 tests that two builds from the same state are byte-equal.
   - The Phase 7 walk downloads twice and compares.
   - The download filename is `gold-<sample_id>.jsonl`, with no date in it.

3. **The 2 MB cap assumes single-byte notes.** Accepted.
   - The cap is now **8 MB**, in bytes. It is sized from a maximal multilingual draft:
     1,500 labels × 1,000 characters at 4 bytes each, plus metadata, comes to about
     6.5 MB.
   - Phase 3 tests that a maximal Gurmukhi/Arabic draft is accepted and that a body over
     8 MB gets 413.
   - Phase 5 adds a client-side UTF-8 byte guard before each PUT.

4. **No font strategy, and no Gurmukhi coverage.** Accepted.
   - Phase 6 adds a `script-text` font stack in `styles.css`. It names local and system
     fonts only, with no web-font download: Noto and the platform fonts for Arabic,
     Hebrew, Gurmukhi and Devanagari.
   - Cell text gets `dir="auto"`, a `lang` attribute and that class.
   - Page tests now include a Gurmukhi (`pa`) cell.
   - The Phase 7 walk checks Arabic, Hebrew and Gurmukhi rendering in real Chrome.

5. **External version lookup isn't run-aware.** Accepted.
   - A `<dir>` version must be a run directory. Lookup swaps the `runs/<run>/` prefix of
     each row's `scores_path` for `<dir>/`.
   - These cases fail loudly, each with a test:
     - gold rows from more than one run combined with a directory version;
     - a duplicate `(model_id, question_id)` in any scores file that is read;
     - a missing file or row.

## claude

1. **The committed sample sits outside the copyright audit. Not accepted, by owner ruling.**
   - The owner's spec-gate ruling 5 (2026-11-10, relayed by the architect) says:
     counsel's position is that this research is fair use; include NRSV; remove "the
     audit-scan extensions that existed only for copyright"; keep only what the existing
     test gate already requires to stay green.
   - Teaching `_iter_source_dicts` the sample shape and scanning `review/` is exactly the
     extension the owner ruled out. The existing gate (`audit.py` over
     `git ls-files runs/`) is untouched and stays green.
   - What I added instead is documentation. `review/README.md` and the arch docs (in the
     review phase) record the ruling next to the "no committed artifact may derive from
     a restricted source" fact, so the two don't read as a contradiction to a future
     contributor.
   - For the record, the sample's NRSV cells cite at most the run's 31 distinct verses,
     well inside the existing 500-verse allowance. There's no test for this, per the
     ruling.

2. **Phase 4 rebuilds a static host that already exists.** Accepted.
   - `apps/api/src/static.ts` now ports the in-repo `apps/viewer/server/index.mjs`, which
     is pinned by `deploy.test.ts`, rather than multibench's edge. The only addition is
     that `/api/*` is excluded from the fallback.
   - `apps/viewer/railway.json`, `server/index.mjs` and `pnpm start` are left untouched.
     Whether a live service uses them is the owner's to say. The `apps/api` README names
     `apps/api/railway.json` as the review deployment's config.
   - The plan now states that the review origin builds with `pnpm build`, not
     `build:pages`, so its browsing pages show the "no runs" empty state.

3. **The store would retry a 413 forever.** Accepted.
   - A 413, or any 4xx other than 409, 401 or a CSRF 403, is now a **terminal** save
     failure. It isn't retried, it's shown visibly, and the label is kept in memory.
   - The client-side byte guard raises the same terminal error before sending.
   - Both have regression tests. The cap is also raised to 8 MB (codex point 3).

**Non-blocking points (all accepted):**

- **Prompt arms:** the per-text report lines show the count per `source.condition`.
- **Phase 6 was oversized:** it's split into Phase 6 (pages) and a new Phase 7 (the
  local walk and docs).
- **Environment inventory:** Phase 4 now has an explicit table: `DATABASE_URL`,
  `REVIEW_INVITE_CODE`, `SAMPLE_PATH`, `VIEWER_DIST`, `PORT`, `ALLOWED_ORIGINS`. Phase 3
  adds an explicit test that signup stays closed while the invite code is unset.
- **`:` in a cell id used as a route parameter:** a single `reviewLinks.ts` helper
  encodes and decodes it, with a round-trip test. The download name uses the sample id.
- **Sample size estimate:** corrected to 2–3.5 MB.
- **Pin-test cost:** kept the full regeneration pin. It's the only check that the
  committed sample is reproducible, and the parsing cost is seconds. A digest pin
  wouldn't verify reproducibility.
