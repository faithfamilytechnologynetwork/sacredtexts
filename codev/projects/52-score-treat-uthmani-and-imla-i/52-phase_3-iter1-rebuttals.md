# Phase 3 iter1 — consult dispositions

**Verdicts:** codex APPROVE · claude COMMENT (non-blocking, CONFIDENCE HIGH).

Both consults read the Phase-3 changes from disk and reconciled every refreshed number against the
regenerated artifacts; claude also re-ran the pipelines suite (640 pass / 2 skip) and confirmed the
CODE_WALKTHROUGH claims against `score.py`. No REQUEST_CHANGES / REJECT. claude raised four comments.

## Finding 1 — stale `bounded_contains` references in cold docs — **ADDRESSED**
claude: `arch.md:162` and `lessons-learned.md:183` still name `score.bounded_contains` for the FAccT
edition counterfactual, but Phase 2 moved it to `score.fold_aware_contains` (`facct.py:291`).

Verified: `facct.py:291` calls `score.fold_aware_contains`; its docstring (`:17`) already says so.
Fixed both cold-doc references to `score.fold_aware_contains` (lessons-learned.md also notes
"fold-aware since Spec 52"). Legitimate staleness; the lessons entry's whole point is "the analysis
stage reuses the scorer's own predicate", so the name must be the current one.

## Finding 2 — cold arch tier had no record of the contract change; hot/cold tier split inverted — **ADDRESSED**
claude: `arch.md § score.py` never mentioned the Spec-52 fold, while ~900 chars of *reference* detail
(rule specifics, call-sites, test name) were appended to the always-on hot bullet — inverting the
`update-arch-docs` hot=behavior-changer / cold=reference discipline.

Fixed both halves:
- Added the full Spec-52 fold record to cold `arch.md § score.py` (the rules: optional long-ā at each
  dagger/`ىٰ`, symmetric folds, spacing, `score_normalize` before the mark pass, strict superset,
  byte-stable equality submetrics, the shared call-sites, the #60 residual).
- Trimmed the hot `arch-critical.md` bullet to a behavior-changer pointer (fold is containment-only,
  strict SUPERSET, byte-stable — no generator drift) that now defers the rule enumeration to
  "arch.md § score.py". Hot stays a decision-changer; cold carries the reference.

## Finding 3a — `lessons-critical.md` at 11 entries vs the ≈10 cap — **N/A (pre-existing; claude: leave it)**
Pre-existing overrun; this phase consolidated the two viewer gotchas into one before adding the
fold-design lesson, so there is **no net growth** (still 11). claude explicitly says "I'd leave it",
and `update-arch-docs` says "when in doubt, KEEP". Leaving at 11; thread wording corrected from
"stays at cap" to "stays at the same 11 (no growth)".

## Finding 3b — `CODE_WALKTHROUGH.md` absolute line refs (`score.py:340`/`:255`) rot silently — **REBUTTED**
The `file:line` pointer is the document's established, deliberate convention: its guard
(`test_code_walkthrough.py`) asserts `len(_pointers()) >= 20`, resolves each pointer to a real file,
and checks the line is within EOF — and its own docstring states it "does not pin exact lines … a
drifted line is a convenience to fix", with the symbol name as the stable anchor. ~50 such pointers
already exist. Switching these two to symbol-only would make them *inconsistent* with the whole doc
for no guard benefit. The two new pointers are exact today. Keeping the convention.

## Finding 4 — moved-numbers packet to the architect still pending — **ACKNOWLEDGED (standing order)**
Correct per the no-self-approval standing order (the maintainer scar): the packet goes to the architect at
the **pr gate**, and it will include the 8-cell #60 hamza-alef residual census (the review doc's
moved-numbers table + residual section are its source). Not an omission — a sequencing requirement.

## Suite
Changes are docs-only (`arch.md`, `arch-critical.md`, `lessons-learned.md`). Re-ran the gate:
pipelines 640 pass / 2 skip, viewer lane pass. Tree otherwise unchanged.
