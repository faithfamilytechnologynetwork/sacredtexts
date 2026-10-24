# Review: FAccT benchmark card + cross-edition reading (Spec 32)

## Summary

Carved out part 3 of 3 of Jonathan Karr's PR #30: a shared cross-edition index and a FAccT
benchmark card, reworked against the scoring contract now on `main`. Four implement phases on one
PR — a shared `edition_index` module + CLI, the card data (`facct.json`), the markdown card
(`facct.md`), and generating + committing the real card over `runs/original-2026-10-21` — plus the
audit extended to cover the committed `.md`. The card reads the committed run as-is, never
re-scores, and derives every number from `scores.jsonl` / `summary.json`.

## Spec Compliance

- [x] AC1: One command reads `runs/original-2026-10-21/` and writes `facct.json` + `facct.md` beside it, zero network/API calls (Phase 3/4; `facct` CLI).
- [x] AC2: Every outcome count equals that run's `scores.jsonl` / `summary.json`; the card never recomputes an outcome (Phase 2; bidirectional verification).
- [x] AC3: No second refusal definition and no `fabrication` label; the string does not appear as a classification (Phase 2; regression test).
- [x] AC4: Census covers all 17 selected texts by tradition/language/document_type/license, lists zero-question source languages, and the 2 excluded texts with manifest reasons (Phase 2 data, Phase 3 per-text table).
- [x] AC5: Edition counterfactual reports numerator **and** denominator per model for incorrect Bible `retrieve_quote` cells, tags them `other_edition`, states Bible-`retrieve_quote`-only + why (Phase 2/3; 32 across the panel, 3 tagged).
- [x] AC6: Non-Bible (Arabic/Hebrew/Aramaic) citations are never matched to a Bible edition — excluded by construction (Phase 2; `cite_key` returns None + `work == "The Bible"` filter; test).
- [x] AC7: The edition index is `license != restricted` filtered; a restricted NABRE target present locally never enters it (Phase 1; test).
- [x] AC8: A standalone `edition-index` CLI exports JSONL + manifest on the frozen schema for #21; restricted versions never in the file and named in `excluded_restricted` (Phase 1; test).
- [x] AC9: The card builds its counterfactual from that same module in-process (Phase 2).
- [x] AC10: No number in `facct.md` is typed; a drift guard ties the card to the run (Phase 3 fixture guard + Phase 4 committed-run guard, json **and** md).
- [x] AC11: The card fails fast with no partial write on inconsistent evidence (Phase 2 `FacctError`; Phase 3 atomic both-or-neither writer).
- [x] AC12: All card prose lives in one editable location (`facct.CARD_PROSE`), separate from counting logic (Phase 3).
- [x] AC13: The copyright audit passes and now content-scans `.md`; no committed card artifact derives from a restricted source (Phase 4; `audit._AUDITED_SUFFIXES`, markdown-injection + card-census-origin tests).
- [x] AC14: Jonathan Karr's authorship preserved on the carry-over commits (Phases 1–3 authored `Jonathan Karr <jka83321@gmail.com>`).
- [x] AC15: Tests cover the builder against a fixture run and assert counts match the fixture `scores.jsonl` (Phase 2).

Viewer per-run card view: **out of scope** by architect decision (dropped from the spec). Three-edition agreement table: **excluded** (scope decision in the plan).

## Deviations from Plan

- **Containment predicate promoted.** The plan said reuse `score`'s `contains_reference`; in practice
  that meant promoting the private `_bounded_equal` to a public `bounded_contains` (alias kept). As planned in intent.
- **`facct.md` written by default, not opt-in.** Folded from spec review before Phase 3 — the command
  writes both files by default, matching the spec's "one command writes both".
- Otherwise the plan held: Phase 1 module → Phase 2 data → Phase 3 markdown → Phase 4 generate+commit.

## Consultation Feedback

### Specify (Round 1)
- **codex / claude** REQUEST_CHANGES → **Addressed**: `expected` schema is task-dependent; counterfactual scoped to `retrieve_quote` (complete_unit excluded); denominator required; restricted-index gate corrected to `license != restricted`; Problem Statement reframed (run vs catalogue); zero-question-language universe defined; fail-fast specified. Folded + rebuttal.

### Plan (Round 1)
- **codex / claude** REQUEST_CHANGES → **Addressed**: containment pinned to `score`'s predicate; manifest `corpus_hash`/`digest`/ordering/`excluded_restricted` pinned for #21; audit extended to `.md`; both files atomic within run dir; Phase-4 integrity by byte digests; raw-source read path pinned; agreement table excluded; committed-card drift guard added. Folded + rebuttal.

### Phase 1 — EditionIndex (Rounds 1–2)
- **codex** APPROVE (R1). **claude** REQUEST_CHANGES (R1) → **Addressed**: canonical-language guard tested; default export gitignored; `export_rows` fails fast on conflicting wordings. Polish: atomic export, CLI smoke test, tradition-collapse note. **Both APPROVE** (R2).

### Phase 2 — Card data (Rounds 1–2)
- **codex / claude** REQUEST_CHANGES (R1) → **Addressed**: bidirectional scores↔summary verification + recomputed `_overall`; one-to-one join; explicit `other_edition` tag; requested-edition exclusion tested; `task` guard; evidence-immutability test. Polish: rates recomputed from counts; `n_questions` cross-check. **Both APPROVE** (R2).

