# Experiment: does each provider's NATIVE search change scripture fidelity?

**Date**: 2026-10-29 · **Requested by**: Waleed · **Issue**: #54
**Status**: harness complete, **live run pending native API keys** (see below)

Full hypotheses, success criteria, and design: `codev/specs/54-experiment-provider-native-sea.md`.
Analysis (when data lands): `codev/reviews/54-experiment-provider-native-sea.md`.

## What this is

A paired A/B over 56 committed questions (28 Qur'an + 28 Sahih al-Bukhari from
`runs/original-2026-10-21`), asking each of three models **both ways** — search-off and
search-on — on that vendor's **own** search stack:

| provider | model | search-on mechanism |
|----------|-------|---------------------|
| anthropic | claude-sonnet-5.5 | Anthropic server-side `web_search` |
| openai | a current OpenAI model | Responses-API native `web_search` |
| gemini | gemini (argon / 3.8-flash) | Google-Search grounding |

56 questions × 3 models × 2 arms = **336 cells**, estimated well under $10. The only delta
within a model's arm pair is search: same questions, same native endpoint, `temperature: 0`.
"Native" is the point — OpenRouter `:online` / Exa are rejected as unrepresentative of the
real product search experience, and `config.py` refuses `web_search` on a third-party host.

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
- `models.yaml` — the 6-entry panel (3 models × search on/off), native endpoints, temp 0.
  Model slugs marked `(confirm)` are finalised when keys land.
- `dry_run.py` — keyless harness check (panel loads, questions load, arms have distinct
  fingerprints, plan = 336 cells). Makes no network call.

## 🔑 Blocker: native API keys

`.env` currently has only `OPENROUTER_API_KEY`. The live collect needs **native** keys that
Waleed provisions:

- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`

The code and harness are complete and tested keyless; only the live collect + scoring wait on
these.

## How to run (once keys are in the environment)

```bash
# 0. keyless sanity check (no network)
uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/dry_run.py

# 1. (re)build the questions if needed
uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/build_questions.py

# 2. confirm the model slugs in models.yaml are current, then collect (336 cells)
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

**Pending** — blocked on native keys. Conclusions and the hypothesis verdicts will be filled
in here and in `codev/reviews/54-experiment-provider-native-sea.md` once the run completes.
