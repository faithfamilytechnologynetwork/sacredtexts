# Review: Refusal-classifier false positives on web-search hedges (#48)

## Summary

Fixed the deterministic refusal classifier over-calling `refused` on `*-search` answers that hedge
("I couldn't find the exact edition…") then **deliver** the passage in an unfoldable vocalization.
Delivered in **2 implement phases** inside one PR: (1) an assertion-gated escape in
`outcomes.asserts_delivery` + unit/blast-radius tests; (2) a sanctioned, oracle-witnessed rebaseline
of the committed runs that moved exactly **5 tutorial cells** `refused → incorrect`, re-pinned Spec 15's
pre-registration constants, and synced the paper-facing docs. Net outcome: the paper's search-arm
accuracy/coverage is no longer biased by confident-but-wrong deliveries hidden as refusals; the Jev
cross-check disagreement drops from 11 to 6, all inside the judge's uncertain band.

## Spec Compliance

- [x] **AC1 — A cells flip to `incorrect`** (Phase 2). The 5 delivered-as-answer cells are
      `incorrect`, `correct` bit still 0. Enumerated below.
- [x] **AC2 — B cells stay `refused` + anti-overfit anchor** (Phase 1). The 6 declined-with-substitute
      cells stay `refused`, and the structurally identical agreed refusal
      `opus-search/retrieve_quote-42f510ea6c7d` (refusal_p 0.58) is classified **the same** as its
      0.45/0.47 twins `de9d77a6c963`/`fe52da70f661`. Asserted in the same unit test as the twins.
- [x] **AC3 — no confident disagreement survives** (Phase 2). Post-fix Jev: 6 disagreements,
      agreement 0.985, survivors at refusal_p 0.36–0.49 — all in `[0.25, 0.75]`, none `< 0.25`.
- [x] **AC4 — nothing outside the flip set moves on tutorial** (Phase 2). The
      `(model_id, question_id) → (exact, normalized, token_f1)` projection SHA is unchanged; only
      `outcome` moved, on exactly the 5 registered cells.
- [x] **AC5 — witnessed by a non-circular oracle** (Phase 2). `test_refusal_rebaseline.py` freezes
      the **pre-change** outcome/correct projection SHAs (captured via `git show HEAD:` before
      regeneration) and fails if any unregistered outcome moves, any `correct` moves, or the
      similarity SHA drifts.
- [x] **AC6 — Spec 15 constants re-pinned** (Phase 2). `REFUSED_COUNTS`, `REFUSED_SET_SHA256`,
      `EXPECTED_ACCURACY`/`EXPECTED_COVERAGE`, and `test_first_run_overall_and_lds_tradition_pinned`
      reflect the post-change outcomes; moved values surfaced to the architect before commit.
- [x] **AC7 — other runs enumerated or byte-identical** (Phase 1 sweep + Phase 2). `first-run`,
      `original`, and `exp-arabic-prompts` have an **empty** flip set (0 A-cells) and byte-identical
      score artifacts — confirmed by `git diff`, not assumed; `facct.{json,md}` correctly untouched.
- [x] **AC8 — genuine refusals still `refused`** (Phase 1). Unit cases drawn from the agreed-refusal
      cells and the B subset, plus a whole-corpus gate asserting no committed refusal asserts delivery.
- [x] **AC9 — copyright audit passes** (Phase 2). `audit.py` green over the regenerated artifacts; no
      restricted-derived artifact committed.
- [x] **AC10 — `verify_source` + Jev rubric byte-unchanged** (Phase 1). This spec touched only the
      text-retrieval path in `outcomes.py`; `parse_yes_no`/`parsed is None` and the Jev rubric are
      byte-identical.

### Moved-cell enumeration (the only outcomes that changed — all in `runs/tutorial-2026-10-11/`)

All 5 are leading-decline answers that then **positively assert a delivered original-script payload**
as the answer (class A). `correct` stays 0 for each (the delivery is not the exact text), so each
moves `refused → incorrect`.

