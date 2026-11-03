# Runs

Answers and scores live here. Dated evidence from earlier work is in `archive/`. A new run is one model, then `base` (temperature 0, search off), then the same folders as `items/for-test/`.

```text
runs/haiku/base/christianity/english/population/answers.jsonl
runs/haiku/base/sikhism/native/population/scores.jsonl
runs/archive/original-2026-10-21/
```

The command is `items/for-test/join_run.py`. It creates a folder only when that file is collected. It reads `OPENROUTER_API_KEY` from the environment, or from `.env` in the repo root if that variable is not already set. Do not commit the key.

## Models

Ids for `--model`, from `items/for-test/models/openrouter.yaml`. Temperature 0, search off. `python items/for-test/check_models.py` calls each one with the key in `.env` and writes `runs/<id>/model.json` (input and output price per million tokens, context length, and the probe's token counts and cost).

| id | model |
|---|---|
| `fable` | `anthropic/claude-fable-5.1` |
| `opus` | `anthropic/claude-opus-5.5` |
| `sonnet` | `anthropic/claude-sonnet-5.5` |
| `haiku` | `anthropic/claude-haiku-5.5` |
| `astra` | `openai/gpt-6-astra` |
| `sol` | `openai/gpt-6.1-sol` |
| `terra` | `openai/gpt-6.1-terra` |
| `luna` | `openai/gpt-6-luna` |
| `argon` | `google/gemini-4-argon` |
| `gemini-flash` | `google/gemini-3.8-flash` |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` |
| `kimi` | `moonshotai/kimi-k3.1-pro` |
| `beam` | `reflection/beam-1.0-501b-a23b` |
| `gemma-31b` | `google/gemma-4-31b-it` |
| `qwen3-32b` | `qwen/qwen3-32b` |
| `gpt-oss-20b` | `openai/gpt-oss-20b` |

## Where a tradition is stored

Population is the run. Familiarity is on disk and is not collected by this command. `—` means this corpus has no English edition.

```text
runs/<model>/base/
  christianity/  english/  + native/masoretic/  + native/greek/     360
  judaism/       english/  + native/                                  360
  islam/         english/  + native/                                  360
  hinduism/      english/  + native/                                  360
  sikhism/       —         + native/                                  240
  buddhism/      —         + native/                                  240
```

Each of those has `population/` (and `familiarity/`, not in the run). A native edition is `prompt-english/` and `prompt-native/`.

## Collected so far

Snapshot while collection is still running, 2 November 2026. Saved answer cells: **29,197 of 32,562 (89.7%)**. That target is the original plan plus the English Book of Mormon and encyclicals (240 questions each, every model). The original six-tradition plan alone is **26,558 of 28,722 (92.5%)**. The two English sets are **2,639 of 3,840 (68.7%)**.

A full model is 2,160 cells (1,920 + 240). A limited model is 1,938 (1,698 + 240). Limited means Buddhism is the first 9 questions of each Buddhism file. Finished at that target: argon, deepseek-v4-pro, gemini-flash, gemma-31b, haiku, kimi, luna, opus, sonnet, terra. Still short: astra 1,313, beam 1,935, fable 1,553, gpt-oss-20b 1,438, qwen3-32b 815, sol 1,653.

To rebuild the figures, the LaTeX tables, the claim tests and the findings from one run, name its folder with `--run-dir`:

```bash
uv --project pipelines run python items/for-test/paper_figures.py --run-dir runs/rerun-2026-11-03
uv --project pipelines run python items/for-test/claim_tests.py --run-dir runs/rerun-2026-11-03
uv --project pipelines run python items/for-test/facct_findings.py --run-dir runs/rerun-2026-11-03
```

Each script reads only `<run-dir>/<model>/base/` and writes to `runs/paper/`. It stops if an answer has no question in the current question files. `--allow-partial` writes anyway and says what it left out. The table below came from `--run-dir runs`, the run on this page. A dash has not been run. An asterisk is a tradition that has been started and not finished. Accuracy is correct / (correct + incorrect). Refusals are excluded.

## Correct so far

Same numbers as `runs/paper/models-by-tradition.tex`, in percent. `*` is partial.

| model | Chr | Jud | Isl | Hin | Sik | Bud | BoM | Enc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fable` | 73.4 | 26.3 | 81.9* | 58.6* | 41.5* | — | — | — |
| `opus` | 71.4 | 26.5 | 80.5 | 63.7 | 29.7 | 83.3* | 89.0 | 50.6 |
| `sonnet` | 55.2 | 14.7 | 74.9 | 51.4 | 17.0 | 37.5* | 42.7 | 33.3 |
| `haiku` | 47.9 | 21.9 | 71.9 | 56.5 | 22.0 | 29.1 | 23.4 | 33.3 |
| `astra` | 65.4 | 41.1 | 90.7 | — | 24.3* | — | — | — |
| `sol` | 64.0 | 36.3 | 90.1 | 50.7* | 23.3 | — | — | — |
| `terra` | 58.5 | 26.4 | 85.0 | 51.1 | 21.2 | 72.8 | 60.0 | 31.6 |
| `luna` | 54.1 | 18.0 | 78.7 | 54.6 | 22.2 | 41.6 | 31.4 | 27.0 |
| `argon` | 68.9 | 29.5 | 90.6 | 61.4 | 25.3 | 82.4* | 79.2 | 51.0 |
| `gemini-flash` | 63.7 | 29.7 | 81.7 | 61.9 | 20.2 | 72.1 | 70.1 | 51.2 |
| `deepseek-v4-pro` | 57.2 | 14.2 | 61.9 | 44.8 | 22.6 | 18.8* | 41.7 | 28.3 |
| `kimi` | 59.6 | 23.2 | 74.1 | 55.6 | 23.5 | 50.0* | 52.2 | 37.5 |
| `beam` | 59.2* | 23.2 | 78.8 | 61.3 | 26.0 | 26.7* | 57.6* | 30.8 |
| `gemma-31b` | 26.1 | 14.9 | 39.2 | 26.5 | 17.1 | 17.0 | 15.8 | 21.7 |
| `qwen3-32b` | 27.7 | 15.4 | 25.3* | — | — | — | — | — |
| `gpt-oss-20b` | 17.8 | 15.7 | 15.8* | 14.3* | 14.1 | — | — | — |

## A model

`--model` is required. It is the id in `items/for-test/models/openrouter.yaml` (`haiku`, `opus`, `sol`, `gpt-oss-20b`, and the rest of that list). Answers go under `runs/<model>/base/`.

Calls run in parallel. The panel file sets `concurrency: 4`, so four questions are in flight at once. Pass `--concurrency 10` to raise that for one run. Ten is a reasonable step for a cheap model. A higher number can trip OpenRouter's rate limit, and those cells stay pending for the next run.

```bash
python items/for-test/join_run.py --model haiku
python items/for-test/join_run.py --model qwen3-32b --concurrency 10
```

That walks every population question file (familiarity is not included). Each folder receives `answers.jsonl`, then `scores.jsonl`, `summary.json`, and `summary.md`. Run the same command again to retry cells that failed. Finished question-and-model pairs are not called again.

## A tradition

`--tradition` limits the run to one tradition. Names are `christianity`, `judaism`, `islam`, `sikhism`, `hinduism`, and `buddhism`. Repeat the flag for more than one. A later run of the same model without `--tradition` fills in the traditions that were skipped.

```bash
python items/for-test/join_run.py --model haiku --tradition islam
python items/for-test/join_run.py --model opus --tradition sikhism --tradition hinduism
```

`--only` is a path fragment when you want one file rather than the whole tradition:

```bash
python items/for-test/join_run.py --model haiku --only christianity/english/population
```

## A short test, then the rest

```bash
python items/for-test/join_run.py --model haiku --tradition islam --test
python items/for-test/join_run.py --model haiku --test
```

`--test` calls the first 3 passages of each tradition, all four tasks for those passages. That is 3 passages per tradition, not 3 per file and not 18 passages in one pile. A file that does not contain those 3 is skipped. The Greek New Testament file is skipped when Christianity's 3 are Hebrew Bible verses. The same 3 are still asked in each file that does contain them (English, and both Masoretic prompts). The answer file is stamped with the full question file, not with the 3-passage slice. Drop `--test` and run the same model again. The 3 passages stay, and the remaining passages are added to the same `answers.jsonl`. The scores are rewritten from the whole file.

Sikhism and Buddhism have no English edition, so there is no `sikhism/english/` folder until a translation is in the corpus. Collecting that later is a new folder. It does not replace the Gurmukhi answers.

## Archive

`archive/` holds `original-2026-10-21`, `tutorial-2026-10-11`, `first-run-2026-10-11`, and the two 29 October experiments. The viewer lists a folder there when it has a `summary.json`. Do not re-collect those runs.
