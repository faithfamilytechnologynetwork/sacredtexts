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

## 2026-10-25 — Phase 3 implement (equivalence-index consumer), iter 1
- **Context**: phase-1 had ALREADY wired most of the index plumbing (`judge(index=,index_digest=)`,
  `with_equivalence=index is not None`, `KIND_Q`, `judgment_state` sets `indexed_other_wordings`,
  sidecar manifest + per-row `index_digest`, `_load_manifest` resume fail-fast on `index_digest`).
  phase-3 added the CONSUMER + CLI + keying + tests.
- **jev.py**: new `EquivalenceIndex` class (lookup keyed `(work,citation,language)`; `.wordings(work,
  citation,language,expected_text)` returns OTHER wordings, excluding the requested by exact text) +
  `load_equivalence_index(path, *, run_corpus_hash)` consuming #32's schema VERBATIM (JSONL
  `{work,citation,language,wordings:[{version,text}]}` + `<path>.manifest.json`
  `{corpus_hash,row_count,digest,excluded_restricted}`). Fail-fast: missing manifest / missing file /
  `corpus_hash` mismatch vs run / malformed row / dup `(work,citation,language)` / `row_count`
  disagreement. `_alternates` + `run_cell` now key on work+language (were citation-only). Module
  docstring updated ("consuming #32's schema", not "wired in a later phase").
- **cli.py**: `judge` gains `--equivalence-index <path>` + `--questions <path>` (the corpus_hash source
  — answers carry NO corpus_hash; it lives only in `questions.jsonl.manifest.json`, located by the
  explicit option, never co-location-guessed). New `_run_corpus_hash(questions)` helper. `index`/
  `index_digest` threaded into both `estimate` and `judge`. `--equivalence-index` without `--questions`
  (and vice-versa) → `BadParameter`.
- **Resume identity**: `index_digest` is already in the sidecar manifest + `_load_manifest` check from
  phase-1, so a changed index on resume fails fast even if `corpus_hash` is unchanged — exercised by a
  new test (`test_judge_mixed_index_resume_fails_fast`).
- **Fixture + tests**: `testdata/equivalence_index.sample.jsonl` + `.manifest.json` (hand-written, #32
  schema, NO #32-branch dep). +10 tests (loader happy/corpus-mismatch/missing-manifest/row-count/
  malformed; judge-with-index asks equivalence + records digest; no-index not_evaluated; mixed-index
  resume; CLI requires-questions; CLI corpus_hash mismatch). CLI JevError surfaces as `r.exception`
  under CliRunner (main() formats it in a real run) — asserted accordingly.
- **TUTORIAL.md**: `--equivalence-index`/`--questions` usage + the resume/score-provenance note.
- **Verified**: full suite via `.codev/checks/test.sh` → **437 passed, 1 pre-existing skip** (was 427).
  Real-CLI dry-run (no `--yes`, no spend): loaded fixture index, bound corpus_hash from the questions
  manifest, ran pre-flight (1 cell), stopped at the gate. No live Decisions calls (unit tests inject a
  fake decider). Signalling phase complete next; expect 2-way codex+claude consult.

### Phase 3 iter 1 review (codex REQUEST_CHANGES / claude REQUEST_CHANGES) — folded
- Both blocking + convergent. Rebuttal: `21-phase_3-iter1-rebuttals.md`. Suite 437→**443 passed**.
- **claude #1 (blocking, BAKED)**: index `wordings[].text` reached the Decisions API with NO restricted
  guard → `load_equivalence_index(restricted_keys=)` checks each wording's `(work,version,language)`,
  fails fast ("RESTRICTED target … broken index"); CLI passes `aud.restricted_keys(sources)`.
- **codex #1 / claude #4**: `judge` now DERIVES `index_digest` from `index.digest` (rejects a
  disagreeing explicit digest; an index_digest w/o an index raises). Mixed-index test rewritten to use
  two real different indexes.
- **codex #2 / claude resume**: `_load_existing` gains `pinned_index_digest` (`_UNCHECKED` sentinel vs
  real None); judge/estimate bind every existing row's index_digest. provenance path leaves it unchecked.
