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

Full suite: 578 passed, 2 skipped. Guards green.

## Phase 1 impl consult iter2 (2026-10-29) — BLOCKING defect → design PIVOT (architect-endorsed)

claude found the big one: `dagger→alef` makes the U+0670 diacritic LOAD-BEARING. The
defective-spelling class (هذا/ذلك/الرحمن) OMITS the long-ā alef in Imla'i (lexical, not positional),
so forcing dagger→ا un-credits them — flipping 2 verbatim-correct committed tutorial cells to wrong.
2276/2648 dagger words affected. Inverts the spec's own harm.

**PIVOT (architect endorsed):** long-ā alef is OPTIONAL; ALL orthographic flex moves into the
CONTAINMENT predicate; normalize()/exact/normalized/token_f1 UNCHANGED.
- fold_arabic_orthography = symmetric folds only (ء→ا, BARE ى→ي; a ى carrying a dagger is left
  alone — else ءَاتَىٰنَا "He gave us" collides with ءَاتَيْنَا "we gave").
- fold_aware_contains = bounded_contains OR fold-match-with-optional-ā(ا?) + ws-flex + bounded.
  STRICT SUPERSET → normalized=1⇒contains=1, only ADDS credit.
Validated: 2 cells preserved, plene/defective/digraph/final/hamza/word-boundary credited, experiment
converges, negatives rejected (therapist/Jude 1:30/digit-separators/sub-word), superset asserted.

**Blast radius SHRANK**: rebaseline moves ONLY contains_reference/correct/outcome; ALL similarity
submetrics (incl. non-Arabic) frozen. Witness simpler; #48 rebase simpler. Updated spec (kept
هذا/الرحمن as the counterexample per architect), plan Phase-2 wiring, score.py docstring.

codex iter2 (both fixed + carried into pivot): (1) Arabic-Indic digits were treated as Arabic in
ws-flex (١ ٣ matched ١٣) → gate flex on Arabic LETTERS (cat L, excl digits); (2) allow-list froze
only bucket keys → now pins per-bucket strict-skeleton SETS.

Full suite: 575 passed, 2 skipped. normalize() byte-identical, ANCHOR_DIGEST stable.

## Phase 1 impl consult iter3 (2026-10-29) — pivot verified correct; 1 blocking bug + fixes

Both confirmed the pivot is correct + corpus-validated. Fixes:
- codex: **direction-independence** — fold only made long-ā optional when the REFERENCE had a
  dagger. Now match the ref pattern against BOTH score_normalize(answer) AND _answer_plene_form
  (dagger→ا), so Imla'i-ref↔Uthmani-ans works. Kept per-position ا? (mixed verse هذا الكتاب).
- claude BLOCKING: _fold_containment_pattern dropped normalize's whitespace collapse → a `\n` in a
  ref became a required literal newline → fold branch DEAD for 23 hadith refs in original-2026-10-21
  (#39 is hadith-heavy). Fixed: fold any ch.isspace()→" ". Added multiline test.
- claude: diagnostic swept only score_normalize equality → blind to ا?/plene branch. Now sweeps BOTH
  answer forms; residue = 10 buckets (9 + plene-only راا رَأَىٰ/رَءَا), all pinned. Named the optional-ā
  class in score.py comment + spec.
- claude: _answer_plene_form was a 3rd pipeline copy (caused the ws bug). Parameterized
  _normalize(text,*,fold,plene); all delegate. Extended invariance test to plene form.

Full suite: 577 passed, 2 skipped. Guards + ANCHOR_DIGEST unchanged.

## Phase 1 COMPLETE (2026-10-29). Phase 2 BLOCKED on #48 merge-order.

porch advanced to phase_2. BUT architect decision stands: **#48 lands FIRST, then I rebase onto it
and do Phase 2 atomically**. Checked: #48 (aspir-48) has NO PR yet / not merged (its phase_1
rebaseline is done locally, 585 passed, but still in implement). So Phase 2's rebaseline is blocked —
the scorer wiring moves committed contains_reference, can't go green without the rebaseline, and the
rebaseline must happen ONCE over the post-#48 baseline.

