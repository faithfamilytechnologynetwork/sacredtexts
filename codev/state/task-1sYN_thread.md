# task-1sYN — explorer result filter four-way

2026-11-02. Owner request: the error explorer's `result` filter was two-way and its
`incorrect` option matched every non-correct cell (wrong + refused + missing), so choosing
`incorrect` showed missing cells.

Change (minimal, no other UI):
- `apps/viewer/src/lib/explorer.ts` — `ExplorerFilters.correct` is now
  `'correct' | 'incorrect' | 'missing'`. `incorrect` ⇒ `failureMode(r) === 'wrong'` (answered,
  not refused, not correct); `missing` ⇒ `r.missing`. Refused cells are still reachable through
  the `failure mode` dropdown and through `all`.
- `ExplorerFilters.tsx` — added the `missing` option and widened the onChange guard.
- `router.tsx` — the `?correct=` validator now also accepts `missing`.
- `ExplorerPage.tsx` — one helper-text sentence explaining the new `incorrect` meaning.
- `explorer.test.ts` — updated the incorrect expectation (b,c,d,e → b,d) and added cases:
  `incorrect` excludes missing and refused cells; `missing` returns only missing cells.

No porch project (plain task). Verify: `pnpm -C apps/viewer test` + `check-types`. The viewer has
no lint script.

## Scope change (architect, 2026-11-03T00:20Z) — five-way
The owner widened the filter to all / correct / incorrect / refused / missing. `refused` ⇒
`failureMode(r) === 'refused'` (answered but declined); `incorrect` stays scored-wrong only;
`missing` is unchanged. Added the option, the `?correct=refused` validator value, the helper
sentence ("refused and missing cells each have their own option"), and a test that `refused`
returns only refused cells. Pushed to the same PR (#89).
