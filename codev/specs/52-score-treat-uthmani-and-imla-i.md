# Specification: Treat Uthmani and Imla'i Arabic orthographies as equivalent in scoring

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/XXXX-*.md.
-->

## Problem Statement

A Qur'anic verse can be written correctly in more than one orthography. The two that matter
for this benchmark are **Uthmani** (the script of the QUL corpus the benchmark is built from —
hamzat-wasl ٱ, dagger-alif ـٰ, dotless alef-maqsura ى, and words like يٰبنى written as a single
unit) and standard modern **Imla'i** (plain alef ا, dotted ya ي, يا بني written as two words).
A model that reproduces a verse *word-for-word and correct* but in the orthography the prompt
elicited is being scored as if it got the verse wrong.

This matters because the benchmark's headline question is whether models can *retrieve and
reproduce* sacred text. Penalizing a content-correct answer for its script turns a
presentation choice into a measured accuracy gap, so the numbers stop meaning what the
benchmark claims they mean.

Affected: anyone reading Arabic (specifically Qur'an) results today, and — acutely — the
planned **#39 Arabic-instruction subset**, which this issue is a declared prerequisite for.
The 2026-10-29 Arabic-prompt experiment showed Arabic-scaffolded prompts switch both tested
models to Imla'i output, so an unmodified scorer systematically under-credits Arabic-prompted
runs. Requested by Nancy in the working group (2026-10-29) after that experiment.

## Current State

Scoring folds Arabic through a script-scoped normalisation pass (`strip_script_marks`, called
from `normalize()` after NFKD and before the punctuation pass). What it does **today**,
verified empirically against the code:

- NFKD decomposition followed by deletion of Arabic/Hebrew combining marks (category Mn) and
  the editorial code points (tatweel, the U+06D6–U+06ED annotation block) **within the RTL
  Unicode blocks U+0590–U+08FF and U+FB1D–U+FB4F only**. (That range also covers Syriac,
  Thaana, N'Ko, Samaritan, Mandaic marks — their marks are stripped too; harmless for this
  benchmark's corpora. **Latin and all non-RTL scripts are byte-for-byte untouched** — a pinned
  invariant — but "every other script" is not: only non-RTL scripts are invariant.)
- an atomic fold of hamzat al-wasl ٱ → bare alef ا, and Hebrew maqaf → space.

Consequently these pairs **already fold today** (do not re-list them as gaps): **alif madda**
آ → ا, **hamza-on-alef** أ/إ → ا, **hamza-on-waw** ؤ → و, **hamza-on-ya** ئ → ي (all via NFKD
decomposing to letter + Mn mark, then Mn deletion), and **wasl** ٱ → ا.

What does **not** fold today — the actual gaps, each confirmed by running `normalize()` on a
minimal pair:

| Pair | `normalize()` today | Why |
|------|---------------------|-----|
| dagger-alif `يَـٰبُنَىَّ` vs `يَا بُنَيَّ` | `يبنى` vs `يا بني` → **DIFF** | U+0670 is category Mn, so it is **deleted**, not folded to ا (ordering: a dagger→alif fold must run *before* the Mn deletion) — and a word-boundary difference remains |
| alef-maqsura `هدى` vs `هدي` | `هدى` vs `هدي` → **DIFF** | ى (U+0649) is a base letter, neither decomposed nor Mn |
| ىٰ digraph `أَتَىٰكُمْ` vs `أَتَاكُمْ` | `اتىكم` vs `اتاكم` → **DIFF** | the ى+dagger digraph representing long ā is not equated with ا |
| standalone hamza `أَرَءَيْتُمْ` vs `أَرَأَيْتُمْ` | `ارءيتم` vs `ارايتم` → **DIFF** | ء (U+0621, category Lo) is not decomposed and not Mn |
| word boundary `يَـٰبُنَىَّ` vs `يَا بُنَيَّ` | one token vs two → **DIFF** | Uthmani writes some compounds as one orthographic word, Imla'i as two |

Measured effect (`runs/exp-arabic-prompts-2026-10-29/`): strict scorer 82.1% / 78.6% (en,
gpt-6.1-sol / claude-sonnet-5.5) vs 71.4% / 71.4% (ar) — an ~8–11 point drop that hand
inspection attributes **entirely** to orthography, with zero content-level flips in either
direction. All movement is in `retrieve_quote`.

## Desired State

Two content-identical renderings of the same Qur'anic passage — one Uthmani, one Imla'i —
score the same wherever doing so does **not** also merge two genuinely different Arabic words.
A model is credited for retrieving the verse regardless of orthography, in either direction
(answer vs expected), consistent with how `strip_script_marks` already treats vocalisation
direction-independently. The fix lives in the scorer, not in prompt engineering (the experiment
showed the fold also rescues English-prompted cells, so strict accuracy is partly orthographic
luck today for everyone).

Non-RTL scoring is unchanged: Latin stays byte-for-byte identical. Hebrew and other RTL scripts
are not touched by the new Arabic-specific rules.

## Success Criteria

- [ ] For each enumerated orthographic pair where equating the two does not collide with a
      distinct Arabic word, the two renderings normalise to the same string in both match
      directions. The gaps in scope: dagger-alif → ا, alef-maqsura ى → ي, the ىٰ digraph → ا,
      standalone hamza ء, and Arabic word-boundary equivalence.
- [ ] **The long-ā alef is OPTIONAL (handled in containment, not a canonical fold).** The long ā
      written in Uthmani as a dagger-alif ـٰ or the ىٰ digraph is written as a full alef by the
      **plene** class (`ٱلْكِتَٰبِ→الكتاب`, `سُبْحَٰنَ→سبحان`) but **omitted** by the **defective-spelling
      (رسم ناقص)** class (`هَٰذَا→هذا`, `ذَٰلِكَ→ذلك`, `ٱلرَّحْمَٰنِ→الرحمن`) — a **lexical**, not positional,
      distinction. A context-free `dagger→ا` fold therefore un-credits the defective class (it would
      mark `هذا`/`الرحمن` wrong — the inverse of this spec's purpose, and it broke two verbatim-correct
      committed cells in prototyping). **So the equality-fold approach was abandoned**: the long-ā is
      instead matched as an OPTIONAL alef (`ا?`) inside the containment predicate, while the symmetric
      letter folds (alef-maqsura ى→ي, standalone hamza ء→ا) stay canonical. `normalize()` and the
      equality submetrics (`exact`/`normalized`/`token_f1`) are **unchanged**.
- [ ] **No-wrong-credit gate (operative).** The fold must not cause any committed answer to be
      credited for a wrong word. The containment predicate is a strict **superset** of today's
      `bounded_contains` (so `normalized=1 ⇒ contains_reference=1` holds and the fold can only ADD
      credit), and the no-wrong-credit gate is enforced at **scoring granularity**: every Arabic cell
      that moves under the rebaseline is hand-verified a true Uthmani↔Imla'i equivalence before it is
      pre-registered. A word-level corpus sweep is a supporting diagnostic, not a standalone
      pass/fail — see the known limitation below.

**Known limitation (accepted — architect 2026-10-29, not a blocker).** A literal word-level
zero-collision gate is infeasible: the two symmetric letter folds each merge a few rare
consonantal-skeleton minimal pairs that are genuinely distinct words. Enumerated against the QUL
corpus (9 word-buckets, pre-registered in `test_arabic_orthography_fold.py`):

- **maqsura (ى→ي)** — rescues the largest class (`هدى↔هدي`, `بُنَىَّ↔بُنَيَّ`) but merges
  `نبى`(prophet)/`نبّئ`(inform!), `قرى`(towns)/`قرئ`(was recited), `أمرى`(my affair)/`امرئ`(a man).
  `نبى`/`نبّئ` is **mostly pre-existing** (`نبّئ`→`نبي` already today via the ئ seat-fold).
- **standalone hamza (ء→ا)** — the only coherent target (dropping it is asymmetric and fails
  `أَرَءَيْتُمْ↔أَرَأَيْتُمْ`) but merges `سواء`(equal)/`سوء`(evil), `جزاء`(recompense)/`جزء`(a part),
  `وراء`(behind)/`ورءا`, `ملأ`(chiefs)/`ملء`(fill), `شىء`/`شيـٔا`, `برىء`/`بريـٔا`.

These are documented and accepted because (a) rejecting either rule would abandon the fix, and
(b) the no-wrong-credit gate at scoring granularity catches any case that would actually mis-credit
a committed answer. The benchmark scores verse-length references, where a single-word ambiguity
essentially never flips a cell. The residue is a frozen allow-list, so a *new* collision from any
future rule change fails the test.
- [ ] On `runs/exp-arabic-prompts-2026-10-29`, re-scoring converges the two conditions and
      credits every content-correct cell that can be credited without a word-level collision;
      the set of cells whose headline flips is pre-registered and reproduced exactly.
- [ ] Latin output of `normalize()` is byte-for-byte unchanged (the existing Latin-invariance
      guard still passes); Hebrew/other-RTL regression coverage is added for the new rules.
- [ ] The **Spec 15 four-submetric contract** is honored: because all orthographic flexibility
      lives in the containment predicate, Arabic `exact`, `normalized`, and `token_f1` keep their
      current meaning unchanged (no whitespace stripping inside `normalize()`); only
      `contains_reference` — and the headline `correct`/`outcome` it drives — moves. This is the
      minimal, deliberate change.
- [ ] The change is executed as a **sanctioned, oracle-witnessed rebaseline** defined by a
      **before/after projection delta** (not the #15 containment signature): every committed run
      whose Arabic cells move — `tutorial-2026-10-11`, `original-2026-10-21`,
      `first-run-2026-10-11`, and the experiment run — has its oracle re-pinned so that **no
      non-Arabic `(exact, normalized, token_f1)` projection value changes** and the Arabic cells
      that move match a pre-registered set.
- [ ] **All score-derived artifacts are regenerated** for every rebaselined run, not just
      `scores.jsonl`: `summary.json`/`summary.md` (all runs), `original-2026-10-21/facct.*`
      (Spec 32 FAccT card), and `tutorial-2026-10-11/jev_agreement.*` (whose `judge_only: 27`
      orthographic near-misses are precisely this fold's target and will move). No run ships with
      a `summary.md` disagreeing with its `scores.jsonl`.
- [ ] **"Arabic cell" is defined** for the oracle allow-list (by answer-script: a cell is
      "Arabic" iff its answer or expected text contains Arabic-script code points — so
      `first-run-2026-10-11`'s 2 Arabic-bearing answers over English questions count as Arabic
      and may move). The byte-for-byte re-score guards that will break are named and updated:
      `test_first_run_regression.py` and `test_tutorial_run.py`, alongside
      `test_contains_reference_rebaseline.py`.
- [ ] The moved headline numbers are surfaced to the architect before merge.
- [ ] The copyright audit gate and the full test suite pass; no artifact derived from a
      `restricted` source is committed or altered.

## Constraints

- **Scoring-contract change ⇒ sanctioned-rebaseline procedure.** A deliberate change to what
  `correct` means, following the established procedure: a durable projection-SHA oracle + a
  pre-registered flip set, committed scores regenerated once with panel/usage fed back verbatim,
  moved numbers surfaced to the architect first (arch-critical; lessons-critical).
- **Oracle signal is a projection delta, NOT the #15 containment signature.** Because this
  changes `normalize()` itself, orthography matches flip strict `normalized` 0→1 and move
  `token_f1`. The oracle therefore pins before/after projections per cell; it must **not** reuse
  the "`correct` flips while `normalized`==0" rule, which was specific to the #15 containment
  rebaseline.
- **Ordering is load-bearing.** The dagger-alif → ا fold must run **before** the Mn-mark
  deletion (U+0670 is itself a mark the current pass deletes). The documented order
  "Arabic/Hebrew marks BEFORE the punctuation pass" must not be broken.
- **Script-scoped only.** New rules apply to Arabic script; Latin must stay byte-for-byte
  identical and the rules must not reach Hebrew or other RTL scripts.
- **Direction-independent.** Applied to both answer and expected text.
- **No wrong credit.** The operative gate is that no committed answer is credited for a wrong
  word, enforced by hand-verifying every moved cell at scoring granularity. A literal word-level
  zero-collision gate is infeasible (it would abandon the core maqsura→ya fold); the rare,
  largely pre-existing minimal-pair residue (the `نبى`-class) is an accepted, documented
  limitation — see Success Criteria.
- **Issue steer: one mechanism, not both** — a deterministic fold in the scorer *or* Jev
  equivalence adjudication, not both. Jev-as-default is excluded by #21.
- **Native-speaker review is a #39 gate, not this one.** Nancy's caution (2026-10-29) that
  AI-translated prompts can miss religious subtleties applies to the Arabic *scaffolds* (#41)
  before a scaled #39 run; recorded here so #39 does not skip it.
- **Parallel-work coordination.** builder-48 (#48, refusal decline-cues) is making a concurrent
  scoring-contract rebaseline. This spec's oracle delta is defined on text-match projections
  (`exact`/`normalized`/`token_f1`/`contains_reference`), **independent of refusal outcomes**, so
  a rebase onto #48 stays clean. Merge-order resolution is the architect's call at PR time.

## Assumptions

- The QUL Uthmani corpus is the ground-truth orthography; models may answer in either
  orthography. The fold is direction-independent so a future natively-Imla'i corpus still holds.
- **A context-free character fold is insufficient** (demoted from an earlier assumption that
  "a fold covering all listed pairs resolves every cell"). Verified: the context-free full
  collapse of {ا, ى, ي, ـٰ, ٱ} that covers all four residual pairs merges distinct words —
  `قَالَ≡قِيلَ`, `بَيْت≡بَات`, `سَأَلَ≡سَالَ` — and a naive ىٰ→ا breaks the frequent `عَلَىٰ↔على`.
  A position-aware rule set (e.g. medial ىٰ→ا, word-final ى→ي) is required and was confirmed to
  fix the frequent cases without those collisions.
- The word-boundary difference in the headline example cannot be resolved by any character rule;
  it requires an Arabic word-segmentation/whitespace decision with the Spec-15 submetric
  consequence noted in Success Criteria.
- The committed runs' Arabic cells (`tutorial` 132, `original-2026-10-21` 840, `first-run` 2
  Arabic-bearing answers) are the only scores that move; no non-Arabic cell is affected
  (validated by the projection oracle).

## Solution Approaches

### Approach 1: Deterministic, position-aware Arabic orthography fold in the scorer (recommended)

Extend the Arabic normalisation so the in-scope orthographic variants fold to a canonical
skeleton, with (a) the dagger-alif fold ordered before the Mn deletion, (b) **position/context
awareness** for the ى / ىٰ rules so distinct frequent words are not merged, (c) a decided
word-boundary rule, and (d) a word-level collision gate that rejects any rule introducing a
collision. Applied symmetrically, confined to Arabic script.

- **Pros:** free (no extra model calls), deterministic and reproducible, lives where the
  experiment concluded the fix belongs, expressible as a SHA-pinned rebaseline oracle, extends an
  existing well-understood pass.
- **Cons:** the rules are context-dependent, so the implementation is more than a character map;
  a careless rule over-folds (mitigated by the collision gate + projection oracle). The
  word-boundary rule has a documented Spec-15 submetric cost.
- **Risk/complexity:** moderate. Main subtleties: the ordering constraint, the context-dependence
  (proven), the word-boundary/submetric decision, and the multi-run + derived-artifact rebaseline
  scope.

### Approach 2: Jev equivalence adjudication

Let the Jev judge adjudicate orthographic equivalence (it already flagged this class — the 27
`judge_only` near-misses in the Spec 21 cross-check).

- **Pros:** no rule enumeration; absorbs context-dependence and variants a rule set might miss.
- **Cons:** a paid, separate, non-deterministic pass that is never the default grader (#21); can't
  be the headline contract without an oracle problem; adds cost/latency; harder to surface as a
  reproducible SHA-witnessed rebaseline. Default-grader honesty constraints argue against making
  retrieval depend on a model judge.
- **Risk/complexity:** higher for a default-path change; better as an optional cross-check than the
  production fix the #39 prerequisite needs.

**Recommendation: Approach 1**, position-aware and collision-gated. It is deterministic, free,
reproducible, and what the experiment's own conclusion calls for. Approach 2 remains available as
an optional equivalence grader and as a cross-check for residual cells the collision gate blocks,
but is not the default-path fix (per "either, not both").

## Open Questions

- **Critical:** The exact position-aware rule for ى / ىٰ. Confirmed necessary; the precise
  context predicate (medial vs word-final, and interaction with the dagger fold) is decided in the
  plan and validated against corpus vocabulary. Blocks a correct implementation.
- **Critical:** The word-boundary rule and its Spec-15 submetric consequence — strip Arabic
  whitespace inside `normalize()` (degenerating Arabic `token_f1`), restrict whitespace handling to
  the containment predicate, or leave the 2 whitespace-only cells as documented residuals? Shapes
  the contract.
- **Important:** The standalone-hamza rule's canonical target. "Dropped" is asymmetric (measured
  `ارتم` vs `ارايتم` for the أَرَءَيْتُمْ↔أَرَأَيْتُمْ pair); a consistent target (e.g. ء → ا) is
  needed and must pass the collision gate.
- **Important:** Word-level collision-gate mechanics — the corpus vocabulary set checked against,
  and the disposition when a rule collides (reject rule, keep residual, document).
- **Important (coordination):** Merge order with #48; the oracle delta is refusal-independent so
  the rebase is clean, but final order is the architect's call.
- **Nice-to-know:** Arabic-Indic digit folding and leading «نعم»/«لا» parsing (from the
  experiment's `analyze.py`) — proposed out of scope for #52, recorded for #39.
- **Nice-to-know:** Expose the fold as a named/toggleable step vs fold silently into the existing
  Arabic pass (default: fold in, it is a correctness fix to the same contract).

## Test Scenarios

- **Per-gap unit coverage:** one minimal pair per in-scope rule (dagger-alif, alef-maqsura ى→ي,
  ىٰ digraph, standalone hamza, word boundary) folds together; the already-folded cases (madda,
  hamza-seats, wasl) still fold.
- **Context-dependence (negative):** `أَتَىٰكُمْ↔أَتَاكُمْ` fold equal **and** `عَلَىٰ↔على` are not
  broken by the ىٰ rule.
- **Word-level non-collision:** `قَالَ`≠`قِيلَ`, `بَيْت`≠`بَات`, `سَأَلَ`≠`سَالَ` (and a broader
  corpus-vocabulary sweep) do not collide after folding.
- **Latin invariance:** a representative Latin pair normalises byte-for-byte as before.
- **Hebrew/other-RTL regression:** a Hebrew pair is unaffected by the new Arabic rules.
- **Submetric contract:** the Arabic `exact`/`normalized`/`token_f1`/`contains_reference` behaviour
  under the word-boundary rule is asserted to the decided contract.
- **Evidence replay:** re-scoring `exp-arabic-prompts-2026-10-29` converges the conditions and
  flips exactly the pre-registered cells.
- **Rebaseline oracle (per run):** non-Arabic projection hashes identically; Arabic flips match the
  pre-registered set; `summary`/`facct`/`jev_agreement` regenerated and self-consistent;
  `test_first_run_regression.py` and `test_tutorial_run.py` updated and green.
- **Audit/suite:** copyright audit gate passes; full suite green.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A fold rule merges two distinct Arabic words (false "correct") the oracle can't see | Medium | High | Word-level collision gate against corpus vocabulary; non-collision beats convergence |
| Context-free fold used, breaking عَلَىٰ↔على or missing residual cells | Medium | High | Spec mandates position-aware rules; context-dependence negative tests |
| Dagger fold ordered after mark deletion (silently no-ops) | Medium | High | Ordering stated as load-bearing + unit test on the dagger pair |
| Word-boundary rule silently changes Arabic submetric meaning | Medium | Medium | Spec-15 consequence decided and asserted in tests |
| Rebaseline misses a committed run or a derived artifact | Medium | Medium | Scope enumerated (4 runs) incl. summary/facct/jev_agreement; per-run oracle re-pin |
| Latin/Hebrew accidentally affected | Low | High | Script-scoped rules; Latin-invariance guard; Hebrew regression; projection SHA |
| Rebase churn vs #48 merging first | Medium | Low–Medium | Oracle delta refusal-independent; coordinate merge order with architect |
| Moved numbers merged without architect sight | Low | Medium | Surface moved headline numbers before merge (hard gate) |

## References

- Issue #52; related #39 (Arabic-instruction subset), #41 (independent rater / native-speaker
  scaffold review), #48 (refusal cues), #21 (judge grader never default), #32 (FAccT card),
  #15 (containment rebaseline — the oracle pattern, not the signal to reuse here).
- `runs/exp-arabic-prompts-2026-10-29/` (README: full analysis + orthography-fold re-score).
- `pipelines/sacredbench/score.py` (`normalize`, `strip_script_marks` — current Arabic pass and
  ordering contract).
- `pipelines/tests/test_contains_reference_rebaseline.py` (projection-SHA + pre-registered flip-set
  oracle pattern); `pipelines/tests/test_first_run_regression.py`, `test_tutorial_run.py`
  (byte-for-byte re-score guards that will be updated).
- arch-critical.md (scoring contract, sanctioned rebaseline); lessons-critical.md (never re-score
  committed evidence except a deliberate contract change).