**Intel from aspir-48's thread (critical for my Phase 2):**
- #48 moves ONLY tutorial (5 cells refused→incorrect; correct unchanged). first-run/original/arabic
  byte-identical; facct untouched; jev_agreement untouched.
- #48 re-pinned test_contains_reference_rebaseline.py tutorial constants (REFUSED_COUNTS hs35→34
  os24→20, EXPECTED_ACC hs.80→.7879 os.9737→.9250, EXPECTED_COV, REFUSED_SET_SHA256) + added
  test_refusal_rebaseline.py. So after I rebase, those tutorial pins are #48's values; MY orthography
  changes layer on top.
- **SUMMARY SCAR**: naive score_file/renderer regen NULLS the panel AND emits extra
  max_tokens/temperature cols → breaks test_committed_summary_md/test_panel. Must SURGICALLY SPLICE
  moved numeric leaves into summary.json/md, panel/usage/generated_at byte-verbatim. #48 already
  spliced tutorial's summary → my tutorial splice lands on #48's file. (Folded into plan Phase 2.)

ACTION: surfaced block to architect; holding for #48 merge + their go. porch "Refresh your context"
task is pending — reasonable to refresh when resuming Phase 2 fresh.

## Hold prep (architect: HOLD entirely, no early PR; #48 imminent) — 2026-10-29

Architect said hold, use the time to pre-draft. Done (all committed):
- `codev/projects/52-.../phase2-runbook.md` — the one-clean-motion Phase-2 script: rebase onto
  post-#48 → capture pre-change SIM/MOV SHAs (ready-to-run snippet) → wire bounded_contains→
  fold_aware_contains (score_answer contains_reference, cite verdict, outcomes, facct, probes) →
  SURGICAL summary splice (the #48 scar) → facct/jev_agreement regen → fix analyze.py path → re-pin
  oracles + new test_orthography_rebaseline.py witness → viewer re-pin + dispatcher runs→both-lanes
  → hand-verify every moved cell → moved-numbers packet to architect → one atomic commit.
- `codev/reviews/52-*.md` — review doc; Phase-1 sections final, moved-numbers table TBD in Phase 2.
- `codev/projects/52-.../pr-body.md` — PR body draft, moved-numbers TBD.

STATE: Phase 1 complete & committed; Phase 2 fully scripted & ready. HOLDING for architect's
"#48 merged" ping, then execute the runbook as one motion. Nothing else to do until then.

## Phase 2 GO — rebase + dry-run witness (2026-10-29)

Architect pinged: #48 (PR #55) + jasbir's SGGS PR #51 merged externally; also a cli.py canary gate
(generate only, no scoring contact). Rebased builder/aspir-52 onto origin/main — CLEAN, no
conflicts (Phase 1 was additive/unwired). Suite 612 passed / 2 skipped on the merged baseline
(pre-wiring). PR #51 moved ANCHOR_CORPUS_HASH/ANCHOR_DIGEST (SGGS in corpus); generation untouched
by me so the digest is whatever #51 set — my witness must compute over this corpus state.

WIRED (working tree, not committed): 5 call-sites bounded_contains→fold_aware_contains —
score.py contains_reference (:486) + cite verdict (:457), outcomes.classify_refusal (:348),
facct.py (:291), probes.py (:203). cite_passage/facct/probes are Latin-only no-ops on committed
data (0 Arabic citations; facct skips non-Bible) — swapped anyway per plan's "one shared contract"
(prevents future divergence). Updated the adjacent docstrings/comments.

DRY-RUN WITNESS (re-scored every committed run's answers with the wired scorer, wrote NOTHING to
runs/): SIM (exact/normalized/token_f1) projection SHA byte-identical on all 5 score files — frozen
oracle holds. 58 moved cells, ALL 0->1 / incorrect->correct, zero losses, zero coverage change:
- tutorial 86.0->93.2% (+20), original 47.7->49.1% (+15: cu +6, rq +9), first-run 0.
- exp via its analyze.py (path-patched to worktree scorer, scratch dir): pre-fold en 82.1/78.6 ar
  71.4/71.4 w/ 5 en->ar flips -> POST-FOLD all four 96.4%, 0 flips. Artifact eliminated. (en 9, ar 14.)
GOTCHA found: my first exp dry-run scored RAW answers-ar.jsonl and showed 14 bogus verify_source
correct->refused flips — because exp scores the NORMALIZED copy (answers-ar-normalized.jsonl, نعم/لا
-> Yes/No). Using analyze.py's real path, those 14 stay correct. Lesson: exp has a bespoke scoring
path; don't lens it through generic score_answer.
HAND-VERIFIED all 58: each the same verse/hadith word-for-word in Imla'i; shortest ref 8 words
(median 17) -> no short-fragment collision.

SURFACED packet to architect (held in mailbox) with ONE decision: exp is EXPERIMENT evidence —
(A) regenerate its scores in place + README pre/post sections, or (B) keep committed scores as the
pre-fold record + README-only post-fold proof. Recommended (A) + fix analyze.py:14 hardcoded
main-checkout import path. HOLDING the runs/ commit for the architect's ack on exp treatment.
Review doc moved-numbers table filled. Next: write test_orthography_rebaseline.py witness + re-pin
oracles while waiting; do the atomic commit after ack.

## URGENT HOLD — competing #57 merged (2026-10-29)

Architect URGENT HOLD mid-Phase-2: Jonathan Karr merged PR #57 (karr/issue-52-arabic-orthography,
154e0ef) directly to main — a COMPETING implementation of #52 — outside review, while I was
executing the rebaseline. Do NOT commit, do NOT open PR, until the architect reconciles with Waleed.