### Phase 3 — Markdown card (Rounds 1–3)
- **codex / claude** REQUEST_CHANGES (R1) → **Addressed**: prose unified into `CARD_PROSE`; typed counts derived; per-text 17-row table added; task glosses; atomic/path-safe writes; systematic drift guard.
- **codex** REQUEST_CHANGES / **claude** COMMENT (R2) → **Addressed**: collision-safe atomic writer with rollback; panel + correctness rule on the card; "English" dropped; tasks derived from the run.
- **codex / claude** REQUEST_CHANGES (R3) → **Addressed**: per-task correctness note; `_within` refuses evidence aliases + directory targets; dead `write_facct_json` removed; language names, 0/0 note, multi-tradition note. Phase force-advanced at `max_iterations` (3) with all R3 items resolved in the committed fixes.

### Phase 4 — Generate + commit (Round 1)
- **Both APPROVE.** **claude** COMMENT → **Addressed**: `facct.md` drift guard; audit origin layer reads the card's `census.selected_texts`; docstring remedy note; panel provider note. Prose nits (Aramaic labelled `Hebrew (he)`; provider `openai` for `anthropic/…`) flagged to Jonathan — faithful to the data, his wording call.

### PR Review (Round 1 / 1b)
- **codex** REQUEST_CHANGES / **claude** APPROVE (consult), plus the **architect integration review**
  (3 blocking + 2 non-blocking, then items 6–9) → **all Addressed** (see
  `32-review-iter1-rebuttals.md`): export `corpus_hash` made generate-comparable (== run manifest);
  the counterfactual bound to the run's `selected_texts` + question language; one shared atomic
  writer (`atomic_write_texts`) for both `write_export` and `write_card`; `_bounded_equal` alias
  removed; `by_cite` re-keyed to `(work, language, raw citation)` matching `export_rows` (with a
  one-for-one equality test), `_BOOK_ALIAS` and `by_norm`/`Passage.norm` deleted; `_within` inverse
  rule; zero-question languages unioned with canonical languages (Latin now shown — the only line the
  committed card changed on); README de-hardcoded, `CODE_WALKTHROUGH.md` + `arch.md` updated.
- **Deferred to the architect** (not this PR): Qur'an tradition data (→ working-group thread #27);
  `cli.py` textual conflict with #21 (merge-order resolution).

No `CONSULT_ERROR`s. Gemini not used — per-phase consult is `["codex","claude"]` (Gemini can't see the worktree; `.codev/config.json`).

## Lessons Learned

### What Went Well
- The shared-producer decision (architect) paid off: one `EditionIndex` with a frozen export for #21, consumed in-process by the card — no duplicate logic.
- Reusing `score.bounded_contains` kept a single containment definition; the card cannot diverge from the headline.
- Deriving every card number from the run, with json+md drift guards, makes a future rebaseline safe-by-construction.

### Challenges Encountered
- The `expected` schema is task-dependent — only visible in the real data; the spec review caught my wrong generalization early.
- Genuine both-or-neither for two output files needed a collision-safe temp + rollback writer, not a naive two-`os.replace`; it took three review rounds to land.
- A chained `porch next`/`porch done` across the phase_3→phase_4 boundary advanced phase_4 past its build; recovered by implementing+committing before the consult.

### What Would Be Done Differently
- Run porch one command at a time at phase boundaries and read each result.
- State the per-task correctness rule in the card from the start (not containment-for-all) — a FAccT reviewer reads the markdown, not the JSON.

### Methodology Improvements
- The per-phase 2-way (codex+claude) review with a context file on re-review worked well; the `max_iterations` force-advance is a reasonable ceiling when residual items are resolved in-commit.

## Architecture Updates

- Routed: **cold** (`arch.md`) — new "FAccT card + edition index (Spec 32)" section: the shared `edition_index` producer, its **frozen** export schema (don't change without #21), and `facct.py` as a pure analysis/visualisation stage. HOT not touched (subsystem-narrow; the "four subsystems" + "never re-run over committed evidence" + "#21" HOT facts already cover the invariants).
- Routed: **cold** (`arch.md`, Test gate) — the audit now content-scans `.md` (`_AUDITED_SUFFIXES`) and recognises a card's `census.selected_texts` origins.

## Lessons Learned Updates

- Routed: **cold** (`lessons-learned.md`, Process / SPIR) — don't chain `porch next`/`porch done` across a phase boundary (it can consume the next phase's build task); run one command at a time.
- Routed: **cold** (`lessons-learned.md`, Process / SPIR) — an analysis stage reuses the scoring contract's public predicates (`bounded_contains` + `normalize`), never a second copy. HOT tiers not touched (both are capped; these are narrow enough for cold).

## Flaky Tests

No flaky tests encountered. One pre-existing skip (`test_original_run_regression.py` generation-invariance half) is the documented CI skip when `texts/standardized/` is absent — not flaky.

## Follow-up Items

- Issue #21 (Jev passage-equivalence judge) consumes the frozen `edition-index` export.
- Viewer per-run card view — deferred; its own issue if wanted.
- Three-edition agreement table — out of scope; a follow-up if the paper wants it.
- Card wording is provisional pending Jonathan Karr's FAccT paper (one editable block, `facct.CARD_PROSE`); Aramaic-Talmud language label and the OpenRouter `provider` display are his to finalize.
