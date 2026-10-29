# aspir-52 — score: treat Uthmani and Imla'i orthographies as equivalent for Arabic

Issue #52 (prereq for #39). ASPIR, strict mode. Protocol driven by porch.

## Specify phase (2026-10-29)

**Problem understood.** `normalize()` → `strip_script_marks()` folds *some* Arabic variants
(alef-wasla ٱ→ا, deletes Mn combining marks + the U+06D6–ED annotation block + tatweel) but
cannot equate the orthographic pairs that distinguish Uthmani (QUL corpus) from standard Imla'i:
dagger-alif ـٰ↔full alif ا, dotless ى↔ي, hamza seating (أَرَءَيْتُمْ↔أَرَأَيْتُمْ), ى+dagger
digraph (أَتَىٰكُمْ↔أَتَاكُمْ), alif madda آ, standalone hamza ء. So the *same correct verse*
written in the two orthographies scores unequal.

**Ordering gotcha (confirmed in code):** the dagger alif U+0670 is category Mn, so
`strip_script_marks` currently *deletes* it. A dagger→full-alif fold must run BEFORE the mark
pass (or exclude U+0670 from the Mn deletion and fold it).

**Evidence:** `runs/exp-arabic-prompts-2026-10-29/`. en 82.1/78.6 vs ar 71.4/71.4 strict; under
an orthography fold both conditions converge on 52/56 with the identical 4 residual cells
(10:50, 14:34 — the two further rules). All 112 answers contain the content-correct verse. Fold
also rescues 7 *en* cells → strict accuracy is partly orthographic luck today.

**Scope finding (important):** committed runs carry Arabic — tutorial-2026-10-11 132 answer rows,
original-2026-10-21 840, first-run-2026-10-11 2. So changing `normalize()` for Arabic rebaselines
THOSE runs too, not only the experiment run. The sanctioned-rebaseline oracle (`test_contains_
reference_rebaseline.py`) pins a projection SHA over first-run + tutorial → those SHAs will move
for their Arabic cells and must be re-pinned; original-2026-10-21 needs a flip set too.

**Coordination (architect note 2026-10-29):** builder-48 is doing refusal decline-cues in
parallel — also a rebaseline. Expect rebase + oracle re-run if #48 merges first. Keeping my flip
set defined on `correct flips 0→1 while normalized==0` (pure orthography), independent of refusal
outcomes, so the rebase stays clean.

**Approaches:** (1) deterministic Arabic orthography fold in the scorer [recommended — free,
reproducible, belongs in scorer per the experiment's own conclusion]; (2) Jev equivalence
adjudication [paid/non-default, non-deterministic]. Issue says "either, not both".

Next: finish spec draft → `<signal>SPEC_DRAFTED</signal>` → porch runs 3-way consult.
