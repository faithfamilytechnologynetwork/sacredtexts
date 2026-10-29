# Specification: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/XXXX-*.md.
-->

## Problem Statement

A Qur'anic verse can be written correctly in more than one orthography. The two that matter
for this benchmark are **Uthmani** (the script of the QUL corpus the benchmark is built from,
with hamzat-wasl ٱ, dagger-alif ـٰ, dotless ى) and standard modern **Imla'i** (plain alef ا,
dotted ي, words like يا بني written out). A model that reproduces a verse *word-for-word and
correct* but in the orthography the prompt elicited is being scored as if it got the verse
wrong.

This matters because the benchmark's headline question is whether models can *retrieve and
reproduce* sacred text. Penalizing a content-correct answer for its script turns a
presentation choice into a measured accuracy gap, so the numbers stop meaning what the
benchmark claims they mean.

Affected: anyone reading Arabic (and specifically Qur'an) results today, and — acutely — the
planned **#39 Arabic-instruction subset**, which this issue is a declared prerequisite for.
The 2026-10-29 Arabic-prompt experiment showed Arabic-scaffolded prompts switch both tested
models to Imla'i output, so an unmodified scorer will systematically under-credit every
Arabic-prompted run.

Requested by Nancy in the working group (2026-10-29) after that experiment.

## Current State

Scoring folds Arabic through a script-scoped normalisation pass (`strip_script_marks`, called
from `normalize()` before the punctuation pass). Today it:

- folds hamzat al-wasl ٱ → bare alef ا (atomic replacement),
- deletes Arabic/Hebrew combining marks (category Mn) and the editorial code points (tatweel,
  the U+06D6–U+06ED Qur'anic annotation block) **within the RTL Unicode blocks only**,
- leaves Latin and every other script byte-for-byte unchanged (a pinned invariant).

What it **cannot** do, and the orthographic pairs that therefore score unequal:

- **dagger alif** ـٰ (U+0670) ↔ full alif ا. U+0670 is category Mn, so it is currently
  *deleted* by the mark pass — never converted to a letter. (Ordering consequence: a
  dagger→alif fold cannot sit after the mark deletion.)
- **dotless ya / alef maqsura** ى ↔ dotted ya ي.
- **hamza seating**: أَرَءَيْتُمْ ↔ أَرَأَيْتُمْ (seat of the hamza differs).
- **ى + dagger-alif digraph** أَتَىٰكُمْ ↔ أَتَاكُمْ.
- **alif madda** آ, **standalone hamza** ء.

Concrete example (37:102, from the experiment): the English-prompted answer reproduces the
QUL form «ٱلسَّعْىَ … يَـٰبُنَىَّ» byte-exactly; the Arabic-prompted answer gives the correct
«السَّعْيَ … يَا بُنَيَّ». `normalize()` folds the wasl and strips marks but cannot equate the
dagger-alif or ى↔ي, so the second answer scores incorrect though it is the same verse.

Measured effect (`runs/exp-arabic-prompts-2026-10-29/`): strict scorer 82.1% / 78.6% (en,
gpt-6.1-sol / claude-sonnet-5.5) vs 71.4% / 71.4% (ar) — an ~8–11 point drop that hand
inspection attributes **entirely** to orthography, with zero content-level flips in either
direction. All movement is in `retrieve_quote`.

## Desired State

Two content-identical renderings of the same Qur'anic passage — one Uthmani, one Imla'i —
score the same. A model is credited for retrieving the verse regardless of which orthography
it rendered it in, in either direction (answer vs expected), consistent with how
`strip_script_marks` already treats vocalisation direction-independently.

Concretely, on the experiment evidence: both prompt conditions converge (the fold recovers the
Imla'i-rendered cells), no content-correct Qur'an answer is scored incorrect on orthography
alone, and the #39 subset can be run at scale without the scorer artifact. The fix lives in the
scorer, not in prompt engineering — the experiment showed the fold also rescues English-
prompted cells, so strict accuracy is partly orthographic luck today for *everyone*.

Non-Arabic scoring is unchanged: Latin stays byte-for-byte identical, and the fold is confined
to Arabic script, so Hebrew and every other corpus are untouched.

## Success Criteria

- [ ] Two renderings of the same Qur'anic unit that differ only in orthography (across the
      pairs enumerated in Current State: dagger-alif, ى↔ي, hamza seating, ى+dagger digraph,
      alif madda, standalone hamza, in addition to the wasl already handled) normalise to the
      same string, in both match directions.
- [ ] On `runs/exp-arabic-prompts-2026-10-29`, re-scoring under the contract converges the two
      conditions and credits every content-correct cell; the set of cells whose headline flips
      0→1 is pre-registered and reproduced exactly.
- [ ] Latin output of `normalize()` is byte-for-byte unchanged (the existing Latin-invariance
      guard still passes).
- [ ] The change is executed as a **sanctioned, oracle-witnessed rebaseline**: every committed
      run whose Arabic cells move (at minimum `tutorial-2026-10-11`, `original-2026-10-21`,
      `first-run-2026-10-11`, plus the experiment run) has its oracle re-pinned, and the
      rebaseline moves **only** Arabic cells — no non-Arabic `(exact, normalized, token_f1)`
      projection value changes.
- [ ] The moved headline numbers are surfaced to the architect before merge.
- [ ] The copyright audit gate and the full test suite pass; no run artifact derived from a
      `restricted` source is committed or altered.

## Constraints

- **Scoring-contract change ⇒ sanctioned-rebaseline procedure.** This is a deliberate change to
  what `correct` means, not a forbidden re-score. It follows the established procedure: a
  durable projection-SHA oracle + a pre-registered flip set (`test_contains_reference_
  rebaseline.py` is the pattern), committed scores regenerated once with panel/usage fed back
  verbatim, moved numbers surfaced to the architect first. (arch-critical; lessons-critical
  "Never re-run collect/score/generate over committed run evidence — Exception: a deliberate
  scoring-contract change".)
- **Ordering is load-bearing.** The orthography fold must run **before** the Mn-mark deletion,
  because the dagger alif (U+0670) is itself a combining mark the current pass deletes. The
  documented order "Arabic/Hebrew marks BEFORE the punctuation pass" must not be broken.
- **Script-scoped only.** The fold applies to Arabic script; Latin must stay byte-for-byte
  identical (pinned snapshot) and the fold must not reach Hebrew or other scripts.
- **Direction-independent.** The fold is applied to both the answer and the expected text, so
  neither the Uthmani-expected/Imla'i-answer nor the reverse case is privileged.
- **Issue steer: one mechanism, not both** — a deterministic fold in the scorer *or* Jev
  equivalence adjudication, not both.
- **Native-speaker review is a #39 gate, not this one.** Nancy's caution (2026-10-29) that
  AI-translated prompts can miss religious subtleties applies to the Arabic *scaffolds* (#41)
  before a scaled #39 run; it does not gate this scorer change, but the spec records it so #39
  does not skip it.
- **Parallel-work coordination.** builder-48 (#48, refusal decline-cues) is making a
  concurrent scoring-contract rebaseline. This spec's oracle must define its flip set on the
  orthography signal (headline `correct` flipping 0→1 while strict `normalized` stays 0),
  independent of refusal outcomes, so a rebase onto #48 stays clean.

## Assumptions

- The QUL Uthmani corpus is the ground-truth orthography; models may answer in either
  orthography. (If a future corpus were natively Imla'i the fold still holds, being
  direction-independent.)
- The enumerated fold rules are sufficient for the observed phenomena: the experiment's quick
  fold left 4 residual cells, and hand inspection attributed all 4 to exactly two further rules
  (hamza seating, ى+dagger digraph) already listed here — so a fold covering all listed pairs
  resolves every cell in the evidence.
- Folding to a bare consonantal/orthography-neutral skeleton does not collapse two *distinct*
  Qur'anic units into one within the benchmark's question set (to be checked against the corpus
  during implementation; see Open Questions).
- The committed non-experiment runs' Arabic cells are the only other scores that move; no
  non-Arabic cell is affected (validated by the projection oracle).

## Solution Approaches

### Approach 1: Deterministic Arabic orthography fold in the scorer (recommended)

Extend the existing Arabic normalisation so the orthographic variants listed in Current State
fold to a single canonical skeleton, with the fold ordered **before** the Mn-mark deletion.
Applied symmetrically to answer and expected, confined to Arabic script.

- **Pros:** free (no extra model calls), fully deterministic and reproducible, lives exactly
  where the experiment concluded the fix belongs, expressible as a durable contract with a
  SHA-pinned oracle, and extends an existing, well-understood pass. Resolves 100% of the
  evidence cells.
- **Cons:** rules must be enumerated and justified; a careless rule could over-fold and collide
  distinct units (mitigated by checking against the corpus and by the projection oracle, which
  forbids any non-Arabic movement and pins Arabic movement to a registered set).
- **Risk/complexity:** low-moderate. The main subtlety is the ordering constraint, which is
  already documented in the code, and the rebaseline scope (several committed runs carry
  Arabic).

### Approach 2: Jev equivalence adjudication

Let the Jev judge adjudicate orthographic equivalence (it already flagged exactly this class —
27 orthographic near-misses in the Spec 21 cross-check).

- **Pros:** no rule enumeration; naturally absorbs variants the rule set might miss.
- **Cons:** a paid, separate pass that is never the default grader (issue #21); non-
  deterministic, so it cannot be the headline contract without an oracle problem; adds cost and
  latency to every run; harder to surface as a reproducible, SHA-witnessed rebaseline. The
  benchmark's default-grader honesty constraints argue against making provenance/retrieval
  depend on a model judge.
- **Risk/complexity:** higher for a default-path change; better suited as an optional
  cross-check than as the production fix the #39 prerequisite needs.

**Recommendation: Approach 1.** It is deterministic, free, reproducible, resolves every cell in
the evidence, and is what the experiment's own conclusion calls for ("the production fix belongs
in the scorer, not in prompt engineering"). Approach 2 remains available as an optional
equivalence grader but should not be the default-path fix.

## Open Questions

- **Important:** Does any fold rule collapse two *distinct* benchmark units into the same
  skeleton? Must be checked against the Qur'an corpus during implementation; the projection
  oracle plus a corpus-collision check bound the risk.
- **Important:** Exact rebaseline scope — confirmed that `tutorial-2026-10-11`,
  `original-2026-10-21`, and `first-run-2026-10-11` all carry Arabic answers (132 / 840 / 2
  rows) and will move, alongside the experiment run. Each needs its oracle re-pinned; the plan
  must enumerate them so none is missed.
- **Important (coordination):** Merge order with #48 (builder-48). If #48 merges first, this
  work rebases and re-runs its oracle. Flip set is kept orthography-defined and refusal-
  independent to keep that rebase clean. Resolution is the architect's call at PR time.
- **Nice-to-know:** Should the fold be exposed as a named/toggleable normaliser step, or folded
  silently into the existing Arabic pass? Default: fold into the existing pass, since it is a
  correctness fix to the same contract, not a new selectable grader.
- **Nice-to-know:** Arabic-Indic digit folding and leading «نعم»/«لا» parsing surfaced in the
  experiment's `analyze.py` as answer pre-normalisation — are they in scope here or deferred to
  #39? Proposed: out of scope for #52 (this issue is orthography of retrieved *text*); record
  for #39.

## Test Scenarios

- **Happy path:** a verse rendered Uthmani and the same verse rendered Imla'i normalise equal;
  `contains_reference` / `normalized` credit the retrieval in both directions.
- **Per-pair unit coverage:** one minimal case per fold rule (dagger-alif, ى↔ي, hamza seating,
  ى+dagger digraph, alif madda, standalone hamza) — each pair folds together; the existing
  wasl case still folds.
- **Latin invariance:** a representative Latin answer/expected pair normalises byte-for-byte as
  before (regression guard).
- **Non-collision:** two genuinely different Qur'anic units do **not** fold to the same
  skeleton.
- **Evidence replay:** re-scoring `exp-arabic-prompts-2026-10-29` converges the two conditions
  and flips exactly the pre-registered cells; the 4 formerly-residual cells now credit.
- **Rebaseline oracle:** for each committed run with Arabic, the non-Arabic
  `(exact, normalized, token_f1)` projection hashes identically (nothing non-Arabic moved) and
  Arabic headline flips match the pre-registered set.
- **Audit/suite:** copyright audit gate passes; full test suite green.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Over-folding collides two distinct units | Low | High (false "correct") | Corpus-collision check; projection oracle forbids non-registered movement |
| Fold ordered after mark deletion (dagger alif already gone) | Medium | High (silently no-ops) | Ordering constraint stated as a load-bearing contract + unit test on the dagger-alif pair |
| Rebaseline misses a committed run with Arabic | Medium | Medium (stale/inconsistent evidence) | Scope enumerated (tutorial/original/first-run/experiment); oracle re-pin per run |
| Latin/Hebrew accidentally affected | Low | High (breaks pinned snapshot) | Script-scoped fold; Latin-invariance guard; projection SHA |
| Rebase churn vs #48 merging first | Medium | Low–Medium | Flip set defined on orthography signal, refusal-independent; coordinate merge order with architect |
| Moved numbers merged without architect sight | Low | Medium | Surface moved headline numbers to architect before merge (hard gate in criteria) |

## References

- Issue #52; related #39 (Arabic-instruction subset), #41 (independent rater / native-speaker
  scaffold review), #48 (refusal cues), #21 (judge grader never default).
- `runs/exp-arabic-prompts-2026-10-29/` (README: full analysis + orthography-fold re-score).
- `pipelines/sacredbench/score.py` (`normalize`, `strip_script_marks` — current Arabic pass and
  ordering contract).
- `pipelines/tests/test_contains_reference_rebaseline.py` (the sanctioned-rebaseline oracle
  pattern: projection SHA + pre-registered flip set).
- arch-critical.md (scoring contract, sanctioned rebaseline); lessons-critical.md (never
  re-score committed evidence except a deliberate contract change).
