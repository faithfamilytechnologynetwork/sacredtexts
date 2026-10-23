# aspir-21 — Jev-based evaluator (Spec 21)

Protocol: ASPIR (strict). Part 2 of 3 of Jonathan Karr's PR #30 (the Jev judge).

## 2026-10-23 — Specify phase

### Architect brief (treated as baked)
- Reuse Karr's PR #30 judge code where it fits; keep his authorship on carried-over commits (`git commit --author`).
- Land through the Spec 15 graders seam (`graders.py`, `score --evaluator`): a **separate-pass, paid grader, NEVER default**.
- Refusal stays an **OUTCOME** (`outcomes.py`), not a grader. Judge contributes verdict on **containment + passage-equivalence only**.
- Live verification mandatory before acceptance criteria; derive shape from the real response; fail fast; no fallbacks.
- Budget: ≤ $8 live spend for this spec; stop + ping above it.
- Never re-run collect/score over committed run evidence (`runs/original-2026-10-21`, `runs/tutorial-2026-10-11`); judge output → fresh `runs/<id>/` or a sidecar; committed `scores.jsonl` byte-identical.
- Public repo: no key material, no NABRE/TLG text in any committed artifact.
- PR: "Part 2 of 3 of #30", close #21, no Generated-with / Co-Authored-By lines. Ping architect with spec summary before plan.

### Live verification (DONE — total spend ≈ $0.00005, far under $8 cap)
- Working decisions model id is **`jev-latest`** → resolves to build **`typesafe/jev-1.14-20261014`**.
- **Both `typesafe/jev-1.13` (Karr's JEV_MODEL) and `typesafe/jev-router` (architect's note) FAIL** on `POST https://openrouter.ai/api/alpha/decisions` with `{"error":{"message":"Model ... does not exist","code":400}}`.
  - `typesafe/jev-router` IS in `v1/models` but has `endpoints: []` and pricing `-1/-1` (no servable endpoint).
- Real HTTP-200 response shape **matches Karr's `interpret()` exactly**:
  `{model, provider:"TypeSafe", id, answers:{refusal:{type:noul,noul:p}, matches_requested:{type:noul,noul:p}, kind:{type:choice,choice,probabilities{...},confidence}}, usage:{input_tokens,output_tokens,cost}}`.
  A 3-question call cost ~$0.0000269.
- Conclusion: the ONLY required change to Karr's `jev.py` is `JEV_MODEL`. Everything else (QUESTIONS, interpret, resumable append keyed on rubric_id, post_decision retry policy) verified correct against the wire.

### Key dependency / open question for the spec
- `jev.py` imports `EditionIndex, cite_key` from `cross_translation` for the passage-equivalence `indexed_other_wordings`. **`cross_translation.py` is NOT on main** — it is a sibling part of the #30 split. `outcomes.py` IS on main.
  - Options to resolve: (a) make the edition index optional — containment + refusal-diagnostic work without it, equivalence's `other_indexed_wording` label never fires; (b) vendor a minimal citation→wordings index from the committed question pool; (c) sequence equivalence after the cross-translation part lands.
  - Surfaced to architect in the spec's Open Questions (Critical).

### State on main
- `graders.py` already models the non-inline `jev` grader seam (commented example, `inline=False`, verdict-less, `default=False`); `resolve_evaluators` fails fast if a non-inline grader is selected inline on `score`.
- `score.py` writes per-row `metrics` map that a separate pass can merge into.
- `outcomes.py` owns refusal (`classify_refusal`, `_with_outcome`).
