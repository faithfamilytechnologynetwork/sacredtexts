# Builder aspir-48 — Refusal-classifier false positives (#48)

## Specify phase (2026-10-29)

**Problem**: `outcomes.classify_refusal` over-calls `refused` on `*-search` answers that hedge
("I couldn't find the exact edition…") then deliver the passage in a different vocalization that
`bounded_contains` can't fold. Both halves of the rule (leading cue + reference-not-delivered) fire,
so a genuine attempt is labelled `refused` and dropped from the accuracy denominator — biasing the
paper's search-arm accuracy/coverage.

**Pre-registered set**: the exact 11 `(model_id, question_id)` cells in
`runs/tutorial-2026-10-11/jev_agreement.json` where deterministic=`refused` but judge `refusal_p`
low (`deterministic_only=11`, `judge_only=0`). All `retrieve_quote`, 10 opus-search + 1 haiku-search.
Enumerated in the spec table. These flip `refused → incorrect` (correct bit already 0).

**Recommended approach**: detect best-effort delivery past the hedge (Approach 1) — keeps refusal
deterministic/byte-stable, does NOT wire the judge into the outcome layer (that's the cross-check,
not a runtime input). Rebaseline committed scores.jsonl under the sanctioned-rebaseline discipline
(projection-SHA oracle + pre-registered flip set, à la `test_contains_reference_rebaseline.py`),
surface moved numbers to architect before commit.

**Open**: which runs beyond tutorial-2026-10-11 the global rule also moves (plan must enumerate);
sequencing vs #52 (aspir-52, concurrent normalize()/orthography rebaseline — architect heads-up
2026-10-29: expect rebase + oracle re-run if their PR merges first).

Spec drafted; signalled SPEC_DRAFTED. Porch ran the 2-way consult (codex + claude).

### Consult + major reframe (2026-10-29)

- **codex: COMMENT** (minor) — "near-certain" overstated (6/11 at refusal_p 0.36-0.49); pin moved numbers.
- **claude: REQUEST_CHANGES (HIGH)** — the decisive finding, which I verified directly in the run data:
  the issue's "flip all 11" premise is UNSATISFIABLE. Agreed refusal `opus-search/retrieve_quote-42f510ea6c7d`
  (refusal_p 0.58, NOT in set) is textually identical to flip-set members `de9d77a6c963` (0.45) and
  `fe52da70f661` (0.47) — same "I couldn't find X; closest is a DIFFERENT line «…»; can't say it's the
  segment; pointer". No length/script/quote signal separates them (confirmed: 42f=484 chars vs de9=445).
  So flipping all 11 while keeping the 0.58 twin refused = overfitting the oracle.

- **Resolution** (architect ENDORSED my default, 2026-10-29): split by **assertion**, not refusal_p.
  A = delivered-as-answer (model presents text AS its answer, "from memory X is:", "best reconstruction")
  → flips refused→incorrect. B = declined-with-substitute (different/unidentified line + pointer, explicitly
  NOT the requested passage) → STAYS refused. The 5 confident cells (refusal_p ≤0.16) are A; the 6 borderline
  (0.36-0.49) + the 0.58 twin are B. Rationale: taxonomy asks "did the model purport to answer?"; scoring B
  incorrect rewards confident confabulation; coverage already prices the decline (Spec 15). Mirrors
  verify_source leading-stance. Jev rubric UNTOUCHED this PR (#47 grader identity); divergence noted,
  re-align in future sacredbench-jev-2.

- **Pinned numbers** (confident-5 flip): opus-search retrieve_quote acc 0.9737→0.9250, cov 0.76→0.80,
  refused 24→20; haiku-search 0.80→0.7879, cov 0.65→0.66, refused 35→34. (flip-all-11 would've been
  opus 0.8605 — withdrawn.)
- **Retargeted criterion**: not "agreement_rate==1.0" (needs overfit) but "no surviving refusal disagreement
  with refusal_p<0.25; survivors lie in [0.25,0.75]". Anti-overfit test: 42f510ea6c7d must get the SAME
  outcome as its 0.45/0.47 twins.
- **Must re-pin** Spec 15's hand-surveyed constants (REFUSED_COUNTS/REFUSED_SET_SHA256/EXPECTED_*/
  test_first_run_*) — they break and go unmentioned in draft 1.
