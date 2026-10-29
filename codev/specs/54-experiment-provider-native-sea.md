# Experiment 54 — Provider-native search arm: does real search change scripture fidelity?

**Protocol**: EXPERIMENT (soft mode) · **Issue**: #54 · **Requested by**: Waleed (2026-10-29)
**Status**: harness complete, **live run blocked on native API keys** (see Blockers)
**Run dir**: `runs/exp-provider-native-search-2026-10-29/`

Related: #52 (orthography), #48, #39, #29, #11 (panel tools identity), Spec 8 (web-search seam).

---

## Phase 1 — Hypothesis

### The question

Does giving a model its provider's **native** web-search stack change how faithfully it
reproduces, locates, and verifies scripture? "Native" is load-bearing: the search a user
actually gets from Claude, ChatGPT, and Gemini is each vendor's own server-side search
(Anthropic `web_search`, OpenAI Responses-API `web_search`, Google-Search grounding) — **not**
a uniform third-party layer. OpenRouter `:online` / Exa are explicitly rejected as
unrepresentative of the real product experience.

### Pre-registered hypotheses (directional, stated before any data)

- **H1 — refusals fall.** Search-on reduces refusals on hadith (our largest refusal effect),
  i.e. **coverage rises**. Predicted direction: `coverage(on) > coverage(off)` for the hadith
  text, by ≥ 5 percentage points on at least one model.
- **H2 — citation/locus errors fall.** Search-on reduces `wrong_locus` / citation-form errors
  on `cite_passage` and `retrieve_quote`. Predicted direction: fewer `wrong_locus` failures
  on-arm than off-arm, aggregated across models.
- **H3 — edition/orthography mismatches rise.** Search-on *increases* `other_edition` and
  orthography mismatches — the model quotes whatever edition it fetched rather than the
  corpus edition. Predicted direction: more `other_edition` / orthography near-misses on-arm
  than off-arm, concentrated in the Qur'an (interacts with #52's Uthmani↔Imla'i finding).

These are **not** mutually exclusive: H2 and H3 together predict search trades citation
accuracy *up* for edition fidelity *down* — the headline-interesting outcome. The experiment
is falsifiable in each direction: an arm that moves the wrong way, or not at all, disconfirms
that hypothesis and is reported as such.

### Success / failure criteria (defined upfront)

The experiment **succeeds as an experiment** (regardless of which hypotheses hold) iff:

1. The harness runs all 336 cells live on native endpoints with **zero silently-dropped
   cells** (failed cells stay pending, run exits non-zero).
2. Search-on and search-off are a clean paired A/B: identical questions, identical panel
   identity except the `tools` axis; the arms stay distinct in the committed panel
   (`_panel_fingerprint` / `panel.tools`).
3. Provenance is captured where the APIs expose it: per-cell search-request count and cited
   URLs, recorded in the answer row's `usage`.
4. Each pre-registered hypothesis gets an explicit **confirmed / disconfirmed / inconclusive**
   verdict against the criteria above, with the per-task, per-text numbers shown — including
   the ones that cut against the hypothesis.

It **fails** if arms are confounded (e.g. a third-party search layer leaks in, or tools flip
between collect and score), if provenance is absent where the API provides it, or if any
hypothesis is scored only post-hoc without the pre-registered direction.

### Scope

**In scope**: the three implementation gaps the live run needs (OpenAI Responses-API
web_search; Gemini google_search grounding; relaxing config's anthropic-only tool fail-fast to
a per-provider *native*-tool map), the 56-question paired harness, and the dated run.

**Out of scope**: Phase-2 interpretation/recommendation; third-party search layers (rejected);
scorer changes for orthography (that is #52 — this experiment *measures* the effect, it does
not fix the scorer); adding search to the shipped `configs/models.example.yaml` (kept
anthropic-only so its reproducibility test is untouched; the 3-provider panel lives in the run
dir).

**Caveat stated up front**: live web results drift, so this arm is a **dated snapshot**, not a
reproducible artifact. The README and panel record the collection date; re-running later will
not reproduce the same fetched pages. This is inherent to measuring real search and is
declared, not hidden.

---

## Phase 2 — Design

### Approach: paired A/B, native both arms, tools the only delta

- **Questions**: the 28 Qur'an + 28 Sahih al-Bukhari questions from the committed
  `runs/original-2026-10-21/questions.jsonl`, copied **verbatim** (ids, prompts, expected,
  source all byte-identical). Qur'an carries the orthography findings (#52); Sahih al-Bukhari
  is our largest refusal effect. A `build_questions.py` filters them with a byte-exact oracle
  (reconstruct == original or fail loud), mirroring the Arabic-prompt experiment's discipline.
