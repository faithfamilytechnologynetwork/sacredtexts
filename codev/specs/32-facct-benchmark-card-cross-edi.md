# Specification: FAccT benchmark card + cross-edition reading over the current scoring contract

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/32-*.md.
-->

## Problem Statement

A run of this benchmark produces a single accuracy percentage per model per task. That number is
dangerous on its own: it mixes four different kinds of text (a public-domain KJV, two other
public-domain Bible editions, Vatican-style documents, an English/Aramaic Talmud, Arabic Qur'an and
hadith), it counts a refusal and a wrong verse as the same failure unless you look closely, and it
says nothing about *who* the questions represent. A reader — especially a reviewer of the FAccT
paper Jonathan Karr is drafting — cannot tell from the percentage alone what the benchmark is
allowed to conclude.

Two specific blind spots matter most:

1. **Who the questions represent.** Nobody reading the leaderboard can see, without digging, that
   the questions are original-language editions only, that two texts were dropped because their
   language is not canonical, that whole languages in the catalogue have zero questions, or which
   license governs each slice.
2. **The edition trap.** Three of the texts are different English editions of the same Bible
   (KJV, ASV 1901, WEB). A model that recites `Romans 3:23` in the WEB wording when the prompt asked
   for the KJV scores as a miss, even though it produced a faithful edition of the same citation.
   The percentage punishes that as if the model had invented text.

Jonathan Karr's PR #30 built exactly this card (`facct.py`) and a cross-edition reading
(`cross_translation.py`), but against the **October-11 scoring contract**: an eight-way label set
with its own refusal regex and a `fabrication` label, exact-match headline. The contract on `main`
has since changed (Spec 15, Spec 26): outcomes are the three values `correct` / `incorrect` /
`refused` decided once in `outcomes.py` and written to `scores.jsonl`, the headline is the
containment contract, and the pool is the 17-text original-language set. His card must be reworked
against that contract so the card and the leaderboard tell the same story, rather than inventing a
second, conflicting definition of a refusal.

## Current State

- **The run exists and is committed.** `runs/original-2026-10-21/` holds `questions.jsonl` (+
  `.manifest.json`), `answers.jsonl`, `scores.jsonl`, `summary.json`, `summary.md`, `README.md` for
  a 3-model panel (gpt-oss-20b, haiku, opus) over 476 questions across 17 texts. It is the data the
  card reads, as-is.
- **The scoring contract is settled on `main`.** `scores.jsonl` carries, per cell,
  `metrics.outcome ∈ {correct, incorrect, refused}` plus the text-retrieval sub-metrics
  (`exact / normalized / token_f1 / contains_reference`). `summary.json` carries per-model per-task
  `accuracy` (= correct/(correct+incorrect)), `coverage`, `refused_rate`, the `panel` (provider,
  model, tools, endpoint, served_by), and `evaluators` (`["strict","containment"]`). Outcome is
  decided once in `outcomes.py`; there is exactly one definition of a refusal in the codebase.
- **The manifest already answers most census questions.** `questions.jsonl.manifest.json` lists
  `selected_texts` (17) and `excluded_texts` (2: Papal Encyclicals and the English Talmud, each with
  a `reason` string naming the `language != canonical_language` rule). The catalogue
  (`texts/raw/*/source.yaml`) carries each text's license and canonical language, and therefore which
  catalogue languages have zero questions.
- **Jonathan's PR #30 code is available but not merged** and not on `main`. It assumes the old
  contract: `facct.py` declares an eight-label set (`exact`, `right_verse_plus_extra`,
  `other_tradition`, `other_edition`, `near_miss`, `refusal`, `empty`, `fabrication`), its own
  `_REFUSAL` regex and `is_refusal()`, and an exact-match headline. `cross_translation.py` builds an
  `EditionIndex` keyed by Bible-style citations and already computes edition agreement and
  same-words-across-traditions — that machinery is sound and contract-independent.
- **Today there is no card for this run.** A reader has `summary.md` (the raw numbers) and nothing
  that frames what the numbers may and may not mean.

## Desired State

A reviewer can run one command against `runs/original-2026-10-21/` and get, written next to the run,
a benchmark card (`facct.json` + `facct.md`) that:

