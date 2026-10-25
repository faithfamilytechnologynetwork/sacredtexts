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

## 2026-10-25 — Phase 1 verify loop iter 3 (max_iterations)
- **iter 3** (re-verify): codex REQUEST_CHANGES (2 findings) + claude APPROVE (confirmed iter-2 mixed-build blocker fixed; 5 non-blocking). Folded the real ones:
  - codex #1: `_load_existing` now validates each existing row's `question_set_digest` against the set being judged (`pinned_qsd`) — a corrupted row with matching qid/model/answer but a different question-set digest no longer resume-skips as "done".
  - codex #2: negative `--limit` now fails fast (`_check_limit`, both `estimate`+`judge`) — `pending[:-1]` would have judged all-but-one, uncapping the budget guard.
  - claude #1: `summarize()` wraps a truncated-line `json.JSONDecodeError` in `JevError` (the spec's interrupt case) — clean error, not a traceback.
  - claude #2: `judge` CLI wraps corrupt-answers parse in `BadParameter`.
  - **Declined w/ evidence**: claude #4 (up-front `judge_model` requested-id equality) would break the legitimate "pin to the exact resolved build" resume (jev-latest manifest vs pinned-build arg → requested ids differ but resolved builds match); resolved build is the identity per spec. claude #3 (cosmetic already_judged count). claude #5 (trailers — tracked pre-PR).
- New tests (4): row qsd mismatch; negative-limit zero-call; summarize-truncated; CLI corrupt-answers. **Suite now 414 passed, 1 pre-existing skip.**
- This is porch's max_iterations=3 cycle — after `porch done`/`porch next` the implement loop force-advances. codex's iter-3 findings are genuinely fixed in-commit, so the force-advance does not mask an unaddressed blocker (verified per the force-advance lesson).

## 2026-10-25 — Phase 2 implement (grader seam registration + evaluator provenance), iter 1
- **Scope**: register `jev` in the Spec-15 seam, fix the del-in-finally test fixture, add the explicit
  `score --judgments` provenance opt-in, extend the CODE_WALKTHROUGH recipe. 4 source/doc + 3 test files.
- **graders.py**: replaced the commented example with the real registration
  `Grader("jev", ("matches_requested_p","refusal_p","kind"), None, default=False, inline=False)` (metric
  keys = the sidecar field names). Import-time inline-key check exempts non-inline graders, so the
  non-canonical keys are fine. `DEFAULT_EVALUATORS` excludes it (filters `default and inline`);
  `resolve_evaluators(["jev"])` fails fast ("separate-pass"). Docstring updated ("now registered").
- **test_graders.py**: killed the fixture that did `GRADERS["jev"]=…` / `del` in finally (would now
  delete the REAL entry → order-dependent failures). Split into 3 tests: jev is a real separate-pass
  registration; jev survives the module (explicit anti-regression); the metric-merge path. Dropped the
  now-unused `Grader` import.
