# experiment-54 thread — provider-native search arm

Project 54 (EXPERIMENT protocol, soft mode). Issue #54.
Question: does each provider's **native** search stack change scripture fidelity?
Paired A/B (search-on vs search-off), same 56 questions (28 Qur'an + 28 Sahih al-Bukhari
from the committed `runs/original-2026-10-21` set), native APIs for both arms.

## Phase map (porch experiment protocol)
hypothesis → design → execute → analyze (gate: experiment-complete).

## Key facts learned on orientation (2026-10-29)
- `.env` (symlink → sacredtexts/.env) has ONLY `OPENROUTER_API_KEY`. The native keys
  (ANTHROPIC/OPENAI/GEMINI) are NOT provisioned. Live run (336 cells) is BLOCKED on keys;
  all code/harness/dry-run work is keyless and can proceed. Keys are Waleed's to provision.
- Anthropic `web_search` path already works end-to-end (`providers._anthropic`,
  `WEB_SEARCH_TOOL`, incomplete-turn fail-loud, usage `web_search_requests`). Spec 8 built it.
- Implementation gaps (issue §"Implementation gaps", in scope):
  1. `providers._openai`: OpenAI Responses-API web_search (native only) + usage/citations.
  2. `providers._gemini`: google_search grounding + usage/citations.
  3. `config.py`: relax the anthropic-only tool fail-fast (`_ANTHROPIC_ONLY_TOOLS`) to a
     per-provider native-tool map — web_search native on all three, but REJECTED on
     openai when `base_url` is set (that's a third-party layer: OpenRouter `:online`/Exa,
     which Waleed explicitly rejected as unrepresentative).
- Panel identity: `tools` is baked into `_panel_fingerprint` (collect.py) and emitted as a
  real `panel.tools` list (cli.py). Endpoint = `urlparse(base_url).netloc` or native default.
  Search-on/off stay distinct standings rows. Don't break this.
- Tests: `pipelines/tests/test_phase2_tools.py` is the tool-seam suite. `test_web_search_on_
  non_anthropic_rejected` will need updating (the openai+base_url case must STILL reject, but
  with a third-party-host message, not "requires provider 'anthropic'").
- Evidence rule (arch-critical): run artifacts live in `runs/<id>/`; never re-score committed
  evidence. New experiment run dir will be `runs/exp-provider-native-search-2026-10-29/`.

## Deliverables plan
- `codev/specs/54-experiment-provider-native-sea.md` — hypothesis + success criteria + design.
- Code: `config.py` + `providers.py` changes, tests in `test_phase2_tools.py`.
- `runs/exp-provider-native-search-2026-10-29/`: build_questions.py, questions.jsonl,
  models.yaml, README (points to spec; holds results when keys land).
- `codev/reviews/54-experiment-provider-native-sea.md` — analysis (BLOCKED on data).

## Log
- 2026-10-29: oriented. Starting Hypothesis phase. Key blocker flagged to architect up front.
- 2026-10-29: Hypothesis + Design spec written (codev/specs/54-...md), porch advanced
  hypothesis→design→execute.
- 2026-10-29: EXECUTE — code done. Verified every API shape in a REPL first:
  - OpenAI Responses: `client.responses.create(input=, tools=[{"type":"web_search"}],
    max_output_tokens=)`, text from `output_text`, status=="completed" gate, web_search_call
    items counted, url_citation annotations captured.
  - Gemini: `Tool(google_search=GoogleSearch())`, finish_reason.name=="STOP" gate,
    `grounding_metadata.web_search_queries` (count) + `grounding_chunks[].web.uri` (citations).
  - config.py: `_NATIVE_SEARCH_PROVIDERS` map + base_url guard (openai+base_url+web_search
    rejected as third-party host).
  - Provenance lands in `usage` dict: `web_search_requests` + `citations` (deduped), same
    shape the Anthropic path already used.
  Tests: updated the now-wrong rejection test, added native-accept + full Responses/grounding
  seam tests (faked SDKs). Full suite: 572 passed, 2 pre-existing skips.
- 2026-10-29: EXECUTE — harness built + committed (2 commits: 651e64b code/tests, 803f3a0
  harness). runs/exp-provider-native-search-2026-10-29/: 56 questions (digest 64ce2d44f418e0c0,
  28 Qur'an + 28 Bukhari, verbatim, oracle passed), models.yaml (6 entries, native, temp 0),
  dry_run.py (validates 336 cells + distinct fingerprints keyless), README. Allow-listed in
  .gitignore. Copyright audit OK (origin-only). Full porch test-dispatcher: 572 passed.
  Model slugs in models.yaml marked (confirm) — finalise when keys land (gpt-6.1, gemini-3.8-
  flash are placeholders; design is slug-independent).
- 2026-10-29: **BLOCKED** — execute's gather_data + the whole analyze phase need native keys
  (ANTHROPIC/OPENAI/GEMINI) that aren't provisioned. NOT advancing porch past execute (would
  falsely claim data gathered) and NOT touching the experiment-complete gate. Stopped, notified
  architect, waiting. All keyless deliverables done; porch phase stays at `execute` until the
  live run can run. Resume path: keys in env → run README's recipe (collect → score) → fill
  Results + write codev/reviews/54-...md → `porch done 54` to analyze → gate.