1. **Reports the run census** — who the questions represent, read from the manifest and catalogue:
   a table by tradition, language, document type, and license; the catalogue languages that have
   zero questions; and the texts excluded from the pool, each with the manifest's reason. No model is
   named "better"; the census describes the questions, not the answers.
2. **Reports outcomes in the contract's own terms** — the three outcomes `correct` / `incorrect` /
   `refused` straight from `scores.jsonl` / `summary.json`, with accuracy stated beside its coverage
   (so a high score on thin coverage cannot masquerade as mastery). No second refusal definition, no
   `fabrication` label, and the word "fabrication" does not appear for an unmatched answer.
3. **Reports the edition counterfactual** — for the texts that have sibling editions (the three
   English Bibles, and *only* those in this pool), how many `incorrect` text-retrieval cells would
   have been `correct` under the containment contract if **any** indexed edition of the same citation
   were accepted. Those specific misses are tagged `other_edition`. The card states plainly that this
   counterfactual is computed for Bible citations only, because they are the only sibling editions in
   the pool.
4. **Carries the card's prose as a card** — the claim this run supports, what would make it fail,
   what the card will not conclude, and that scholar / community review is not attached — all held in
   **one editable place** so Jonathan can revise the wording while drafting the paper without
   touching analysis code.

The card is a pure analysis/visualisation stage: it reads committed run evidence plus the public
raw editions, never re-runs `generate` / `collect` / `score`, never calls a model, and writes only
to a new path under the run directory. Optionally, the viewer gains a read-only per-run card view
that renders `facct.json` with no scoring logic of its own.

## Success Criteria

- [ ] A single CLI command reads `runs/original-2026-10-21/` and writes `runs/original-2026-10-21/facct.json` and `facct.md`, writing nothing outside that run directory and making zero network/API calls.
- [ ] Every outcome count on the card (correct / incorrect / refused, per model and per task) equals the corresponding count in that run's `scores.jsonl` / `summary.json` — the card never recomputes an outcome.
- [ ] The card contains no second refusal definition and no `fabrication` label; the string "fabrication" does not appear as a classification of a model answer.
- [ ] The census table covers all 17 selected texts by tradition, language, document type, and license; lists catalogue languages with zero questions; and lists the 2 excluded texts with the manifest's reason for each.
- [ ] The edition counterfactual reports, for the three English Bibles, the count of `incorrect` text-retrieval cells that contain some indexed edition's wording of the same citation, tags those cells `other_edition`, and states explicitly that it is Bible-only and why.
- [ ] Citation handling does not silently mis-handle the Arabic (surah:ayah, hadith numbers) and Hebrew/Aramaic (daf:line) citations in the pool: either those citations are parsed correctly, or they are excluded from the edition counterfactual by construction (because they have no sibling edition) and the card says so — never parsed into a wrong edition match.
- [ ] All card prose (claims, failure conditions, non-conclusions, review-not-attached) lives in one editable location, separate from the counting logic.
- [ ] The copyright audit (`pipelines/sacredbench/audit.py`, run by `.codev/checks/test.sh`) passes: no committed card artifact embeds NABRE or Greek Orthodox TLG text or derives from a restricted source.
- [ ] Where Jonathan's PR #30 code is carried over, his authorship is preserved on the carrying commit.
- [ ] Tests cover the card builder against a small fixture run and assert the outcome counts match the fixture's `scores.jsonl`.

## Constraints

Fixed decisions from issue #32 and the architect's brief (treated as baked):

- **Part 3 of 3 of PR #30.** Start from Jonathan Karr's card layout and `cross_translation` idea;
  preserve his authorship on any commit carrying his code (`git commit --author`). The PR
  description reads "Part 3 of 3 of #30" and closes #32. No `Generated with` / `Co-Authored-By`
  lines.
- **Rework against `main`'s contract, not Oct-11.** Outcomes `correct` / `incorrect` / `refused`
  come from `outcomes.py` and `scores.jsonl`; **no** second refusal regex; **no** `fabrication`
  label; the headline is the containment contract (Spec 15). Do not use the word "fabrication" for
  an unmatched answer.
- **Pool is the 17-text Spec-26 original-language set**, with Arabic / Hebrew / Aramaic citations.
  Multi-faith by construction: citation parsing must handle the current pool, or the edition
  counterfactual must be explicitly limited to texts with sibling editions and say so.
