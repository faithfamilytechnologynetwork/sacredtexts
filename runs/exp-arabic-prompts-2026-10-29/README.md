# Experiment: does asking the Qur'an questions *in Arabic* change the answers?

**Date**: 2026-10-29 · **Requested by**: the maintainer · **Status**: complete, one-shot A/B.
**Scores rebaselined under the Spec-52 orthography fold** (see *Scoring* and the two results
sections below) — the committed `scores-{ar,en}.jsonl` now reflect the current scorer.

## Design

The 28 Qur'an questions from the committed `runs/original-2026-10-21` suite (ids preserved),
in two conditions:

- **en** (`questions-en.jsonl`): the original English prompt scaffolds, verbatim.
- **ar** (`questions-ar.jsonl`): only the scaffold translated to Arabic
  (`build_questions.py`; every English prompt is template-parsed and reconstructed
  byte-exactly as an oracle before substitution). Quoted passages, citations, and the
  Yes/No example form are byte-identical across conditions. Name mapping collapses the
  English spelling axis (Quran/Koran/Qur'an → القرآن; the Holy Qur'an → القرآن الكريم).

**Panel** (`models.yaml`): `anthropic/claude-sonnet-5.5` and `openai/gpt-6.1-sol` via
OpenRouter, temperature pinned to 0, max_tokens 4096, no tools, UNPRICED. 112 cells,
zero failures.

**Scoring** (`analyze.py`): the committed scorer (`score_file`), via a repo-relative import so it
always uses this checkout's scorer. As of Spec 52 that scorer treats Uthmani and Imla'i
orthographies as equivalent in the containment predicate (`fold_aware_contains`). The ar
condition is still scored on a normalized *copy* of the answers (`answers-ar-normalized.jsonl`):
Arabic-Indic digits folded to ASCII, and (verify_source only) a leading «نعم»/«لا» mapped
to Yes/No, since the leading-stance Yes/No parse is English-only by contract. 14 of 56 ar answers
were transformed. Raw answers are untouched in `answers-ar.jsonl`.

## Results (current — under the Spec-52 orthography fold)

| condition | model  | accuracy | coverage | ✓ / ∅ / ✗ |
|-----------|--------|---------:|---------:|-----------|
| en | sol (gpt-6.1-sol)      | 96.4% | 100% | 27 / 0 / 1 |
| en | sonnet (claude-5.5)    | 96.4% | 100% | 27 / 0 / 1 |
| ar | sol                    | 92.9% | 100% | 26 / 0 / 2 |
| ar | sonnet                 | 92.9% | 100% | 26 / 0 / 2 |

