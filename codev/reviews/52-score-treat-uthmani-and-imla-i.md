# Review: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

**Spec**: [codev/specs/52-score-treat-uthmani-and-imla-i.md](../specs/52-score-treat-uthmani-and-imla-i.md) ·
**Plan**: [codev/plans/52-score-treat-uthmani-and-imla-i.md](../plans/52-score-treat-uthmani-and-imla-i.md)

> Draft started during the Phase-2 hold (#48 merges first). Phase-1 sections are final; the
> moved-numbers table and Phase-2/3 notes are filled when the rebaseline runs.

## What shipped

A model that reproduces a Qur'anic verse correctly but in a different orthography than the QUL
Uthmani corpus (the common case when prompted in Arabic — #39) is now credited. The equivalence is
implemented **entirely in the containment predicate** (`fold_aware_contains`), as a strict superset
of the previous `bounded_contains`: `normalize()` and the similarity submetrics
(`exact`/`normalized`/`token_f1`) are byte-for-byte unchanged, so the only scores that move are
`contains_reference`, the headline `correct`, and `outcome`.

The fold: symmetric letter folds (standalone hamza ء→ا, bare alef-maqsura ى→ي) are canonical in
`score_normalize`; the long ā (dagger-alif ـٰ and the ىٰ digraph) is matched as an **optional** alef
(`ا?`) with whitespace-flex between Arabic letters, word-bounded, and direction-independent (the
reference pattern is matched against the answer in both its dagger-deleted and plene forms).

## Lessons learned

- **The hard part was NOT a character fold — it was that the long ā is lexically optional.** Standard
  Imla'i writes the long ā as a full alef for the plene class (الكتاب, سبحان) but OMITS it for the
  defective-spelling (رسم ناقص) class (هذا, ذلك, الرحمن, لكن). A context-free `dagger→ا` fold
  therefore *un-credits* the defective class — it would mark `هذا`/`الرحمن` wrong, the inverse of
  the spec's purpose, and in prototyping it flipped two verbatim-correct committed tutorial cells to
  incorrect. Optionality cannot live in a canonical string, so it had to live in the containment
  regex. **Lesson: an orthographic "equivalence" that is present-on-one-side / absent-on-the-other
  is not a fold; it is an optional match.**
- **A strict-superset containment is the safe way to change a scoring headline.** Defining the new
  predicate as `bounded_contains OR fold_match` makes `normalized=1 ⇒ contains=1` true by
  construction, guarantees the change only ADDS credit, and shrinks the rebaseline to one submetric
  family — which also made the witness and the #48 rebase far simpler.
- **Put a fold in the scoring-comparison path, not the shared `normalize()`.** `generate.py` and
  `editions.py` share `normalize()`; folding there would have moved the committed question-set
  `ANCHOR_DIGEST` and touched the copyright-audit path. Keeping it out of `normalize()` left
  generation and the audit untouched.
- **Context-free Arabic folds are provably insufficient** and some necessary folds merge rare
  distinct-word minimal pairs (the 10-bucket residue below). The honest gate is no *wrong credit*,
  enforced by hand-verifying every moved cell at scoring granularity, with the vocab residue pinned
  as a drift-detecting allow-list — not a literal zero-collision rule.
- **Cross-builder thread reuse paid off**: aspir-48's thread surfaced the summary.json/summary.md
  "splice scar" (naive regeneration nulls the panel; the renderer emits extra columns that break the
  committed-summary guards) before I hit it.

## Accepted collision residue (known limitation, architect-approved 2026-10-29)

10 QUL word-buckets where a necessary fold merges genuinely distinct words sharing a consonantal
skeleton; pinned in `test_arabic_orthography_fold.py`:
- hamza (ء→ا): سواء/سوء, جزاء/جزء, وراء/ورءا, ملأ/ملء, شىء/شيـٔا, برىء/بريـٔا
- maqsura (ى→ي): نبى/نبّئ, قرى/قرئ, أمرى/امرئ
- optional-long-ā branch: رَأَىٰ/رَءَا

Benign at verse-length references; the no-wrong-credit gate catches any that would mis-credit a
committed answer.

**Under-credit residual (distinct from the collisions above) — [#60].** The fold does NOT cover the
word-initial **hamza-alef ءَا (Uthmani) ↔ alef-madda آ (Imla'i)** equivalence: `score_normalize`
renders e.g. Q14:34 «وَءَاتَىٰكُم» vs «وَآتَاكُم» as `وااتىكم` vs `واتاكم` (the `ء→ا` rule yields two
alefs where madda yields one), so they do not match. **This is 8 committed cells, not one** (a
census-corrected count — the earlier "one cell / no bias" claim was wrong; caught by the claude
phase-2 iter-3 consult and self-corrected). Pre-registered by exact id in
`test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL`:
- tutorial: `haiku/retrieve_quote-1d74fc87541b` (8:52), `haiku/retrieve_quote-a8df3e43d35d` (2:285)
- original: `haiku` & `opus` `/retrieve_quote-8c4ce779621f` (14:34)
- exp-ar & exp-en: `sonnet` & `sol` `/retrieve_quote-8c4ce779621f` (14:34)

All are under-credits (the answer IS the correct verse; the committed rebaseline stays a strict
superset — nothing is wrongly credited). But the two tutorial cells are **asymmetric**: on the same
verse `haiku-search` wrote «ءَا» (credited) while `haiku` wrote «آ» (uncredited), so **~2–3 pts of the
committed haiku 88% → haiku-search 92% "search lift" is this orthography residual, not retrieval, and
`haiku` is slightly under-credited.** NOT fixed here — the `ءَا↔آ` (and `ىٰ`↔maqsura) extension needs
its own collision analysis; deferred to **[#60]** with the pinned set as its ready-made oracle
(architect-approved defer 2026-10-29). This is the honest boundary of the fold.

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

**Digraph vs bare maqsura (conservative, flagged for #39).** A reference `ىٰ` digraph compiles to the
optional long-ā alef (`ا?`) only, so a *reference* long-ā written as a digraph does not match an
*answer* that wrote a bare maqsura/ya there (`علىٰ` ref vs `على`/`علي` answer). Conservative (only
ever withholds credit, never grants a wrong one), affects **0 committed cells**, but could
under-credit at #39's scale; logged and not widened now (broadening the digraph atom risks new
collisions — its own analysis). (claude phase-2 consult.)

**Phase-2 "Arabic-cell partition count" deliverable.** It landed as BOTH the exact per-cell
mover-identity sets (strictly stronger for moved cells) AND an explicit
`test_arabic_cell_partition_pinned` (letters-only `_is_arabic_letter`, pinning arabic-expected and
arabic-either counts per run) — the latter catches a corpus/question-set change that alters the
fold's domain even when no cell moves. (codex phase-2 consult asked for the count; claude noted the
mover-sets subsumed it — kept both.)

## Consult trail (Phase 1)

Spec: 1 iteration (codex + claude, both REQUEST_CHANGES → folded). Plan: 2 iterations. Implement
phase_1: 3 iterations — iter2 caught the blocking dagger defect (→ the containment-only pivot,
architect-endorsed); iter3 caught direction-independence, a dead-fold-branch whitespace bug for
newline-bearing hadith references, and the diagnostic's blind spot (now sweeps both answer forms).

## Moved numbers (Phase 2 rebaseline, witnessed over the post-#48 + post-#51 baseline)

Captured 2026-10-29 by re-scoring each run's committed answers with the wired scorer (dry run,
nothing written to `runs/` until the architect saw these). **58 moved cells total, every one
`0→1` (`contains_reference`/`correct`), `incorrect→correct`; zero losses, zero coverage change,
zero similarity drift** (the `(exact, normalized, token_f1)` projection SHA is byte-identical on
all five score files — the frozen oracle holds).

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
flipped en→ar (all orthographic)**; post-fold **all four conditions 96.4%, 0 cross-condition
flips** — the ~8–11pt Arabic-prompt accuracy drop is fully resolved, which is the direct proof of
the fix and the prerequisite clearance for #39. (en 9 movers, ar 14 movers.)

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

## Reconciliation with the competing #57 / #58 implementation

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

## Flaky tests

None observed.
