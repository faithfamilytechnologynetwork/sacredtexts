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

## 2026-10-23 — Specify DONE, holding before plan
- Spec drafted, 2-way consult (codex REQUEST_CHANGES / claude COMMENT) folded (13 points, all actioned), rebuttal written. `porch done` advanced phase to **plan**.
- Commits: initial draft / with-review / rebuttal.
- Pinged architect with spec summary + 2 decisions: (1) model id must be `jev-latest` not jev-1.13/jev-router; (2) Critical scope call on the passage-equivalence edition index (option (a) provisionally taken vs (b) vendor minimal index).
- **HOLDING: do not start plan work until architect answers the scope question** (per brief: "ping me with the spec summary before the plan phase").

## 2026-10-24 — Plan phase
- Architect answered both decisions (00:00 + 00:01 addendum): jev-latest + resolved-build-as-identity (fail-fast on build-mismatch resume, no mixed-build files); equivalence OFF unless --equivalence-index, records not_evaluated; consume **#32's index schema VERBATIM** (JSONL {work,citation,language,wordings:[{version,text}]} + <path>.manifest.json {corpus_hash,row_count,digest,excluded_restricted}; fail fast on missing manifest / corpus_hash mismatch vs run manifest; record index digest per row; hand-written fixture, no #32 branch dep; drop cross_translation import). Live validation pre-flight shown to architect before the pass; refusal_p diagnostic only.
- Folded all into spec → committed "[Spec 21] Specification with user feedback"; acked architect.
- Karr authorship for carried code: `Jonathan Karr <jka83321@gmail.com>` (from PR #30 commits) → use `git commit --author` on the jev.py commit.
- Wrote plan (4 phases): (1) Jev judge pass + CLI [Karr authorship], (2) grader registration + evaluator provenance + recipe, (3) equivalence-index consumer (#32 schema), (4) validation on committed tutorial run. Committed "[Spec 21] Initial implementation plan". PLAN_DRAFTED signalled; porch ran plan checks OK.
- 2-way plan consult (codex+claude) running in background.

## 2026-10-24 — Plan DONE → implement/phase_1
- 2-way plan consult: both REQUEST_CHANGES (codex 7 issues, claude 9), both code-grounded + complementary. Folded all 16 into plan ("[Spec 21] Plan with multi-agent review"), rebuttal written. "Repo moved" banner in both = my own thread/porch commits, plan file untouched — verified via git log.
- Key plan refinements: explicit `score --judgments <path>` provenance opt-in (NO implicit sidecar discovery) w/ build in a NEW sibling summary key (evaluators stays list[str], no cost field — test_tutorial_run.py:66 guards it); fix test_graders.py del-in-finally that would delete the real jev registration; grader metric_keys = sidecar names (matches_requested_p/refusal_p/kind); index_digest in sidecar manifest identity + resume fail-fast; --equivalence-index moved to Phase 3 w/ explicit --questions source for corpus_hash (answers lack it; lives in questions.jsonl.manifest.json); PR#30 retrieval path + local cite_key reimpl (drop cross_translation import); keep summarize(); 1-cell live smoke at end of Phase 1; agreement = tested module; generated_at defeats summary byte-identity (compare modulo timestamp; Phase 4 never re-runs score so git diff must be empty).
- porch advanced to IMPLEMENT phase_1 "Jev judge pass and CLI".
- Karr authorship: `git commit --author="Jonathan Karr <jka83321@gmail.com>"` on the jev.py commit.
- HOLD POINT remains: Phase 4 live pass needs architect pre-flight sign-off (~$0.011, 400 cells).

## 2026-10-24 — Phase 1 DONE (Jev judge pass + CLI)
- `jev.py` (carried from Karr, corrected), `cli.py` judge/judge-summary, `test_jev.py` (13 tests), fixture `testdata/jev_decision_sample.json`, TUTORIAL/README judge step. Full suite: 399 passed, 1 pre-existing skip.
- Pre-flight dry run on committed tutorial answers = 400 cells ~$0.0108 (matches plan). Refuses to spend without --yes.
- Committed authored by **Jonathan Karr <jka83321@gmail.com>** (carries his code) — `[Spec 21][Phase 1]`.
- **TODO before PR**: strip `Co-Authored-By: Claude Opus 4.8` trailers from my earlier spec/plan/thread/rebuttal commits — global CLAUDE.md + architect brief both say NO Co-Authored-By. I wrongly added them during spec/plan; stopped as of Phase 1. Clean the branch history (message-only rewrite, tree unchanged) just before opening the PR, verify with git log.

## 2026-10-25 — Phase 1 verify loop (iter 1 + iter 2)
- **iter 1** (review): codex REQUEST_CHANGES + claude REQUEST_CHANGES, both code-grounded. Folded all (total spend surfaced; manifest-less sidecar fail-fast; flat `kind` schema; strict fail-loud `interpret`; `--limit`/concurrency/missing-manifest/cost-sum tests; exact qsd equality). Rebuttal written; Phase-1 commit (Karr authorship) amended → `a7d33b2`. Suite 403 passed.
- **Phase-1 single-cell live smoke RAN** (the required real-path check): `judge runs/tutorial-2026-10-11/answers.jsonl --limit 1 --yes` → scratch sidecar, committed evidence untouched. Tutorial's first cell (a refusal) judged `refusal_p=0.97 / matches_requested_p=0.03 / equivalence not_evaluated`; resolved build `typesafe/jev-1.14-20261014`, manifest written, spend **$0.000027**. Total project live spend ≈ **$0.00008**, far under the $8 cap. Pre-flight on full committed tutorial answers = 400 cells ≈ **$0.0108** (matches plan).
- **Git divergence resolved**: I had `--amend`ed `fe1e929` after porch pushed it, so the branch diverged from origin. Human (Waleed, relayed by architect main) APPROVED `git push --force-with-lease origin builder/aspir-21` for this branch only — ran it, lease held (`2d41f03...29a11e1`), branch reconciled. Lesson: never amend a commit porch has already pushed.
- **iter 2** (re-verify): codex REQUEST_CHANGES (1 blocking) + claude APPROVE (5 non-blocking). Both converged on the mixed-build invariant. Folded all:
  - codex (blocking): `_load_existing` now validates every existing row's `judge_model_resolved` against the manifest's pinned build (and rejects a row missing it) — a hand-edited/half-written mixed-build file is refused on resume, not trusted + extended.
  - claude #4: `_load_manifest` now requires a non-empty `judge_model_resolved` (a manifest lacking it could let the next response re-pin — same hole, manifest side).
  - claude #1: `judge-summary` on a missing sidecar → clean `BadParameter` (was zeros + exit 0).
  - claude #2: `judge` on a missing answers file → `input path not found` (was raw `FileNotFoundError`).
  - claude #3: `--yes` budget gate now has a CLI test (`CliRunner`) — no `--yes` ⇒ exit 2, `jev.judge` never called, nothing written.
  - claude #5: `_single_question_set_digest` now fails on a present/absent digest mix (all-or-none).
- New tests (7): existing-row build mismatch / missing-build / manifest-without-build / mixed-digest-presence; CLI `--yes` gate / missing-answers / missing-sidecar. **Suite now 410 passed, 1 pre-existing skip.**
- **TODO before PR** (unchanged): strip `Co-Authored-By: Claude Opus 4.8` trailers from earlier spec/plan/thread/rebuttal commits (message-only rewrite, tree unchanged); expect cli.py textual conflict with #34 on next rebase onto main (whoever merges second rebases).