- **claude #2**: `.wordings()` now excludes the requested edition by `version` (threaded from
  `source.version`), not brittle exact-text — the orthographic-variance regime this diagnoses.
- **claude #3**: `_run_corpus_hash` now also verifies the questions manifest's `question_set_digest`
  == the answers' digest (a mis-pointed --questions is refused).
- **claude #5 housekeeping**: commit phase-3 + `git add` the 2 fixture files EXPLICITLY at the boundary.
- Real-CLI dry-run (no spend) re-smoked green. Signalling done next; this is iter 1 of max 3.

### Phase 3 iter 2 review (codex REQUEST_CHANGES / claude APPROVE) — folded
- Rebuttal: `21-phase_3-iter2-rebuttals.md`. claude verified ALL 5 iter-1 findings fixed. Suite 443→**446**.
- **codex (blocking) + claude #1 (same gap, 2 sides)**: the `--questions`↔answers digest binding was
  silently skippable — a manifest with corpus_hash but no question_set_digest (codex), or answers with
  no/mixed digest (claude #1), bypassed the check. Fixed: under `--equivalence-index`, answers must
  have exactly one non-empty qsd (else BadParameter), and `_run_corpus_hash` requires the manifest qsd
  present AND equal. +2 CLI tests.
- **claude #2**: `estimate(index_digest=)` untested though the CLI hits it before judge → +1 test
  (`test_estimate_mixed_index_fails_fast`).
- **claude #3 (declined, follow-up)**: a huge index row can exceed `_STATE_CHAR_LIMIT` → that cell
  fails every retry. No safety issue (judgment_state fails fast, never sends oversized); recoverability
  only; not reachable with fixture/#32 shape; capping alternates would truncate evidence (semantic
  change). See FOLLOW-UPS.
- **claude #4 housekeeping**: commit + explicit `git add` of fixtures at the boundary.
- This is iter 2 of max 3.

### Phase 3 iter 3 (final) review — CLEAN PASS (codex APPROVE / claude APPROVE)
- Both APPROVE, HIGH, **zero blocking** — a genuine clean pass, NOT a force-advance. claude verified
  both iter-2 binding fixes in code (answers-side + manifest-side), the restricted guard covers all 3
  state fields that leave the process (requested_text cell-level, indexed_other_wordings per-wording;
  model_answer out of scope), the mixed-index guard covers index→other/→none/none→index, and committed
  run evidence is untouched. Suite **446 passed, 1 skip**.
- Non-blocking, NOT patched (kept the clean pass clean): (1) `neither` can't be distinguished from
  "no index row for citation" → FOLLOW-UP for Phase 4 (add `n_indexed_other_wordings`); (2)
  `restricted_keys` defaults to empty (sole caller passes it — declined); (3) `row_count` check skipped
  when absent (digest is the required identity — declined); (4) housekeeping commit + git add fixtures.
- phase_3 DONE. Commit phase_3 (code + 2 fixtures EXPLICITLY + review artifacts + thread), then porch
  advances to phase_4 (validation on the committed tutorial run — the PRE-APPROVED ~$0.011 live pass).

## 2026-10-25 — Phase 4 implement (validation on the committed tutorial run), iter 1
- **Context-refresh boundary**: phase_3→phase_4 "Refresh your context" task appeared then porch advanced
  to phase_4 implement before the bound `afx self-refresh` could run (same as phase_2→3). Non-blocking;
  continued with intact context.
- **Built (offline first)**: `jev_agreement.py` (tested module: join answers×scores×judgments on
  (qid,model_id); containment `matches_requested_p`≥0.5 vs `contains_reference`; refusal `refusal_p`≥0.5
  vs `refused` outcome; raw per-class prob distribution; exhaustive disagreement enumeration) +
  `test_jev_agreement.py` (8 tests) + a `judge-agreement` CLI subcommand (reproducible report, not a
  one-off script).