- **Panel** (`runs/.../models.yaml`): three models, each as a search-off + search-on pair, so
  **6 panel entries**. All on **native** endpoints (no `base_url` → the vendor's own host):
  - `claude-sonnet-5.5` (anthropic) — `web_search` server tool (already wired).
  - a current OpenAI model (openai, native) — Responses-API `web_search`.
  - gemini (`gemini-argon` or `gemini-3.8-flash`) — google_search grounding.
  Temperature pinned to 0 (joins the fingerprint). Exact model slugs are finalised when keys
  land; the design is slug-independent.
- **Arms × cells**: 56 questions × 3 models × 2 arms = **336 cells**, estimated well under $10.
- **Why native both arms**: search-off must be the *same vendor stack* with the tool simply
  absent, so the only measured delta is search — not provider, not host, not SDK.

### Dependencies

- SDKs already in `pipelines/pyproject.toml`: `anthropic>=0.40`, `openai>=1.50`,
  `google-genai>=1.0` (installed: anthropic 1.13, openai 3.28, google-genai present). No new
  deps.
- **Keys** (the one hard blocker): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`.
  `.env` currently has only `OPENROUTER_API_KEY`. Harness + dry-run proceed keyless; the live
  collect does not. Waleed to provision.

### Implementation plan

1. **`config.py`** — replace the `_ANTHROPIC_ONLY_TOOLS` fail-fast with a per-provider
   **native**-tool map: `web_search` is valid on anthropic / openai / gemini, but **rejected
   on provider=openai when `base_url` is set** (a third-party OpenAI-compatible host =
   third-party search layer, which the experiment forbids). Message names the real reason.
2. **`providers._openai`** — when `web_search` ∈ tools: call the **Responses API**
   (`client.responses.create`, `tools=[{"type":"web_search"}]`, `max_output_tokens`), require
   native (no `base_url`), fail loud on an incomplete turn (`status != "completed"`), take text
   from `output_text`, and record `web_search_requests` (count of web_search calls in `output`)
   and `citations` (url_citation annotations) into `usage`. Search-off path unchanged
   (chat.completions).
3. **`providers._gemini`** — when `web_search` ∈ tools: pass
   `tools=[Tool(google_search=GoogleSearch())]`, fail loud on a non-STOP finish, and record
   `web_search_requests` (len of `grounding_metadata.web_search_queries`) and `citations`
   (`grounding_chunks[].web.uri`) into `usage`. Search-off path unchanged.
4. **Tests** (`pipelines/tests/test_phase2_tools.py`) — update the now-wrong rejection test
   (openai+base_url+web_search must STILL reject, but as a third-party-host error); add
   native-openai and native-gemini *accept* cases; add provider-seam tests with faked SDKs for
   the Responses and grounding paths (text, usage, citations, incomplete-turn fail-loud).
5. **Harness** — `runs/exp-provider-native-search-2026-10-29/`: `build_questions.py`,
   `questions.jsonl` (56), `models.yaml` (6), `README.md`; a keyless dry-run that proves config
   loads, questions build, and the 336-cell plan is correct.

### Measurements

Per arm × model × text (and per task):
- **accuracy** = correct/(correct+incorrect) and **coverage** = (correct+incorrect)/n
  (refusal is an outcome, excluded from accuracy) — the committed scorer, untouched.
- **failure-kind mix**: `wrong_locus`, `other_edition`, orthography near-misses (via the
  existing `failure_kind` / Jev machinery) — the H2/H3 signal.
- **provenance**: per-cell search-request count and cited URLs from `usage`; aggregated
  "did search actually fire, and what did it cite" per model.

Each hypothesis → confirmed / disconfirmed / inconclusive against the Phase-1 criteria, with
the counter-evidence shown. Conclusions land in `codev/reviews/54-...md` and the run README.

---

## Design update (2026-10-29, architect-directed) — OpenRouter transport, gemini deferred

The pre-registered **hypotheses and success criteria above are unchanged.** Only the mechanism
and panel changed, on the architect's call (Waleed asked "can't we still use OpenRouter"):

- **Transport**: run through OpenRouter on the existing `OPENROUTER_API_KEY` instead of three
  native keys. This is legitimate **only because** each arm is verified per-run to forward to
  the provider's *own native* search — not OpenRouter's `:online`/Exa layer. The Baked Decision
  ("native, not a third-party layer") is preserved and enforced by a required per-arm
  verification (provider-of-record + `server_tool_use_details` + per-provider annotation shape),
  recorded in the run README. `config.py`'s guard moved from "native host only" to a
  **per-model-family** map of families OpenRouter forwards natively (`anthropic/`, `openai/`).
- **Panel**: **2 models** (sonnet + sol), 56 × 2 × 2 = **224 cells**. Matches the main panel +
  exp-arabic comparability.
- **Gemini deferred**: `google/gemini-3.8-flash` does not reliably fire native search through
  OpenRouter (routing-variance: AI Studio 429s, Vertex `finish=error`, no server-tool evidence).
  A flaky arm is not experiment-grade, so gemini is deferred to a native `GEMINI_API_KEY` — the
  pipeline's native `google_search` grounding path (`providers._gemini`) is built and tested for
  that. H1–H3 are evaluated on the 2 arms that passed verification; gemini is future work.
