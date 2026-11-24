# air-163 thread — review progress page: download-all-labels CSV

## 2026-11-24 implement

- `GET /api/labels.csv` (`apps/api/src/routes/labelsCsv.ts`, behind `requireAuth`), linked from
  `/review/progress` as a plain `<a href>` "Download CSV".
- **Mid-flight scope amendment (architect, 2026-11-24, Nancy's request):** the CSV carries `prompt`,
  `expected`, `answer` too, superseding the issue's "no payloads" line. `expected` reuses the
  project's expected-text rule (`failure_kind.expected_text` / viewer `localResults.expectedText`:
  first of `text`/`citation`/`answer`), so verify_source gives yes/no and complete_unit gives the
  scored continuation, not `full_text`.
- Decisions I made where the issue was silent:
  - Drafts of **every** sample are exported (the issue has a `sample_id` column and says exports must
    not drop data); context columns join on cell_id against the active sample only.
  - A row is any label with a non-null outcome, as the issue says — looser than `/api/progress`
    (which counts only the four LABEL_OUTCOMES). They differ only on malformed drafts.
  - `question_id` and `run` come from the sample too (not parsed from cell_id), so they're empty for
    unknown cells.
  - UTF-8 BOM + CRLF so Excel reads Arabic/Hebrew/Gurmukhi. No formula escaping (verbatim data).
  - Filename `review-labels-<UTC date>.csv` (no sample id, since rows span samples).
- **Adjacent fix:** the sign-in form said "Your labels are saved privately". That is false once any
  signed-in reviewer can download everyone's labels + emails, so I reworded it. Flagged for the owner.
- Surprise: `Response.text()` strips a UTF-8 BOM (Fetch spec), so the test reads bytes.
- Live check: served the app on a socket with the real `facct-2026-11-03-k10` sample (PGlite),
  signed up, saved 4 labels, curl'd the CSV: headers, gzip, 401, and Python `csv` round-trip OK.

## 2026-11-24 pr (#164)

- CMAP: codex REQUEST_CHANGES (formula injection), claude APPROVE. Fixed claude's items (sort tie-break
  pinned by a second unknown cell + mutation check, literal header assertion, the `U+FEFF` escape instead of
  a literal BOM, cross-sample matcher_outcome caveat in the README, formula caution on the page + test).
- Did NOT add formula escaping: verbatim is what analysts need, every downloader can already read the
  whole file, and no sample payload starts with `= + - @` (only typed notes/names can). Raised to the
  architect as an owner decision; it's a one-line change in `csvField` if they want Excel-safe output.
- Note: `consult` right after `pr-create` said "No PR found for branch" (GitHub index lag); a re-run
  a minute later worked.
