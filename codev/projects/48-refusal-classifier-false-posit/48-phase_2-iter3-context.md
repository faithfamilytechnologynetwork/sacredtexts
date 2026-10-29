### Iteration 1 Reviews
- codex: APPROVE — Phase 2’s witnessed rebaseline is exact: only the five registered tutorial outcomes changed, projections and other runs remain unchanged, and required constants are correctly re-pinned.
- claude: REQUEST_CHANGES — The rebaseline is impeccable and fully witnessed (5 cells, verified pre-change SHAs, byte-reproducible scores, faithful summary splice, both lanes green), but the run's own README still publishes the pre-fix numbers and an inverted caveat about one of the flipped cells.

### Builder Response to Iteration 1
# Phase 2 — impl-consult iteration 1 rebuttals

**codex: APPROVE (HIGH)** — "the witnessed rebaseline is exact: only the five registered tutorial
outcomes changed, projections and other runs remain unchanged, constants correctly re-pinned." No
issues raised; nothing to address.

**claude: REQUEST_CHANGES (HIGH)** — confirmed the rebaseline itself impeccable (recomputed the
pre-change SHAs from the base commit, byte-reproduced `scores.jsonl`, verified the 48-leaf
`summary.json` splice, both lanes green, post-fix Jev 0.985/6). The REQUEST_CHANGES is entirely
about **paper-facing docs left un-synced** beside the regenerated numeric evidence. All accepted and
fixed in commit `b15263e`.

---

## Issue 1 — `runs/tutorial-2026-10-11/README.md` headline/prose stale (ACCEPTED, fixed)

The rebaseline regenerated `summary.{json,md}` and `scores.jsonl` but the run's README still
published the pre-fix numbers, contradicting `summary.md` in the same directory. This is the exact
"stale paper-facing doc no test catches" class the spec's own risk table calls out for `facct`, and
Spec 15's rebaseline had a docs-sync pass for this file — I missed it here.

**Changed:**
- Headline table: opus-search `97% / 76% / 74·2·24` → `92% / 80% / 74·6·20`; haiku-search
  `80% / 65% / 52·13·35` → `79% / 66% / 52·14·34` (matches `summary.md` byte-for-byte). Added a
  parenthetical recording the move and the pre-fix figures as historical contrast.
- Prose: "outranks opus-search's 97%" → 92%; "answers more (76%) at near-perfect accuracy (97%)" →
  "(80%) at 92% accuracy", with a clause that four newly-answered Talmud cells are confident
  *wrong* deliveries (why accuracy fell to 92%); haiku lift "71% → 80%" → "71% → 79%".
- Talmud cut: "8 correct retrievals at 29% coverage" → "8 correct / 6 incorrect / 20 refused —
  57% accuracy at 41% coverage", matching `summary.md`'s opus-search Judaism row.

## Issue 2 — README L84–91 caveat inverted (ACCEPTED, fixed)

The paragraph described flipped cell `retrieve_quote-e2d74279aaf0` as `refused` and framed "counting
it incorrect would put haiku-search at 78.8%" as a *rejected hypothetical* — but that is precisely
what Spec 48 did. Its calibration figure ("267 of 268 … this is the only one above `token_f1` 0.3")
was also obsolete once the 0.68 outlier flipped out.

**Changed:** rewrote the caveat to state that Spec 48 reclassifies the leading-decline-then-deliver
answer as a class-A delivery, now scored `incorrect` (and the four analogous opus-search Talmud
deliveries likewise); this is what moves haiku-search to 79% and opus-search to 92%. I **recomputed
the calibration directly from the rebaselined `scores.jsonl`**: all **122** refused cells in the run
now sit below `token_f1` **0.13** (max 0.1294) — the single delivered-but-refused outlier is gone, so
the refusal set is clean with no exception to name.

## Issue 3 — `jev_agreement.{json,md}` unmarked (ACCEPTED, resolved without touching those files)

The consult wanted an in-file "superseded" marker so the "11 disagreements" figure isn't cited as
current. There is a direct tension: the **architect's standing condition is that
`jev_agreement.{json,md}` stay UNTOUCHED** as pre-fix historical evidence. I honored the architect
and satisfied the consult's intent by putting the pointer in the **README** (the directory's
human-facing doc, which I was already editing): it now states the Jev cross-check was computed
against the pre-fix classifier, its deterministic-refusal column and "11 disagreements" are
superseded by this rebaseline (post-fix: 6 disagreements, agreement 0.985), and refusal counts
should be read from `summary.json`. The review doc will carry the same note.

## Issue 4 (minor) — other stale citations (PARTIALLY ACCEPTED)

- `codev/resources/lessons-learned.md:15` "opus-search 97%/cov76%" → "92%/cov80%" (fixed), plus a
  clause noting the Spec 48 positive-delivery escape.
