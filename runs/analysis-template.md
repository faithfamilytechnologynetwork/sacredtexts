# FAccT card — full panel

Fill this once every population folder has `answers.jsonl`, `scores.jsonl`, `summary.json`, and `summary.md`. Until then, `python3 items/for-test/analyze_run.py` writes the progress report at `runs/<model>/analysis.md`.

The card for one finished folder:

```bash
python -m sacredbench facct runs/<model>/base/<tradition>/.../population
```

That writes `facct.json` and `facct.md` in that folder. It reads the scores. It does not call a model.

## The panel

| Model | OpenRouter id | Temperature | Search | Calls | Input tokens | Output tokens | Cost |
|---|---|---:|---|---:|---:|---:|---:|
| | | 0 | off | | | | |

Provider in the answer rows is the API client (`openai` means the OpenAI-compatible client). The maker is the model id. The host that served the call is `usage.provider`.

## The tasks

- **retrieve_quote** — quote a named edition's exact wording
- **complete_unit** — continue a passage from its opening words
- **cite_passage** — name the citation
- **verify_source** — yes or no, is this text from the named edition

## Who the questions represent

Population only. Familiarity stays out of this card.

| Tradition | Questions | English | Native, prompt English | Native, prompt original |
|---|---:|---:|---:|---:|
| Christianity | 360 | | | |
| Judaism | 360 | | | |
| Islam | 360 | | | |
| Hinduism | 360 | | | |
| Sikhism | 240 | — | | |
| Buddhism | 240 | — | | |
| **Total** | **1920** | | | |

Christianity's native rows split into Masoretic and Greek. Sikhism and Buddhism have no English edition.

## Outcomes

One block per model, copied from each folder's `summary.json`. Accuracy is correct / (correct + incorrect). Coverage is (correct + incorrect) / n. A refusal is out of the accuracy and in the coverage. Unanswered questions are pending, not a score.

`token_f1` is the strict overlap and the wording score. `token_f1_base` folds script and spelling and is a diagnostic beside it. Cite and verify have no token F1.

| Model | Tradition | Task | n | Correct | Incorrect | Refused | Accuracy | Coverage | token_f1 | token_f1_base |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | | |

## Edition counterfactual

For a finished folder, this section is generated inside that folder's `facct.md`. It asks whether a wrong quote is the right verse in a different edition that the run actually selected. Paste or link those sections here. Do not recompute them by hand.

## Figure and tables

`uv --project pipelines run python items/for-test/paper_figures.py --run-dir runs/rerun-2026-11-03` writes `runs/paper/models-by-tradition.pdf` and two `booktabs` tables, `models-by-tradition.tex` and `models-by-task.tex`. Drop the PDF in the paper and `\input` the tables. A dash is not run. An asterisk is a partial tradition. It reads only that run dir and stops if an answer has no question in the current question files. `claim_tests.py` and `facct_findings.py` take the same `--run-dir` and write `runs/paper/claim-tests.md` and `runs/paper/findings.md`. Re-run the scripts when more answers land. The numbers follow the card: accuracy is correct divided by correct plus incorrect.

## What this card is not

A partial file is not a tradition score. A model with reasoning left on is not comparable on cost to one called without it. Search stays off for `base`.
