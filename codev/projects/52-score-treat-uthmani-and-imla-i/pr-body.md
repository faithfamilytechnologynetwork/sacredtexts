# PR body draft (Spec 52) — fill the moved-numbers after the Phase-2 rebaseline

**Title:** `[Spec 52] Score Uthmani and Imla'i Arabic orthographies as equivalent (prereq for #39)`

---

## What & why

A model that reproduces a Qur'anic verse correctly but in a different orthography than the QUL
Uthmani corpus is no longer penalised. The 2026-10-29 Arabic-prompt experiment showed Arabic-
scaffolded prompts switch models to standard Imla'i output, costing ~8–11 measured accuracy points
that were entirely a scorer artifact — this is the declared prerequisite for #39 (the Arabic-
instruction subset). Requested by Nancy in the working group.

## How

All orthographic flexibility lives in the containment predicate `fold_aware_contains`, a strict
**superset** of the old `bounded_contains`:
- symmetric letter folds (standalone hamza ء→ا, bare alef-maqsura ى→ي) are canonical in
  `score_normalize`;
- the long ā (dagger-alif ـٰ / the ىٰ digraph) is matched as an **optional** alef, because Imla'i
  writes it plene for some words (الكتاب) and omits it for the defective-spelling class (هذا,
  الرحمن) — a lexical, not positional, distinction that a context-free fold gets wrong;
- whitespace-flexed between Arabic letters (Uthmani one-word ↔ Imla'i two-word), word-bounded,
  and direction-independent.

`normalize()` and the similarity submetrics (`exact`/`normalized`/`token_f1`) are **unchanged**, so
generation's question-set digest and the copyright audit are untouched and only `contains_reference`
/ `correct` / `outcome` move. The change is a **sanctioned, oracle-witnessed rebaseline**:
non-Arabic and all similarity projections are frozen against pre-change SHAs, and every moved Arabic
cell is pre-registered and hand-verified.

## Rebaseline (moved numbers)

A **sanctioned, oracle-witnessed rebaseline**: **58 cells move, every one `incorrect → correct`
(`contains_reference`/`correct`/`outcome`); zero losses, zero coverage change, zero similarity
drift** (the `(exact, normalized, token_f1)` projection SHA is byte-identical on all five committed
score files). Every moved cell was hand-verified against its verse (shortest reference 8 words,
median 17) — the same text in Imla'i orthography, never a different text.

| Run | accuracy before → after | coverage | moved |
|---|---|---|---|
| tutorial-2026-10-11 (retrieve_quote) | 86.0% → 93.2% | 69.5% (unchanged) | 20 |
| original-2026-10-21 (overall) | 47.7% → 49.1% | 76.6% (unchanged) | 15 |
| first-run-2026-10-11 | unchanged | unchanged | 0 |
| exp-arabic-prompts (en, both models) | 80.4% → **96.4%** | 100% | 9 |
| exp-arabic-prompts (ar, both models) | 71.4% → **96.4%** | 100% | 14 |

The exp A/B is the proof: pre-fold, Arabic-prompted answers dropped ~8–11 pts and 5 cells flipped
en→ar — **entirely a scorer artifact**; post-fold en and ar are identical at 96.4% with **0
cross-condition flips**, clearing the #39 prerequisite. Witnessed by `test_orthography_rebaseline.py`
(SIM frozen on all 5 files + superset + per-run mover counts + exp recovery) and the re-pinned
`test_contains_reference_rebaseline.py` / `test_refusal_rebaseline.py`.

## Reconciliation with the competing #57

A competing #52 (PR #57) folded the orthography inside `normalize()`, materialising dagger-alif →
full alef. That un-credits the defective-spelling class — its own test asserted
`normalize("2:2") == "ذالك الكتاب…"` (Uthmani ذٰلك → **ذالك**) while Imla'i writes **ذلك**, so it
would score the defective class *wrong* — and it moves the `normalized` tier, the generation ANCHOR
digest, and the audit path. This PR converges on the reviewed **containment-only** design (the
long-ā alef is OPTIONAL, `normalize()` frozen) as the single source of truth, and **keeps Jonathan
the contributor's unrelated `outcomes.py` `_INTRODUCER` regex-escape fix**. One tutorial cell
(`e2d74279aaf0`) composes cleanly across both rebaselines: `refused` (pre-#48) → `incorrect` (#48)
→ `correct` (#52, a verbatim-Imla'i delivery).

## Known limitations

- **10 rare collision buckets** — distinct-word minimal pairs sharing a skeleton after a necessary
  fold (see the review and `test_arabic_orthography_fold.py`); accepted, pinned as a drift-detecting
  allow-list, harmless at verse-length references.
- **Hamza-alef ءَا ↔ alef-madda آ under-credit (8 cells) — deferred to #60.** The fold does not yet
  equate word-initial «ءَا» (Uthmani) with «آ» (Imla'i), so 8 committed cells where the answer is the
  correct verse are left under-credited (strict superset preserved — never a wrong credit). Pinned by
  exact id in `test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL` as the follow-up's ready-made
  oracle. **It is asymmetric on the tutorial run**: for two verses haiku-search wrote «ءَا» (credited)
  and haiku wrote «آ» (uncredited), so ~2–3 pts of the committed haiku 88%→haiku-search 92% "search
  lift" is this residual rather than retrieval — documented in that run's README. The fold extension
  (plus the `ىٰ`↔maqsura case) needs its own collision analysis; filed as **#60**.

## Coordination

Stacks on #48 (refusal decline-cues, PR #55) and the SGGS corpus (PR #51); rebased onto current
`main` (including #57/#58, see Reconciliation) and the orthography witness re-run byte-identically
over that base.

## Tests

Full suite green (pipelines pytest + viewer vitest); copyright audit passes; committed-run guards
and `ANCHOR_DIGEST` as expected (similarity frozen, only containment/headline moved).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
