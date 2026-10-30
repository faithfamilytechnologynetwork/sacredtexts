# arch.md — System Architecture (COLD / reference)

On-demand reference. The always-injected subset lives in `arch-critical.md`.
Seeded from Spec 1 (Phase 1 benchmark) — the first implementation round.

## Repository shape

- `pipelines/` — single `uv` project `sacredbench`; run `uv --project pipelines run
  python -m sacredbench …` from the repo root.
- `apps/viewer/` — React 19 / Vite / TS / Tailwind 4 / HeroUI v3 (provider-less) /
  TanStack; a benchmark viewer over local `runs/` (leaderboard + error explorer +
  cross-run standings). Originally seeded from multibench's multibrowser; that surface and
  its GitHub data layer have been removed (provenance in `README.multibrowser.md`).
- `texts/` — the corpus (two tiers, below). `configs/` — model panels. `runs/` — run
  evidence (gitignored except the committed first run). `codev/` — SPIR artifacts.

## Texts: two tiers + catalogue

- `texts/raw/<tradition>/` holds committed source payloads + one `source.yaml` per
  tradition. `source.yaml` is a **targets manifest** (shared provenance + a `targets:`
  list), not one flat record; each target = `{payload glob, converter, work, version,
  language, document_type, tradition[], license, license_detail?}`.
- `license` is the 3-value gate: `public-domain` / `open` / `restricted`. Restricted
  payloads (NABRE, the Greek Orthodox TLG extracts) are gitignored/local-only; their
  `source.yaml` is still committed so the catalogue stays complete and auditable.
- `texts/standardized/<source-id>/<target-slug>/` is the converted output (gitignored;
  rebuilt by `convert`). The standardized path mirrors the raw path so `generate`
  recovers a document's licence from its path. `convert`/`generate` exclude
  `restricted` targets unless `--include-restricted`.
- **Any catalogue fact `generate` needs is recovered through the path-based metadata
  channel** (`metadata_for_standardized_path` / `license_for_standardized_path`), not the
  `Document` (which carries none of it): `license`, `requested_as`, and
  `canonical_language` are its users. This is why the standardized path must mirror the raw
  path, and why a converter that re-stamps `work` (encyclicals) still resolves correctly.
- `catalogue.py`: `Target`/`Source`/`Provenance`, `discover_catalogue` (globs
  `texts/raw/**/source.yaml`), `select_targets`, path↔licence mapping; fail-fast on
  unknown licence, bad target, or missing field.

## Interchange format (working-group flat JSON)

`{source:{tradition[], work, version, language, document_type, source_url?},
entries:[{unit_type, citation, text}]}`. `tradition` is a **list** (traditions share
texts). `export.py` assembles standardized shards per `(work, version, language)`
with a tradition union, dedup by `(citation, text)`, and an inverse-grouping
round-trip that proves no invention/reordering.

## Pipeline (four subsystems, JSONL seams)

`convert` → `texts/standardized` → `generate` → `questions.jsonl` → `collect` →
`answers.jsonl` → `score` → `scores.jsonl` + `summary.{json,md}`.

- **generate.py**: four working-group templates (`retrieve_quote` / `complete_unit` /
  `cite_passage` / `verify_source`), **original-language-only by default** (a text is in the
  pool iff `language == canonical_language`; excluded texts recorded in the manifest with a
  reason); deterministic (content-derived ids, seeded); a per-text quota (`--per-text`, default
  28) split over the active templates; `<edition>` rendered as a seeded choice from the text's
  `requested_as` names; writes a `.manifest.json` (seed, params, corpus hash, question-set
  digest, selected + excluded texts). (Spec 26 retired `identify_version`/`identify_source` and
  the tradition-balanced sampler.)
