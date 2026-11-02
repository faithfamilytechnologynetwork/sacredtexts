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

Population questions only. `qwen3-32b` is the only model with answers. The run was stopped during the first file, so there is no `summary.json` yet and the correctness table below stays at 0.

| | |
|---|---:|
| file | `christianity/english/population` |
| answers | 55 of 120 |
| other files | 0 |
| input tokens | 3,323 |
| output tokens | 51,080 |
| cost | $0.0146 |

Output tokens are high because Qwen3 reasoning is still on. The same command continues this file, then the rest of the population.

`python3 items/for-test/analyze_run.py` rewrites `runs/<model>/analysis.md` from the answer files. `runs/analysis-template.md` is the blank FAccT card for when every folder has scores.

## Correct so far

Replace a `0` when that model’s `summary.json` files are in. These are scored results, not answer counts.

| model | Chr | Jud | Isl | Sik | Hin | Bud |
|---|---:|---:|---:|---:|---:|---:|
| `fable` | 0 | 0 | 0 | 0 | 0 | 0 |
| `opus` | 0 | 0 | 0 | 0 | 0 | 0 |
| `sonnet` | 0 | 0 | 0 | 0 | 0 | 0 |
| `haiku` | 0 | 0 | 0 | 0 | 0 | 0 |
| `astra` | 0 | 0 | 0 | 0 | 0 | 0 |
| `sol` | 0 | 0 | 0 | 0 | 0 | 0 |
| `terra` | 0 | 0 | 0 | 0 | 0 | 0 |
| `luna` | 0 | 0 | 0 | 0 | 0 | 0 |
| `argon` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gemini-flash` | 0 | 0 | 0 | 0 | 0 | 0 |
| `deepseek-v4-pro` | 0 | 0 | 0 | 0 | 0 | 0 |
| `kimi` | 0 | 0 | 0 | 0 | 0 | 0 |
| `beam` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gemma-31b` | 0 | 0 | 0 | 0 | 0 | 0 |
| `qwen3-32b` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-oss-20b` | 0 | 0 | 0 | 0 | 0 | 0 |

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
