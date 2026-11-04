# bugfix-149 thread — Talmud containment fold (issue #149)

## Investigate (2026-11-03)
- Guide TSV from the architect (182 rows) at the architect's scratchpad; to be committed as
  `pipelines/sacredbench/talmud_normalization_terms.tsv` beside `citation_aliases.yaml`.
- Reproduced on facct-2026-11-03 cells: `הימנו`/`ממנו` (argon 19dbddcec133e074), `אע"פ`+`י'`
  (argon c27efcf355bf0717), `גוי`/`נכרי` + leading ו (astra 742ec7f9e32d8b35), `את היציע`/`יציע`
  (astra 08a251f8313886ca), `וחייבין`/`וחייבים` (astra 5f8211f4ad7949d1), `רשב"ג` (astra
  be7285a2571426df) — all `contains_reference: 0`, outcome incorrect.
- Root cause: `score.fold_aware_contains` has no Talmud canonicalisation (a Hebrew reference falls
  through to `return False` after `bounded_contains`), and `score_answer` never receives the
  source's `work` — only `language` — so a Talmud-only fold has nothing to key on. Language can't
  key it: the Masoretic WLC is also `he` (and `arc` for its Aramaic chapters).
- Key: `question.source.work == "Talmud Bavli"` AND a Hebrew-script reference (the English
  Davidson edition shares the work name).
- Scale: 3840 committed Talmud Aramaic retrieve_quote/complete_unit cells (1920 in facct).
- `normalize()` turns ״/׳ into spaces (`אע"פ` → `אע פ`), so the canonicaliser must read the
  raw (mark-stripped) text, before the punctuation pass.
- Plan: new module `talmud_fold.py` (loader + canonicaliser + lattice containment so ambiguous
  forms resolve against the other side); `work=` threaded score_file → score_answer →
  fold_aware_contains / classify_refusal; jev.string_settled passes it too.

## Fix (2026-11-03)
- `pipelines/sacredbench/talmud_fold.py`: loads the guide once; data rows → tables (abbreviations,
  censorship → `@NOKHRI`, divine → `@DIVINE`, letter numerals, number words, lexical); rule rows
  (orthography/prefix/punctuation/numeral ranges) switch on code rules; unknown row → error;
  review-only / DO NOT normalize skipped. Both sides become a word lattice (each token = a set of
  readings) and containment is a lattice-path match, so ambiguous forms (`א״ר`, `ר״י`, `ה׳`, `כ״א`)
  resolve against the other side; full names are never collapsed.
- Judgment calls (flag to architect): `עובדי כוכבים` / `… ומזלות` derived from the row's note; tens
  words derived from unit words (שלשה → שלשים, + the ים→ין fold gives Aramaic תלתין) for the
  `עשרים … תשעים` range row; teens (`שלש עשרה` = 13) via the compound rule (different magnitudes
  sum); a prefix (ו/ה/ב/כ/ל/מ/ש/ד, up to 2) may attach to a form (`בר״ה`, `לגוי`).
- Movers: 64 committed cells, all incorrect → correct (33 in facct-2026-11-03; 0 in archive/);
  each hand-checked at word level — every diff is a guide form. No refused cell moves, so #117's
  native-decline registry is unchanged. Residual near-misses are real text differences or
  review-only rows (`באתרא`/`באתריה`, `כפלגא`, `אמרו`/`אמרי`).
- Regression: with the Talmud branch disabled 36/51 new tests fail.
- Size: ~280-line module + ~25 lines threading — at the BUGFIX ceiling.

## PR #151 + CMAP (2026-11-03)
- First consult run failed for all three ("Multiple projects found"); rerun with `--issue 149`.
- gemini APPROVE. claude APPROVE (notes). codex REQUEST_CHANGES:
  - `ט״ו`/`ט״ז` (15/16) not read as numerals — fixed (within the guide's 11–99 range); no new movers.
  - `-ים`→`-ין` on 3-letter words folds `מים`→`מין` — the guide's own threshold; kept, documented
    as accepted residue with `שמנים` (oils) → 80 and the unconditional `כותי`/`ארמאי` fold, pinned in
    `test_accepted_collisions_are_pinned`. Owner's call to change; flagged to the architect.
- claude: oracle read committed outcomes (would go red after the facct re-score) — now derives
  off/on from answers.jsonl only. Talmud branch rewritten as `… and talmud_contains(): return True`.
- Handoff: the registry keys cells by (folder, row, qid); the #147 Talmud re-collect changes the
  answers, so the movers TSV must be regenerated in that commit (as #143 did for Gurmukhi).
- Architect review (P2): prefixed number words didn't fold (`משלשה`/`מג׳`, `בעשרים ואחד`/`בכ״א`).
  `canon()` now splits a 1–2 letter prefix like `_readings` (head + words[rest]); a prefixed number
  can start a compound (`ב20`+`1` = `ב21`). Codex round 2 (on that working tree) added prefixed
  two-letter numerals (`בי״ג`, `בכ״ב`, `בט״ו`) — numeral read on the remainder after every table
  lookup, so `בר״ה` stays an abbreviation. P3 `ימים`/`ימין` documented + pinned with `מים`/`מין`.
  Oracle unchanged: still exactly the 64 registered cells. Suite 1405 passed, 35 skipped.
- Merged origin/main (#148, Talmud daf scoring) in 69caf39; one conflict in arch-critical's
  scoring bullet, resolved by taking main's line plus the one-sentence Talmud-fold clause.
- Architect consult round (3 P2s, none touching the 64 movers):
  1. Gate on language too: fold only for work == Talmud Bavli AND language in (he, arc) — an English
     Davidson reference with a Hebrew gloss never routes through the lattice. `language` threaded
     into fold_aware_contains / _with_outcome / classify_refusal.
  2. `ד׳`/`ה׳` no longer match each other: their divine reading is tagged by letter
     (`@DIVINE:ד׳`), and `השם`/`יי` carry every tag, so either still matches them.
  3. Compounds only as the guide says: a ו-joined pair of a new magnitude, plus the teen form
     (unit then ten). `עשרים שנים` (twenty years) is no longer 22. A standalone `שנים` still matches
     another numeral 2 (`שתים`, `ב׳`) — that is the "other side has a numeral" case.
  P3s documented + pinned: `י״א` only 11 (no יש אומרים row in the guide); `שתין` folds onto `שתים`.
  Oracle: still exactly the 64 registered cells.
- Owner approved PR #151; architect ran `porch approve … --a-human-explicitly-approved-this`.
- Merged origin/main after #152 (#150 completion head: complete_unit also counts on the first ten
  words of the continuation). Conflicts: score_answer's contains_reference (now loops over
  `references` with work/language passed), the arch.md fold paragraph (both kept), arch-critical
  (main's line + the Talmud clause).
- With #150 in, the fold-level oracle no longer matched the headline (2 of the 64 are now credited by
  the head alone). The oracle now scores each Talmud cell through `score_answer` with the fold off and
  on: 85 movers, all incorrect → correct (42 in facct-2026-11-03; 52 complete_unit, 33
  retrieve_quote). The 23 new ones are completions whose first ten words differ only by guide forms
  (leading ו, האסורים/האסורין, ממנו/הימנו) — hand-checked against the head.
