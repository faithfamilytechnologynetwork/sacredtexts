# Review: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

**Spec**: [codev/specs/52-score-treat-uthmani-and-imla-i.md](../specs/52-score-treat-uthmani-and-imla-i.md) ·
**Plan**: [codev/plans/52-score-treat-uthmani-and-imla-i.md](../plans/52-score-treat-uthmani-and-imla-i.md)

## Summary

A model that reproduces a Qur'anic verse correctly but in a different orthography than the QUL
Uthmani corpus (the common case when prompted in Arabic — #39) is now credited. Three implement
phases: **phase_1** built the fold capability, **phase_2** wired it into the five containment
call-sites and ran a sanctioned oracle-witnessed rebaseline, **phase_3** routed the governance
facts. The equivalence lives **entirely in the containment predicate** (`fold_aware_contains`), a
strict superset of the previous `bounded_contains`: `normalize()` and the similarity submetrics
(`exact`/`normalized`/`token_f1`) are byte-for-byte unchanged, so the only scores that move are
`contains_reference`, the headline `correct`, and `outcome`. Net outcome: **56 committed cells move
`incorrect→correct`, zero losses, zero coverage change, zero similarity drift**; the motivating
Arabic-prompt A/B resolves from an ~8–11pt gap to **en 96.4% / ar 92.9%** with a single residual
cross-condition flip (a #60 hamza-alef cell, not retrieval), clearing the #39 prerequisite.

## Spec Compliance

- [x] **Enumerated orthographic pairs equate without distinct-word collision** (phase_1) — dagger-alif
  → optional ā, alef-maqsura ى→ي, the ىٰ digraph → optional ā, standalone hamza ء→ا, and Arabic
  word-boundary equivalence, all in `score_normalize` / `fold_aware_contains`.
- [x] **The long-ā alef is OPTIONAL, handled in containment not a canonical fold** (phase_1) — the
  equality-fold approach was abandoned (it un-credits the defective-spelling class هذا/الرحمن); the
  long ā is matched as an optional alef (`ا?`). `normalize()` and the equality submetrics unchanged.
- [x] **No-wrong-credit gate (operative)** (phase_1/phase_2) — `fold_aware_contains` is a strict
  superset of `bounded_contains` (`normalized=1 ⇒ contains_reference=1` by construction), and every
  one of the 56 moved cells was hand-verified a true Uthmani↔Imla'i equivalence at scoring
  granularity before pre-registration.
- [x] **exp-arabic-prompts-2026-10-29 converges** (phase_2, refined in review) — en 96.4% / ar
  92.9% with a single residual cross-condition flip (Q27:59, a #60 hamza-alef cell, not retrieval);
  the pre-registered flip set reproduces exactly.
- [x] **Latin `normalize()` byte-for-byte unchanged; Hebrew/other-RTL regression coverage added**
  (phase_1) — Latin-invariance guard passes; `test_normalize_nonlatin.py` extended, invariance test
  extended to `_answer_plene_form`.
- [x] **Spec 15 four-submetric contract honored** (phase_2) — all orthographic flexibility is in the
  containment predicate; Arabic `exact`/`normalized`/`token_f1` keep their meaning; only
  `contains_reference` and the headline it drives move.
- [x] **Sanctioned, oracle-witnessed rebaseline via before/after projection delta** (phase_2) — no
  non-Arabic `(exact, normalized, token_f1)` projection value changes (SHA byte-identical on all 5
  score files); moved Arabic cells match the pre-registered set. Witness
  `test_orthography_rebaseline.py`.
- [x] **All score-derived artifacts regenerated** (phase_2) — `scores.jsonl`, `summary.*` (all runs),
  `original-2026-10-21/facct.*`, and `tutorial-2026-10-11/jev_agreement.*`; no `summary.md`
  disagrees with its `scores.jsonl`.
- [x] **"Arabic cell" defined for the oracle allow-list** (phase_2) — by answer/expected script
  (contains Arabic-script code points); the byte-for-byte re-score guards named in the spec were
  updated.
- [x] **Moved headline numbers surfaced to the architect before merge** (phase_2 / pr gate) — packet
  below, re-sent at the pr gate including the #60 residual census.
- [x] **Copyright audit gate + full suite pass; no restricted-derived artifact committed/altered**
  (all phases) — audit OK; pipelines 640 pass / 2 skip, viewer vitest pass.

**Accepted known limitation (architect-approved 2026-10-29, per spec):** a literal word-level
zero-collision gate is infeasible; the fold merges 10 rare consonantal-skeleton minimal-pair buckets
(detailed under *Accepted collision residue* below). Accepted because rejecting either rule abandons
the fix, and the no-wrong-credit gate at scoring granularity catches any mis-credit on a committed
answer.

## Deviations from Plan

- **Containment-only pivot (phase_1).** The plan's first option (fold inside `normalize()`) was
  abandoned mid-phase_1 after the iter-2 consult proved a context-free `dagger→ا` fold un-credits the
  defective-spelling class. Pivoted to the containment-only / optional-ā design (architect-endorsed);
  the spec was updated to encode it. This is the central deviation and it is the reason the change is
  safe.
- **Doc paths (phase_3).** The plan named `pipelines/TUTORIAL.md` and `pipelines/CODE_WALKTHROUGH.md`;
  both actually live at the **repo root**. Edited the root files.
- **`first-run-2026-10-11` carries no rebaseline note** — it is English-only (digest ef837474),
  `scores.jsonl` untouched, 0 movers; the Arabic-only fold cannot affect it. Deliberate.
- **8-cell `ءَا↔آ` residual deferred to #60** (phase_2) — the architect chose option (B)
  (document + pin + defer the fold extension) on 2026-10-29 rather than widening the fold in this spec.

## Consultation Feedback

Per-phase 3-way consult (codex + claude; Gemini excluded — it cannot see the worktree, per
`.codev/config.json`). Full dispositions in `codev/projects/52-score-treat-uthmani-and-imla-i/*-rebuttals.md`.

### Specify Phase (Round 1)
- **codex — REQUEST_CHANGES** → **Addressed**: non-collision requirement and scope clarified in the spec.
- **claude — REQUEST_CHANGES** → **Addressed**: "alif madda آ already folds (NFKD); the real residue
  is standalone hamza ء"; the hamza rule was restated precisely and the asymmetric-drop pitfall
  (`أَرَءَيْتُمْ`) captured.

### Plan Phase (Rounds 1–2)
- **codex — REQUEST_CHANGES (both rounds)** → **Addressed/Rebutted**: the distinct-word-collision
  objection was reconciled by moving the no-wrong-credit gate to *scoring granularity* with a pinned
  residue allow-list (architect-ratified as the accepted known limitation), not a literal
  zero-collision rule.
- **claude — REQUEST_CHANGES (both rounds)** → **Addressed**: named which call-sites move
  (`_citation_candidates` vs the verdict; the `audit.py` `strip_script_marks` comment); dispositions
  written down for the pre-existing `سَأَلَ`/`سَالَ` merge.

### Implement phase_1 (Rounds 1–3)
- **codex — REQUEST_CHANGES (iter3)** → **Addressed**: direction-independence — the reference pattern
  is now matched against the answer in both its dagger-deleted and plene (`_answer_plene_form`) forms;
  reverse-direction + mixed-verse tests added.
- **claude — REQUEST_CHANGES (iter3)** → **Addressed**: (1) **blocking** whitespace-collapse bug in
  `_fold_containment_pattern` (newline-bearing hadith references) fixed; (2) diagnostic now sweeps
  both answer canonicalisations and pins the 10-bucket union residue; (3) triple-duplication root
  cause removed via `_normalize(text, *, fold=, plene=)`.

### Implement phase_2 (Rounds 1–3)
- **codex — APPROVE (iter3)** (REQUEST_CHANGES iters 1–2, all **Addressed**).
- **claude — REQUEST_CHANGES (iter3)** → **Addressed**: caught a real, self-corrected documentation
  error — the `ءَا↔آ` residual was understated as 1 cell; the correct census is **8 cells** with a
  tutorial-run asymmetry. Surfaced to the architect, who chose option (B): pre-registered the 8-cell
  set (`test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL`), filed **#60**, quantified the ~2–3 pt
  tutorial artifact. Non-blocking comments (probe `_LETTER_FOLD` divergence, short-citation fold)
  also addressed.

### Implement phase_3 (Round 1)
- **codex — APPROVE**, no issues.
- **claude — COMMENT** (non-blocking) → **Addressed**: cold-doc fold references tightened; folded in
  `dd35f56`.

### Review Phase — PR #62 consult (Round 1)
- **claude — APPROVE (HIGH)**: independently re-verified every quantitative claim (then-58 cells all
  `incorrect→correct`; SIM SHAs frozen *non-circularly* against the pre-#52 base; `facct`/`jev_agreement`
  recompute byte-identically; no ReDoS). Four non-blocking minors, all folded (see below).
- **codex — REQUEST_CHANGES (HIGH)**: "direction independence fails for mixed Imla'i references"
  (`fold_aware_contains("هَٰذَا ٱلْكِتَٰبَ","هذا الكتاب")==False`) → **Rebutted + claims narrowed**. This
  is the intended, documented boundary (carried by the reference's daggers; a mixed *daggerless* Imla'i
  reference cannot be reproduced by the two global answer forms) — raised by the codex Phase-2 consult
  and architect-endorsed. It only withholds credit, on 0 committed cells. Addressed by narrowing the
  spec criterion + PR body and pinning the boundary in
  `test_mixed_daggerless_imlai_reference_is_the_documented_boundary`. Stale "not yet wired" test
  docstring → **Addressed**.
- **Minors folded**: `outcomes.py` docstring `bounded_contains`→`fold_aware_contains` (**Addressed**);
  strict-grader scope paragraph added to the `fold_aware_contains` docstring (**Addressed**);
  `_single_citation_correct` verse-length-fold inheritance → **Rebutted** (verified no-op, 0 Arabic
  citations, guarded by the partition pin; citation predicate is a #39 decision); haiku ceiling signal
  → **N/A** (working-group note). Full dispositions in `52-review-iter1-rebuttals.md`.

### Review Phase — PR #62 architect integration review (Round 2)
Both PR consults REQUEST_CHANGES/HIGH; the architect verified hands-on and directed folding all six
items (none merged). All **Addressed**:
1. **Segmentation over-credit** (codex) → the whitespace flex in `_fold_containment_pattern` was
   confined to the long-ā join boundary (abutting an optional-long-ā atom), so a multiword reference
   no longer matches a distinct single word (منشر ≠ "من شر", "ك تب" ≠ كتب). **RE-VERIFIED all movers:
   1514 text cells across the 3 scores.jsonl runs unchanged; exp-ar dropped 2 cells** — surfaced to
   the architect, who approved the rebaseline (they were accidental over-credits bridging the #60
   `ءَآ↔آ` gap; see Appendix C). codex's negative tests added.
2. **False narrative in committed evidence** (claude) → a SECOND residual class (verse-number sign
   glued to the final word, U+06DD + Arabic-Indic digits) leaves tutorial `haiku/e2d74279aaf0`
   (4:176) verbatim-correct but uncredited. With it, haiku-off's three Qur'an misses are ALL scorer
   residuals, 0 genuine — so the entire haiku→haiku-search Qur'an gap is artifactual. Fixed the
   tutorial README prose, pinned the cell in `VERSE_NUMBER_RESIDUAL`, caveated the viewer test; the
   digit-strip code fix is deferred to #60.
3. **cite_passage call-site** (claude) → reverted `_single_citation_correct` to `bounded_contains`
   (citation EQUALITY, not the verse-length fold); candid comment kept, pointed at #39. No-op on
   committed evidence (0 Arabic citations).
4. **Public-API clarity** (codex) → `fold_aware_contains` documented as THE public text-retrieval
   containment contract; `bounded_contains` marked the legacy/equality floor (used only by citations
   + as the superset floor), with a "new text-retrieval analyses must use fold_aware_contains" warning.
5. **Stale Phase-1 docstring** (confirm) → fixed in `03a9443` (lands in this PR).
6. **Watch items to #60** → filed as additions to #60 (U+06DD digit-strip; `failureKind.ts` token
   arithmetic under whitespace-flexed credits); added the `score.py`→`probes.fold_arabic_letters`
   cross-pointer now. Full dispositions in `52-review-iter2-rebuttals.md`.

**Force-advance note.** phase_1 and phase_2 reached porch's `max_iterations` ceiling (3). The final
rebuttals show every remaining concern resolved in the force-advance commit (phase_1 `4a5c3a2`
predecessors; phase_2 `4a5c3a2`), not carried unresolved — verified against the rebuttal docs, per
the force-advance lesson in `lessons-critical.md`.

## Lessons Learned

### What Went Well
- **Strict-superset containment is the safe way to move a scoring headline.** Defining the predicate
  as `bounded_contains OR fold_match` makes `normalized=1 ⇒ contains=1` true by construction, so the
  change can only ADD credit — which shrank the rebaseline to one submetric family and made both the
  witness and the #48 rebase far simpler.
- **Keeping the fold out of shared `normalize()`** left generation's `ANCHOR_DIGEST` and the
  copyright-audit path untouched — the minimal, deliberate change the spec demanded.
- **Cross-builder thread reuse paid off**: aspir-48's thread surfaced the `summary.json`/`summary.md`
  "splice scar" (naive regeneration nulls the panel; the renderer emits extra columns that break the
  committed-summary guards) before I hit it.

### Challenges Encountered
- **The hard part was not a character fold — the long ā is lexically optional.** Imla'i writes it
  plene for some words (الكتاب, سبحان) but OMITS it for the defective-spelling class (هذا, ذلك,
  الرحمن, لكن). A context-free `dagger→ا` fold therefore *un-credits* the defective class — the
  inverse of the spec's purpose; in prototyping it flipped two verbatim-correct committed cells to
  incorrect. Optionality cannot live in a canonical string, so it had to live in the containment
  regex. Resolved by the containment-only pivot.
- **A competing implementation (#57/#58) merged to `main` mid-flight.** Reconciled to the reviewed
  containment-only design (detail below); the witness re-ran byte-identically over the post-#57/#58
  base, so the baseline never moved.

### What Would Be Done Differently
- **Census the residual before claiming its size.** The `ءَا↔آ` residual was first documented as "1
  cell / no bias"; the claude phase-2 iter-3 consult proved it is 8 cells with a tutorial asymmetry.
  A proper detector (delete a hamza immediately before an alef, then run the optional-ā fold) should
  have been run before writing any count.

### Methodology Improvements
- The ASPIR force-advance at `max_iterations` is safe here only because the rebuttals genuinely
  resolved the concerns; a reviewer reading `status.yaml` alone cannot tell a resolved force-advance
  from an unresolved one. Surfacing the final-iteration rebuttal summary into the review (as done
  here) closes that gap — worth making a protocol habit.

## Architecture Updates

Governance facts routed by tier (Spec 987), committed in phase_3:

- Routed: **hot** — `arch-critical.md` scoring bullet — added the one-line Spec 52 fact ("Arabic
  orthography folds in the CONTAINMENT path only; `fold_aware_contains` is a strict SUPERSET;
  `normalize()`/equality submetrics stay BYTE-STABLE; witnessed by `test_orthography_rebaseline.py`"),
  trimmed to a pointer into cold arch.md to respect the cap.
- Routed: **cold** — `arch.md` § score.py — full fold record (rules, the 5 call-sites, the
  optional-ā `ا?` mechanism, the sanctioned-rebaseline procedure).
- Routed: **cold** — `arch.md` — the facct predicate-name reference updated to `fold_aware_contains`.
- No hot-tier displacement was required beyond the trim-to-pointer above; the hot scoring bullet
  absorbed the fact within the existing entry.

## Lessons Learned Updates

- Routed: **hot** — `lessons-critical.md` — "A context-free Arabic orthography fold is provably
  insufficient" (the Uthmani↔Imla'i equivalence must be position-aware and live in a scoring-only
  normaliser, never shared `normalize()`, to avoid question-set/generator drift; Spec 52;
  `test_orthography_rebaseline.py`). To stay under the cap, the two viewer gotchas were consolidated
  into one entry (hot file now 11 entries).
- Routed: **cold** — `lessons-learned.md` (Scoring & evaluation) — the strict-superset rebaseline
  technique and the splice-scar avoidance, with the residual-census lesson.

## Flaky Tests

No flaky tests encountered. The 2 skips in the pipelines suite are pre-existing and unrelated
(`test_edition_index.py`, `test_original_run_regression.py` environment-gated cells).

## Follow-up Items

- **#60** (filed) — the follow-up now carries **two pre-registered under-credit residual classes**,
  both strict-superset-safe (never a wrong credit) and both the follow-up's ready-made before/after
  oracle:
  - **Hamza-alef `ءَا ↔ آ`** (`HAMZA_ALEF_RESIDUAL`) — extend the fold to equate word-initial Uthmani
    hamza-then-alef with Imla'i alef-madda, plus the `ىٰ`↔bare-maqsura case. **10 committed cells**
    (the original 8 plus the 2 exp-ar `retrieve_quote-317f7f727f3c` cells exposed by the round-2
    whitespace tightening). **Asymmetric** on both the tutorial run (haiku-search «ءَا» credited,
    haiku «آ» not → the *entire* haiku→haiku-search Qur'an "search lift" is this + the verse-number
    residual, not retrieval) and the exp A/B (en «ءَآ» credited, ar «آ» not → the one exp
    cross-condition flip, ar 92.9% vs en 96.4%).
  - **Verse-number gluing** (`VERSE_NUMBER_RESIDUAL`, PR-review round 2) — a trailing U+06DD +
    Arabic-Indic verse number fused to the final word breaks the word boundary (tutorial
    `haiku/e2d74279aaf0`, 4:176, verbatim-correct). The fix (strip a trailing verse-number before the
    boundary match) is deferred to #60.
  - **Watch items filed to #60**: the digit-strip code fix above; `failureKind.ts` token arithmetic
    under whitespace-flexed credits.
  Architect-approved defer (option B), 2026-10-29.
- **#39** — the Arabic-instruction subset this spec unblocks; a native-speaker review of the Arabic
  scaffolds (#41) should precede any scaled run (Nancy's ~20% AI-translation-subtlety caution).
- **Digraph vs bare maqsura** (conservative, 0 committed cells) — a reference `ىٰ` digraph does not
  match an answer's bare maqsura; only ever withholds credit. Logged for #39's scale, not widened now
  (broadening the digraph atom risks new collisions).

---

## Appendix A — Moved numbers (Phase 2 rebaseline, witnessed over the post-#48 + post-#51 baseline)

Captured 2026-10-29 by re-scoring each run's committed answers with the wired scorer (dry run,
nothing written to `runs/` until the architect saw these). **56 moved cells total, every one
`0→1` (`contains_reference`/`correct`), `incorrect→correct`; zero losses, zero coverage change,
zero similarity drift** (the `(exact, normalized, token_f1)` projection SHA is byte-identical on
all five score files — the frozen oracle holds). [Was 58: the PR-review whitespace tightening
(round-2 item 1) removed 2 accidental exp-ar over-credits — see Appendix C.]

| Run | n | accuracy before → after | coverage | moved cells |
|---|---|---|---|---|
| tutorial-2026-10-11 (retrieve_quote) | 400 | 86.0% → **93.2%** | 69.5% (unchanged) | 20 |
| original-2026-10-21 (overall) | 1428 | 47.7% → **49.1%** | 76.6% (unchanged) | 15 |
| — original complete_unit | 357 | 32.8% → 35.1% | 75.1% | 6 |
| — original retrieve_quote | 357 | 38.8% → 45.5% | 37.5% | 9 |
| — original cite_passage / verify_source | — | unchanged | unchanged | 0 |
| first-run-2026-10-11 | 400 | unchanged | unchanged | 0 |

**exp-arabic-prompts-2026-10-29** (the motivating A/B, scored via its own `analyze.py` over the
normalized-answers copy): pre-fold en 82.1% (sol) / 78.6% (sonnet), ar 71.4% / 71.4%, **5 cells
flipped en→ar (all orthographic)**; post-fold **en 96.4% / ar 92.9%, with ONE residual
cross-condition flip** — `retrieve_quote-317f7f727f3c` (Q27:59), en-correct→ar-incorrect for both
models, a `ءَآ↔آ` hamza-alef residual (#60), NOT a retrieval difference. So the ~8–11pt
Arabic-prompt drop resolves down to a single pre-registered residual cell — the direct proof of the
fix and the prerequisite clearance for #39. (en 9 movers, ar 12 movers; the 2 removed ar movers were
the accidental over-credits caught by the round-2 whitespace tightening — Appendix C.)

**Coverage never moves**: the shared `outcomes.classify_refusal` edit cannot independently
reclassify a committed cell under the default graders (a contained cell already has `correct=1`),
so no answered↔refused movement occurred in any committed benchmark run.

### Hand-verification method (the no-wrong-credit gate)

Every one of the 58 moved cells was inspected against its reference: each is the **same verse /
hadith reproduced word-for-word in Imla'i orthography** (plain alef for hamzat-wasl ٱ, plene or
omitted dagger-alif ـٰ, dotted ي for dotless ى, one-word↔two-word spacing, ZWNJ/editorial marks),
never a different text. Quantitative backstop: the shortest moved reference is 8 words (median 17,
max 58), far above the single-word collision residue — no short-fragment false match is possible at
these lengths. No cell lost credit; no similarity submetric moved.

**Independent corroboration (regenerated `jev_agreement`, tutorial).** Recomputing the Jev
judge-vs-deterministic agreement against the rebaselined scores: on the **containment** column
agreement rose 0.9325 → **0.9825** (both 239 → 259, **judge-only 27 → 7, deterministic-only 0
throughout**). The Jev judge had independently marked 20 of the fold's newly-credited cells as
matches, and the fold credited nothing the judge rejected (deterministic-only stays 0) — an
independent no-wrong-credit corroboration, exactly the 27 orthographic near-misses this fold
targeted. The refusal column is unchanged by Spec 52 (0.985, 6 deterministic-only — the Spec-48
cells). (claude phase-2 consult flagged the stale artifact; regenerated + folded.)

## Appendix B — Accepted collision residue (known limitation, architect-approved 2026-10-29)

10 QUL word-buckets where a necessary fold merges genuinely distinct words sharing a consonantal
skeleton; pinned in `test_arabic_orthography_fold.py`:
- hamza (ء→ا): سواء/سوء, جزاء/جزء, وراء/ورءا, ملأ/ملء, شىء/شيـٔا, برىء/بريـٔا
- maqsura (ى→ي): نبى/نبّئ, قرى/قرئ, أمرى/امرئ
- optional-long-ā branch: رَأَىٰ/رَءَا

Benign at verse-length references; the no-wrong-credit gate catches any that would mis-credit a
committed answer.

**Under-credit residual class 1 — hamza-alef `ءَا ↔ آ` — [#60].** The fold does NOT cover the
word-initial **hamza-alef ءَا (Uthmani) ↔ alef-madda آ (Imla'i)** equivalence: `score_normalize`
renders e.g. Q14:34 «وَءَاتَىٰكُم» vs «وَآتَاكُم» as `وااتىكم` vs `واتاكم` (the `ء→ا` rule yields two
alefs where madda yields one), so they do not match. **10 committed cells** — the original 8 plus 2
exp-ar cells on Q27:59 that the round-2 whitespace tightening EXPOSED (the old over-permissive `\s*`
had accidentally bridged them via the plene form; see Appendix C). Pre-registered by exact id in
`test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL`:
- tutorial: `haiku/retrieve_quote-1d74fc87541b` (8:52), `haiku/retrieve_quote-a8df3e43d35d` (2:285)
- original: `haiku` & `opus` `/retrieve_quote-8c4ce779621f` (14:34)
- exp-ar & exp-en: `sonnet` & `sol` `/retrieve_quote-8c4ce779621f` (14:34)
- exp-ar: `sonnet` & `sol` `/retrieve_quote-317f7f727f3c` (27:59 «ءَآللَّهُ») — EN stays credited

All are under-credits (the answer IS the correct verse; the committed rebaseline stays a strict
superset — nothing is wrongly credited). Two asymmetries fall out of it: (a) on the tutorial run
`haiku-search` wrote «ءَا» (credited) while `haiku` wrote «آ» (uncredited); combined with residual
class 2 below, **the entire haiku 88%→92% Qur'an "search lift" is scorer residual, not retrieval**;
(b) in the exp A/B the EN answers wrote «ءَآللَّهُ» (credited) while the AR scaffold elicited «آللَّهُ»
(uncredited) — the one exp cross-condition flip (ar 92.9% vs en 96.4%). NOT fixed here — the `ءَا↔آ`
(and `ىٰ`↔maqsura) extension needs its own collision analysis; deferred to **[#60]**.

**Under-credit residual class 2 — verse-number gluing — [#60].** A verbatim-correct āyah left
uncredited because a trailing **verse-number sign is fused to the final word** (U+06DD end-of-āyah +
Arabic-Indic digits, e.g. `…عليم۝١٧٦`), breaking the word-bounded containment's trailing boundary.
A tokenisation gap, distinct from class 1. Tutorial `haiku/retrieve_quote-e2d74279aaf0` (4:176) — the
third of haiku-off's three Qur'an misses, all scorer residuals. Pinned in `VERSE_NUMBER_RESIDUAL`;
the digit-strip fix is deferred to **#60** (not a Spec 52 code change). Both classes architect-
approved to defer, 2026-10-29. This is the honest boundary of the fold.

**Directionality boundary.** The per-position optional-ā is carried by the *reference's* daggers, so
the fold matches any answer orthography (plene/defective/mixed) against a reference in either
reproduction direction — the dual answer form (`score_normalize` + `_answer_plene_form`) is
load-bearing (14 committed cells match only via the plene form, where the answer wrote a dagger the
reference wrote as a full alef). The one case it does NOT fully cover is a reference *itself* written
in mixed Imla'i (defective `هذا` + plene `الكتاب`, with no daggers to mark the optional positions):
the two global answer forms cannot reproduce a per-word mix. This never arises on the committed
corpora — references are always the corpus orthography (Uthmani QUL for the Qur'an, carrying the
daggers), and #39's Arabic subset scores against the same corpus — so the earlier "direction-
independent" phrasing is narrowed to this accurate statement. (codex phase-2 consult, folded.)

**Phase-2 "Arabic-cell partition count" deliverable.** It landed as BOTH the exact per-cell
mover-identity sets (strictly stronger for moved cells) AND an explicit
`test_arabic_cell_partition_pinned` (letters-only `_is_arabic_letter`, pinning arabic-expected and
arabic-either counts per run) — the latter catches a corpus/question-set change that alters the
fold's domain even when no cell moves. (codex phase-2 consult asked for the count; claude noted the
mover-sets subsumed it — kept both.)

## Appendix C — Reconciliation with the competing #57 / #58 implementation

While Phase 2 was executing, Jonathan Karr merged a competing #52 implementation (PR #57, `154e0ef`)
directly to `main`, then a "fix double code branch" commit (`08f43b8`) and PR #58 (which merged this
builder's Phase-1 branch). Waleed greenlit reconciliation; the architect's directive was to converge
to the reviewed containment-only design as the single source of truth.

**What converged, and why mine prevailed on the evidence.** #57's approach folded the orthography
inside `normalize()` (`strip_script_marks`), MATERIALISING the dagger-alif as a full alef. That is
the exact approach this spec's Phase-1 review rejected: it un-credits the defective-spelling class,
and #57's own test encoded the defect — it asserted `normalize("2:2") == "ذالك الكتاب…"` (Uthmani
ذٰلك → **ذالك**), yet Imla'i writes **ذلك**, so the fold would mark the defective class *wrong*. It
also moves the `normalized` similarity tier (and would move the generation ANCHOR digest and the
audit path). By the time I rebased, `08f43b8` had already resolved the "double branch" toward THIS
design — frozen `normalize()`, my symmetric `fold_arabic_orthography`, `score_normalize` /
`fold_aware_contains` / the optional-`ا?` containment pattern, and the original skeleton
`test_normalize_nonlatin` (his materialise-fold assertions reverted) — leaving only the wiring
(`contains_reference` still on `bounded_contains`) for me to supply. **Kept from #57:** Jonathan's
unrelated `outcomes.py` `_INTRODUCER` regex-escape fix (`\-`→`-`, removes a `SyntaxWarning`).

**Witness unchanged by the rebase.** Re-run over the post-#57/#58/#51 base, the 58-cell transform
is byte-identical to the pre-reconciliation packet (SIM frozen on all 5 score files, coverage
frozen, exp all-four 96.4% / 0 flips). Committed run artifacts were untouched by #57/#58, so the
baseline never moved.

**A clean cross-rebaseline composition (nice anecdote).** One tutorial cell —
`haiku-search retrieve_quote-e2d74279aaf0` — is an honest decline that then delivers the correct
4:176 āyah from memory in near-Imla'i orthography. Its scoring journey is `refused` (pre-#48) →
`incorrect` (#48 recognised the delivery but it was not byte-exact) → `correct` (#52 recognises the
delivery IS the verse in a folded orthography). The composition is correct and is now pinned
explicitly in `test_refusal_rebaseline.py` (re-pinned to current-state invariants per the
architect's stacking-robustness ruling) and `test_contains_reference_rebaseline.py`.
