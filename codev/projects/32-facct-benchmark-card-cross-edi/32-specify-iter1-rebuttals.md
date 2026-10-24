# Spec 32 — Rebuttal to specify iteration-1 reviews

Both reviewers returned **REQUEST_CHANGES / HIGH**, and both verified their claims against the real
run data, catalogue, `outcomes.py`, and PR #30. I verified the two load-bearing data claims myself
before accepting them (see "My verification" below). **Every point is accepted; none disputed.** The
revised spec is committed as `[Spec 32] Specification with multi-agent review`.

## My verification (independent, before accepting)

- `expected` keys per task, read from `runs/original-2026-10-21/answers.jsonl`:
  `retrieve_quote → {text}`, `complete_unit → {text, full_text}`, `cite_passage → {citation}`,
  `verify_source → {answer, true_work, true_version, true_language, true_citation}`. Citation is in
  `source.citation` for every task (empty on `verify_source`). → **confirms claude's Defect 1.**
- Incorrect Bible text-retrieval cells split **32 `retrieve_quote` / 21 `complete_unit`** (53 total),
  joining `scores.jsonl` outcome to `answers.jsonl` on `(question_id, model_id)`. → **confirms the
  counterfactual-scope numbers both reviewers cite.**

## Claude review

1. **`expected` schema in Assumptions is wrong (Defect 1).** *Accepted.* My draft generalized from a
   `cite_passage` row. Rewrote the Assumptions bullet to state the task-dependent schema, that
   `source.citation` is the citation key, and that the gold wording for `retrieve_quote` is
   `expected.text` (the raw index supplies only *sibling* editions' wording).
2. **`complete_unit` counterfactual undefined (Defect 2).** *Accepted.* Scoped the counterfactual to
   `retrieve_quote` only; the spec now says `complete_unit` is excluded because its gold is a partial
   unit with no well-defined sibling-edition segment. Updated Desired State, Success Criteria, Test
   Scenarios (added a `complete_unit`-excluded test).
3. **Report the denominator.** *Accepted.* The counterfactual now reports numerator **and**
   denominator (all incorrect Bible `retrieve_quote` cells) per model; the criterion and the core
   test require both.
4. **Restricted-index guard justified by the wrong gate; NABRE is a fourth English Bible.**
   *Accepted.* Replaced the "already excluded from the pool" justification with an explicit
   `license != restricted` filter on the EditionIndex (`select_targets(include_restricted=False)`),
   added a Success Criterion and a compliance test that a restricted target present locally never
   enters the index, and fixed the Risks row.
5. **Resolve Open Question 1 (containment vs exact).** *Accepted.* Baked containment (noting exact is
   a subset of containment, so there was never a real fork) and that `other_edition` excludes the
   *requested* edition. Also resolved the license Open Question per claude's note that the manifest
   uses nominal catalogue names, so the join is direct with no fallback.
6. **Join mechanics / task-scoped sub-metrics worth stating.** *Accepted.* Added an Assumptions
   bullet: score rows carry no text identity (join on `(question_id, model_id)`); the
   `exact/normalized/token_f1/contains_reference` sub-metrics exist only on text-retrieval rows.
7. **Structure conformant to the template.** No change needed (noted as "not an issue").

## Codex review

1. **Counterfactual underspecified for `complete_unit`.** *Accepted* — same fix as claude Defect 2;
   limited to `retrieve_quote`.
2. **Resolve the two Important open questions; Q1 is not two distinct rules.** *Accepted* — both
   resolved in-spec; stated the requested edition is excluded when assigning `other_edition`.
3. **Problem Statement misdescribes run content (Vatican docs / English Talmud).** *Accepted.*
   Rewrote the opening to describe the actual 17-text selected pool (three English Bibles, three LDS
   scriptures, Aramaic Talmud, Arabic Qur'an + nine hadith) and moved the encyclicals / English
   Talmud into a parenthetical as *excluded* catalogue members — framed as catalogue coverage vs run
   composition, which the card must surface, not misreport.
4. **"Catalogue languages with zero questions" is ambiguous.** *Accepted.* Defined the universe as
   catalogue **source** languages (each source's `language` field) that contribute zero questions to
   the pool — the reader-facing language, not the canonical-language axis.
5. **Define fail-fast behavior for inconsistent/incomplete evidence.** *Accepted.* Added a Success
   Criterion, a Test Scenario, and a Risks row: the card fails fast (non-zero exit, no partial
   `facct.{json,md}`) on a missing file, a non-joining answer/score row, a `scores.jsonl`↔
   `summary.json` count disagreement, or an unresolved catalogue target.

## Net

No open disagreements. The counterfactual is now `retrieve_quote`-only with an explicit denominator,
the `expected` schema and join mechanics are stated correctly, the restricted-edition guard is the
correct gate with a test, the census language universe and excluded-vs-selected framing are
unambiguous, and the card is specified to fail fast rather than write a partial artifact.
