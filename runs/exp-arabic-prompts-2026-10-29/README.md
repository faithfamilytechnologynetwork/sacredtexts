# Experiment: does asking the Qur'an questions *in Arabic* change the answers?

**Date**: 2026-10-29 · **Requested by**: Waleed · **Status**: complete, one-shot A/B

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

**Scoring** (`analyze.py`): the committed scorer (`score_file`), untouched. The ar
condition is scored on a normalized *copy* of the answers (`answers-ar-normalized.jsonl`):
Arabic-Indic digits folded to ASCII, and (verify_source only) a leading «نعم»/«لا» mapped
to Yes/No, since the leading-stance parse is English-only by contract. 14 of 56 ar answers
were transformed. Raw answers are untouched in `answers-ar.jsonl`.

## Results

| condition | model  | accuracy | coverage | ✓ / ∅ / ✗ |
|-----------|--------|---------:|---------:|-----------|
| en | sol (gpt-6.1-sol)      | 82.1% | 100% | 23 / 0 / 5 |
| en | sonnet (claude-5.5)    | 78.6% | 100% | 22 / 0 / 6 |
| ar | sol                    | 71.4% | 100% | 20 / 0 / 8 |
| ar | sonnet                 | 71.4% | 100% | 20 / 0 / 8 |

Per task: cite_passage 7/7 and verify_source 7/7 for **both models in both languages**
(the نعم/لا answers parse cleanly after the documented mapping); complete_unit 6–7/7
everywhere; all movement is in retrieve_quote (en: sol 3/7, sonnet 1/7 → ar: 0/7 both).

**5 of 56 cells flipped, all en-correct → ar-incorrect — and all five are the same
phenomenon, none is a content error.** Hand inspection of every flip: the Arabic-prompted
answer is the right verse, word-for-word, but written in standard modern (Imla'i)
orthography — plain alef ا, يا بني as two words, ي — while the corpus (QUL Uthmani) and
the English-prompted answers use Uthmani orthography: hamzat-wasl ٱ, dagger alef ـٰ,
dotless ى. Example (37:102): en answer reproduces «ٱلسَّعْىَ … يَـٰبُنَىَّ» byte-exactly;
ar answer gives «السَّعْيَ … يَا بُنَيَّ». `normalize()` folds alef-wasla and deletes
marks but cannot equate dagger-alef ↔ full alef or ى ↔ ي, so these score incorrect.

## Conclusions

1. **Knowledge/content: no detectable difference.** Both models retrieve, complete,
   cite, and verify the Qur'an equally well when asked in Arabic; zero content-level
   flips in either direction on this sample.
2. **Real behavioral difference: output orthography follows prompt language.** English
   prompts elicit faithful Uthmani-script reproduction; Arabic prompts switch both
   models to standard Imla'i orthography — an ~8–11-point *measured* accuracy drop
   that is entirely a scorer artifact.
3. **Implication for #39 (Arabic-instruction subset)**: before running it at scale, the
   scorer needs an Uthmani↔Imla'i orthography fold (or Jev equivalence adjudication,
   cf. the 27 orthographic near-misses in the Spec-21 cross-check); otherwise
   Arabic-prompted runs are systematically under-credited.

**Caveats**: n=7 per task per model, one seed, temperature 0, two models, scaffold
translation written by the architect (not a native-speaker-reviewed instrument).
Directional evidence only.

## Follow-up: orthography-fold re-score (2026-10-29)

Re-scoring both conditions under a small Uthmani↔Imla'i fold applied **before**
`normalize()` (dagger alif → full alif, hamzat al-wasl → alif, alif madda → alif,
standalone hamza dropped, ى → ي, whitespace removed; containment match) is decisive:

- **en: 45 strict-correct + 7 fold-recovered = 52/56**
- **ar: 40 strict-correct + 12 fold-recovered = 52/56**

Identical scores, and the **identical four residual cells** (two verses ×
both models × both conditions): retrieve_quote-5d482247f058 (10:50) and
retrieve_quote-8c4ce779621f (14:34). By hand inspection those four are the same
phenomenon via two rules the quick fold leaves out — hamza seating
(أَرَءَيْتُمْ ↔ أَرَأَيْتُمْ) and the ى+dagger-alif digraph (أَتَىٰكُمْ ↔ أَتَاكُمْ).
So every one of the 112 answers contains the content-correct verse; no
content-level difference between prompt languages survives orthographic
equivalence. Note the fold rescues **English-prompted** cells too (7), i.e. even
en-condition strict accuracy is partly orthographic luck — the production fix
(#39 prerequisite) belongs in the scorer, not in prompt engineering.
(Ordering gotcha for implementers: `normalize()` deletes the dagger alif as a
combining mark, so the dagger-alif → full-alif fold must run before it.)