- **Data source is `runs/original-2026-10-21`, read as-is.** Never re-run `generate` / `collect` /
  `score` over committed run evidence. The card is a pure analysis/visualisation stage reading
  `scores.jsonl` + `summary.json` (+ `answers.jsonl` and the manifest/catalogue it needs), written
  under a new output path.
- **Derived artifacts live next to the run** (`runs/<id>/facct.{json,md}`). Never rescore.
- **Zero live API spend expected.** If the work appears to need any, stop and ping the architect
  first.
- **Repo is public.** The card must not embed NABRE or TLG text; `audit.py` must pass.
- **Docs bar is Waleed's**: one linear recipe, non-engineer readable, no asides.
- **Card wording is provisional** (Jonathan is drafting the paper): the card's prose lives in one
  editable place.
- **Viewer** per-run card view is optional; if built, it reads `facct.json` and adds no new scoring
  logic.

## Assumptions

- `runs/original-2026-10-21/scores.jsonl` and `summary.json` are authoritative for outcomes; the card
  trusts `metrics.outcome` and the summary counts rather than recomputing them.
- The embedded question in `answers.jsonl` carries `source` (tradition list, work, version, language,
  document_type, citation) and an `expected` that holds the **citation**; the gold text for a
  citation is resolved from the raw editions index, not from the answer row.
- The three English Bibles (KJV, ASV 1901, WEB) are the only sibling editions in this pool; no other
  text in the 17 has a second indexed edition of the same citation, so the edition counterfactual is
  inherently Bible-scoped.
- The public-domain raw editions needed for the edition index are present under `texts/raw/`;
  restricted payloads are absent and are never indexed or embedded.
- Jonathan will review and may rewrite the card prose at PR time; the analysis counts are what must
  be correct and stable.

## Solution Approaches

### Approach 1: Rework `facct.py` + `cross_translation.py` in the pipeline; prose in a constants block (recommended)

Carry over Jonathan's `facct.py` and `cross_translation.py`, strip the old contract out of them
(delete the eight-label set, the `_REFUSAL` regex / `is_refusal`, the `fabrication` and exact-match
headline), and re-point the card at `scores.jsonl` / `summary.json` for the three outcomes. Keep his
`EditionIndex` / citation machinery for the edition counterfactual, scoped to Bible citations. Hold
all card prose (uses, non-uses, claims, review-not-attached) in one clearly-marked constants block in
`facct.py`. Expose it as a `facct` CLI subcommand that writes `facct.{json,md}` beside the run.

- **Pros:** Preserves the valuable core and Jonathan's authorship; one contract, one refusal
  definition; the counterfactual reuses proven index code; prose is in one file Jonathan can edit.
- **Cons:** Requires careful surgery to remove the old contract without breaking the index code;
  the constants block is "one editable place" but still inside a `.py` file (acceptable per the
  brief, which says "one editable place", not "a separate prose file").
- **Risk/complexity:** Moderate. The main risk is accidentally keeping a vestige of the old
  contract (e.g. a stray `fabrication` branch). Mitigated by a test asserting the card's counts equal
  the fixture `scores.jsonl` and that forbidden strings are absent.

### Approach 2: Prose in a separate editable file (YAML/Markdown), code reads it

Same analysis code, but lift the prose out into a standalone `facct_prose.yaml` (or `.md`) that the
builder loads and interpolates.

- **Pros:** Cleanest possible "one editable place" for a non-engineer; Jonathan edits prose with no
  Python nearby.
- **Cons:** Adds a file-loading seam and a schema for the prose; risk of the prose file and the
  computed sections drifting out of sync; more moving parts for a card that is read a handful of
  times.
- **Risk/complexity:** Low-moderate. Reasonable, but heavier than the problem needs; a well-marked
  constants block already satisfies the brief.

**Recommendation: Approach 1.** It preserves the core and authorship, enforces a single contract,
and keeps the prose in one editable block without introducing a prose-file schema. Approach 2's
separate-file idea can be revisited if Jonathan asks for it during paper drafting.

## Open Questions