- Per-cell A/B dispositions locked at PLAN phase. Spec revised + checks pass.

### Plan phase (2026-10-29)

Per-cell A/B LOCKED (verified against full answer text in answers.jsonl; sha of crux cell
349b0b401f72 opus-search matches its judgment answer_digest — no data drift):
- A (flip refused→incorrect, 5): e2d74279aaf0(haiku-search), d4c3bda0b400, d0239d95ae29,
  b33e7e040058, 349b0b401f72 (opus-search). All assert "the text IS [requested passage]",
  disclaiming only edition/vocalization.
- B (stay refused, 6): f0ffc67a458e, 4c6f201c7192, de9d77a6c963, b1a04c81d33f, fe52da70f661,
  eaf381cf82d3 (opus-search). All carry a passage-IDENTITY disclaimer (segment not confirmed /
  different line / "start of daf" ≠ requested segment).
- B anchor (anti-overfit, not in 11): 42f510ea6c7d (0.58) + f143cc3f6c63 (0.68) — identical
  template to de9d77a6c963/fe52da70f661, MUST classify same (refused).

Gotcha learned: URL pointer is NOT a B marker — A cell 349b0b401f72 also has a sefaria URL.
The discriminator is passage-identity disclaimer vs vocalization-only disclaimer.

2 phases: (1) outcomes.py assertion rule + unit tests (no run evidence); (2) sanctioned rebaseline
of all 4 runs + projection-SHA oracle (sibling of test_contains_reference_rebaseline.py) + re-pin
Spec 15 constants (REFUSED_COUNTS/REFUSED_SET_SHA256/EXPECTED_*/test_first_run_*). Pinned numbers:
opus-search rq 0.9737→0.9250 / 0.76→0.80 / 24→20; haiku-search 0.80→0.7879 / 0.65→0.66 / 35→34.

Plan drafted; porch runs 2-way plan consult next.

### Plan consult + revision (2026-10-29)

Both plan consults REQUEST_CHANGES (HIGH), all verified in-data, folded (no architect decision needed):
- **Rule form fixed**: conjunctive "assertion AND no-disclaimer" is FALSIFIED by my own A cell
  d4c3bda0b400 ("I'm not sure which passage is segment 9" — a disclaimer, yet A). Switched to
  ASSERTION-ONLY (positive identity assertion fires → not refused; disclaimer not consulted).
- **Negation-aware / positive-frame**: flat "from memory" substring appears in 147 currently-REFUSED
  cells (38 tutorial/34 first-run/75 original), nearly all declines. Rule must match the positive
  frame "…text of X is:" NOT under a negation — never a bare substring family.
- **Blast-radius sweep moved into Phase 1**: read-only across all 4 runs + all _TEXT_RETRIEVAL tasks
  (complete_unit incl — original has 89 refused complete_unit), asserting global refused-delta ==
  locked flip set BEFORE any regen. Non-tutorial flip sets pre-registered empty unless sweep proves.
- **Artifact fixes (all verified)**: arabic run has NO scores.jsonl/summary — has scores-{ar,en}.jsonl
  + answers-{en,ar,ar-normalized}.jsonl + local analyze.py (fold); must regen via analyze.py path.
  original has facct.{json,md} (paper-facing, reads refused/acc/cov from metrics.outcome, no test
  catches staleness) + test_original_run_regression.py — both were missing from my file list.
- **Non-circular oracle**: freeze PRE-change (model,qid)->outcome SHA + correct SHA via git show HEAD;
  assert apply(flip_set, prechange)==postchange exactly + correct unchanged. Re-pinning
  REFUSED_SET_SHA256 alone is circular.