- **Viewer test comment "97%→93%" vs `summary.md` 92%** — NOT stale, left as-is. The viewer formats
  with `Math.round(0.925*100) = 93%` (`LeaderboardTable.tsx:18`), while `summary.md` truncates with
  Python `int(92.5) = 92%`. This is a pre-existing round-vs-truncate convention difference between
  the two renderers, not a Spec 48 regression; the comment correctly describes what the viewer
  displays. Surfaced to the architect rather than "fixed" by making the comment disagree with the
  viewer it documents.
- Review-doc deliverable (per-run moved-cell enumeration + moved similarity means) is a **review-
  phase** artifact (`codev/reviews/48-*.md`), written after the implement phases close; the numbers
  are already computed and banked in the builder thread for it.

---

**Verification:** both lanes green after the fix — viewer 187 passed (19 files), pipelines 586
passed / 2 skipped. Only `README.md` and `lessons-learned.md` changed (doc prose/numbers only; no
score/summary/oracle artifact touched).


### Iteration 2 Reviews
- codex: REQUEST_CHANGES — The rebaseline is correct, but the documentation sync introduced two factual misstatements about the classifier and moved cells.
- claude: APPROVE — Phase 2's witnessed rebaseline is independently verified exact — 5 registered cells, outcome-only, frozen SHAs reproduce, three runs byte-identical — and iteration 1's doc-staleness finding is fully resolved with the viewer-comment dispute confirmed a true false positive.

### Builder Response to Iteration 2
# Phase 2 — impl-consult iteration 2 rebuttals

**claude: APPROVE (HIGH)** — independently re-verified the rebaseline exact (5 cells, outcome-only,
frozen SHAs reproduce from the merge base, three runs byte-identical, Jev 0.985/6, both lanes green),
confirmed iteration 1's REQUEST_CHANGES fully resolved, and confirmed the viewer `92 vs 93` dispute is
a true false positive. Non-blocking carry-forwards noted and accepted (see below). Nothing to address.

**codex: REQUEST_CHANGES (HIGH)** — two factual-precision issues that my iteration-1 doc-sync
introduced (the rebaseline itself was re-confirmed correct). Both accepted and fixed in commit
`206692f`.

---

## Issue 1 — README Talmud bullet overstated the moved count (ACCEPTED, fixed)

My iteration-1 wording said opus-search's Talmud cells were "8 correct retrievals *plus* 6
confident-but-wrong deliveries that the pre-fix rule had hidden as refusals" — implying all six
`incorrect` cells moved from `refused`. Only **four** moved. Pre-fix opus-search Judaism was
`8 correct / 2 incorrect / 24 refused`; post-fix it is `8 / 6 / 20`. The flip set is exactly the four
opus-search Talmud A-cells (`d4c3bda0b400`, `d0239d95ae29`, `b33e7e040058`, `349b0b401f72`); the other
two `incorrect` cells were already scored wrong before Spec 48.

**Changed:** reworded to "8 correct retrievals and 6 wrong deliveries, of which **Spec 48 newly
exposed 4** that the pre-fix rule had hidden as refusals (the other 2 were already scored `incorrect`
before the fix)." (The headline prose already said "four of the newly-answered Talmud cells" — correct
— so only this bullet needed the fix.)

## Issue 2 — lessons-learned framed the assertion escape as an alternative detection condition (ACCEPTED, fixed)

My edit read "Detection is deterministic (a leading decline cue AND the reference not delivered — or,
Spec 48, a positive delivery assertion past the decline)". The "or" wrongly reads the positive-delivery
assertion as a *third way to detect refusal*. It is the opposite: a cell with a leading decline and no
containment is `refused` **unless** a positive delivery assertion fires, in which case it is scored
(class A), not refused.

**Changed:** reworded to "Detection is deterministic: a leading decline cue AND the reference not
delivered — **unless** a positive delivery assertion fires past the decline (Spec 48 escape, so a
from-memory / best-reconstruction delivery is scored, not refused)."

---

## Non-blocking carry-forwards (claude, accepted — not phase_2 blockers)

1. **Review-doc enumeration** — `codev/reviews/48-*.md` does not exist yet; the per-run moved-cell
   enumeration (with answer text) and the moved-similarity means are a **review-phase** deliverable.
   The numbers are computed and banked in the builder thread; the review phase will write them out
   rather than inherit them as done. Agreed.
2. **`test.sh` `runs/|texts/` → both-lanes mapping** imposes the pnpm toolchain on a pipelines-only
   builder that touches `runs/`. Documented inline as accepted on this machine; worth confirming in
   other environments. No change this PR.

**Verification:** both lanes green after the fix — viewer 187 passed (19 files), pipelines 586 passed
/ 2 skipped. Only `README.md` and `lessons-learned.md` changed (doc prose only; no score/summary/
oracle artifact touched).


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
