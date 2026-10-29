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

## Specify consult iter1 (2026-10-29) — both REQUEST_CHANGES, both excellent

Empirically verified their claims in a REPL before revising (don't guess Unicode):

- **NFKD already folds** madda آ, hamza-seats أ/إ→ا, ؤ→و, ئ→ي, wasl ٱ. I had wrongly listed
  madda + seats as gaps. **Real gaps:** dagger-alif (deleted as Mn, not →ا), alef-maqsura ى→ي,
  ىٰ digraph, standalone hamza ء, and a **word-boundary** diff (يا بني vs يٰبنى).
- **CRITICAL (claude):** no context-free character fold works. ىٰ must →ا for أَتَىٰكُمْ↔أَتَاكُمْ
  but →ى/ي for عَلَىٰ↔على; the full-collapse map that covers all pairs MERGES distinct words —
  verified قال≡قيل, بيت≡بات, سأل≡سال. ⇒ fold MUST be **position-aware** + a **word-level
  collision gate** (containment/token_f1 are substring/token-level, so the projection oracle
  can't catch a word merge).
- **Oracle signal corrected:** since we change normalize(), orthography flips `normalized` 0→1
  — NOT the #15 containment signature. Oracle = before/after projection delta, non-Arabic frozen,
  Arabic flips pre-registered. (Sent architect the correction.)
- **Rebaseline scope widened:** must regenerate derived artifacts too — summary.json/md (all),
  original-2026-10-21/facct.*, tutorial/jev_agreement.* (its judge_only:27 are this fold's target).
  Named guards test_first_run_regression.py + test_tutorial_run.py (byte-for-byte) will break.
- **"Arabic cell" defined** by answer-script (first-run's 2 Arabic answers count).
- **Spec-15 submetric consequence** of any Arabic-whitespace rule made explicit (token_f1
  degenerates) — left as a Critical open question for the plan to decide.

Spec revised in place; rebuttal written; porch advanced to PLAN (ASPIR autonomous on spec).

## Plan phase (2026-10-29) — resolved both Critical open questions by prototyping

Prototyped the fold against real code + the exp run (scratchpad only, not committed):

- **ى/ىٰ = position-aware**: medial digraph ىٰ→ا (long ā), word-final digraph + bare maqsura ى→ي,
  lone dagger→ا, standalone hamza ء→ا. Verified أَتَىٰكُمْ↔أَتَاكُمْ merge AND عَلَىٰ↔على preserved,
  AND قال≠قيل, بيت≠بات. Runs BEFORE Mn deletion (dagger is Mn).
- **word boundary = whitespace-insensitive containment predicate ONLY** (not in normalize()),
  preserving exact/normalized/token_f1 meaning (Spec-15). يَـٰبُنَىَّ↔يَا بُنَيَّ caught via contains.
- **collision gate**: before/after corpus sweep (19002 Qur'an words) is a DIAGNOSTIC — it shows
  65 "introduced" merges but most are CORRECT same-word Uthmani↔plene reunions (current scorer's
  dagger-DELETION spuriously split عِبَـٰدَنَآ→عبدنا); a few genuine merges (نبى/نبّئ). ⇒ the real
  gate is the HAND-VERIFIED pre-registered flip set at scoring granularity.
- **End-to-end validation on exp run**: converges — en retrieve_quote sol 3→6, sonnet 1→6; ar both
  0→5; complete_unit→7/7. My fold is MORE complete than the README quick-fold (resolves 10:50
  5d482247 residual via hamza rule). Exact flip set frozen during implement Phase 2.

Plan = 3 phases, rebaseline done ONCE: P1 build+test fold capability UNWIRED (committed scores
byte-identical, suite green); P2 wire into normalize()+containment + atomic rebaseline of all 4
runs + new test_orthography_rebaseline.py witness (non-Arabic SHA frozen + pre-registered flip
set) + rescope #15 oracle non-Arabic + re-pin first-run/tutorial guards; P3 governance docs +
run-README notes + architect moved-numbers packet.

Next: PLAN_DRAFTED → porch plan consult (codex+claude).

## Plan consult iter1 (2026-10-29) — both REQUEST_CHANGES, strategy endorsed; big blast-radius finds

claude grepped the real consumers and found gaps I missed. Re-verified each, then revised:
- **Scoping decision**: fold goes in NEW `score_normalize()`, shared `normalize()` UNTOUCHED.
  generate.py/editions.py use normalize() → folding there would move the committed question-set
  ANCHOR_DIGEST (generator drift) + touch the copyright audit. Scoping to scoring keeps digest
  stable. Architect endorsed.
- **Containment contract**: extend the single `bounded_contains` to be fold-aware (callers:
  score_answer, outcomes.classify_refusal:133, facct:277, probes:203) — one contract, no silent
  facct divergence.
- **Refusal-independence FALSIFIED**: fold-aware containment in outcomes ⇒ some Arabic `refused`
  cells reclassify. Flip set NOT refusal-independent. Corrected architect (my earlier claim was
  wrong).
- **Word-final detector must skip Mn+editorial** (fold runs pre-mark-deletion): 2972 corpus words
  have final maqsura behind marks (وَعَلَىٰٓ) — naive adjacency mis-folds →وعلا. Added predicate +
  stacked-mark test.
- **Omitted guard** test_original_run_regression.py (THE Arabic guard, 840 cells): re-pin re-score
  + facct asserts; digest assert stays stable.
- **Witness** strengthened to pin FULL Arabic before/after delta (normalized/token_f1/
  contains_reference/correct/outcome), not just flips.
- exp-run layout corrected (scores-en/ar + analyze.py, no summary; keep answers-ar-normalized as
  provenance). سأل≠سال noted unsatisfiable+pre-existing. TUTORIAL.md+CODE_WALKTHROUGH.md added to P3.

## Architect decisions (2026-10-29)
- **Merge order: #48 FIRST**, I rebase + re-run witness over post-#48 baseline. Recorded in plan.
- Both plan decisions endorsed (scoring-only score_normalize; hand-verified moved cells as gate).
- Directive: document نبى-class collision residue as a stated limitation in the SPEC (done — not a
  blocker).

Next: plan rebuttal + spec limitation edit committed → porch done (plan).

## Plan consult iter2 (2026-10-29) — both REQUEST_CHANGES, strategy holds; 2 silent-corruption traps

claude found two HIGH traps + wiring errors; codex found the submetric-wiring + ordering bugs:
- **TRAP: viewer false-green.** .codev/checks/test.sh maps runs/**→pytest lane ONLY; apps/viewer/
  src/local/tutorialRun.test.ts pins rebaselined tutorial numbers off-disk → "suite green" could
  hide red vitest. Fix: re-pin viewer test + run `pnpm -C apps/viewer test` explicitly + map runs→
  BOTH lanes.
- **TRAP: analyze.py:14 imports MAIN checkout** (`sys.path.insert(0,"/Users/.../sacredtexts/
  pipelines")`) → re-run from worktree uses UNFOLDED scorer (silent non-rebaseline). Fix path
  repo-relative first.
- **Wiring fixed**: exact stays RAW; token_f1 must switch its internal normalize()→score_normalize
  (else Arabic token_f1 won't move); normalized→score_normalize; contains→fold-aware bounded_contains;
  cite_passage _citation_candidates+boundary AND verdict both move together (else n_candidates
  disagrees → false hedge).
- **Ordering fixed**: score_normalize INTERLEAVES fold as NFKD→fold→marks, NOT fold()+normalize()
  (which runs fold before NFKD → compat forms evade). Prototype already did this; plan prose was wrong.
- **Rebaseline re-pin surface completed**: FLIP_SET + invariants + EXPECTED_ACCURACY/COVERAGE in
  test_contains_reference_rebaseline; non-Arabic SHA from pre-change `git show HEAD:` (not circular).
- **probes.py:18-40 fork** (looser context-free fold_arabic_letters used by clustered_accuracy):
  re-express over score_normalize (nothing committed depends on it).
- **Refusal nuance**: under default strict+containment, classify_refusal edit can't independently
  move an outcome (contained⇒correct=1⇒not refused via headline); matters only under --evaluator
  strict. Refused-set change flows through the flip set.
- Arabic-cell count pinned to chosen def (≈2/132/452; 840 was a looser count).

All folded into plan. iter2 rebuttal committed → porch done → plan approved, advanced to IMPLEMENT.

## Implement Phase 1 (2026-10-29) — fold capability, UNWIRED

Added to score.py (all unwired — default path byte-identical):
- `fold_arabic_orthography(text)`: position-aware. Manual scan: ىٰ digraph medial→ا / final→ي
  (medial detector SKIPS Mn+editorial to find next real letter — the وَعَلَىٰٓ trap), lone dagger→ا,
  standalone hamza ء→ا, bare maqsura→ي. Expects NFKD'd input; runs before mark deletion.
- `score_normalize(text)`: NFKD→quote/dash→fold→strip_script_marks→punct→ws (fold interleaved, not
  wrapped). normalize() untouched.
- `arabic_ws_insensitive_contains(answer,expected)`: fold-aware, whitespace-stripped containment
  for the word-boundary cases.

Tests: pipelines/tests/test_arabic_orthography_fold.py — 13 tests: per-pair folds (both
directions), already-folded cases, position-awareness (medial ا vs final ي), stacked-mark
وَعَلَىٰٓ→وعلي (not وعلا), must-differ قال/قيل + بيت/بات, NFKD-first (U+FEEF→ي), word-boundary helper,
Latin byte-invariance, Hebrew untouched, and a corpus collision DIAGNOSTIC over QUL (introduced
merges bounded <150 AND each is a true orthographic variant via a dagger→alef-aware skeleton).
Caught 2 bugs in my own reference skeleton (dagger must fold→alef not delete; tatweel must be
stripped) — fold itself was correct.

Full suite: 577 passed (564 + 13), 2 skipped. Committed-run guards green (byte-identical).

## Phase 1 impl consult iter1 (2026-10-29) — both REQUEST_CHANGES, fold logic confirmed correct

claude independently corpus-verified the fold (211 medial / 400 final / 15 bare-medial maqsura,
0 non-adjacent daggers). Two defects fixed:
- **Containment helper was script-blind + unbounded** (equated the rapist/therapist, Jude 1:3 in
  1:30, هدي in المهديون). Fixed with Arabic-gated anchored `\s*`-between-chars pattern (claude's
  approach); non-Arabic refs keep plain bounded containment. Added negative tests.
- **Diagnostic blind to its own collision class**: skeleton neutralized ء/ى so the 9 distinct-word
  merges passed silently; 4 are the hamza ء→ا class the spec hadn't named. Fixed: strict skeleton
  that KEEPS ء/ى distinct → residue = exactly 9 buckets, pinned as hand-annotated allow-list
  (_ACCEPTED_DISTINCT_WORD_MERGES); new collision fails. Two-sided bound (40<n<120) catches a no-op.
- Minors: parameterized `_normalize(text,*,fold)` so normalize/score_normalize can't drift;
  simplified vacuous _folds_equal.
- Documented the hamza collision class in score.py comment AND spec known-limitation (was
  maqsura-only). Residue: hamza {سواء/سوء, جزاء/جزء, وراء/ورءا, ملأ/ملء, شىء/شيـٔا, برىء/بريـٔا},
  maqsura {نبى/نبّئ, قرى/قرئ, أمرى/امرئ}.

Full suite: 578 passed, 2 skipped. Guards green. Next: commit P1 fixes, porch done, Phase 2.
