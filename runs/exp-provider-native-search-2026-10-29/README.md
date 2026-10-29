# Experiment: does each provider's NATIVE search change scripture fidelity?

**Date**: 2026-10-29 · **Requested by**: Waleed · **Issue**: #54
**Status**: harness complete + nativeness-verified; **live run authorized** (OpenRouter key)

Full hypotheses, success criteria, and design: `codev/specs/54-experiment-provider-native-sea.md`.
Analysis (when data lands): `codev/reviews/54-experiment-provider-native-sea.md`.

## What this is

A paired A/B over 56 committed questions (28 Qur'an + 28 Sahih al-Bukhari from
`runs/original-2026-10-21`), asking each model **both ways** — search-off and search-on —
through **OpenRouter**, which forwards each model's request to that vendor's **own native**
search stack (verified per arm; see "Nativeness verification"):

| provider | model (OpenRouter slug) | search-on mechanism |
|----------|-------|---------------------|
| anthropic | `anthropic/claude-sonnet-5.5` | Anthropic server-side `web_search` (block forwarded) |
| openai | `openai/gpt-6.1-sol` | OpenAI Responses native `web_search` |

56 questions × 2 models × 2 arms = **224 cells**, well under $10. The only delta within a
model's arm pair is search: same questions, same model, same host, `temperature: 0`. Panel
matches the signed-off main panel + the exp-arabic experiment (sonnet + sol) for comparability.

"Native" is the point — OpenRouter's own `:online` / Exa layer is rejected as unrepresentative.
Running native *through* OpenRouter is legitimate **only because it is verified** to forward to
the provider's own search, per arm, below; `config.py` refuses `web_search` on this host for any
model family it does not forward natively.

### Gemini dropped from this run (deferred to a native key)

`google/gemini-3.8-flash` does **not** reliably fire native search through OpenRouter —
**routing-variance** across Google's backends: Google AI Studio shared-pool **429s** (4/4
attempts), Google Vertex returns `finish_reason=error` with **no** `server_tool_use_details`
and zero citations (2/2). A flaky/non-firing arm is not experiment-grade, so gemini is deferred
to a native `GEMINI_API_KEY`, where the pipeline's `google_search` grounding path (built +
tested, `providers._gemini`) runs it. This is a one-sided outcome recorded, not hidden: the
architect's single earlier probe *did* fire, which is itself the routing-variance evidence.

## Nativeness verification (REQUIRED before the paid run)

Each search-on arm was probed live through OpenRouter and checked on the three signals that
separate a provider's own native search from a uniform OpenRouter/Exa web layer:

| arm | provider-of-record | `server_tool_use_details` | citation annotation style | native? |
|-----|--------------------|---------------------------|---------------------------|---------|
| `anthropic/claude-sonnet-5.5` | **Claude Platform on AWS** | `web_search_requests: 1` | `url_citation` **with `content` snippet** | ✅ |
| `openai/gpt-6.1-sol` | **OpenAI** | `web_search_requests: 2` | `url_citation` **with char `start/end_index`, no content** | ✅ |
| `google/gemini-3.8-flash` | Google | **absent** | — (`finish_reason: error`) | ❌ dropped |

The decisive signal: the two surviving arms carry **structurally different** citation shapes —
Anthropic ships content snippets, OpenAI ships character offsets into the answer. A single
OpenRouter/Exa layer would return **identical** annotation shapes across providers; the
per-provider difference is positive proof each arm uses its own vendor's native search. Each
collected answer row also records its `usage.provider` (provider-of-record) and
`usage.web_search_requests`, so the committed evidence re-proves nativeness per cell.

## Pre-registered hypotheses (full text in the spec)

- **H1** search-on reduces hadith refusals (coverage up).
- **H2** search-on reduces `wrong_locus` / citation errors.
- **H3** search-on *increases* other-edition & orthography mismatches (quotes whatever edition
  it fetched) — interacts with #52.

Each gets an explicit confirmed / disconfirmed / inconclusive verdict against the data,
counter-evidence shown.

## ⚠️ Dated snapshot, not reproducible

Live web results drift. This arm is a snapshot **as of its collection date**; re-running later
will fetch different pages and will not reproduce the same answers. This is inherent to
measuring real search and is stated up front, not hidden. The panel records the date.

## Files

- `build_questions.py` — filters the 56 questions from the committed set, **verbatim**, with a
  round-trip + per-work-count oracle. Already run → `questions.jsonl`.
- `questions.jsonl` — the 56 questions (digest `64ce2d44f418e0c0`).
- `models.yaml` — the 4-entry panel (2 models × search on/off) via OpenRouter, temp 0.
- `dry_run.py` — keyless harness check (panel loads, questions load, arms have distinct
  fingerprints, plan = 224 cells). Makes no network call.

## Key: OpenRouter

The live collect needs only `OPENROUTER_API_KEY` (already in `sacredtexts/.env`). The code and
harness are complete and tested keyless; the paid collect is architect-authorized (<$10).

## How to run

```bash
# 0. keyless sanity check (no network)
uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/dry_run.py

# 1. (re)build the questions if needed
uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/build_questions.py

# 2. collect (224 cells) — OPENROUTER_API_KEY must be in the environment
uv --project pipelines run python -m sacredbench collect \
  runs/exp-provider-native-search-2026-10-29/questions.jsonl \
  --config runs/exp-provider-native-search-2026-10-29/models.yaml \
  --out    runs/exp-provider-native-search-2026-10-29/answers.jsonl

# 3. score with --config (cross-checks panel identity against the collected fingerprints)
uv --project pipelines run python -m sacredbench score \
  runs/exp-provider-native-search-2026-10-29/answers.jsonl \
  --questions    runs/exp-provider-native-search-2026-10-29/questions.jsonl \
  --config       runs/exp-provider-native-search-2026-10-29/models.yaml \
  --scores-out   runs/exp-provider-native-search-2026-10-29/scores.jsonl \
  --summary-out  runs/exp-provider-native-search-2026-10-29/summary.json
```

Failed cells stay pending and make `collect` exit non-zero; re-running retries exactly the
missing cells. Provenance (search-request count + cited URLs) lands in each answer row's
`usage`.

## Results

**Pending (run in progress).** Conclusions and the hypothesis verdicts will be filled in here
and in `codev/reviews/54-experiment-provider-native-sea.md` once the run completes.