- **jev.py**: added `load_provenance(judgments, *, question_set_digest)` — validates the sidecar's
  sibling `.manifest.json` (rubric == RUBRIC_ID, non-empty resolved build, qsd binds to the answers)
  and returns `{"model_resolved", "rubric_id"}`. Fails fast (JevError) on missing manifest / wrong
  rubric / absent build / qsd mismatch. Deliberately does NOT check index_digest (provenance is
  decoupled from index state; `_load_manifest`'s index check is for the resume path only).
- **score.py**: `score_file` gets `judgments: Path | None`. Validated EARLY (right after the digest
  checks, before scores.jsonl is written → no half-written side effect on a mismatch). Stamps
  `summary["judge"] = {"model_resolved", "rubric_id"}` as a SIBLING to `summary["evaluators"]` only
  when `--judgments` is given. `evaluators` stays list[str]; no "cost" substring enters the summary
  (uses `model_resolved`/`rubric_id`). Default `score` (no flag) is byte-identical / summary-unchanged.
- **cli.py**: `score --judgments <path>` option added, passed through both score_file call sites.
  Token-guard in test_jev (`jev.judge`/`post_decision`/`alpha/decisions`/`build_questions` forbidden in
  score.py) stays satisfied — I reference only `jev.load_provenance`.
- **CODE_WALKTHROUGH.md**: "Adding an evaluator" now has a worked Jev example (sidecar + manifest,
  non-inline/verdict-less/non-default registration, `judge` pass, explicit `--judgments` provenance).
- **Verified**: full suite via `.codev/checks/test.sh` → **423 passed, 1 pre-existing skip** (was 414;
  +9 tests), in file-order (test_graders before test_jev/test_score, jev stays registered). Committed-run
  regression/reproducibility tests still green (default score unchanged). Real-CLI smoke: `score
  --evaluator jev` → exit 2 fail-fast; `score --judgments <fixture>` → `judge` provenance present,
  `evaluators` a list, no cost field.
- **No new live spend** (phase 2 is registration/provenance only; no Decisions calls). Signalling
  phase complete next (iter 1); expect the 2-way codex+claude implement consult.

### Phase 2 iter 1 review (codex REQUEST_CHANGES / claude APPROVE) — folded
- Both converged on two substantive points; both actioned. Rebuttal: `21-phase_2-iter1-rebuttals.md`.
- **codex #1 (blocking, real)**: `load_provenance` validated only the manifest → `score --judgments`
  over an empty/absent sidecar would stamp a judge build though no verdicts exist (provenance lie).
  Fixed: require sidecar exists + ≥1 row, and every row agrees with the manifest's build + qsd via
  `_load_existing` (reuses the resume row guard; also addresses codex "row identity agrees" + reduces
  the claude #3 dup). +2 tests (empty-sidecar, row-build-mismatch). My iter-1 fixtures wrongly wrote
  EMPTY sidecars (normalising the bug) — now write a real row.
- **codex #2 / claude #1 (blocking/nonblocking, real)**: docstrings/comment/error-msg/recipe said the
  pass "merges metric_keys into scores.jsonl". Part 2 is sidecar-authoritative, merge deferred.
  Reworded graders.py docstring + registration comment + resolve_evaluators error msg + CODE_WALKTHROUGH
  (kept the `separate-pass` token the tests match).
- **claude #2 (real)**: CODE_WALKTHROUGH graders.py pointers drifted → updated to exact lines
  (GRADERS 54, Grader 38, resolve_evaluators 93, submetrics_for 119, Grader.default 42).
- **claude #3 (partial)**: removed the row-validation dup (delegate to `_load_existing`); kept the
  manifest-field checks separate ON PURPOSE — `_load_manifest` binds index_digest (resume concern),
  provenance must stay decoupled so a Phase-3 indexed sidecar is still usable for provenance.
- **claude #4 (declined, out of scope)**: provenance binds on qsd only, so a sidecar from a DIFFERENT
  collect run over the SAME question set validates. Plan scoped phase-2 to manifest fields.
  **FOLLOW-UP for a later phase/PR**: optional row-level `answer_digest` cross-check vs the specific
  answers being scored (Phase 1 records answer_digest per row, so the data is there).
- **claude #5 (partial)**: moved the mid-file import to top of test_score.py; kept the `"cost" not in`
  summary assertion (mirrors test_tutorial_run.py:66 guard) with a clarifying comment.
- Suite after folding: **425 passed, 1 pre-existing skip** via `.codev/checks/test.sh`. Real-CLI
  re-smoke: real-row sidecar → provenance stamped exit 0; empty sidecar → clean fail-fast.

### Phase 2 iter 2 review (codex REQUEST_CHANGES / claude APPROVE) — folded
- Rebuttal: `21-phase_2-iter2-rebuttals.md`. claude confirmed BOTH iter-1 blockers genuinely fixed.
- **codex #1 (blocking, real)**: my iter-1 fix leaned on `_load_existing` (checks only
  rubric/build/qsd), so a SKELETAL row with just those 3 fields keys as `(None,None,None)` — non-empty
  — and would still stamp `summary["judge"]`. Fixed: `_load_existing` gains opt-in `require_verdict`
  (resume path leaves False); `load_provenance` sets it, enforcing `_validate_verdict_row` (non-empty
  question_id/model_id/answer_digest, numeric refusal_p/matches_requested_p in [0,1], kind OR
  equivalence=not_evaluated). +2 tests (skeletal-row, missing-verdict). CLI smoke: skeletal → "row
  missing question_id; not a complete judgment".
- **claude nits**: (1) vacuous merge test → renamed + driven from `GRADERS["jev"].metric_keys` (catches
  registration↔sidecar drift); (2) bare manifest `json.loads` → wrapped in JevError in both
  `load_provenance` and `_load_manifest` (uniform fail-fast); (3) `kind` key vs `equivalence` sentinel
  → note for the deferred merge pass (no change); (4) CLI `--judgments` error → already clean via
  `main()` JevError catch (exit 2, no traceback — verified), left as-is per claude.
- claude independently verified `summary["judge"]` is viewer-safe (localResults.ts whitelists + drops
  unknowns) and committed run evidence untouched.
- Suite after folding: **427 passed, 1 pre-existing skip**. This is iter 2 of max 3.

### Phase 2 iter 3 (final) review — CLEAN PASS (codex APPROVE / claude APPROVE)
- Both APPROVE, HIGH confidence, **zero blocking issues** — a genuine clean pass, NOT a
  max_iterations force-advance disposition. claude re-verified both prior blockers fixed in-code with
  targeted regressions, the default-score byte-identity (via `test_original_run_regression.py:52`),
  and viewer safety (`localResults.ts` whitelists summary keys → unknown `judge` key dropped).
- Only non-blocking notes, all already recorded as follow-ups: (1) provenance binds on qsd not these
  answers [follow-up]; (2) `kind` vs `equivalence` sentinel for the deferred merge [follow-up];
  (3) `load_provenance`/`_load_manifest` parallel checks — added cross-reference comments in both
  (the one cheap actionable suggestion). Suite still **427 passed, 1 skip** after the comment-only edit.
- phase_2 DONE. porch advances to phase_3 (equivalence-index consumer).

### FOLLOW-UPS for a later phase / the PR (not phase-2 scope)
- Row-level `answer_digest` cross-check: `score --judgments` binds on question-set digest, so a sidecar
  from a DIFFERENT collect run over the SAME question set validates (claude iter-1 #4). Phase 1 records
  answer_digest per row → a real cross-check vs the answers being scored is feasible later.
- The deferred per-row MERGE pass (sidecar verdicts → scores.jsonl open metrics map) must handle the
  `kind` vs `equivalence: not_evaluated` asymmetry (claude iter-2 #3).