Stopped cleanly after the md-splice step. WORKTREE STATE at hold:
- NO commit / push / PR. HEAD = f9561e0 (rebased hold-prep). Branch does NOT contain #57 (I rebased
  onto 59fc3eb = main+#48+#51, pre-#57).
- Done in working tree (uncommitted, reversible): wired 5 call-sites; regenerated
  tutorial/original scores.jsonl (+20/+15) + spliced summary.json/md (panel/usage byte-identical);
  first-run scores byte-identical; exp scores-ar/en (+14/+9) + analyze.py path fix + Option-A
  README rewrite (pre/post sections); test_facct re-pin.
- NOT done: original facct regen, tutorial jev_agreement regen, oracle re-pins,
  test_orthography_rebaseline.py, viewer re-pin, dispatcher both-lanes, commit.
- Witness validated: 58 cells all 0->1, SIM frozen, coverage frozen, exp all-four 96.4% / 0 flips.
  Found + documented a residual: Q14:34 word-initial hamza-alef ءَا ↔ alef-madda آ NOT folded
  (1 cell, identical both conditions, not a content error) — logged in exp README, NOT fixed
  (scope discipline; a ءَا↔آ rule needs its own collision analysis).

HOLDING. No commit, no revert, no further writes. Asked architect whether to keep tree as-is for a
diff vs #57, reset to clean, or proceed to commit if the reviewed/witnessed path prevails.

## Reconciliation + Phase 2 COMPLETE (2026-10-29)

