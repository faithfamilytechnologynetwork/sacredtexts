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

## Status
- specify: spec drafted at codev/specs/32-facct-benchmark-card-cross-edi.md. Acked architect brief. Awaiting porch 3-way consult.
