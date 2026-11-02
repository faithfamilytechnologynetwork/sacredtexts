# Estimated OpenRouter cost

Prices fetched 2026-10-31 14:35 UTC from https://openrouter.ai/api/v1/models.

The run is List A, all 16 models, search off. With all six traditions complete,
budget **$648.79**. That is the higher figure: every model writes as
much as gpt-oss-20b did on the committed run. The floor for those same 2160
questions is **$211.91**.

Questions on disk today are 1920. The dollar tables below were scaled when that
count was 960 (Christianity, Judaism, and the Arabic Qur'an only), so they read
**$94.18** to **$288.35** on List A. Re-run `cost.py` before using them for the
1920-question set.

`search` in the panel file is `false`. No model is sent `web_search`, so this
estimate has no web-search fee. Set that key to `true` or `both` to change it.

The ~$70 and ~$14 figures were for the committed **476-question** run.
The population files now have **1920** questions. The dollars below were scaled
to **960** questions (960 / 476 = 2.017) and have not been repriced. Input is the mean of the three measured models
(206.0 tokens per question). Output for gpt-oss-20b is its own measured
rate (1672.9 tokens per question). Every other model uses the mean
of haiku and opus (517.2). The last column prices every model at the
gpt-oss-20b output rate, which is the verbose-reasoner headroom.

These prompts are not the committed run's prompts. The scale assumes a call
costs about the same per question. Each finished tradition is 360 questions:
the native text asked in English and in its own language (240), plus an
English edition (120). Christianity's native text is the same 30 verses,
Masoretic where the verse is from the Hebrew Bible and Greek where it is
from the New Testament. Islam's English edition on disk is Saheeh International.
Sikhism has only the native edition. Hinduism has Besant's English. Buddhism
has no English edition.

## All six traditions

| Tradition | Questions | How counted |
|---|---:|---|
| Christianity | 360 | NRSV, plus the same 30 in Masoretic or Greek, both prompts |
| Judaism | 360 | Aramaic in both prompt languages, plus the English edition |
| Islam | 360 | Uthmani in both prompt languages, plus Saheeh International |
| Sikhism | 240 | Gurmukhi, both prompts; no English edition in this corpus |
| Hinduism | 360 | Sanskrit in both prompt languages, plus Besant's English |
| Buddhism | 240 | Pali, both prompts; no English edition in this corpus |
| **All six** | **1920** | |

List A and List B totals below were priced for 2160 questions, which counted an
English Guru Granth Sahib and an English Dhammapada this corpus does not have.
The files on disk are 1920. Re-run `cost.py` to reprice. The old 2160 figures
were floor **$211.91**, higher budget **$648.79** (List A) and floor **$42.63**,
higher budget **$129.26** (List B).
That total is the population sample only. Familiarity lists are not in it.

## List A — 16 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `fable` | `anthropic/claude-fable-5.1` | 10.0000 | 50.0000 | $26.80 | $82.28 |
| `opus` | `anthropic/claude-opus-5.5` | 4.0000 | 20.0000 | $10.72 | $32.91 |
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.27 | $0.82 |
| `astra` | `openai/gpt-6-astra` | 10.0000 | 50.0000 | $26.80 | $82.28 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `terra` | `openai/gpt-6.1-terra` | 1.0000 | 5.0000 | $2.68 | $8.23 |
| `luna` | `openai/gpt-6-luna` | 0.1000 | 0.5000 | $0.27 | $0.82 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `gemini-flash` | `google/gemini-3.8-flash` | 0.8250 | 4.1250 | $2.21 | $6.79 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $1.91 | $5.46 |
| `kimi` | `moonshotai/kimi-k3.1-pro` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $0.55 | $1.66 |
| `gemma-31b` | `google/gemma-4-31b-it` | 0.2000 | 0.4000 | $0.24 | $0.68 |
| `qwen3-32b` | `qwen/qwen3-32b` | 0.0800 | 0.2800 | $0.15 | $0.47 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0180 | 0.0900 | $0.15 | $0.15 |

List A, this file: floor **$94.18**, higher budget **$288.35**.

## List B — 7 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $5.36 | $16.46 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.27 | $0.82 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $1.91 | $5.46 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $0.55 | $1.66 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0180 | 0.0900 | $0.15 | $0.15 |

List B for this file: **$18.95**. Verbose-reasoner headroom: **$57.45**.

List A is `models/openrouter.yaml`. List B is `models/openrouter-subset.yaml`.
Both are search off, temperature 0, one `OPENROUTER_API_KEY`.