- **Numbers contingent**: 0.9250/0.80/20 etc are targets re-derived from actual flip set; safe
  fallback strands ambiguous A cells as refused + surface, never hand-fit.

Merge order (architect): I land FIRST, #52 rebases onto me. #52 later extends fold-aware containment
into classify_refusal → moves some Arabic refused-cells afterward (their witness, not mine).

Plan revised; porch re-consult or advance next.

### Implement phase_1 (2026-10-29) — classifier DONE, HOLDING on rebaseline

outcomes.py: added asserts_delivery() — assertion-only (positive identity frame "the line/text/
baraita … is/reads/starts : <script>"), negation-aware (apostrophe REQUIRED in n't so "segment"
doesn't match), + a refusal-to-deliver disqualifier ("don't want to give/guess", "fabricat"). Integrated
into classify_refusal text-retrieval branch (refused unless contains-ref OR asserts_delivery).
test_outcomes.py extended: 34 tests green incl the whole-corpus blast-radius GATE.

Gotchas banked:
- _NEG bug: "n['’]?t" (optional apostrophe) matched the bare "nt" in "segment" → false negation that
  stranded A cell d4c3bda0b400. Fixed to require the apostrophe.
- Whole-corpus sweep caught a REAL surprise: original/complete_unit-9a54331ae425 (opus) — a genuine
  Sahih Muslim refusal ("I don't want to give you a fabricated version") that my intro-regex caught via
  "the text after X is most likely <ar>". Fixed with the refusal-to-deliver disqualifier (principled:
  keyed on refusal-of-DELIVERY, not identity-disclaimers, so A cells unaffected). After fix: global
  blast radius == exactly the 5 tutorial A cells, 0 elsewhere.

BLOCKED-ish / HELD: surfaced to architect + awaiting go-ahead before touching committed evidence.
- Phase boundary collapses: classifier-only can't pass the global re-score guard (test_tutorial_run),
  so classifier + tutorial rebaseline must be ATOMIC. Only tutorial moves.
- Confirmed numbers (regen→tmp): opus-search rq 0.9737→0.9250/0.76→0.80/24→20; haiku-search
  0.80→0.7879/0.65→0.66/35→34. correct unchanged.
- summary.json scar: naive score_file NULLS the panel; current score_file also emits extra
  max_tokens/temperature panel keys (committed is 5-key, test_panel asserts it). PLAN: surgical splice
  of moved aggregates into summary.json/summary.md, panel/usage/generated_at byte-verbatim; regen
  scores.jsonl via score_file; add non-circular oracle (pre-change outcome/correct SHA) + re-pin
  test_contains_reference_rebaseline constants.
- first-run/original/arabic: 0 flips, byte-identical, facct untouched.

### Implement phase_1 COMPLETE — atomic rebaseline done (architect GO'd, 2026-10-29)

Executed exactly as surfaced + architect's 5 conditions:
- Captured pre-change SHAs BEFORE any write: OUTCOME=99a724e1…, CORRECT=de342249…, SIMILARITY=ab970582…
- Regenerated runs/tutorial-2026-10-11/scores.jsonl via score_file (5 cells refused→incorrect, correct unchanged).
- Surgical summary.json: overlaid moved numeric leaves on opus-search/haiku-search only (48 leaf diffs, ALL search arms); panel/usage/generated_at/expected_n/missing byte-verbatim. summary.md: replaced only the 4 moved scoring rows; panel table byte-identical (renderer now emits extra max_tokens/temperature cols — would've broken test_committed_summary_md, so NOT regenerated via renderer).
- jev_agreement.{json,md} UNTOUCHED (historical pre-fix evidence; post-fix agreement noted for review).
- first-run/original/arabic: byte-identical (git confirms only 3 tutorial files changed). facct untouched.
- Non-circular oracle: pipelines/tests/test_refusal_rebaseline.py (pre-change outcome+correct SHA; un-flip reproduces pre-change outcome projection → nothing else moved).
- Re-pinned test_contains_reference_rebaseline.py: tutorial REFUSED_COUNTS (hs 35→34, os 24→20), EXPECTED_ACC (hs .80→.7879, os .9737→.9250), EXPECTED_COV (hs .65→.66, os .76→.80), REFUSED_SET_SHA256 2a560379….
- Reframed my whole-corpus gate to the durable post-rebaseline form: no committed refusal asserts delivery (all 4 runs).

FULL pipelines suite: 585 passed, 2 skipped. Numbers match Waleed-seen plan pins exactly.

### Phase_1 DONE — 3 impl-consult iterations (2026-10-29)

phase_1 ✓ complete. Iteration history (all folded, committed):
- iter1: claude APPROVE / codex REQUEST_CHANGES (gate strength, edge end-behavior, phase-boundary
  doc). Fixed: reproduce-committed gate, classify_refusal==True edges, plan boundary note.
- iter1b (re-consult on fixed code): codex APPROVE / claude REQUEST_CHANGES — _ASSERT_INTRO
  over-fires on reworded B ("the closest line is:", "the opening text of the daf is:"). Fixed:
  _NON_IDENTITY modifier guard on the intro clause.
- iter2: codex+claude REQUEST_CHANGES. codex: _ASSERT_RECON missed _NON_IDENTITY → fixed. claude:
  rebaseline broke apps/viewer tutorialRun.test.ts (haiku-search refused 35→34/wrong 13→14), HIDDEN
  by dispatcher mapping runs/**→pipelines lane only. Fixed: re-pin viewer test (verified vitest 187),
  + architect GO'd dispatcher change: runs/**+texts/**→BOTH lanes (own commit).
- iter3: codex REQUEST_CHANGES (recon/intro negation not scoped widely enough — "reconstruction of
  what is probably NOT the requested line is:") / claude COMMENT (all verified; residual → #52).
  Fixed: scope negation+non-identity to the assertion's own SENTENCE (both paths); all 5 A cells keep
  a negation-free assertion sentence, 0 stranded.

Final rule: asserts_delivery = positive identity frame (INTRO "the <unit> is/reads/starts: <script>"
OR RECON "my best reconstruction of <wording>"), sentence-scoped negation+non-identity guard, global
refusal-to-deliver disqualifier, Hebrew/Arabic/Greek payload. Both lanes green (viewer 187, pipelines
586). Committed evidence: only the 5 tutorial flips.

Post-fix jev agreement (for review): 0.9725→0.985, deterministic_only 11→6, all 6 survivors
refusal_p∈[0.36,0.49]⊂[0.25,0.75], none <0.25 (satisfies retargeted criterion).
Moved similarity means (for review): opus-search token_f1 0.9098→0.8758, normalized 0.8684→0.825,
contains_reference 0.9737→0.925 (haiku-search likewise).

Phase_2 (residual, boundary collapsed into phase_1): per-run enumeration + post-fix jev note +
moved means → REVIEW doc; confirm byte-identical runs. porch emitted a context-refresh at the
phase_1→phase_2 boundary.

### Phase_2 re-entry + confirmation (2026-10-29, post-refresh)

Context refreshed; re-oriented from .builder-state.md + this thread. Confirmed phase_2's evidence
work is fully satisfied by committed phase_1 work (boundary collapse, architect-approved):
- Working tree clean; `git status --porcelain runs/` empty → committed runs byte-identical to HEAD.
- Oracle present: `test_refusal_rebaseline.py` (2 passed). Spec-15 re-pin present:
  `test_contains_reference_rebaseline.py` (13 passed). `test_facct.py` green.
- `jev_agreement.{json,md}` untouched (standing order — historical pre-fix evidence).
- `outcomes.py` module docstring already documents the A/B assertion rule + deliberate Jev divergence.
- Both lanes GREEN via dispatcher: apps/viewer 187 passed (19 files); pipelines 586 passed, 2 skipped.
Nothing new to build in phase_2. Signalling PHASE_COMPLETE (`porch done 48`); 2-way consult next,
then REVIEW doc.