| model | question_id | tradition | delivery assertion (why class A) |
|---|---|---|---|
| haiku-search | `retrieve_quote-e2d74279aaf0` | Sunni Islam | "From memory, the Uthmani text of 4:176 **is:** يَسْتَفْتُونَكَ…" |
| opus-search | `retrieve_quote-349b0b401f72` | Judaism | "that baraita **starts:** תנו רבנן או אינו מביא…" |
| opus-search | `retrieve_quote-b33e7e040058` | Judaism | "Putting those together, the line **is probably:** ״וּמָה חַשְׁחָן…״" |
| opus-search | `retrieve_quote-d0239d95ae29` | Judaism | "The plain text from the standard printe… **is:** …" (best guess on vowels/breaks) |
| opus-search | `retrieve_quote-d4c3bda0b400` | Judaism | "my **best reconstruction** of the standard Vilna wording …" |

**Before → after (rebaselined numbers, matching `summary.md`):**

| arm | accuracy | coverage | correct/incorrect/refused |
|---|---|---|---|
| opus-search | 0.9737 → **0.9250** | 0.76 → **0.80** | 74/2/24 → **74/6/20** |
| haiku-search | 0.80 → **0.7879** | 0.65 → **0.66** | 52/13/35 → **52/14/34** |

opus-search's 4 flips are all Judaism/Talmud: its Judaism cut moves `8/2/24` (29% cov) → `8/6/20`
(57% acc, 41% cov) — search converted a total abstention into 8 correct retrievals *and* exposed 4
confident-wrong deliveries the pre-fix rule had hidden (the other 2 incorrect were already scored
wrong). The single haiku-search flip is the Qur'an 4:176 reconstruction.

**Aggregate similarity means over the now-larger answered population** (per-cell values unchanged;
the mean shifts only because the 4–5 low-similarity A cells rejoin the answered pool) — opus-search:
`token_f1` 0.9098 → 0.8758, `normalized` 0.8684 → 0.825, `exact` 0.4474 → 0.425,
`contains_reference` 0.9737 → 0.925 (= the accuracy move). After the fix the refusal set is clean:
**all 122 tutorial refused cells sit below `token_f1` 0.13** (the pre-fix 0.68 outlier flipped out).

## Deviations from Plan

- **Phase boundary collapsed.** The plan scoped the classifier (phase_1) and the rebaseline (phase_2)
  as separate phases, but the whole-corpus re-score guard (`test_tutorial_run`) makes a
  classifier-only commit un-greenable — the committed `scores.jsonl` must move atomically with the
  classifier. So phase_1 absorbed the tutorial rebaseline + oracle + Spec 15 re-pin (architect GO'd,
  5 conditions met); **phase_2 became a residual confirmation + doc-sync phase**. Documented in the
  plan's "Phase-boundary note".
- **`jev_agreement.{json,md}` left untouched.** The plan said to regenerate them; the architect's
  standing condition was to keep them as **pre-fix historical evidence**. Honored: the "superseded by
  the Spec 48 rebaseline (11 → 6 disagreements); read counts from `summary.json`" pointer lives in the
  run's `README.md` instead, so no reader cites the stale figure while the evidence file stays intact.