- **LIVE pass (pre-approved)**: pinged architect with pre-flight (400 cells, ~\$0.0108) then ran with
  `--yes`, key loaded from `.env` (OPENROUTER_API_KEY) without echoing. **Actual spend \$0.011705**, 0
  failures, build `typesafe/jev-1.14-20261014`, all `not_evaluated` (no index). Sidecar →
  `runs/tutorial-2026-10-11/judgments.jsonl` (+ manifest) as NEW evidence.
- **Evidence integrity VERIFIED**: `git diff` on committed answers/scores/summary(.json/.md) = EMPTY
  (never re-ran score/collect). Audit gate passes (origin-only; restricted payloads absent locally).
- **Agreement**: containment **93.25%** (373/400; both 239, judge-only 27, det-only 0, neither 134);
  refusal **97.25%** (389/400; both 116, judge-only 0, det-only 11, neither 273). Raw dist separates
  cleanly (cont_ref=1 mean 0.971 / =0 mean 0.180 w/ 21 near-misses in top bin; refused mean 0.900 /
  not 0.012). Report → `runs/tutorial-2026-10-11/jev_agreement.{json,md}`.
- **35 disagreements, ALL reviewed + categorized** in `codev/reviews/21-*.md`: (1) 27 containment
  judge-only = orthographic/vocalization near-misses (Arabic Uthmani digitization + KJV archaic
  spelling) — the designed diagnostic recall, **0 deterministic-only** (judge never contradicts a
  deterministic catch); (2) 11 refusal det-only, all `*-search` arms = cue-based refusal classifier
  false-positives on hedged-but-delivering web-search answers (judge correctly low refusal_p, some high
  matches_p) — a genuine finding; (3) a few refusal-boundary (p 0.45–0.49) uncertainty cases.
- **Review doc written** (`codev/reviews/21-jev-based-evaluator-typed-judg.md`) — the 3rd of the 3 docs
  (spec/plan/review). Flagged 2 hot-tier doc candidates (arch-critical + lessons-critical) for MAINTAIN.
