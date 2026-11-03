# bugfix-93 thread — qwen3-32b / gemma-31b / gpt-oss-20b ~0% text retrieval

## 2026-11-02 — investigate

Read the raw `answers.jsonl` for all three models (read-only; `runs/` untouched).

- **No reasoning leaks into `answer`.** gpt-oss-20b (reasoning mandatory, sent `effort: low`) and
  qwen3-32b (sent `effort: none`, some upstreams still think) keep their reasoning in the separate
  `message.reasoning` field; `message.content` is a clean final answer. The large `usage.out` is
  reasoning tokens, not answer text.
- **No empty completions** (0 of 4,866). **No wrong script/language**: answers are in the requested
  script.
- **Truncation is minor:** `usage.out ≥ max_tokens` on 1.1% (gemma), 3.7% (qwen), 4.1% (gpt-oss) of
  cells, mostly degenerate repetition loops. Not the cause of ~0%.
- **Not one bad upstream:** accuracy is near zero on every OpenRouter upstream for each of the three
  models (qwen: DeepInfra/SiliconFlow/Tenstorrent; gemma: CoreWeave/DeepInfra/...; gpt-oss: 10 hosts).
- **Content is wrong, not malformed:** on the 204 "easy" text-retrieval questions (≥9 of the other 13
  models correct), qwen 5/104, gemma 4/204, gpt-oss 1/196 correct, mean token_f1 0.07–0.23.
  The answers are fluent, plausible, wrong verses (e.g. Qur'an 5:3 answered with a made-up verse).
- **Live probe (harness request shape, ~15 calls):** all three answer famous passages correctly
  (John 3:16 / Gen 1:1 NRSV, Qur'an 112:1, John 1:1 Greek), so prompt delivery and answer
  extraction work.

Architect note (2026-11-03): 9 pre-existing failures in test_collect.py / test_phase2_tools.py
(`_DaemonPool._initializer` on Python 3.14) are #97, not ours. Do not patch `_DaemonPool` here.

## 2026-11-03 — A/B on failed questions → root cause: model knowledge, not harness

Re-asked 12 random "easy" run questions per model (all originally wrong), three ways, scored with the
real `score_answer`:

| model | harness (t=0, effort none/low) | host defaults | reasoning high |
|---|---|---|---|
| qwen3-32b | 1 correct / 8 incorrect / 3 truncated | 0 / 12 | 1 / 11 |
| gemma-31b | 0 / 12 | 0 / 12 | 1 / 9 / 2 truncated |
| gpt-oss-20b | 0 / 12 | 0 / 10 / 1 refused / 1 error | 0 / 0 / 2 refused / 10 truncated (8192 tok) |

No parameter variant moves accuracy, and more reasoning only produces more truncation.
**Conclusion: the ~0% is real.** The three models can't recite random verses by reference in these
editions. They know famous ones (probe), but not population-sampled ones. No panel parameter change
is warranted for these entries in `items/for-test/models/openrouter.yaml`.

Secondary defect found (not the cause of #93): `providers._openai` (plain chat path) never checks
`finish_reason`, so a `length`-truncated completion is committed as the answer (1–4% of cells for
these three, ≤1.3% elsewhere, mostly repetition loops). The Anthropic path and the OpenRouter-search
path both fail loud on that. Fixing it changes rerun behaviour (truncated cells become failed and
pending, so collect exits non-zero), which is the architect's call. Raised; holding.

Live spend for the investigation: about 125 OpenRouter calls on the three cheap models (< $0.10).

## 2026-11-03 — fix (architect chose option C)

Architect decision: C only. Record `finish_reason`, don't fail (B rejected: a repetition-loop
truncation is the model failing the question, and leaving those cells pending would hide that).
Evidence comment posted on #93 for the paper to cite.

- `providers.py`: `usage["finish_reason"]` = the host's raw reason on the plain `_openai` chat
  path (the #93 gap), plus `_anthropic` (`stop_reason`), `_openai_openrouter_search`, and `_gemini`
  (search-off now records `MAX_TOKENS` etc. instead of nothing). It's omitted when the host sends
  none, never invented. The Responses-API search path is untouched (it already fails loud unless
  completed).
- `tests/test_finish_reason.py`: 5 tests. 4 fail on HEAD's providers.py and all pass with the fix.
  The test is provider-seam only; a collect-level test would hit `_DaemonPool` (#97).
- arch.md providers bullet: replaced the "latent trap" note with the record-don't-enforce policy.
- Full pipelines pytest: 870 passed, 2 skipped, 9 failed. All 9 are #97 (`_DaemonPool._initializer`
  on Python 3.14, test_collect.py ×6 / test_phase2_tools.py ×3), pre-existing on origin/main.

## 2026-11-03 — PR #103 + CMAP

- PR #103 opened. CMAP: gemini APPROVE, codex COMMENT (stale Gemini search-off test name and
  docstring, fixed in b08c56a), claude APPROVE (non-blocking items: the OpenRouter-search
  `finish_reason` is always "stop", now commented; PR body refreshed).
- After merging origin/main (#99, Python 3.11) the full suite is green: 882 passed, 2 skipped,
  0 failed.
- Caveat for the paper: the 1–4% truncation figures are from the `usage.out >= max_tokens` proxy
  over the committed runs, which predate `usage.finish_reason`. Runs collected after this PR carry
  the field directly.
- First `consult` attempt failed with "Multiple projects found" (the merge brought in bugfix-97's
  project dir). Re-ran with `--issue 93 --project-id bugfix-93`.
