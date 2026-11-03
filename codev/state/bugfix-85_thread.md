# bugfix-85 thread

## 2026-11-03 — investigate

**Reproduced.** `items/for-test/christianity/native/masoretic/` population: 74/84 rows per prompt file carry `/`; familiarity 7/8.

**Root cause.** `items/for-test/review/build_christian_original.py:wlc_books` reads the pinned OSHB morphhb XML and only deletes tags (`re.sub(r"<[^>]+>", "")`). Four kinds of residue survive:
1. `/` morpheme separators inside every `<w>` (`וְ/הָיוּ֩`). `normalize()` turns `/` into a space, so the reference splits into fragments no model writes (architect measured: 344 cells flip on the 11-02 run, Masoretic text-retrieval 11.1% → 37.6%).
2. Ketiv/Qere `<note type="variant">` flattens to ketiv+catchWord+qere glued with no space: Ezek 23:16 `ו/תעגבו/תעגבוַ/תַּעְגְּבָ֥/ה`, Lev 11:21 `לאלאל֤/וֹ`, Dan 2:42 (x2).
3. Editorial `<note>`s inlined in English: Isaiah 49:7 (population) "BHS has been faithful to the Leningrad Codex…", Psalms 23:1 (familiarity) "KJV:Ps.23.1".
4. `<seg type="x-samekh|x-pe">` paragraph markers: Exod 28:43, Exod 30:38, Neh 6:7 end in ` ס`; 81/96 answers omit it.

Model answers on the 11-02 run favour the Qere: Ezek 23:16 has 16 answers with it vs 10 Ketiv-only, Dan 2:42 17 vs 6, Lev 11:21 13 vs 12.

**Decisions (architect, 2026-11-03, all four approved):** drop every `<note>` apparatus; Ketiv/Qere → the pointed QERE; strip ס/פ paragraph segs; keep maqaf, sof pasuq, paseq, vowels, cantillation. Rebuild test: no Masoretic passage contains `/` or any ASCII letter. Record the rules in METHODOLOGY.md as the WLC rendering convention.

**Wider scope (issue comment):** Masoretic passages are also verify `no` donors (Talmud sets, a few others), so regenerate everything with `build_questions.py` and list every changed file + row counts. Add a `collect` carry-forward: copy an answer only when question id AND prompt text are byte-identical (plus same panel fingerprint + max_tokens), re-stamp digest + embedded question (score reads `expected` from it), record `carried_from`; carried rows don't count as collected spend. Estimated ~45 LOC non-test → in budget.

## 2026-11-03 — fix

- `wlc_text()` in `build_christian_original.py` applies the four rules; fail-fast if a rendered verse still has a Latin letter, `<`/`>` or `/`. Ran it over all 16,186 verses of the 16 fetched books: guard never trips. Edge shapes covered: multi-word Ketiv with a Ketiv-only maqaf (1 Sam 9:1), two-word Qere (Isa 36:12), read-not-written (Judg 20:13), written-not-read `<rdg type="x-qere"/>` (Ezek 48:16), exegesis/alternative-accent notes.
- Regenerated with `build_questions.py`: 15 questions.jsonl + 2 Masoretic passages.json changed; every changed row had a slashed Hebrew word; no donor re-drawn. 157 rows have a new prompt (re-collect), 46 keep their prompt with a new `expected` (carry).
- `collect.carry_forward()` + `join_run.py --carry-from`: carry iff question id AND prompt byte-identical AND same panel fingerprint + max_tokens; re-stamps digest and embedded question; `carried_from` = relpath + source digest; `model.json` counts only fresh calls. Not wired into the `sacredbench collect` CLI (the panel run goes through join_run).
- Real-data smoke (read-only from main's `runs/rerun-2026-11-03`, written to scratchpad): carry counts match the table exactly (Masoretic 31 carried / 53 to call; Talmud native 105/15). Rescored carried Masoretic retrieve_quote: opus 0 → 19/21, haiku 0 → 3/21.
- New tests fail on a HEAD export (9 tests), pass here.

## 2026-11-03 — pr

PR #110. CMAP: gemini=APPROVE, codex=APPROVE, claude=APPROVE (all high confidence). Folded Claude's two non-blocking notes: a test for the `max_tokens` carry guard, and a RUNNING.md line that `summary.json` usage still counts carried rows (spend comes from `model.json`). Left as is: a self-closing `<w type="x-ketiv"/>` would over-delete, but the pinned commit has none (all 16,186 verses render). Still open after merge: live re-collection of the 157 changed prompts before any Masoretic number is cited.
