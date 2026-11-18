# air-161 thread: review progress dashboard (#161)

## 2026-11-18: implement

- **API**: `GET /api/progress` (`apps/api/src/routes/progress.ts`), behind `requireAuth`. One
  entry per reviewer with a draft for the active sample: `{name, texts, labelledCellIds,
  submissions, updatedAt}`, ordered by name. Names only, never emails. No schema change: two
  read queries (drafts joined to reviewers; submissions grouped by reviewer).
- **What counts as labelled**: the gold-set rule (`goldSet.LABEL_OUTCOMES`, now exported), i.e.
  the viewer's tolerant parse. A bogus outcome, a non-object label or a cell outside the sample
  is not counted. `texts` is kept only if it is a list of strings (the viewer's zod `.catch`).
- **Decision: cell ids, not per-text counts, on the wire.** The issue allowed either. The rollup
  is "labelled by anyone", which needs a union of cells, so counts alone can't give it. The viewer
  already holds the sample, so it does the join (`lib/reviewProgress.ts`).
- **Viewer**: `/review/progress` (`routes/ReviewProgressPage.tsx`), linked from the `/review`
  header next to the results link. A per-text coverage list (reusing `ReviewProgressBar`), then a
  reviewer table: name, each chosen-or-labelled text as `labelled / cells in the sample` (a text
  labelled in but since un-chosen is marked "not chosen", so per-text sums equal the total),
  total labelled, last activity (UTC date of the draft's last save). Submissions are in the API
  but not shown: the viewer never submits, and the issue's row list leaves them out.
- **Checks**: api build + 109 tests, viewer build + 426 tests, green. Live smoke on a scratch local
  Postgres DB (since dropped) with the real `facct-2026-11-03-k10` sample: two reviewers via curl,
  then `/review/progress` in Chrome. Names only in the body, signed-out 401, a null-outcome label
  not counted, and the rollup counts a cell both reviewers labelled once (116 + 1 = 117 / 1423).
