# FAccT preview — qwen3-32b

What these answers are allowed to mean. Accuracy is correct divided by correct plus incorrect. A refusal is left out of accuracy and counted in coverage. `token_f1` is the strict wording overlap. `token_f1_base` folds script and spelling differences and is a diagnostic, not the headline.

This file is a preview of the answers on disk. It is not the FAccT card. `python -m sacredbench facct` writes that card for one finished folder, and it refuses a partial file. The blank card for the whole panel is `runs/analysis-template.md`.

## Scope

| file | saved | questions in file | correct | incorrect | refused |
|---|---:|---:|---:|---:|---:|
| `christianity/english/population` | 55 | 120 | 17 | 38 | 0 |

55 scored answers. 65 questions in those files are still pending. Other traditions and the other Christianity files have not been called. A score on this slice is not a score for Christianity, and not a score for the panel.

## Outcomes

| task | n | correct | incorrect | refused | accuracy | token_f1 | token_f1_base |
|---|---:|---:|---:|---:|---:|---:|---:|
| cite_passage | 13 | 8 | 5 | 0 | 61.5% | — | — |
| complete_unit | 14 | 0 | 14 | 0 | 0.0% | 0.394 | 0.394 |
| retrieve_quote | 14 | 0 | 14 | 0 | 0.0% | 0.407 | 0.407 |
| verify_source | 14 | 9 | 5 | 0 | 64.3% | — | — |
| **overall** | 55 | 17 | 38 | 0 | **30.9%** | 0.401 | 0.401 |

Cite and verify have no token F1. Those cells are blank on those columns and the overall F1 is the mean of the quote and completion rows only. On English Latin the two F1s match, because there is no script or spelling fold to apply. They separate on Hebrew, Greek, Arabic, Gurmukhi, Devanagari, and romanized Pali.

## What this does not show

- One English NRSV file, stopped partway. Masoretic, Greek, and the other five traditions are absent.
- Familiarity is not in this run.
- Search is off. Temperature is 0.
- Reasoning is still on for this model, so output tokens and call time include the hidden trace. Cost is not comparable to a model called without reasoning.
- The edition counterfactual (a wrong quote that is the right verse in another selected edition) is computed by `sacredbench facct` on a finished folder. It is not estimated here.

## Cost

Input tokens 3,323. Output tokens 51,080.
Catalogue cost $0.0146, from `model.json`.
Serving host: DeepInfra 54, Tenstorrent 1.
