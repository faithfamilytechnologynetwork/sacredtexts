# Builder aspir-32 thread — FAccT benchmark card + cross-edition reading (#32)

Part 3 of 3 of Jonathan Karr's PR #30. Rework his card against main's scoring contract.

## Key facts established (specify phase, 2026-10-23)
- Data source: `runs/original-2026-10-21/` (3 models: gpt-oss-20b, haiku, opus; 476 Q; 17 texts). Read as-is, NEVER re-score/collect/generate.
- Outcomes come from `scores.jsonl` `metrics.outcome ∈ {correct,incorrect,refused}` (set once in `outcomes.py`). NO second refusal regex, NO `fabrication` label.
- Headline = containment contract (Spec 15). `evaluators: ["strict","containment"]`.
- Census source: manifest `selected_texts`(17) + `excluded_texts`(2, with reasons) + catalogue `source.yaml` (license, canonical language, zero-question languages).
- Embedded question `expected` holds only `citation` (NOT text) → gold text resolves from raw editions index by citation.
- Edition counterfactual: only the 3 English Bibles (KJV/ASV1901/WEB) have sibling editions in this pool → counterfactual is inherently Bible-scoped. `cite_key` already parses Bible-style citations. Arabic/Hebrew citations excluded by construction (no sibling edition) — card must SAY so, never mis-parse them into a Bible match. Tag qualifying misses `other_edition`.
- Prose in ONE editable place (Jonathan drafting paper). Chose: constants block in facct.py (Approach 1).
- Output path: `runs/<id>/facct.{json,md}`. Zero API spend. Audit (audit.py) must pass — no NABRE/TLG text. Public repo.
- Preserve Jonathan's authorship on carried-over commits (`git commit --author`). PR: "Part 3 of 3 of #30", closes #32. NO Generated-with/Co-Authored-By.
- Viewer per-run card view = optional (reads facct.json, no new scoring). Likely defer.

## Spec consult (specify iter1, 2026-10-23) — both REQUEST_CHANGES, HIGH. All folded in.
codex + claude both verified against real data. Dispositions (ACCEPTED all):
1. `expected` schema is TASK-DEPENDENT (claude, verified): retrieve_quote→{text}, complete_unit→{text,full_text}, cite_passage→{citation}, verify_source→{answer,true_*}. Citation always in source.citation. Gold wording for retrieve_quote = expected.text (NOT only raw index). Fixed Assumptions.
2. Edition counterfactual scoped to retrieve_quote ONLY (both). complete_unit gold is partial → no well-defined sibling segment. Incorrect Bible cells: 32 retrieve_quote + 21 complete_unit = 53 (verified). Report numerator AND denominator per model.
3. Open Q1 resolved: containment (exact is subset of containment — Q was ill-posed). other_edition = a DIFFERENT edition than requested (requested would already be correct).
4. Restricted-index guard: real gate is select_targets(include_restricted=False)/license!=restricted on the EditionIndex, NOT pool exclusion. NABRE = 4th English Bible (work=The Bible, canonical_language=en) → indexable sibling if payload present. Added explicit filter + test criterion.
5. Problem Statement factual fix (codex): run does NOT contain Vatican docs/English Talmud — those are EXCLUDED catalogue members. Reframed as catalogue coverage vs run composition.
6. Zero-question languages (codex): disambiguated to catalogue SOURCE languages (each source's `language` field) contributing zero to pool.
7. Fail-fast (codex): non-zero exit, no partial facct.{json,md}, on missing files / non-joining rows / scores↔summary disagreement. Added criterion + test + risk.
8. Join mechanics (claude): scores.jsonl rows have no text identity → join answers.jsonl on (question_id,model_id); sub-metrics are task-scoped. Added to Assumptions.
Structure verified conformant to spir/templates/spec.md (claude).

## Architect GO + 3 tweaks (2026-10-24) — folded into spec
1. EditionIndex = SHARED standalone module (for #21). CLI `sacredbench edition-index --out <path>` → JSONL + manifest, mirrors questions.jsonl convention. FROZEN schema:
   row: {work, citation, language, wordings:[{version,text},...]} — one row per (work,citation,language); wordings sorted by version; same-canonical-language editions only; license!=restricted (NABRE never appears); single-wording rows omitted.
   manifest <path>.manifest.json: {corpus_hash, row_count, digest(sha256 prefix of file), excluded_restricted:[version ids]}.
   Card builds counterfactual from this module in-process; file export is for #21. Test: restricted payload present locally never reaches file + named in excluded_restricted.
2. Viewer card view DROPPED entirely (out of scope; its own issue if wanted). No half-scoped items.
3. Every number in facct.md derived at build time from scores.jsonl/summary.json, never typed. Test: card headline figures == summary.json (anti-drift, cf Spec 26 docstring drift).

## Status
- specify: architect GO received + 3 tweaks folded. Committing "[Spec 32] Specification with user feedback". ASPIR has no spec gate → proceeding to PLAN phase.
