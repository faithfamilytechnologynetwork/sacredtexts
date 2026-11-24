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
