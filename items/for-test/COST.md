# Estimated OpenRouter cost

Prices taken 2026-11-03 03:07 UTC from `runs/<id>/model.json`, written by `check_models.py` from the OpenRouter catalogue.

The run is List A, all 16 models, search off. With all six traditions complete,
budget **$539.62**. That is the higher figure: every model writes as
much as gpt-oss-20b did on the committed run. The floor for those same 1800
questions is **$176.34**.

Questions on disk today are 2040. That run is
**$199.85** to **$611.57** on List A.

`search` in the panel file is `false`. No model is sent `web_search`, so this
estimate has no web-search fee. Set that key to `true` or `both` to change it.

The ~$70 and ~$14 figures were for the committed **476-question** run.
The population run has **2040** questions, so those amounts are the wrong scale.
The dollars below keep that run's measured tokens per call and multiply by
2040 / 476 (4.286). Input is the mean of the three measured models
(206.0 tokens per question). Output for gpt-oss-20b is its own measured
rate (1672.9 tokens per question). Every other model uses the mean
of haiku and opus (517.2). The last column prices every model at the
gpt-oss-20b output rate, which is the verbose-reasoner headroom.

These prompts are not the committed run's prompts. The scale assumes a call
costs about the same per question. Each finished tradition is 360 questions:
the native text asked in English and in its own language (240), plus an
English edition (120). Christianity's native text is the same 30 verses,
Masoretic where the verse is from the Hebrew Bible and Greek where it is
from the New Testament. Islam adds Saheeh International. Sikhism has
no English edition, so it is 240 questions. Buddhism has no English
edition and its Pali text is asked with the English prompt only, so it
is 120 questions.

## All six traditions

| Tradition | Questions | How counted |
|---|---:|---|
| Christianity | 360 | NRSV, plus the same 30 in Masoretic or Greek, both prompts |
| Judaism | 360 | Aramaic in both prompt languages, plus the English edition |
| Islam | 360 | Uthmani in both prompt languages, plus Saheeh International |
| Sikhism | 240 | Gurmukhi, both prompts; no English edition in this corpus |
| Hinduism | 360 | Sanskrit in both prompt languages, plus Besant's English |
| Buddhism | 120 | Pali, English prompt only; no English edition in this corpus |
| **All six** | **1800** | |

List A, six traditions: floor **$176.34**, higher budget **$539.62**.
List B, six traditions: floor **$35.65**, higher budget **$107.84**.
That total is the population sample only. Familiarity lists are not in it.

## List A — 16 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `fable` | `anthropic/claude-fable-5.1` | 10.0000 | 50.0000 | $56.95 | $174.84 |
| `opus` | `anthropic/claude-opus-5.5` | 4.0000 | 20.0000 | $22.78 | $69.93 |
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.57 | $1.75 |
| `astra` | `openai/gpt-6-astra` | 10.0000 | 50.0000 | $56.95 | $174.84 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `terra` | `openai/gpt-6.1-terra` | 1.0000 | 5.0000 | $5.70 | $17.48 |
| `luna` | `openai/gpt-6-luna` | 0.1000 | 0.5000 | $0.57 | $1.75 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `gemini-flash` | `google/gemini-3.8-flash` | 0.7500 | 3.7500 | $4.27 | $13.11 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $4.05 | $11.59 |
| `kimi` | `moonshotai/kimi-k3.1-pro` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $1.16 | $3.52 |
| `gemma-31b` | `google/gemma-4-31b-it` | 0.2000 | 0.4000 | $0.51 | $1.45 |
| `qwen3-32b` | `qwen/qwen3-32b` | 0.0800 | 0.2800 | $0.33 | $0.99 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0300 | 0.1300 | $0.46 | $0.46 |

List A, this file: floor **$199.85**, higher budget **$611.57**.

## List B — 7 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $11.39 | $34.97 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.57 | $1.75 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $4.05 | $11.59 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $1.16 | $3.52 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0300 | 0.1300 | $0.46 | $0.46 |

List B for this file: **$40.41**. Verbose-reasoner headroom: **$122.22**.

List A is `models/openrouter.yaml`. List B is `models/openrouter-subset.yaml`.
Both are search off, temperature 0, one `OPENROUTER_API_KEY`.