- Suite **454 passed, 1 pre-existing skip**. Reported results to architect. This is the FINAL phase →
  PR next (one PR, "Part 2 of 3 of #30", closes #21).

### Phase 4 iter 1 review (codex REQUEST_CHANGES / claude APPROVE) — folded
- Rebuttal: `21-phase_4-iter1-rebuttals.md`. **codex's ONLY blocker**: phase_4 files untracked → absent
  from its review diff. Fixed by committing the phase (code+evidence+review `e98233e`). claude explored
  the worktree, independently re-verified EVERYTHING (recomputed all 400 answer_digests → 0 mismatches,
  report byte-reproducible, evidence untouched, every number exact, manual-review quality sound) → APPROVE.
- claude polish folded: (1) documented `judge-agreement` in TUTORIAL + CODE_WALKTHROUGH; (2) added a
  CLI test for judge-agreement; (3) `join_cells` now cross-checks each judgment's answer_digest vs the
  joined answer (report self-verifying) + test; (4) documented restricted-text reachability (transitive
  guard) in the module docstring + review; (5) fixed the "recorded" docstring nit. (6) commit = done.
- Suite 454→**456**. Committed report byte-identical after the answer_digest check. This is iter 1 of max 3.

### Phase 4 iter 2 (re-verify) — CLEAN PASS (codex APPROVE / claude APPROVE)
- Both APPROVE, HIGH, **zero blocking**. Both iter-1 blockers resolved (files now tracked in `e98233e`;
  answer_digest self-verify + CLI test landed). claude re-derived EVERY number exactly from committed
  data, confirmed byte-reproducibility + evidence integrity + 456-gate + audit + manual-review quality.
- 3 non-blocking minors, NOT patched (clean pass stands, not re-opening an approved phase):
  (1) agreement report has no `judge_model_resolved`/`rubric_id` header — spec-satisfied elsewhere
  (rows + sidecar manifest + score provenance) → FOLLOW-UP; (2)/(3) review-prose nits (category-1
  narrative overlaps the 2 Hebrew both-axes cells; English near-miss token_f1 is 0.98 not 0.86–0.98) —
  per-axis COUNTS (27/11) are exact; acknowledged, substance correct.
- **phase_4 DONE → project implementation COMPLETE (all 4 phases).** Next: PR ("Part 2 of 3 of #30",
  closes #21) with the PR TODOs below.

### FOLLOW-UP (from phase_4 iter-2 claude): self-describing agreement report
- Stamp `judge_model_resolved` + `rubric_id` into the `jev_agreement.{json,md}` header (derive from the
  judgment rows' consistent build) so the paper-citable artifact is self-describing without a join.

## 2026-10-26 — Review phase: trailer strip + rebase + PR
- **Trailer strip (human-approved, Waleed via architect)**: message-only `git filter-branch --msg-filter`
  over merge-base..HEAD stripped `Co-Authored-By: Claude Opus 4.8` from the 10 pre-Phase-1 commits.
  VERIFIED tree hashes byte-identical before/after (55 commits), 0 trailers remain. `git push
  --force-with-lease` succeeded (f7fdcfd...1636db1, lease held). Safety tag `pre-rebase-aspir21`.
- **Rebase onto origin/main (feeba97, #44 merged)**: human-approved. cli.py conflicts resolved
  (additive — kept main's edition-index/facct/probe/editions/splits commands+imports AND my
  judge/judge-summary/judge-agreement + merged main()'s error tuple to include JevError+AgreementError).
  TUTORIAL/README auto-merged. **Full suite 557 passed, 1 skip** (main's ~100 new tests + mine).
- **#32 producer is now on main** (`edition-index` command). Ran the deferred real-export smoke:
  produced the real 31,102-row index (corpus_hash 5ae493e7e249575c, excluded_restricted [NABRE,TLG]);
  my `load_equivalence_index` consumes it cleanly — schema fits VERBATIM, digest/row_count validated,
  restricted guard passes (no excluded edition reaches the judge), lookup returns the right alternates
  (ASV/WEB excluding requested KJV). Consumer↔producer compatible.
- Next: force-push the rebased branch, open the PR, ping architect.

### PR TODOs (do at PR time)
- Strip `Co-Authored-By: Claude Opus 4.8` trailers from early spec/plan/thread/rebuttal commits
  (message-only rewrite, tree unchanged, verify git log) JUST before opening the PR.
- Rebase onto main; expect a cli.py textual conflict with #34 (whoever merges second rebases + re-runs).
- PR body: "Part 2 of 3 of #30", closes #21. NO Co-Authored-By / Generated-with lines.
- `porch done 21 --pr <N> --branch builder/aspir-21`, then `--merged <N>`.

### FOLLOW-UPS for a later phase / the PR (not phase-2 scope)
- **(phase 4, from iter-3 claude #1)** With an index supplied but no index row for a citation,
  `indexed_other_wordings` is `[]` and the judge can only answer requested_wording/neither/refusal — so
  `neither` conflates "alternates existed, none matched" with "no index row for this citation". Record
  `n_indexed_other_wordings` (count of alternates sent) per row so Phase 4's agreement report / the paper
  can separate those cases. Add in Phase 4 (writes a fresh sidecar anyway), with a test.
- **(phase 3, from iter-2 claude #3)** A very large equivalence-index row (many/long wordings) can push
  `judgment_state` past `_STATE_CHAR_LIMIT`; that cell fails fast and stays pending on every retry.
  Consider capping the number of alternates sent (recoverable) vs. the current fail-fast. Not reachable
  with the hand fixture or #32's current shape.
- Row-level `answer_digest` cross-check: `score --judgments` binds on question-set digest, so a sidecar
  from a DIFFERENT collect run over the SAME question set validates (claude iter-1 #4). Phase 1 records
  answer_digest per row → a real cross-check vs the answers being scored is feasible later.
- The deferred per-row MERGE pass (sidecar verdicts → scores.jsonl open metrics map) must handle the
  `kind` vs `equivalence: not_evaluated` asymmetry (claude iter-2 #3).
