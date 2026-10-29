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

# 2. collect (224 cells) — OPENROUTER_API_KEY must be in the environment.
#    `questions` and `config` are POSITIONAL args; the answers path is --out.
uv --project pipelines run python -m sacredbench collect \
  runs/exp-provider-native-search-2026-10-29/questions.jsonl \
  runs/exp-provider-native-search-2026-10-29/models.yaml \
  --out runs/exp-provider-native-search-2026-10-29/answers.jsonl

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

## Results (collected 2026-10-29, OpenRouter; dated snapshot)

224/224 cells, zero failures. Nativeness re-proven per cell: every `sonnet*` row's
provider-of-record is **Claude Platform on AWS**, every `sol*` row's is **OpenAI**. Scored with
the committed deterministic scorer (`strict`+`containment`), untouched. `analyze.py` →
`analysis.json`. **n = 28 per text per arm — directional pilot signals, not significance-tested.**

**Search actually fired** (native server-tool, from `usage`): sonnet 14/56 cells, sol **49/56**.
A real per-provider difference in search *propensity* (not pre-registered): sol searches
readily, sonnet mostly answers from parametric memory.

### Overall & by text — accuracy (coverage), off → on

| model | overall | Qur'an | Sahih al-Bukhari |
|-------|---------|--------|------------------|
| sonnet | 60.0% → 55.8%  (cov 89.3→92.9) | 75.0% → 75.0% | 40.9% → 33.3%  (cov 78.6→**85.7**) |
| sol    | 57.1% → **66.1%**  (cov 100→100) | 78.6% → 85.7% | 35.7% → **46.4%**  (cov 100) |

### By task — accuracy, off → on

| task | sonnet | sol |
|------|--------|-----|
| retrieve_quote | 0% → 0% | 14.3% → 21.4% |
| complete_unit | 64.3% → 57.1% | 64.3% → **92.9%** |
| cite_passage | 50% → 50% | 50% → 50% |
| verify_source | 100% → 100% | 100% → 100% |

### Pre-registered hypothesis verdicts

- **H1 (refusals fall / coverage up on hadith): CONFIRMED, narrowly.** sonnet's Bukhari coverage
  rose 78.6→85.7% (refusals 6→4). sol never refused (floor — nothing to reduce). **Caveat**: the
  cells sonnet stopped refusing were mostly answered *wrong*, so its Bukhari accuracy *fell*
  (40.9→33.3%) — search buys coverage at an accuracy cost here.
- **H2 (wrong_locus / citation errors fall): DISCONFIRMED.** `cite_passage` is flat — 7 correct /
  7 incorrect, all 7 incorrect classified `wrong_locus`, in **every** arm. Even with sol
  searching 49/56, locus/citation-form accuracy did not move at all.
- **H3 (other-edition / orthography mismatches rise): MIXED → mostly DISCONFIRMED.** The
  orthography prediction fails: `other_script` on `retrieve_quote` did **not** rise — sol *fell*
  7→4, sonnet flat 3→3. Only the "other-edition" half gets weak support: sol's `retrieve_quote`
  gained 3 `wrong_passage` on-arm (0→3) — the model quoting a different passage it fetched.

### Unregistered but clearest finding

**Native search helps the model that uses it and barely moves the one that doesn't.** sol
(49/56 searches): +9pp overall, +11pp Bukhari, **+29pp complete_unit** (64.3→92.9%). sonnet
(14/56): −4pp overall (within noise for n=56), concentrated where it searched least. Provider
search-*propensity*, not just search *quality*, drives the scripture-fidelity delta.

### Cost / latency note

Search injects fetched pages as prompt tokens: `sol-search` used **502k** input tokens vs
`sol`'s 9.5k (≈53×); `sonnet-search` 674k vs 14.7k. Token totals in `summary.md`; the run stayed
well under the $10 cap (per-cell OpenRouter costs from the verification probes ⇒ ≈$5–7 total).
UNPRICED by design, so `score` reports tokens only.

Full discussion, limitations, and next steps: `codev/reviews/54-experiment-provider-native-sea.md`.
