# Review: Review tool — human audit of deterministic correctness scoring

> Started in implement phase 7 with the local end-to-end walk. The other sections are
> completed in the review phase.

## Summary

_Completed in the review phase._

## Local end-to-end walk (phase 7, 2026-11-10)

Run against a real Postgres and in a real browser (Chrome, through the claude-in-chrome
extension), as the plan's phase 7 sets out. Nothing was provisioned.

**Setup**

- Database: `createdb sacredtexts_review_dev` on the local Postgres (`localhost:5432`), then
  `pnpm -C apps/api migrate`, which created the 4 tables. This is the only database the walk
  created. To remove it: `dropdb sacredtexts_review_dev` (also in `apps/api/README.md`).
- Viewer: `pnpm -C apps/viewer build` (the plain build, with no runs baked in).
- Service: `pnpm -C apps/api start` with `SAMPLE_PATH` set to
  `review/samples/facct-2026-11-03-k10.json`, `VIEWER_DIST` set to `apps/viewer/dist`, and a
  local-only invite code. It logged the active sample `facct-2026-11-03-k10`, and
  `/api/health` returned `{"status":"ok","db":"up"}`.
- Accounts: two throwaway accounts, `reviewer-a@example.test` and `reviewer-b@example.test`,
  in the local database only.
- Screenshots and captured files are in the session scratchpad. None is committed.

**Steps**

| # | Step | Result |
|---|---|---|
| 1 | Sign up with the invite code | Pass. "Create a reviewer account" accepted the code and signed Reviewer A in. The page showed the sample header (`facct-2026-11-03-k10`, 1,423 cells, seed `spec-154`, 10 per stratum) and the 13 texts. |
| 2 | Pick the Qur'an (Uthmani), the Talmud (Aramaic) and the Sri Guru Granth Sahib | Pass. The pass became 339 cells (101 + 120 + 118), in sample order, with a progress bar per text. |
| 3 | Arabic, Hebrew and Gurmukhi render legibly and in the right direction | Pass. Hebrew prompts and answers render right-to-left and right-aligned. Arabic inside an English prompt is embedded right-to-left with its marks intact. Gurmukhi renders left-to-right with correct shaping. The Arabic note typed into the notes box runs right-to-left (`dir="auto"`). |
| 4 | Label 5 cells, with notes in Arabic and a defect flag | Pass, with 6 cells labelled: 3 Talmud, 1 Qur'an, 2 SGGS. The Qur'an `verify_source` cell has a refusal ("نعم" only at the end), labelled `refused` with an Arabic note. Both SGGS cells carry the defect flag: the first with a note, the second set while checking the dropped clicks (below). The server's draft held all 6 labels byte for byte, the Arabic note included. |
| 5 | Reload, and the labels persist | Pass. After a hard reload of a deep-linked cell and of `/review`, the outcome, the notes (Arabic included), the chosen texts and the progress (6 / 339; 1, 3 and 2 per text) all came back from the server. |
| 6 | Sign out, sign in as a second account, and it sees none of the first's labels | Pass. Reviewer B signed up in the same tab, without a reload (the cross-reviewer leak path). B saw no chosen texts and 0 labels. The cell A labelled showed no outcome and empty notes. |
| 7 | Sign back in, download the gold set twice, and the two files are identical | Pass. Signed back in as A: the 6 labels were back. The two downloads were byte-identical: 12,015 bytes, 6 rows, the same SHA-256. |
| 8 | `review-compare --version committed --version current` on it gives a report | Pass. 6 gold rows from 1 reviewer. It judged 4 and excluded the 2 defect-flagged rows. Both versions agreed 4 / 4, with no disagreements and no movers. |
| 9 | `/api/sample` is 401 when signed out | Pass. With curl before any sign-in, and from the browser after signing out: `401 {"error":"unauthorized"}`. |

**How the downloads were captured.** To keep the files out of the user's Downloads folder,
the page's `<a download>` click was hooked in the page. The hook read the very Blob the
**Download gold set** button produced and posted its bytes to a local receiver, which wrote
them to the scratchpad. The download code path (`buildGoldSet` → Blob → anchor) ran
unchanged.

**What the walk turned up**

- **Fixed: a `verify_source` "No" cell hid where its passage comes from.** The card shows only
  the expected Yes/No. On a "No" item (about a third of the sample's 389 `verify_source` cells
  have a blank citation) the reviewer couldn't see which text the passage really quotes, and
  needs that to use the question-defect flag (does the Talmud quote Judges 17:11?). The sample
  already carries it in `expected.true_*`. The cell page now shows "Passage source: <citation>
  · <version> · <tradition>" under the card (`ReviewCellPage.tsx`, with a test). The explorer is
  unchanged. After a rebuild and a service restart, the line showed in Chrome on the Talmud
  "No" cell that quotes Judges 17:11.
- **Documented: the service reads `index.html` once.** A viewer rebuilt while the service runs
  gives a blank page: the old shell points at bundles the rebuild deleted, and a missing
  `/assets/*` path gets the SPA shell with a 200. That is a local dev-loop issue only: a deploy
  builds before it starts. The local runbook now says to restart after a rebuild.
- **Not a defect: dropped clicks.** Two quick clicks in a row through the browser automation
  sometimes never reached the page. An event log showed no pointer events at all for the
  dropped clicks, and every click that arrived toggled the control correctly. Leaving a
  second between clicks fixed it.
- **Data note, not changed:** a `verify_source` cell's `true_tradition` is the generator's
  label, so the Masoretic Text shows as "Christianity". It's shown as recorded.

## Spec Compliance

_Completed in the review phase._

## Deviations from Plan

_Completed in the review phase._

## Consultation Feedback

_Completed in the review phase._

## Lessons Learned

_Completed in the review phase._

## Flaky Tests

- `apps/viewer/src/routes/ExplorerPage.test.tsx`, the wrong-answer filter test: a
  pre-existing flake (a missing `waitFor`). It failed about once in 10 full viewer runs
  during phase 6. It isn't in this project's files and wasn't changed.

## Follow-up Items

_Completed in the review phase._
