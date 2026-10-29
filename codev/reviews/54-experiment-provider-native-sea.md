# Experiment 54 — Review: provider-native search arm

**Protocol**: EXPERIMENT (soft mode) · **Issue**: #54 · **Status**: complete (2-model pilot)
**Spec**: `codev/specs/54-experiment-provider-native-sea.md` ·
**Run**: `runs/exp-provider-native-search-2026-10-29/` (README has the full tables)

## What we asked

Does giving a model its provider's **native** web search change scripture fidelity? Paired
A/B (search-off vs search-on), 56 committed questions (28 Qur'an + 28 Sahih al-Bukhari), native
search for both arms, tools the only delta. Pre-registered H1 (refusals fall), H2 (citation/
locus errors fall), H3 (edition/orthography mismatches rise).

## How it actually ran (and what changed from the spec)

- **Transport pivoted to OpenRouter** on the existing key (architect call; Waleed asked "can't
  we still use OpenRouter"). Legitimate only because each arm was **verified** per-run to
  forward to the provider's own native search — not OpenRouter's `:online`/Exa layer. The
  decisive proof: the two arms carry **structurally different** citation annotations (Anthropic
  = content snippets, OpenAI = character offsets); a uniform Exa layer would return identical
  shapes. Provider-of-record (`Claude Platform on AWS` / `OpenAI`) and per-cell
  `server_tool_use_details` corroborate. Full table in the run README.
- **Gemini dropped.** `google/gemini-3.8-flash` does not reliably fire native search through
  OpenRouter — routing variance across Google backends (AI Studio shared-pool 429s 4/4; Vertex
  `finish_reason=error`, no server-tool evidence, 2/2). A flaky/non-firing arm is not
  experiment-grade. Deferred to a native `GEMINI_API_KEY`, where the pipeline's `google_search`
  grounding path (`providers._gemini`, built + tested) runs it. Note the honest asymmetry: the
  architect's single earlier probe *did* fire — that very inconsistency is the disqualifier.
- **Panel = 2 models** (sonnet + sol), 224 cells. Matches the main panel + exp-arabic.

## Findings (n = 28 per text per arm — directional, not significance-tested)

1. **Search helps the model that uses it; it barely moves the one that doesn't.** sol searched
   49/56 cells → +9pp overall (57.1→66.1%), +11pp Bukhari, **+29pp complete_unit**
   (64.3→92.9%). sonnet searched only 14/56 → −4pp overall (within noise). The dominant driver
   is **search propensity**, which differs sharply by provider — this was *not* in the
   hypotheses and is the most actionable result.
2. **H1 — CONFIRMED, narrowly.** sonnet's hadith coverage rose 78.6→85.7% (refusals 6→4); sol
   had no refusals to reduce (floor). Trade-off: sonnet's recovered cells were mostly wrong, so
   its Bukhari *accuracy* fell (40.9→33.3%). Search reduces refusal where refusal exists, at an
   accuracy cost.
3. **H2 — DISCONFIRMED.** `cite_passage` is perfectly flat (7/7, all misses `wrong_locus`) in
   every arm. Even with sol searching 49/56, citation locus/form did not improve — locus looks
   like a parametric formatting skill search doesn't touch.
4. **H3 — MIXED → mostly DISCONFIRMED.** The orthography half fails: `other_script` on
   `retrieve_quote` did not rise with search (sol fell 7→4, sonnet flat). Only the
   other-edition half gets weak support: sol gained 3 `wrong_passage` on-arm (0→3), consistent
   with quoting a fetched edition. So "search drags in the wrong edition" is a real but small
   effect; "search corrupts orthography" is not supported here.

## Limitations

- **Pilot power**: 28 questions per text per arm; per-cell flips of 1–3 are not significant.
  Treat every delta as directional.
- **Dated snapshot**: live results drift; this is not reproducible by construction (stated in
  the README). The panel records the date.
- **Two texts, two models**: Qur'an + Sahih al-Bukhari; sonnet + sol. Gemini absent (deferred).
- **Scorer unchanged**: orthography near-misses still score incorrect (the #52 Uthmani↔Imla'i
  gap). `other_script` is a proxy for script divergence, not a full edition audit.

## Recommendations / next steps

- **Gemini via a native key** (`GEMINI_API_KEY`): the `google_search` grounding path is built
  and tested; running it closes the 3-provider design. Do NOT pursue gemini search through
  OpenRouter — it is not experiment-grade.
- **Measure search propensity directly** as a first-class metric in any scaled search study —
  it, not search quality alone, moved fidelity here.
- **Scale cautiously**: before a larger search run, the #52 orthography fold (or Jev
  adjudication) matters for retrieve_quote, or orthography near-misses keep masking the signal.
- **Production framing (Phase 2)**: "turn search on" is not uniformly good — it traded
  refusals for wrong answers on sonnet/hadith. Any recommendation must be per-model and
  per-task, not global.

## Process notes

- The required per-arm nativeness verification caught the gemini problem *before* the paid run —
  cheap probes ($0.09) that de-risked a design-altering pivot. Verify the mechanism empirically
  before spending.
- `collect`'s `config` is a positional arg, not `--config` (cost me one no-op background run;
  the run README recipe is now correct).
- Native code paths (OpenAI Responses, Gemini grounding) were kept even though this run used
  OpenRouter transport — they are the path for the deferred native-gemini run and future
  native-key runs.
