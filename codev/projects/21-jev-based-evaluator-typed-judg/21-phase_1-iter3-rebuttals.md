# Spec 21 — Phase 1 (Jev judge pass + CLI) iteration 3 rebuttal

**codex REQUEST_CHANGES** (two findings) and **claude APPROVE** (confirmed the iter-2 mixed-build
blocker fixed; raised five non-blocking items). Both of codex's findings and the two actionable
claude minors are fixed; two claude items are declined with evidence. Full suite now **414 passed, 1
pre-existing skip** (was 410; +4 tests).

## Accepted and fixed

**codex #1 — resume ignored each row's question-set digest.** The resume key is
`(question_id, model_id, answer_digest)` and omits the question-set digest, so a hand-corrupted row
with those three matching but a *different* `question_set_digest` would be mistaken for a completed
cell of the current set. Fixed: `_load_existing(path, *, pinned_build, pinned_qsd)` now also fails
fast when any existing row's `question_set_digest` differs from the set being judged; both `estimate`
and `judge` pass the current `qsd` (which `_load_manifest` already pins to the manifest's). New test
`test_existing_row_question_set_digest_mismatch_fails_fast`.

**codex #2 — negative `--limit` uncapped the budget guard.** `pending[:limit]` with `limit=-1` judges
all-but-one cell — the opposite of a cap, and a real hole given the $8 budget. Fixed: new
`_check_limit` rejects `limit < 0` at the top of both `estimate` and `judge` (0 is allowed = judge
nothing). New test `test_negative_limit_fails_fast_before_any_call` asserts zero decision calls and no
file written.

**claude #1 — `summarize()` raised a raw `json.JSONDecodeError` on a truncated line.** A truncated
last line is exactly the interrupt case the spec names ("interrupting mid-run leaves a valid,
appendable file"), and `_load_existing` already wraps this in `JevError` with `file:line`.
`summarize` now does the same, so `judge-summary` over a half-written file takes the clean error path.
New test `test_summarize_on_truncated_file_fails_fast`.

**claude #2 — `judge` parsed the answers file with a bare `json.loads` per line.** A corrupt answers
file gave a traceback, not the `typer.BadParameter` pattern the command uses one line above for the
missing-file case. Wrapped. New test `test_cli_judge_corrupt_answers_is_a_clean_error`.

## Disputed / declined (with evidence)

**Disputed: claude #4 — validate `manifest["judge_model"]` (the requested id) up front on resume.**
Declined: this would introduce a false-positive failure against a legitimate, spec-sanctioned
workflow. The spec makes the **resolved build** the identity, not the requested id. The intended way
to resume a `jev-latest` sidecar reproducibly is to pin `--model <the-build-jev-latest-resolved-to>`.
In that case the requested ids legitimately differ (`jev-latest` in the manifest vs the pinned build
on the command line) while the resolved builds match — so an up-front requested-id equality check
would wrongly reject the exact reproducibility path the design intends. The resolved-build comparison
(`established[0]`) already enforces true identity correctly; the only cost claude cites is "one wasted
call", which is bounded by `--limit` and far under the cap. Keeping the identity on the resolved build
is deliberate, so no up-front requested-id gate is added.

**Declined (cosmetic): claude #3 — `estimate()["already_judged"]` counts all sidecar rows, not only
rows in the current answers set.** The pre-flight line reports sidecar state, and the number never
affects what is judged (resume-skip keys on `done` membership, not on this count). Changing it to a
current-set intersection risks double-counting task-skipped/restricted rows for no functional gain.
Left as the plain sidecar-row count; noted here so it isn't lost.

**Tracked (pre-PR): claude #5 — `Co-Authored-By` trailers on ~10 branch commits.** Already logged in
`codev/state/aspir-21_thread.md` as a message-only history rewrite to run just before opening the PR
(global CLAUDE.md + architect brief both forbid the trailers). Not a code change; flagging only.

## Note

jev.py's origin is the contributor's PR #30, carried under that authorship on the feat commit (`a7d33b2`). This
iteration's review-driven hardening is committed under my authorship, consistent with the iter-1/iter-2
review commits. No `Co-Authored-By`/`Generated-with` trailers on the new commits.