Waleed greenlit reconciliation of the competing #57/#58. Rebased branch+tree onto origin/main
(b93e881, post #57/#58/#51/canary) — CLEAN (my Phase-1 commits patch-skipped via #58).
BIG FINDING: `08f43b8` ("fix double code branch") had ALREADY converged to MY design — frozen
normalize(), my symmetric fold_arabic_orthography, score_normalize/fold_aware_contains/optional-ā
pattern, original skeleton test_normalize_nonlatin (his materialise-fold + ذالك asserts reverted),
kept his outcomes _INTRODUCER escape fix. Only wiring (contains_reference still bounded) remained →
my WIP supplied it. His approach was the REJECTED one (materialises dagger→alef; his own test
asserted normalize('2:2')=='ذالك...' = the defective-class defect).

Re-regenerated everything on the new base + re-ran witness: IDENTICAL to the 58-cell packet (SIM
frozen all 5 files, coverage frozen, exp all-four 96.4%/0 flips) → no re-surface needed.

Phase-2 done (all in working tree, uncommitted):
- scores regen: tutorial +20, original +15, first-run 0, exp ar+14/en+9.
- summary.json/md surgical splices (panel/usage/generated_at byte-identical both runs).
- original facct regen (embedded outcomes moved; counterfactual unchanged). jev_agreement LEFT
  historical per #48 precedent (README already directs to summary.json); README note extended.
- analyze.py import path fixed (repo-relative); exp README Option-A rewrite (post-fold current,
  pre-fold historical, the Q14:34 hamza-alef↔madda residual documented).
- oracle re-pins: test_contains_reference_rebaseline[tutorial] FLIP_SET 20→40 + ACC;
  test_refusal_rebaseline re-pinned to current-state invariants (A, architect-approved, docstring
  cites PR#55/review/pre-#52 b93e881); test_facct literal; NEW test_orthography_rebaseline.py (SIM
  frozen all 5 + superset + mover counts + exp recovery). Viewer tutorialRun.test.ts re-pinned.
- run READMEs (tutorial + original) updated for moved numbers + orthography narrative;
  lessons-learned.md orthography lesson updated.
- e2d74279aaf0 triple-penalty (refused→incorrect→correct) pinned + documented.

Suites: pipelines 625 pass / 2 skip; viewer 187 pass; copyright audit OK. NOTHING committed yet.
NEXT: update pr-body, stage explicitly, ONE atomic commit, push, open PR via normal pr gate.

## Phase_2 consult rounds + iter3 HOLD (2026-10-29)

iter1 (codex+claude REQUEST_CHANGES): folded — regenerated jev_agreement (containment 0.9325→0.9825,
judge-only 27→7, det-only 0 = independent no-wrong-credit corroboration); strengthened witness to
exact mover-identity sets + summary↔scores self-consistency; narrowed the directionality claim.
Commits 185b40c.
iter2 (claude APPROVE; codex RC on the Arabic-cell partition pin): folded — added
test_arabic_cell_partition_pinned (letters-only predicate, arabic-expected + arabic-either per run)
+ _overall summary guard + digraph/maqsura doc. Commit e49ff5a.
iter3 (codex APPROVE clean; claude REQUEST_CHANGES HIGH): claude caught a REAL error — the ءَا↔آ
residual I'd called '1 harmless cell, no bias' is ~8 cells (verified ≥3 by hand) and ASYMMETRIC:
on tutorial, same-verse, haiku-search wrote ءَال/ءَامَنَ (credited) vs haiku آل/آمَنَ (not) → ~2pts
of the haiku 88%→92% 'search lift' is an orthography artifact; haiku is under-credited (conservative,
never wrong-credited). Verified cells: tutorial a8df3e43d35d, 1d74fc87541b, e2d74279aaf0 (haiku).

HOLDING porch at iter3 (NOT advancing to pr gate). Surfaced to architect with options:
(A) fix the fold now (collapse ءا↔آ) = ~full Phase-2 redo (re-rebaseline + re-consult); or
(B) document honestly + pin residual + surface in packet + defer fold to #39 (claude explicitly
endorses B). Recommended B. Awaiting architect decision. Then fold claude's 2 minor comments
(probes _LETTER_FOLD divergence doc; cite_passage fold-branch looseness for #39) either way.

## iter3 resolved — architect chose (B); advancing to pr gate (2026-10-29)

Architect: (B) document+pin+defer. Done:
- Exact 8-cell ءَا↔آ residual set found (proper detector: delete hamza-before-alef + existing
  optional-ā → matches claude's 8). Pinned in test_orthography_rebaseline.py::HAMZA_ALEF_RESIDUAL
  + test asserting all 8 contains_reference=0 (ready-made oracle for the follow-up).
- Filed issue #60 (fold extension ءَا↔آ + ىٰ↔maqsura, pinned set, asymmetry evidence).
- Corrected review residual section (8 cells not 1, asymmetry, #60). Tutorial README: quantified
  ~2-3pt artifact (haiku under-credited; 2 of 3 "missing" are residual not content errors), #60.
  exp README: #60 ref + noted exp's 4 cells are symmetric (no en/ar skew). PR body known-limitations.
- Folded claude minors: probes _LETTER_FOLD divergence doc; cite_passage fold-branch #39 note.
Suite 638 pass / 2 skip; viewer 187; audit OK. Committing, then porch → pr gate (HUMAN approval;
I do NOT self-approve). Packet to architect at the gate includes the residual census.
