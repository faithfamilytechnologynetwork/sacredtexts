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