- **Important** — Should the edition counterfactual accept a sibling edition only when the answer
  *contains* that edition's wording of the citation (containment, matching the headline contract), or
  also when it is an exact normalized match? Recommendation: containment, to match Spec 15's headline;
  surface the exact-only subset as an informational count if cheap.
- **Important** — Does "license" on the card come from each text's `source.yaml` license field via
  the catalogue, and how are encyclical-style documents (whose work name differs from the catalogue
  target) resolved? Recommendation: read license from the catalogue targets with a documented
  fallback for document types whose work title is file-derived.
- **Nice-to-know** — Should the viewer per-run card view ship in this PR or be deferred? It is
  optional; defer unless it is cheap once the JSON is stable.
- **Nice-to-know** — Should the card also surface the three-edition agreement table (how often
  KJV/ASV/WEB agree after normalization) that Jonathan's `cross_translation.py` already computes? It
  is informative context for the edition counterfactual; include if it fits the one-recipe doc bar.

## Test Scenarios

- **Census correctness (happy path):** Given the committed run, the card's census lists all 17
  selected texts with tradition/language/document_type/license, the 2 excluded texts with their
  manifest reasons, and the catalogue languages with zero questions. Spot-checked against the
  manifest.
- **Outcome fidelity (happy path):** For each model×task, the card's correct/incorrect/refused counts
  equal the counts derivable from `scores.jsonl` (and match `summary.json`). A deliberate mismatch in
  a fixture makes the test fail.
- **Edition counterfactual (core):** A fixture with a Bible `retrieve_quote` cell whose answer is the
  WEB wording of a citation the prompt asked for in KJV, scored `incorrect`, is tagged `other_edition`
  and counted in the "would pass if any edition were gold" total. A genuinely wrong Bible answer is
  not tagged.
- **Non-Bible citations are not mis-parsed (edge):** Qur'an `2:255`, a hadith number, and a Talmud
  daf:line citation are never matched to a Bible edition; they are excluded from the counterfactual by
  construction, and the card says the counterfactual is Bible-only.
- **No forbidden vocabulary (regression):** The generated `facct.json`/`facct.md` contain no
  `fabrication` label and no second refusal definition; a grep-style assertion guards this.
- **Audit passes (compliance):** After generating the card into a run dir, `audit.py` reports no
  restricted-origin or restricted-content artifact.
- **No re-scoring / no network (compliance):** Generating the card does not modify `scores.jsonl` /
  `answers.jsonl` / `summary.json` and makes no outbound request.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A vestige of the old eight-label contract (e.g. `fabrication`) survives the rework | Medium | High — reintroduces the second refusal definition the brief forbids | Delete the label set/regex wholesale; add a regression test asserting forbidden strings are absent and counts come from `scores.jsonl` |
| `cite_key` mis-parses an Arabic/Hebrew citation into a Bible match | Low | High — a false `other_edition` tag on a non-Bible cell | Scope the counterfactual to Bible citations explicitly; test that non-Bible citations never match |
| Card accidentally reads/derives from a restricted source | Low | High — public repo copyright violation | Index only public-domain raw editions; restricted texts are already excluded from the pool; gate on `audit.py` |
| Re-running the card overwrites or rescoring mutates committed evidence | Low | High — corrupts the run's proof | Card writes only `facct.{json,md}`; never invokes score/collect/generate; test asserts other run files are untouched |
| Prose and computed sections drift | Low | Medium | Keep prose adjacent to the builder in one block; the computed sections are assembled in the same place |
| Unplanned API spend | Low | Medium | Card makes zero model calls by design; if any need appears, stop and ping the architect |

## References

- Issue #32 — FAccT benchmark card + cross-edition reading (part 3 of 3 of PR #30).
- PR #30 (Jonathan Karr) — original `facct.py`, `cross_translation.py`, viewer `FacctReading`, under
  the Oct-11 contract.
- Spec 15 — scoring = named graders + always-on outcome; refusal is an outcome; containment headline.
- Spec 26 — 17-text original-language pool; `verify_source` hardening.
- `pipelines/sacredbench/outcomes.py` — the single refusal/outcome definition.
- `runs/original-2026-10-21/` — the committed run the card reads.
- `pipelines/sacredbench/audit.py` — restricted-origin/-content copyright gate.
