# bugfix-150 thread — complete_unit headline against the first 10 words (#150)

## Investigate (2026-11-03)
- Root cause: `score.score_answer` (text-retrieval branch, `target = expected["text"]`) uses the FULL
  continuation as the reference for `normalized` and `contains_reference`, so a prose completion must
  reproduce a 26–166-word remainder verbatim to score.
- Reproduced over committed evidence with a raw-text cut at the 10th normalized word (raw so the
  Spec 52 Arabic fold still sees dagger-alif marks): population matches the issue exactly
  (7,546 scored facct complete_unit cells, 2,880 correct = 38.2%), but **177** move, not 135
  (→ 40.5%). Every mover in every committed run is incorrect→correct: facct 177, runs/<model>/base 205,
  archive/original 18, archive/exp-provider-native-search 3 = 403. No refused→correct, no loss.
- 135 gap: a raw-whitespace cut gives encyclicals +53 (= the issue's 17→70) but the issue defines
  words as normalized tokens (possessives/dashes split → +56). Remaining diff is Gita-en 19,
  Saheeh 33, Bible-en 10 — could not reproduce 135 exactly; registry is by identity anyway.
- Design concern raised with architect: moving `normalized` (strict equality) onto the head flips
  1,177 facct cells normalized 1→0 (answers that ARE the full >10-word continuation) and loses their
  credit under `--evaluator strict` (breaks credit-only). Proposed: keep `normalized` on the full
  continuation, move only containment to the head — identical headline under the default graders.

## Fix (2026-11-03/04)
- Architect approved (00:56Z): normalized/exact/token_f1 stay on the full continuation; only
  contains_reference adds the 10-word head, OR'd with full-continuation containment (credit-only
  by construction). Register what the oracle finds (177 facct / 403 all runs).
- `score.completion_head` cuts the RAW continuation at the first space/punctuation where
  `normalize(prefix).split()` == the first 10 normalized words (fail-fast ScoreError if no such cut;
  none in committed data). Raw, so the Spec 52 dagger-alif fold still works on the head.
- Registry `pipelines/tests/testdata/completion_head_movers.tsv` (403 rows) + oracle in
  `test_completion_head.py`. facct per-text: encyclicals 17→73, Saheeh +33, Aramaic Talmud +26,
  Besant Gita +19, BoM +13, Davidson +10, NRSV +10, Uthmani +6, Dhammapada +2, WLC +2.
- Gotcha: `pytest -n auto` is not available here (no xdist); my first "baseline green" never ran.
- Side effect to note in PR: `jev.string_settled` goes through score_answer, so newly-correct cells
  count as string-settled (Jev is not called on them).

## PR (2026-11-04)
- PR #152. The Gurmukhi registry row fix had already landed on main as #143 (6f05422), so per the
  architect I dropped my duplicate commit (rebase --onto, byte-identical content) and merged
  origin/main; the PR diff is now only #150.
- CMAP: gemini APPROVE; codex REQUEST_CHANGES (wants `normalized` = head OR full so a strict-only
  exact-head answer scores; this conflicts with the architect-approved design, so I rebutted and
  surfaced it to the architect); claude pending at time of writing.
- Gotcha: `consult` in a builder needs `--issue 150 --project-id bugfix-150` here; auto-detect sees
  every project in codev/projects and refuses ("Multiple projects found").