- **collect.py**: concurrency-bounded fan-out; **resumable** (skips answered
  `(question_id, model_id)` cells); failed cells stay pending and the run exits
  non-zero; stamps the question-set digest on every row and refuses to resume a file
  built for a different question set. The `_panel_fingerprint` includes the `tools`
  setting (provider|model|base_url|tools), so the same model run with and without web
  search is two distinct panel entries, not one.
- **providers.py**: `anthropic` / `openai` (any OpenAI-compatible host via
  `base_url`+`api_key_env`, e.g. OpenRouter) / `gemini`; keys from env only; missing
  credentials fail before any network call; bounded retries; per-call timeout. The
  Anthropic path passes the server-side web-search tool (`web_search_20250305`,
  `max_uses: 5`) iff a spec enables it, records `web_search_requests`, and fails loud on
  a non-terminal `stop_reason` (allowlist `end_turn`/`stop_sequence`) so a truncated or
  `pause_turn` turn never silently re-bills; `_openai`/`_gemini` lack that guard (latent
  trap for a future mixed tool-using panel — the tutorial panel is all-anthropic).
- **score.py**: per-task headline contract — `retrieve_quote`/`complete_unit` → the OR of the
  SELECTED graders' verdicts (default `strict` + `containment` ⇒ `normalized OR contains_reference`,
  Spec 15; graders are named + selectable via `score --evaluator`, a paid/separate-pass grader
  expressible for #21; + exact/token-F1 reported); `verify_source` → the **leading-stance** yes/no
  equals expected; `cite_passage` → the single extracted citation must equal ground truth (a
  multi-candidate hedge scores 0; extractor chosen by the ground-truth citation shape). Every
  answered cell also carries an **outcome** (correct/incorrect/**refused**): a deterministic decline
  is `refused` and excluded from `accuracy = correct/(correct+incorrect)`, with **coverage** reported
  beside it (for `verify_source`, `refused ⟺ parsed is None`). A deliberate contract change is a
  sanctioned, oracle-witnessed rebaseline, not a forbidden re-score. **Arabic orthography
  (Uthmani↔Imla'i) is folded in the CONTAINMENT path only (Spec 52):** the text-retrieval
  `contains_reference` — and `outcomes.classify_refusal`, the FAccT counterfactual and the probes —
  share `fold_aware_contains`, which credits the same verse written in either orthography: the long-ā
  alef is made OPTIONAL at each dagger-alif/`ىٰ`-digraph position, with symmetric ى→ي / ء→ا /
  wasl ٱ→alef folds and one-word↔two-word spacing **confined to the long-ā join boundary** (whitespace
  flex only abuts an optional-long-ā position, so a multiword reference can't match a distinct single
  word — PR #62 review), matching an answer normalised by `score_normalize` (= `normalize()` + the
  symmetric folds, interleaved *before* the mark pass) in both its dagger-deleted and plene forms.
  `cite_passage` deliberately stays on `bounded_contains` (boundary-aware citation EQUALITY, not the
  verse-length fold — revisit for #39's Arabic citations); `fold_aware_contains` is the PUBLIC
  text-retrieval containment contract and `bounded_contains` its legacy/equality floor. It is a strict
  **SUPERSET** of `bounded_contains`, so the fold only ADDS credit and `normalized=1 ⇒ contains=1`
  still holds; `normalize()` and every equality submetric (`exact`/`normalized`/`token_f1`) stay
  byte-for-byte unchanged, so the question-set `ANCHOR_DIGEST` never moves (no generator drift). Two
  pre-registered under-credit residual classes, both deferred to **#60** and pinned in
  `test_orthography_rebaseline.py`: the hamza-seat `ءَا↔آ` letter gap (`HAMZA_ALEF_RESIDUAL`) and a
  verse-number-gluing tokenisation gap (`VERSE_NUMBER_RESIDUAL`, a trailing U+06DD + Arabic-Indic
  digits breaking the final word boundary). (verify_source is hardened —
  leading-stance `parse_yes_no`; **#23 PAPER GATE closed, Spec 26**.) `normalize()` is script-aware: it **deletes**
  Arabic/Hebrew combining marks (harakat/niqqud/cantillation) and tatweel and folds
  alef-wasla→alef / Hebrew maqaf→space *before* the punctuation pass, so vocalised
  non-Latin words score fairly; Latin text is byte-for-byte unchanged (a pinned
  invariance snapshot guards it). Emits per-model × task × **tradition** breakdown with a
  missing-cell roster, a `usage` block (per-model + total tokens; cost only when every
  model is priced — prices never invented), a `generated_at` (UTC ISO; the viewer's
  primary run-recency signal since issue #7 — see `lib/recency.ts`), and (with `--config`)
  a `panel` block
  (provider/model/endpoint/served_by, no secrets) where each entry carries a raw unmarked
  `model` (the API model id, no inline tool marker) plus a real `tools` list (sorted; `[]`
  when none) — Spec 11, Approach B.
- **audit.py**: see arch-critical — origin layer always; content-fingerprint layer when
  restricted payloads are present locally; `_norm` strips non-Latin marks too so Arabic/
  Hebrew/Greek unit texts fingerprint consistently (was ASCII-only, a non-Latin no-op).
- **config.py**: model-panel YAML; `ModelSpec` carries optional `price_in`/`price_out`
  and an optional `tools` list (fail-fast parse: non-list / unknown tool / `web_search`
  on a non-anthropic provider → `ConfigError`).

## Viewer local results

`apps/viewer/src/lib/localResults.ts` (`loadRun` fetches `summary.json` + `scores.jsonl`
+ `answers.jsonl` + `questions.jsonl` and joins panel × roster on `(question_id,
model_id)`, surfacing un-answered roster questions as missing cells; `loadSummary` reads
just `summary.json` for the standings rollup). As of the Spec 2 purge the viewer is
**local-only**: the multibrowser surface (`/t/...` traditions, the GitHub-data-layer
`/results`/`/raw` explorers, the `/review*` flows, and their data layer/components) is
gone. The route tree is `/` (the **leaderboard home** — `routes/LeaderboardPage.tsx` +
`components/LeaderboardTable.tsx`, ranking by `lib/leaderboard.ts`),
`/run/$runId/model/$modelId` (the **error explorer** — `routes/ExplorerPage.tsx` +
`components/QuestionList.tsx`/`ExplorerFilters.tsx`, classification/filters in
`lib/explorer.ts`), `/standings` (the **cross-run current standings** —
`routes/StandingsPage.tsx`, rollup in `lib/aggregate.ts`, keyed on the panel's
`(provider, model, tools)` identity, `${provider}\u0000${model}\u0000${sortedTools}` with
a missing `tools` defaulting to `[]`, newest run per that identity winning), plus a 404.
Because the standings key incorporates the `panel.tools` list, a model's search-on/off
variants stay distinct standings rows while two runs of the same model with the same tools
dedupe — so a bare pre-Spec-11 run collides with an explicit search-off run instead of
orphaning it (Spec 11, Approach B, which required the viewer change). The
selected run lives in the URL as a **bare run id**, `/?run=<id>` (validated by a plain
`validateSearch` fn — zod is pruned — and resolved to the fetch base
`/runs/${encodeURIComponent(id)}`); the default is the most-recent run from the
`/runs/_index` index (fetched via `lib/runIndex.ts`, shared by the leaderboard and
standings), and a `?run=` that is not a known id (e.g. the old Spec-1 `?run=/runs/<id>`
base-path form) falls back to that default. `vite.config.ts` `serveRuns()` (logic in
`vite/runsEndpoint.ts`) is a dev-only plugin serving the repo's gitignored `runs/` at
`/runs/` with a `/runs/_index` run index (confined to the runs dir; symlink traversal
rejected, so symlinked run dirs are omitted). The gate renders the committed run through
`loadRun` (`realRun.test.ts`), the leaderboard (`LeaderboardPage.test.tsx`), the explorer
(`ExplorerPage.test.tsx`), and the standings rollup (`StandingsPage.test.tsx`). Production
is a static SPA host (`server/index.mjs`, hono + history fallback; no `/api` proxy).

## Run evidence layout

`runs/<id>/`: `questions.jsonl` (+ `.manifest.json`), `answers.jsonl`, `scores.jsonl`,
`summary.json`, `summary.md`, and a `README.md` that makes the evidence self-describing.
`runs/*` is gitignored with a per-run negation for each committed-evidence dir
(`!runs/first-run-2026-10-11/`, `!runs/tutorial-2026-10-11/` — the latter the Spec-3
KJV/Qur'an(ar)/Talmud(he) 2×2 web-search on/off panel). The per-user
`configs/models.yaml` is gitignored; keys come from the environment only.

## FAccT card + edition index (Spec 32)

`edition_index.py` is the **shared cross-edition producer** (carried from PR #30's
`cross_translation.py`): it indexes same-canonical-language, non-restricted editions that share a
citation. Both consumers group identically — in-process (`EditionIndex.by_cite`, keyed on
`(work, language, raw citation)`) and the file export (`export_rows`, grouped on the same key) —
so #21 (file) and the card (in-process) can never see different sibling sets; `cite_key` /
`is_verse_citation` is only the "is this a Bible-style verse" predicate (the non-Bible guard).
`sacredbench edition-index --out <path>` writes JSONL + `.manifest.json`. **The export row/manifest
schema is frozen** (row `{work, citation, language, wordings:[{version,text}]}`, one per
`(work,citation,language)`, wordings sorted, single-wording rows omitted, `license != restricted`;
manifest `{corpus_hash, row_count, digest, excluded_restricted}`) — don't change it without #21.
`corpus_hash` is **generate's corpus hash over the full non-restricted converted set** (translations
included, before the language filter), so it equals a run manifest's `corpus_hash` for the same
corpus — #21's consumer fail-fasts unless index corpus_hash == run corpus_hash.
`facct.py` (`sacredbench facct <run_dir>` → `facct.{json,md}` beside the run) is a pure
analysis/visualisation stage: census + the three outcomes read verbatim from `scores.jsonl` + the
Bible-`retrieve_quote` edition counterfactual (reusing `score.fold_aware_contains`). The counterfactual
considers only editions in the run manifest's `selected_texts`, scoped to the question's language, so
a Bible edition added to the catalogue later cannot change a historic run's card. The card records a
`selected_corpus_hash` (generate's hash over only the run's selected editions) beside the run's
`corpus_hash`: it changes iff a *selected* edition's wording changes (the committed-card regression
test then fails — remedy: regenerate) and is unaffected by unrelated catalogue additions, so adding a
drop-in tradition leaves a historic card buildable and byte-identical. It is recorded, not enforced. It never re-scores
or calls a model, fails fast with no partial write, and writes both files atomically (the shared
`edition_index.atomic_write_texts`). All card prose is in one editable block `facct.CARD_PROSE`
(Jonathan Karr owns the wording for the FAccT paper); every number is interpolated from the run,
pinned by `test_original_run_regression.py::test_committed_facct_card_matches_the_run`.

## Test gate

Per-builder dispatcher `.codev/checks/test.sh` (global `porch.checks` is unsuitable for
a multi-app repo): routes touched dirs → `pipelines` (`uv … pytest`) and `apps/viewer`
(`pnpm … vitest`). It diffs `origin/main...HEAD`, so changes must be committed to be
tested. The pipelines pytest includes the copyright audit, which content-scans
`.json`/`.jsonl`/**`.md`** (`audit._AUDITED_SUFFIXES`) — the `.md` inclusion (Spec 32) puts the
FAccT card inside the gate; the origin layer stays structured-docs-only (a `.md` has no source
dict, and also recognises a card's `census.selected_texts` origins).
