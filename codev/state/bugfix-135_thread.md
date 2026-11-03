# bugfix-135 thread — Sikh cite_passage at the Ang only

## 2026-11-03 investigate

Issue #135 (Jasbir Singh): SGGS has no standard line numbering within an Ang, so asking for and
scoring `Ang N:k` is meaningless. Reported cell: astra, sikhism prompt-english row 23
(`872d2fa7eaed8469`), expected `Ang 315:44`, answer `ਅੰਗ ੩੧੫:੯` — credited at the Ang since #112,
`segment_match` 0.

Root cause, two layers:
1. **Questions** — `build_questions.py` `sikhism()` keys every pankti `Ang {ang}:{k}` and `rows_for`
   uses that one string for the cite_passage `expected.citation` AND the form example
   (`Ang 1231:12`); both cite templates (EN + Punjabi) ask for "the citation".
2. **Scoring** — swapping only the data to `Ang 315` is not enough. A no-colon expected selects
   `_NUM_CITE`, whose `(?![\d:])` tail skips every `Ang N:k` span, so the matcher sees 0
   candidates and falls back to `bounded_contains`. Reproduced: `Ang 315:9 or Ang 316:2` and
   `Ang 315:9 or John 1:1` score CORRECT (n_candidates 0); `Page 315` scores incorrect;
   `segment_match` is absent rather than null.

Gotcha for the prompt change: several population panktis share an Ang (1296, 1297, 462, 678, 734,
853). The example must be a *different Ang*, not just a different line, or an `Ang N` example can
equal the answer.

Scope: well under 300 LOC (builder tweak, one citations.py branch, one aggregator guard, tests,
rebuilt data). Architect asked (17:54Z) for a per-model Sikh-cite movers table in the PR body
(old `Ang N:k` vs new `Ang N` expected over the committed facct-2026-11-03 answers).

## 2026-11-03 fix

- `rows_for` gained `cited_as` (passage citation → cite citation) + `english_tmpl`; Sikh passes
  `sggs_ang` and `SGGS_EN` ("Answer with the page (Ang) only"). Punjabi cite: `ਸਿਰਫ਼ ਅੰਗ (ਪੰਨਾ) ਲਿਖੋ`
  — needs a native-speaker check. Example picked as a *different Ang*.
- Rebuild (`build_questions.py`, network fetch included): only the 4 Sikh files move, only the 66 cite
  rows (id/prompt/expected). Everything else byte-identical. Review page rebuilt (Sikh page only).
- `citations._score_at_ang`: bare `Ang N` expected → canonical text, `Page`/`ਪੰਨਾ` → Ang, drop any
  volunteered line, colon rivals still a hedge, `segment_match: None`. Summary rollup skips None.
- Oracle over runs/facct-2026-11-03: 7200 non-Sikh + 960 Sikh cite cells reproduce committed metrics;
  Sikh cells rescored at bare Ang → **0 verdict movers** for all 16 models (#112 already credited the
  Ang). Only 3/86 correct Sikh cells also matched the line. Table goes in the PR body.
- New test `test_sggs_ang_only.py` (27): 13 fail on pre-fix code+data. Full gate green.

## 2026-11-03 pr

- PR #136 opened. CMAP: codex=APPROVE, gemini=APPROVE; claude still running when the human said to
  proceed without it (recorded as "not awaited" in the handoff). `pr` gate fired; waiting on the
  architect/human. Merge with `gh pr merge --merge` (no --delete-branch) only after approval.

## 2026-11-03 pr, iteration 2 (architect decision)

- Claude CMAP: APPROVE (HIGH), flagged that on the bare-Ang path an English "Ang 315, line 9" /
  "Ang 315, Mehl 5" read as a hedge while Gurmukhi "ਅੰਗ ੩੧੫, ਮਹਲਾ ੫" scored correct (#112 extractor).
- Architect (18:16Z): FIX NOW. Rule: on the bare-Ang path a rival is only another Ang or a colon
  citation of another work; line/pankti/Mehl(a)/raag qualifiers are not candidates.
- `_score_at_ang` now extracts Angs explicitly (`_angs`) instead of `_single_citation_correct`; colon
  rivals normalized. Tests: qualifiers correct, qualified-Ang + another Ang/colon = hedge, EN/Gurmukhi
  parity. Oracle unchanged: 7200 non-Sikh + 960 Sikh old-expected identical; bare-Ang rescoring still
  0 verdict movers (n_candidates-only diffs 32 → 25). Suite 1274 passed.
- Filed #137: generate.py still builds Sikh cite rows at Ang N:k (moves ANCHOR_DIGEST; out of scope).
