# Phase 2 runbook — one clean motion after #48 merges

Pre-drafted during the hold (architect: #48 lands first, then rebase + re-run witness). Execute
top-to-bottom the moment the architect pings that #48 is merged. The scorer *capability*
(`fold_aware_contains`, `score_normalize`, `_answer_plene_form`) already landed in Phase 1; Phase 2
only **wires** it and does the **single atomic rebaseline**. The design is containment-only, so the
blast radius is: `contains_reference`, headline `correct`, and `outcome` — `exact`/`normalized`/
`token_f1` and all non-Arabic cells are frozen.

## 0. Rebase onto the post-#48 baseline

```bash
git fetch origin main
git rebase origin/main            # picks up #48's tutorial rebaseline + its re-pinned constants
uv --project pipelines run pytest pipelines -q   # expect green on the merged baseline BEFORE my changes
```
If the rebase conflicts in `pipelines/tests/test_contains_reference_rebaseline.py` (the file #48
re-pinned), take #48's tutorial constants and layer my orthography changes on top — do NOT revert
#48's REFUSED_COUNTS/EXPECTED_ACC/EXPECTED_COV/REFUSED_SET_SHA256.

## 1. Capture pre-change oracles BEFORE any write (non-circular witness)

Freeze from the **post-#48, pre-my-change** committed scores (mirrors #48's method):
```bash
# for each run in first-run-2026-10-11 tutorial-2026-10-11 original-2026-10-21 exp-arabic-prompts-2026-10-29
#   SHA over the (model_id, question_id, task) -> (exact, normalized, token_f1) projection  [MUST stay identical]
#   SHA over (model_id, question_id) -> (contains_reference, correct, outcome)               [the movers]
```
Ready-to-run capture (paste into `uv --project pipelines run python -`), reads `git show HEAD:` so
it is genuinely pre-change; paste the printed SIMILARITY SHA into the new witness as the frozen
oracle:
```python
import json, hashlib, subprocess
def arabic(s): return any('؀'<=c<='ۿ' or 'ݐ'<=c<='ݿ' or 'ࢠ'<=c<='ࣿ' for c in s)
for run in ["first-run-2026-10-11","tutorial-2026-10-11","original-2026-10-21"]:
    raw = subprocess.run(["git","show",f"HEAD:runs/{run}/scores.jsonl"],capture_output=True,text=True).stdout
    rows = [json.loads(l) for l in raw.splitlines() if l.strip()]
    sim = sorted((r["model_id"],r["question_id"],r["task"],
                  r["metrics"].get("exact"),r["metrics"].get("normalized"),r["metrics"].get("token_f1"))
                 for r in rows)
    mov = sorted((r["model_id"],r["question_id"],
                  r["metrics"].get("contains_reference"),r["metrics"].get("correct"),r["metrics"].get("outcome"))
                 for r in rows)
    h=lambda x: hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    print(run, "SIM", h(sim), "MOV", h(mov))
```
(The exp run uses `scores-en.jsonl`/`scores-ar.jsonl` — capture those separately.)

## 2. Wire the scorer (the only logic change)

`pipelines/sacredbench/score.py`:
- `score_answer`: `contains_reference` → `int(bool(normalize(target)) and fold_aware_contains(answer, target))`.
- `cite_passage` verdict (`_single_citation_correct` → `bounded_contains`) → `fold_aware_contains`.
  Leave `_citation_candidates`/boundary regex on `normalize` (citation extraction is regex-shaped).
- `outcomes.classify_refusal:133`, `facct.py:277`, `probes.py:203` → `fold_aware_contains` for the
  one shared containment contract. (Under the default `strict`+`containment` graders a contained
  cell already has `correct=1`, so the `outcomes` change only bites under `--evaluator strict` — but
  make it consistent.)
- Do NOT touch `normalize`, `exact`, `normalized`, `token_f1`.

Run the fold-capability tests (`test_arabic_orthography_fold.py`) — still green.

## 3. Regenerate committed evidence (SURGICAL — mind the summary scar)

For each run that has Arabic movers (expect: tutorial, original, exp; first-run only its 2 Arabic
answers — check): regenerate `scores.jsonl` via `score_file`. For `summary.json`/`summary.md` DO
NOT regenerate wholesale — a naive renderer nulls the panel and emits extra `max_tokens`/`temperature`
columns that break `test_committed_summary_md`/`test_panel` (aspir-48 scar). **Surgically splice**
only the moved numeric leaves (accuracy/coverage/correct/contains_reference counts), keeping
`panel`/`usage`/`generated_at`/`expected_n`/`missing` byte-verbatim and the summary.md panel table
byte-identical. For tutorial, splice on top of #48's already-spliced file.

Derived artifacts:
- `original-2026-10-21/facct.{json,md}` — regenerate (its edition counterfactual uses
  `bounded_contains`→now fold-aware); `test_original_run_regression.py` facct assert re-pins.
- `tutorial-2026-10-11/jev_agreement.{json,md}` — its confusion matrix is computed against
  `contains_reference`; the 27 `judge_only` orthographic near-misses are this fold's target, so it
  moves. Regenerate and note the moved headline.
- `exp-arabic-prompts-2026-10-29/`: FIRST fix `analyze.py:14`'s `sys.path.insert` to a repo-relative
  path (else it re-scores with the MAIN checkout's scorer), then re-run it. Keep
  `answers-ar-normalized.jsonl` as provenance; preserve the README's pre-fold headline as *pre-fold*;
  cross-check against the README's prototype re-score.

## 4. Re-pin oracles + add the witness

- `test_contains_reference_rebaseline.py`: the `(exact, normalized, token_f1)` projection SHA is
  UNCHANGED (confirm it still passes as-is). Re-pin `FLIP_SET` (+ check first-run's 2 Arabic cells,
  gemma-3-4b/llama-3.1-8b), the superset invariant, and `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`;
  update any Arabic `refused` reclassifications.
- NEW `test_orthography_rebaseline.py`: (1) full `(exact,normalized,token_f1)` projection SHA frozen
  from the pre-change (post-#48) scores — must be IDENTICAL; (2) the pre-registered set of Arabic
  cells whose `contains_reference`/`correct`/`outcome` moved; (3) pinned rebaselined
  accuracies/coverages; (4) summary self-consistency.
- `test_first_run_regression.py`, `test_tutorial_run.py`: re-pin the byte-for-byte re-score asserts.
- `test_original_run_regression.py`: re-pin re-score + facct; confirm `ANCHOR_DIGEST` UNCHANGED
  (generation untouched); cite_passage decline survey pin unaffected.
- `apps/viewer/src/local/tutorialRun.test.ts`: re-pin moved tutorial numbers. Make
  `.codev/checks/test.sh` map `runs`→BOTH lanes, and run `pnpm -C apps/viewer test` explicitly.

## 5. Hand-verify + gates

- Hand-inspect EVERY moved Arabic cell against its verse before freezing the flip set (the
  no-wrong-credit gate at scoring granularity). Record the method + the moved-numbers table in the
  review doc.
- `bash .codev/checks/test.sh` green (both lanes); copyright audit passes; no restricted-derived
  artifact committed.
- `afx send architect` the moved-numbers packet BEFORE the PR (hard gate).

## 6. Commit

One atomic `[Spec 52][Phase: implement]` commit for the scoring-contract change + regenerated
evidence + oracles. Then Phase 3 (governance docs) and the PR.
