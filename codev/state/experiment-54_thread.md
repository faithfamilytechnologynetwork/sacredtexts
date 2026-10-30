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
- 2026-10-29: architect reply — (b) slugs CONFIRMED: Claude=claude-sonnet-5-5,
  Gemini=gemini-3.8-flash (both already set); OpenAI=native flagship in the gpt-6.1-sol
  family (gpt-6.1 = right family, exact native id fail-fasts at first collect). Comparability
  with main panel + exp-arabic (sonnet+sol) is the tiebreaker. Recorded in models.yaml.
  (c) HOLD the PR — ship code + live evidence together; if keys haven't landed within ~24h
  (≈2026-10-30 17:30Z) architect will have me open a deferred code+harness PR (Refs #54, live
  run deferred). (a) keys with Waleed. STILL WAITING on keys; nothing to advance.
- 2026-10-29 (later): architect UNBLOCK — run on the EXISTING OpenRouter key; native search
  *transported* through OpenRouter (NOT the :online/Exa layer). Directed: adapt harness to
  OpenRouter (one provider=openai, base_url=openrouter, per-model tool shape; config map keyed
  on model FAMILY not native host). REQUIRED per-arm nativeness verification in README before
  the paid run; STOP+surface any arm that looks like a generic Exa layer. Live run GO once
  dry-run passes; <$10, temp 0.