**The ~8–11-point Arabic drop (next section) resolves down to a SINGLE pre-registered residual
cell.** en reaches 96.4% (27/28), ar 92.9% (26/28): exactly **one question flips between conditions**
— `retrieve_quote-317f7f727f3c` (Q27:59), en-correct → ar-incorrect for both models — and it is a
`ءَآ↔آ` hamza-alef residual (#60), **not** a retrieval difference. Per task otherwise: cite_passage
7/7, verify_source 7/7, complete_unit 7/7 everywhere. So the drop was almost entirely a scorer
artifact, removed by the fold except for this one known residual — the direct evidence that clears
the #39 prerequisite.

**Two residual cells, both hamza-alef `ءَآ↔آ` (Uthmani hamza-then-alef vs Imla'i alef-madda), NOT
content errors**, both deferred to **#60** and pinned in
`test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL`:
- **`retrieve_quote-8c4ce779621f` (Q14:34)** — incorrect in all four cells (both models, both
  conditions). *Symmetric*, so it does **not** bias the en/ar comparison. Uthmani «وَءَاتَىٰكُم» vs
  Imla'i «وَآتَاكُم»: `score_normalize` renders `وااتىكم` vs `واتاكم`, a one-alef difference the
  hamza→alef rule doesn't bridge.
- **`retrieve_quote-317f7f727f3c` (Q27:59)** — the *asymmetric* one, and the single cross-condition
  flip. The en answers wrote «ءَآللَّهُ» (credited) while the AR scaffold elicited Imla'i «آللَّهُ»
  (uncredited) → en correct, ar incorrect. Same `ءَآ↔آ` phenomenon. This mirrors the tutorial run's
  haiku/haiku-search asymmetry (see that run's README). **It was accidentally credited before the
  PR-review whitespace tightening** (an over-permissive `\s*` was bridging the uncovered gap via the
  plene form); the tightened predicate correctly leaves it uncredited, which is why ar is 92.9% here
  and not 96.4%.

## Pre-fold finding (historical — the motivation for Spec 52)

**This is the finding that motivated Spec 52 and this PR.** Before the orthography fold, the same
112 answers scored:

| condition | model  | accuracy | coverage | ✓ / ∅ / ✗ |
|-----------|--------|---------:|---------:|-----------|
| en | sol (gpt-6.1-sol)      | 82.1% | 100% | 23 / 0 / 5 |
| en | sonnet (claude-5.5)    | 78.6% | 100% | 22 / 0 / 6 |
| ar | sol                    | 71.4% | 100% | 20 / 0 / 8 |
| ar | sonnet                 | 71.4% | 100% | 20 / 0 / 8 |

(git history holds the pre-fold `scores-{ar,en}.jsonl`.) Then: all movement was in
retrieve_quote (en: sol 3/7, sonnet 1/7 → ar: 0/7 both); cite_passage and verify_source were
7/7 everywhere; complete_unit 6–7/7.

**5 of 56 cells flipped, all en-correct → ar-incorrect — all the same phenomenon, none a content
error.** Hand inspection of every flip: the Arabic-prompted answer is the right verse,
word-for-word, but written in standard modern (Imla'i) orthography — plain alef ا, يا بني as two
words, dotted ي — while the corpus (QUL Uthmani) and the English-prompted answers use Uthmani
orthography: hamzat-wasl ٱ, dagger alef ـٰ, dotless ى. Example (37:102): en answer reproduces
«ٱلسَّعْىَ … يَـٰبُنَىَّ» byte-exactly; ar answer gives «السَّعْيَ … يَا بُنَيَّ». `normalize()`
folds alef-wasla and deletes marks but could not equate dagger-alef ↔ full alef or ى ↔ ي, so
these scored incorrect. Spec 52 moves exactly that equivalence into the containment predicate.

## Conclusions

1. **Knowledge/content: no detectable difference.** Both models retrieve, complete, cite, and
   verify the Qur'an equally well when asked in Arabic; **no content-level flip** in either
   direction on this sample — true both before and after the fold (the one post-fold flip is an
   orthography residual, not content).
2. **Real behavioral difference: output orthography follows prompt language.** English prompts
   elicit faithful Uthmani-script reproduction; Arabic prompts switch both models to standard
   Imla'i orthography — an ~8–11-point *measured* accuracy drop that was **almost entirely a scorer
   artifact**. Spec 52's Uthmani↔Imla'i fold removes it down to a single residual cell (en 96.4% /
   ar 92.9%; the one remaining ar flip is the `ءَآ↔آ` residual deferred to **#60**).
3. **Implication for #39 (Arabic-instruction subset)**: the scorer fix this experiment called for
   has landed (Spec 52). Arabic-prompted runs are no longer systematically under-credited for
   orthography, so #39 can run at scale without that bias. A narrow residual remains (word-initial
   `ءَا`↔`آ`, §Results) — and here it IS mildly asymmetric (one cell, Q27:59, credits en but not ar),
   so #39 should land the fold extension (**#60**) first; the same pattern is also asymmetric on the
   tutorial run's haiku vs haiku-search contrast.

**Caveats**: n=7 per task per model, one seed, temperature 0, two models, scaffold translation
written by the architect (not a native-speaker-reviewed instrument). Directional evidence only.

## Appendix: the prototype fold that preceded the production scorer (2026-10-29)

Before the production scorer existed, a quick context-free prototype fold (applied **before**
`normalize()`: dagger alif → full alif, hamzat al-wasl → alif, alif madda → alif, standalone
hamza dropped, ى → ي, whitespace removed) gave en 52/56 and ar 52/56 with **four** residual
cells — Q10:50 (`retrieve_quote-5d482247f058`) and Q14:34 (`retrieve_quote-8c4ce779621f`) × both
models — attributed to hamza seating and the ى+dagger digraph. The **production** scorer (Spec 52,
`fold_aware_contains`: containment-only, with the long-ā alef *optional* rather than materialized,
so the defective-spelling class هذا/الرحمن is not broken) is strictly better: it recovers Q10:50
in both conditions, leaving only the single Q14:34 `ءَا`↔`آ` residual documented above (54/56 each
condition). The prototype's "materialize dagger→alif" step was abandoned precisely because it
un-credits the defective-spelling class; see the spec for why the equivalence lives in the
containment regex, not in a canonical string.