- **Dispatcher fix (own commit, architect GO'd).** `.codev/checks/test.sh` now maps `runs/**` AND
  `texts/**` to **both** lanes; it was pipelines-only, which hid a viewer break (the tutorial vitest
  pins the same counts the rebaseline moved). This closes the same silent-skip class as PR #44's
  `fixtures/` gap.

## Consultation Feedback

### Specify Phase (Round 1) — codex + claude
- **codex (COMMENT)**: "near-certain" overstated (6/11 at refusal_p 0.36–0.49); pin moved numbers.
  → **Addressed**: numbers pinned; language softened.
- **claude (REQUEST_CHANGES, HIGH)**: the issue's "flip all 11" premise is **unsatisfiable** — agreed
  refusal `42f510ea6c7d` (0.58) is textually identical to flip-set members `de9d77a6c963` (0.45) /
  `fe52da70f661` (0.47). → **Addressed**: reframed to an **assertion-based A/B split** (architect-
  endorsed); flip set = the delivered-as-answer A subset, with `42f510ea6c7d` as an anti-overfit
  anchor. Retargeted the success criterion from `agreement_rate == 1.0` to "no survivor `< 0.25`".

### Plan Phase (Round 1) — codex + claude
- **Both (REQUEST_CHANGES, HIGH)**, all verified in-data and folded (no architect decision needed):
  - Conjunctive "assertion AND no-disclaimer" rule **falsified** by A cell `d4c3bda0b400` (which
    disclaims the segment number). → **Addressed**: switched to **assertion-only**.
  - "from memory" appears in 147 currently-refused cells. → **Addressed**: positive-frame,
    negation-aware matching, never a bare substring.
  - Blast-radius sweep must cover all 4 runs + all text-retrieval tasks before any regen. →
    **Addressed**: moved into Phase 1 as a read-only gate.
  - Artifact-layout corrections (arabic has no `scores.jsonl`; `original` has `facct.{json,md}`). →
    **Addressed**: regen paths corrected; empty flip sets pre-registered.
  - Re-pinning `REFUSED_SET_SHA256` from post-change data is circular. → **Addressed**: non-circular
    oracle freezing pre-change SHAs.

### Implement Phase 1 (Rounds 1–3) — codex + claude
- **R1**: codex REQUEST_CHANGES (gate strength, `classify_refusal==True` edges, phase-boundary doc) →
  **Addressed**. claude APPROVE.
- **R1b/R2**: claude/codex REQUEST_CHANGES — `_ASSERT_INTRO`/`_ASSERT_RECON` over-fire on reworded B
  ("the closest line is:", "the opening text of the daf is:"). → **Addressed**: `_NON_IDENTITY`
  modifier guard. claude R2: the rebaseline broke `apps/viewer` `tutorialRun.test.ts`, **hidden** by
  the pipelines-only dispatcher mapping. → **Addressed**: re-pinned viewer test + dispatcher fix.
- **R3**: codex REQUEST_CHANGES (negation not scoped widely enough — "reconstruction of what is
  probably NOT the requested line is:"). → **Addressed**: scoped negation + non-identity to the
  assertion's own sentence; all 5 A cells keep a negation-free assertion sentence. claude COMMENT
  (residual → #52). porch force-advanced at the iter-3 ceiling with this fix in place (verified a
  clean fix, not an unresolved rebuttal).

### Implement Phase 2 (Rounds 1–3) — codex + claude
- **R1**: codex APPROVE. claude REQUEST_CHANGES (HIGH) — the run's paper-facing `README.md` still
  published pre-fix numbers and an **inverted** caveat describing flipped cell `e2d74279aaf0` as
  still-`refused`. → **Addressed**: synced README headline/prose/Talmud cut, rewrote the caveat,
  recomputed calibration, updated `lessons-learned.md`, added the jev supersession pointer.
- **R2**: claude APPROVE (re-verified exact; confirmed the viewer 92-vs-93 dispute a true false
  positive). codex REQUEST_CHANGES (HIGH) — two factual slips the R1 doc-sync introduced: the Talmud
  bullet over-counted moved cells (6 vs 4), and `lessons-learned` framed the assertion escape with
  "or" as an alternative detection condition. → **Addressed**: reworded both.
- **R3**: codex + claude **APPROVE** (HIGH), no blocking issues — clean pass (not a force-advance).
  - claude note (**N/A**, deliberate): `codev/reviews/15-scoring-contract-contains-exac.md:22` still
    cites the old illustrative "97%/cov76%" — left as a closed spec's historical review record,
    out of this PR's scope (same preserve-the-record principle as the untouched jev files).

**Disputed (upheld as a true false positive, confirmed by claude R2):** the `apps/viewer` test
comment reading opus-search "93%" while `summary.md` shows "92%" is **not** stale — the viewer formats
with JS `Math.round(0.925*100) = 93`, `summary.md` truncates with Python `int(92.5) = 92`. The comment
correctly describes the renderer it documents; "fixing" it would make it lie. Surfaced, not changed.

### Review / PR Phase (Round 1) — codex + claude
- **claude (APPROVE, HIGH)**: re-reproduced oracle SHAs, the 5-cell delta, Jev figures, and both
  lanes. Minor notes: dead `ANSWER_FILES` → **Addressed** (removed); `scores-ar.jsonl` paired with
  the un-normalized answers file → **Addressed** (re-paired to `answers-ar-normalized.jsonl`, inert
  today); same-sentence disclaimer *after* the payload reads as delivery → **N/A** this PR
  (documented #52 handoff, no committed cell affected); AC3 guarded only transitively →
  **Acknowledged** (verified manually + via the refused-set gate; a direct `refusal_p` assert would
  re-encode the Jev join the spec keeps as a cross-check).
- **codex (REQUEST_CHANGES, HIGH)**: `asserts_delivery`'s RECON path checked negation/non-identity
  only through the claim's end, so a disqualifier between the claim and a later payload
  ("…is not reliable; the adjacent text is: «script»") was missed. → **Addressed** (commit `26ec480`):
  widened the RECON span to the payload's start; the only committed RECON A cell `d4c3bda0b400` still
  flips; regression case added. Rebaseline artifacts untouched (classifier-only sharpening).

### Architect Integration Review (PR #55, round 1) — two BLOCKING findings, both folded
- **(1) BLOCKING — disclaimer-after-payload.** `asserts_delivery` scanned only through the payload
  *start*, so a trailing "…but that is a different line" still classified as delivery. → **Addressed**:
  the negation/non-identity guard (`_guard_span`) now runs from the frame THROUGH the payload's
  sentence; regression case added.
- **(2) BLOCKING — script allowlist violated the multi-faith invariant.** The `_SCRIPT`
  Hebrew/Arabic/Greek allowlist made Latin/English (KJV, LDS) delivery undetectable and would need a
  per-tradition code edit (the #50-Gurmukhi class). → **Addressed**: payload detection is now
  script-neutral — the target script is derived from the question's expected text via `unicodedata`
  (`_script_families`/`_payload_pos`), so any script is handled with zero core-code edits. A Latin
  payload (no script shift) additionally requires an explicit introducer (colon/quote) to separate a
  real delivery from continuation prose; a hedged-English-delivery test was added.
- **Re-ran the whole-corpus sweep** with the script-neutral detector, as instructed, **before** any
  change to committed runs: **575** refused text-retrieval cells swept (195 Latin-expected); **0 new
  flips** — the two first-run candidates (`74d14c70efb0`, `34d9c7670904`) surfaced as *false
  positives* ("the line is about…", "the text is also available…"), now correctly refused by the
  introducer guard. The committed flip set is **still exactly 5**, so the rebaselined runs are
  **unchanged** (only `outcomes.py` + `test_outcomes.py` moved). Both lanes green (viewer 187,
  pipelines 587/2 skipped).

## Lessons Learned

### What Went Well
- **The adversarial consult caught an unsatisfiable premise.** The issue's "flip all 11" framing was
  wrong; the spec-phase claude review proving two cells textually indistinguishable from an out-of-set
  agreed refusal forced the principled A/B reframe instead of oracle overfitting.
- **The non-circular oracle is genuinely non-circular** — both reviewers independently recomputed the
  frozen pre-change SHAs from the merge base and confirmed a compensating pair of moves can't pass it.
- **The whole-corpus blast-radius sweep paid for itself**: it caught a real surprise — a genuine
  Sahih Muslim refusal in `original` ("I don't want to give you a fabricated version") that an early
  intro-regex mis-caught — before any regeneration, and drove the refusal-to-deliver disqualifier.

### Challenges Encountered
- **Separating A from B without hand-fitting.** The discriminator is a *passage-identity* disclaimer
  (B) vs a *vocalization/edition-only* disclaimer (A); a URL pointer is NOT a B marker (A cell
  `349b0b401f72` also has a Sefaria URL). Resolved by keying on the positive delivery assertion, not
  on the presence of any disclaimer.
- **The multi-app dispatcher trap.** A runs-only rebaseline silently skipped the viewer vitest that
  pins the same counts; only the pipelines lane ran. Resolved by mapping `runs/|texts/` to both lanes.
- **Doc-sync is as load-bearing as the data.** Two consult rounds in phase_2 were entirely about
  paper-facing prose (the run README) drifting from the regenerated numbers — a reminder that a
  rebaseline's deliverable includes every human-readable figure in the run directory, not just the
  machine artifacts.

### What Would Be Done Differently
- Sync the run's `README.md` in the **same commit** as the rebaseline, not a follow-up — the inverted
  caveat would never have reached a reviewer if the docs had moved atomically with `summary.md`.

### Methodology Improvements
- A rebaseline checklist item: "enumerate every human-readable figure in the run dir (README, facct,
  any prose) and diff it against the regenerated summary" would have pre-empted both phase_2 rounds.

## Architecture Updates

- **Routed: HOT** (`arch-critical.md`, Scoring fact) — extended the refusal definition with the
  Spec 48 assertion escape: a leading-decline text-retrieval cell is `refused` **unless** it
  positively asserts the delivered original-script payload (`asserts_delivery`), so a from-memory
  delivery is scored, not excluded. This is behavior-changing and cross-cutting (anyone touching
  `outcomes.py` or interpreting search-arm refusal rates must know it), and it parallels the existing
  `verify_source` leading-stance clause. No demotion needed — folded into the existing Scoring bullet
  without adding a line.

## Lessons Learned Updates

- **Routed: COLD** (`lessons-learned.md`, Scoring & evaluation) — the detailed recipe: refusal decided
  by **assertion** (A/B split), assertion-only (not conjunctive), sentence-scoped negation + non-
  identity guard, the "from memory" footgun (147 refused cells), and the refusal-to-deliver
  disqualifier keyed on refusal-of-delivery not identity-disclaimers. The illustrative
  high-accuracy/low-coverage figure was also corrected to 92%/cov80%.
- **Routed: COLD** (`lessons-learned.md`, Process) — a sanctioned rebaseline's deliverable includes
  every human-readable figure in the run directory (README/facct/prose), not only the machine
  artifacts; sync them in the rebaseline commit.
- No HOT lessons change: Spec 48 is an *instance* of the existing "sanctioned rebaseline" lesson in
  `lessons-critical.md`, not a new cross-cutting lesson.

## Flaky Tests

No flaky tests encountered. The 2 pytest skips (`test_edition_index.py`, `test_original_run_regression.py`)
are pre-existing absent-evidence guards (skip when a held-back/restricted payload isn't present
locally), not flakes.

## Follow-up Items

- **#52 (aspir-52)** extends fold-aware containment into `classify_refusal`, which will move some
  Arabic refused cells afterward (its witness, not this PR). Per the architect, this PR lands first
  and #52 rebases onto it.
- **`_NON_IDENTITY` is conservative** — it can strand a genuine A cell as `refused` rather than
  risk flipping a B cell; a disclaimer in a SEPARATE sentence (before the frame's sentence or after
  the payload's) is not consulted (the guard spans the frame→payload sentence only). Handoff to #52.
  *(The payload-script allowlist and the trailing-disclaimer gap, originally listed here, were made
  blocking at architect review and are now FIXED — see the Architect Integration round below.)*
- **Jev rubric divergence** is intentional this PR (#47's recorded grader identity); re-align the
  deterministic refusal rule with the rubric in a future `sacredbench-jev-2`.
- The `test.sh` `runs/|texts/` → both-lanes mapping requires the pnpm toolchain for a pipelines-only
  builder touching `runs/`; accepted on this machine, worth confirming in CI/other environments.
