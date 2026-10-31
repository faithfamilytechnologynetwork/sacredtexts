# Estimated OpenRouter cost

Prices fetched 2026-10-31 10:38 UTC from https://openrouter.ai/api/v1/models.

The run is List A, all 16 models, search off. With all six traditions complete,
budget **$396.48**. That is the higher figure: every model writes as
much as gpt-oss-20b did on the committed run. The floor for those same 1320
questions is **$129.50**.

Questions on disk today are 480 (Christianity, Judaism, Islam). That smaller run is
**$47.09** to **$144.17** on List A.

`search` in the panel file is `false`. No model is sent `web_search`, so this
estimate has no web-search fee. Set that key to `true` or `both` to change it.

The ~$70 and ~$14 figures were for the committed **476-question** run.
The population run has **480** questions, so those amounts are the wrong scale.
The dollars below keep that run's measured tokens per call and multiply by
480 / 476 (1.008). Input is the mean of the three measured models
(206.0 tokens per question). Output for gpt-oss-20b is its own measured
rate (1672.9 tokens per question). Every other model uses the mean
of haiku and opus (517.2). The last column prices every model at the
gpt-oss-20b output rate, which is the verbose-reasoner headroom.

These prompts are not the committed run's prompts. The scale assumes a call
costs about the same per question. Christianity stays one English edition.
Every other tradition is two editions once the data is in: native and English,
240 questions each. Islam and Sikhism have only the native edition on disk.
Hinduism and Buddhism have no passages yet.

## All six traditions

| Tradition | Questions | How counted |
|---|---:|---|
| Christianity | 120 | English only, counted from the question file |
| Judaism | 240 | both editions counted from the question files |
| Islam | 240 | 120 on disk; 240 once the English edition is added |
| Sikhism | 240 | 120 on disk; 240 once the English edition is added |
| Hinduism | 240 | estimated: native and English, 30 passages, 4 tasks |
| Buddhism | 240 | estimated: native and English, 30 passages, 4 tasks |
| **All six** | **1320** | |

List A, six traditions: floor **$129.50**, higher budget **$396.48**.
List B, six traditions: floor **$26.05**, higher budget **$78.99**.
That total is the population sample only. Familiarity lists are not in it.

## List A — 16 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `fable` | `anthropic/claude-fable-5.1` | 10.0000 | 50.0000 | $13.40 | $41.14 |
| `opus` | `anthropic/claude-opus-5.5` | 4.0000 | 20.0000 | $5.36 | $16.46 |
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.13 | $0.41 |
| `astra` | `openai/gpt-6-astra` | 10.0000 | 50.0000 | $13.40 | $41.14 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `terra` | `openai/gpt-6.1-terra` | 1.0000 | 5.0000 | $1.34 | $4.11 |
| `luna` | `openai/gpt-6-luna` | 0.1000 | 0.5000 | $0.13 | $0.41 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `gemini-flash` | `google/gemini-3.8-flash` | 0.8250 | 4.1250 | $1.11 | $3.39 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $0.95 | $2.73 |
| `kimi` | `moonshotai/kimi-k3.1-pro` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $0.27 | $0.83 |
| `gemma-31b` | `google/gemma-4-31b-it` | 0.2000 | 0.4000 | $0.12 | $0.34 |
| `qwen3-32b` | `qwen/qwen3-32b` | 0.0800 | 0.2800 | $0.08 | $0.23 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0180 | 0.0900 | $0.07 | $0.07 |

List A, this file: floor **$47.09**, higher budget **$144.17**.

## List B — 7 models

| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |
|---|---|---:|---:|---:|---:|
| `sonnet` | `anthropic/claude-sonnet-5.5` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `sol` | `openai/gpt-6.1-sol` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `argon` | `google/gemini-4-argon` | 2.0000 | 10.0000 | $2.68 | $8.23 |
| `haiku` | `anthropic/claude-haiku-5.5` | 0.1000 | 0.5000 | $0.13 | $0.41 |
| `deepseek-v4-pro` | `deepseek/deepseek-v4-pro` | 1.6000 | 3.2000 | $0.95 | $2.73 |
| `beam` | `reflection/beam-1.0-501b-a23b` | 0.2500 | 1.0000 | $0.27 | $0.83 |
| `gpt-oss-20b` | `openai/gpt-oss-20b` | 0.0180 | 0.0900 | $0.07 | $0.07 |

List B for this file: **$9.47**. Verbose-reasoner headroom: **$28.72**.

List A is `models/openrouter.yaml`. List B is `models/openrouter-subset.yaml`.
Both are search off, temperature 0, one `OPENROUTER_API_KEY`.