- 2026-10-29: ran the REQUIRED verification myself (3 live OpenRouter probes, ~$0.09; raw in
  scratchpad/probe_results.json). VERDICT:
  - anthropic/claude-sonnet-5.5 (Anthropic native block): provider "Claude Platform on AWS",
    server_tool_use_details.web_search_requests=1, 3 url_citations WITH content snippets →
    NATIVE ✓
  - openai/gpt-6.1-sol ({"type":"web_search"}): provider OpenAI, web_search_requests=2, 1
    url_citation WITH char start/end_index (no content) → NATIVE ✓
  - google/gemini-3.8-flash ({"type":"web_search"}): finish_reason=ERROR, NO
    server_tool_use_details, 0 citations, cost 0 → FAILS. Contradicts the architect's probe
    claim. Does NOT go native through OpenRouter.
  KEY EVIDENCE it's not a uniform Exa layer: the anthropic vs openai annotation structures
  DIFFER per provider (content-snippet vs char-offset) — a single OpenRouter/Exa layer would
  return identical shapes. So sonnet+sol are genuinely each provider's native search.
  → STOPPED the gemini arm, surfaced to architect. Recommending: 2-model OpenRouter run now
  (sonnet+sol, matches exp-arabic comparability), defer gemini to a native GEMINI_API_KEY (my
  native grounding path is built+tested). Awaiting scope confirm before rework + paid run.
  Did NOT do the code rework or paid run yet (money + scope-down are the architect's call).
- 2026-10-29: architect: do ONE bounded gemini rescue with OpenRouter provider pinning (AI
  Studio vs Vertex); keep gemini only if a backend fires 2/2, else drop + record + GO on the
  2-model paid collect (no more holds). RESCUE RESULT: AI Studio 429 (4/4 across rescue+fair
  retry, shared-pool rate limit), Vertex finish=error/no-search (2/2). Neither passes →
  DROPPED gemini, deferred to native GEMINI_API_KEY.
- 2026-10-29: EXECUTE rework DONE + committed (5cc089b). config.py: web_search guard on an
  OpenAI-compatible host → per-model-FAMILY map (anthropic/, openai/ forwarded natively;
  google/* rejected). providers.py: _openai routes web_search+base_url → _openai_openrouter_
  search (chat.completions, Anthropic native block for anthropic/*, {type:web_search} else;
  records provider-of-record + web_search count + citations; non-stop finish fails loud).
  Native Responses + Gemini grounding paths kept for native-key runs. models.yaml = 2-model
  OpenRouter panel (sonnet+sol, 224 cells). README has the required per-arm nativeness
  verification table. Spec addendum records the pivot (hypotheses unchanged). 578 tests pass.
- 2026-10-29: live collect DONE — 224/224 cells, zero failures (first attempt used wrong CLI:
  `collect` takes `config` POSITIONAL not `--config`; README recipe fixed). Nativeness re-proven
  per cell: served_by = Claude Platform on AWS / OpenAI, per-cell server_tool_use + citations.
  Search fired: sonnet 14/56, sol 49/56. Scored with committed deterministic scorer. analyze.py
  → analysis.json. Committed evidence (717d4cb).
- FINDINGS (n=28/text/arm, directional): search helps the model that USES it (sol +9pp overall,
  +29pp complete_unit) and barely moves sonnet (searched 14/56, -4pp within noise). H1 CONFIRMED
  narrowly (sonnet hadith cov 78.6->85.7%, refusals 6->4, recovered cells mostly wrong → acc
  fell). H2 DISCONFIRMED (cite_passage/wrong_locus flat every arm). H3 mixed/mostly disconfirmed
  (orthography other_script did NOT rise; sol gained 3 wrong_passage on-arm). Headline: provider
  search-PROPENSITY, not just quality, drives the delta. Full writeup: run README + review.
- NEXT: porch done execute→analyze; analyze work is the committed review; porch done analyze
  reaches the experiment-complete GATE (human approval) → notify architect + STOP (do NOT self-
  approve). Gemini remains deferred to a native GEMINI_API_KEY (native grounding path ready).
- 2026-10-29: reached experiment-complete GATE (WAITING FOR HUMAN APPROVAL). Notified architect.
  Architect: HOLD at gate (Waleed's call); PROTOCOL CORRECTION — builders NEVER run `porch
  approve`; the ARCHITECT runs it after Waleed approves. So I will not run porch approve.
- 2026-10-29: architect: open the PR now. Opened **PR #59** (builder/experiment-54 → main,
  Refs #54, gemini-native deferred, nativeness-verification method credited in the body, no
  attribution lines per CLAUDE.md). Branch already pushed (porch auto-commits reach origin).
  PR goes through the architect's integration review + the normal pr gate. Did NOT run `porch
  done --pr` (parked at the experiment-complete gate; not risking gate-state mutation — architect
  manages the pr gate). HOLDING: (1) Waleed's experiment-complete approval → architect runs
  porch approve; (2) architect's PR review. Nothing further for me to do until then.
- 2026-10-29: architect: PR #59 stale vs main (today's merges: #51 SGGS, #55 refusal semantics/
  Spec 48, #57/#58, canary relocation b93e881). Rebased builder/experiment-54 onto origin/main
  — clean, 14/14, NO conflicts (zero file overlap between main's changes and my surfaces). Full
  gate green: 627 passed, 2 skipped. **Spec 48 refusal-semantics check**: re-scored the same
  answers with the current scorer to a temp path — numbers are BYTE-IDENTICAL to committed
  (sonnet refusals stay 6/4; they're class-B declines-with-substitute, NOT class-A memory
  deliveries that flip refused→incorrect). So no rebaseline, H1/H2/H3 unchanged, committed
  evidence reproduces on current main. Force-pushed (--force-with-lease, sanctioned; branch now
  on b93e881). Doc-sync note flagged to architect: arch-critical.md line 9 still says
  'config.py fail-fasts a tool on a non-anthropic provider' — my PR refines that to the
  family-map; governance-doc update is MAINTAIN's/architect's call, not edited in this PR.
- 2026-10-29: PR #59 round-1 integration review — folded ALL 10 items (commit 993e5f0):
  (1) host-pin guard (config._SEARCH_FORWARDING_HOST_NETLOCS=openrouter.ai + forwarded family;
  arbitrary base_url rejected); (2) H3 → INCONCLUSIVE (other_script is Unicode-script, not
  orthography; wrong_passage is overlap, not edition) in README+review; (3) corrected false
  cost claim in models.yaml + ADDED cost capture to _openrouter_usage for future collects;
  (4) mechanical nativeness gate providers._assert_native_arm (provider-of-record + citation
  shape per family, fail-loud at collect) + citation_style in usage; (5) models.example.yaml
  comment restated; (6) spec header→COMPLETE, dry_run docstring→4/224, PR body→630/190;
  (7) arch-critical.md line 9 restated to the native-search rule; (8) native Responses/grounding
  paths labelled seam-tested/awaiting-live-smoke; (9) single source of truth
  providers.OPENROUTER_SEARCH_TOOL_BY_FAMILY (config derives allowlist via local import);
  (10) viewer excludes exp-* from standings+default home (isExperimentRun/benchmarkRuns, openable
  via ?run=) +tests. Both lanes green via dispatcher: pipelines 630, viewer 190. Committed run's
  112 search-on rows all pass the new provider check (gate consistent with evidence). Findings
  UNCHANGED (H3 relabel is wording). PR body refreshed. Pushed 993e5f0. Awaiting round-2 review
  + Waleed's gate.
