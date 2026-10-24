# Builder aspir-32 thread — FAccT benchmark card + cross-edition reading (#32)

Part 3 of 3 of Jonathan Karr's PR #30. Rework his card against main's scoring contract.

## Key facts established (specify phase, 2026-10-23)
- Data source: `runs/original-2026-10-21/` (3 models: gpt-oss-20b, haiku, opus; 476 Q; 17 texts). Read as-is, NEVER re-score/collect/generate.
- Outcomes come from `scores.jsonl` `metrics.outcome ∈ {correct,incorrect,refused}` (set once in `outcomes.py`). NO second refusal regex, NO `fabrication` label.
- Headline = containment contract (Spec 15). `evaluators: ["strict","containment"]`.
- Census source: manifest `selected_texts`(17) + `excluded_texts`(2, with reasons) + catalogue `source.yaml` (license, canonical language, zero-question languages).
- Embedded question `expected` holds only `citation` (NOT text) → gold text resolves from raw editions index by citation.
- Edition counterfactual: only the 3 English Bibles (KJV/ASV1901/WEB) have sibling editions in this pool → counterfactual is inherently Bible-scoped. `cite_key` already parses Bible-style citations. Arabic/Hebrew citations excluded by construction (no sibling edition) — card must SAY so, never mis-parse them into a Bible match. Tag qualifying misses `other_edition`.
- Prose in ONE editable place (Jonathan drafting paper). Chose: constants block in facct.py (Approach 1).
- Output path: `runs/<id>/facct.{json,md}`. Zero API spend. Audit (audit.py) must pass — no NABRE/TLG text. Public repo.
- Preserve Jonathan's authorship on carried-over commits (`git commit --author`). PR: "Part 3 of 3 of #30", closes #32. NO Generated-with/Co-Authored-By.
- Viewer per-run card view = optional (reads facct.json, no new scoring). Likely defer.

## Spec consult (specify iter1, 2026-10-23) — both REQUEST_CHANGES, HIGH. All folded in.
codex + claude both verified against real data. Dispositions (ACCEPTED all):
1. `expected` schema is TASK-DEPENDENT (claude, verified): retrieve_quote→{text}, complete_unit→{text,full_text}, cite_passage→{citation}, verify_source→{answer,true_*}. Citation always in source.citation. Gold wording for retrieve_quote = expected.text (NOT only raw index). Fixed Assumptions.
2. Edition counterfactual scoped to retrieve_quote ONLY (both). complete_unit gold is partial → no well-defined sibling segment. Incorrect Bible cells: 32 retrieve_quote + 21 complete_unit = 53 (verified). Report numerator AND denominator per model.
3. Open Q1 resolved: containment (exact is subset of containment — Q was ill-posed). other_edition = a DIFFERENT edition than requested (requested would already be correct).
4. Restricted-index guard: real gate is select_targets(include_restricted=False)/license!=restricted on the EditionIndex, NOT pool exclusion. NABRE = 4th English Bible (work=The Bible, canonical_language=en) → indexable sibling if payload present. Added explicit filter + test criterion.
5. Problem Statement factual fix (codex): run does NOT contain Vatican docs/English Talmud — those are EXCLUDED catalogue members. Reframed as catalogue coverage vs run composition.
6. Zero-question languages (codex): disambiguated to catalogue SOURCE languages (each source's `language` field) contributing zero to pool.
7. Fail-fast (codex): non-zero exit, no partial facct.{json,md}, on missing files / non-joining rows / scores↔summary disagreement. Added criterion + test + risk.
8. Join mechanics (claude): scores.jsonl rows have no text identity → join answers.jsonl on (question_id,model_id); sub-metrics are task-scoped. Added to Assumptions.
Structure verified conformant to spir/templates/spec.md (claude).

## Architect GO + 3 tweaks (2026-10-24) — folded into spec
1. EditionIndex = SHARED standalone module (for #21). CLI `sacredbench edition-index --out <path>` → JSONL + manifest, mirrors questions.jsonl convention. FROZEN schema:
   row: {work, citation, language, wordings:[{version,text},...]} — one row per (work,citation,language); wordings sorted by version; same-canonical-language editions only; license!=restricted (NABRE never appears); single-wording rows omitted.
   manifest <path>.manifest.json: {corpus_hash, row_count, digest(sha256 prefix of file), excluded_restricted:[version ids]}.
   Card builds counterfactual from this module in-process; file export is for #21. Test: restricted payload present locally never reaches file + named in excluded_restricted.
2. Viewer card view DROPPED entirely (out of scope; its own issue if wanted). No half-scoped items.
3. Every number in facct.md derived at build time from scores.jsonl/summary.json, never typed. Test: card headline figures == summary.json (anti-drift, cf Spec 26 docstring drift).

## Plan (4 phases, foundation-first)
1. Shared edition_index.py module + `edition-index` CLI (JSONL+manifest, frozen schema for #21, restricted filter, determinism).
2. facct.py card data → facct.json (census, outcomes-from-scores, Bible retrieve_quote counterfactual, fail-fast). Promotes score's contains_reference predicate to public + reuses it.
3. facct.md: one prose block, both files written by default within run_dir (atomic both-or-neither), anti-drift.
4. Generate+commit card for runs/original-2026-10-21; EXTEND audit.py to scan .md + test; byte-digest integrity; real-run drift guard.
Carry-over phases (1-3) committed --author="Jonathan Karr <jka83321@gmail.com>".
Scope decision: 3-edition agreement table EXCLUDED (keep docs bar simple).

## Plan consult (plan iter1, 2026-10-23) — both REQUEST_CHANGES HIGH, all folded
Both verified real data; claude confirmed ≈32 incorrect Bible retrieve_quote cells exactly. Key facts I re-verified:
- audit.py (L130/132) scans only .json/.jsonl → .md NOT covered. Extend in Phase 4.
- score.py: _contains(L193) + _bounded_equal(L252); contains_reference uses _bounded_equal(L305). Reuse THAT predicate (promote to public) — don't reimplement containment.
- generate.corpus_hash = sha256[:16] (L465); question_set_digest [:16] (L453) → pin digest length.
- index must read texts/raw/** via convert.convert_target (standardized is gitignored/absent in CI).
Dispositions: (1) pin containment to score's predicate+normalize (2) pin corpus_hash/digest/ordering/excluded_restricted (3) extend audit to .md+test (4) write both files by default atomically within run_dir (5) byte-digest integrity not git status (6) raw-source pin (7) both-files (8) exclude agreement table + add real-run drift guard. Rebuttal committed.

## IMPLEMENT phase_1 DONE (2026-10-23)
Created pipelines/sacredbench/edition_index.py (carries over Jonathan's cite_key/Passage/EditionIndex/index_documents from PR#30 cross_translation.py; added language to Passage, load_edition_documents, export_rows, write_export/build_manifest). CLI `edition-index` wired + EditionIndexError in main() handler. Tests: test_edition_index.py (7 pass). README line added.
Verified real catalogue: 31,102 Bible rows (KJV/ASV/WEB share every citation), excluded_restricted=['NABRE','TLG']. NABRE=The Bible/NABRE/en/en (restricted, 4th English Bible) — filtered by license even with payload present (test proves it). Full suite 393 passed/1 skip.
Export default path: texts/edition_index.jsonl (NOT committed — derived on demand; card uses module in-process; #21 regenerates).
Commit authored to Jonathan Karr <jka83321@gmail.com> (carries his code).

## Phase_1 impl review (2026-10-23): codex APPROVE, claude REQUEST_CHANGES — both fixed
- Fix1: canonical-language guard (language==canonical) was untested → added assertions (real catalogue: Talmud-English/Encyclicals absent; tmp fixture: non-canonical Davidson-English edition). Removing guard now fails.
- Fix2: default --out texts/edition_index.jsonl was NOT gitignored (17MB) → added to .gitignore (both file+manifest).
- Minor adopted: export_rows now RAISES EditionIndexError on conflicting (work,citation,version) duplicate (fail-fast; +test). Gives EditionIndexError a real use.
- Minor adopted: NOTE on by_cite that Bible consumer (Phase2) must filter work=="The Bible" (LDS also uses Book ch:verse).
- Suite: 394 passed/1 skip. Rebuttal committed. Phase_1 fixes commit authored as me (review-response work, not new carried code).
Phase2 reminder: filter Bible-only via work=="The Bible"; source tradition from catalogue not Passage; reuse score's contains_reference predicate (promote _bounded_equal).

## Phase_1 COMPLETE ✓ (commits 5a4c64b carry-over[Jonathan], + fix commit, + polish commit). iter2 both APPROVE. Suite 395 pass/1 skip.

## === PHASE 2 RESUME NOTES (card data → facct.json) ===
Goal: pipelines/sacredbench/facct.py `build_facct(run_dir)` → writes facct.json. Pure analysis, no network, fail-fast no-partial.
Reads from run_dir: scores.jsonl, summary.json, answers.jsonl, questions.jsonl.manifest.json. Plus catalogue (cat.discover_catalogue) + edition_index module in-process.

DATA SHAPES (verified):
- scores.jsonl row: {question_id, model_id, task, metrics:{...,outcome}}. outcome∈{correct,incorrect,refused}. Text-retrieval metrics also: exact/normalized/token_f1/contains_reference. cite_passage: {correct,n_candidates,outcome}. verify_source: {parsed,expected,correct,outcome}. NO text identity on score rows → JOIN to answers.jsonl on (question_id, model_id).
- answers.jsonl row has embedded `question`: {id,task,prompt,expected,source}. source={tradition[list],work,version,language,document_type,citation,requested_as}. expected is TASK-DEPENDENT: retrieve_quote→{text}, complete_unit→{text,full_text}, cite_passage→{citation}, verify_source→{answer,true_*}. Gold wording for retrieve_quote = expected.text. citation always in source.citation.
- summary.json: {models:{<id>:{<task>:{n,accuracy,coverage,correct,incorrect,refused,refused_rate,...}, _overall:{...}}}, by_tradition, by_text, usage, panel, evaluators:["strict","containment"], generated_at}.
- manifest: selected_texts[17]({work,version,language}), excluded_texts[2]({work,version,language,reason}), corpus_hash, question_set_digest, n_questions.

PHASE 2 BUILD (from plan + reviews):
1. census: 17 selected texts by tradition/doc_type/license(from catalogue target join on (work,version,language)) + language; source languages contributing zero questions; 2 excluded texts w/ manifest reasons. SOURCE tradition/doc_type/license from CATALOGUE target, NOT Passage.
2. outcomes: counts straight from scores.jsonl metrics.outcome (verify vs summary.json). NO recompute, NO fabrication label, NO 2nd refusal regex.
3. counterfactual: incorrect Bible retrieve_quote cells only (NOT complete_unit). Filter Bible via work=="The Bible" (by_cite has no work!). For each, check if answer CONTAINS some OTHER edition's wording of same citation using PROMOTED score predicate. Tag other_edition. Report numerator+denominator per model. Requested edition excluded. Non-Bible citations never match (cite_key returns None).
   → MUST FIRST promote score._bounded_equal (word-bounded over normalize, used by contains_reference L305) to PUBLIC in score.py; reuse verbatim. facct.py defines NO containment/normalize of its own. Test it agrees with scorer boundary/script cases.
4. fail-fast FacctError (no partial facct.json) on: missing file, non-joining row, unresolved catalogue target, scores↔summary count disagreement.
CLI: @app.command("facct") run_dir arg, writes facct.json by default. Wire FacctError in main().
Tests: test_facct.py — outcome fidelity, counterfactual core, complete_unit excluded, non-Bible not matched, requested-edition not tagged, fail-fast, no-fabrication, no-private-matcher.
Expected real numbers: 32 incorrect Bible retrieve_quote cells across panel (21 complete_unit excluded).
Phase3 after: facct.md both-files-by-default atomic within run_dir, one prose block, anti-drift. Phase4: extend audit.py to .md + test, byte-digest integrity, real-run drift guard, author carry phases to Jonathan.

## PHASE 2 COMPLETE ✓ (facct.json card data)
- score.py: promoted _bounded_equal → public `bounded_contains` (kept `_bounded_equal = bounded_contains` alias for existing callers/outcomes.py). This is THE contract containment predicate; facct reuses it verbatim.
- facct.py: build_facct(run_dir, raw_root) → dict. census (17 texts by tradition/lang/doctype/license from catalogue Target join on text_key; zero_question_languages = all target langs − pool langs; excluded_texts w/ manifest reasons); outcomes (counts from scores.jsonl metrics.outcome, verified == summary.json, FacctError on disagreement); counterfactual (incorrect Bible retrieve_quote only, work=="The Bible" filter, skip requested version, reuse score.bounded_contains, numerator+denominator per model seeded for ALL models, other_edition tags). FacctError fail-fast (missing file / non-join / unresolved target / scores↔summary mismatch) BEFORE any write. write_facct_json separate.
- cli.py: `facct <run_dir>` writes facct.json (default <run_dir>/facct.json). FacctError wired.
- test_facct.py: 12 tests incl real-run (census n_texts=17, zero_q=['grc'], excluded={Encyclicals,Talmud}, denom=32).
- REAL RUN VERIFIED: 17 texts, 476 Q; counterfactual denom total=32 (gpt-oss 0/17, haiku 3/15, opus 0/0), 3 other_edition tags (haiku: Jeremiah 38:15 ASV→KJV etc). Run evidence untouched.
- Suite 407 pass/1 skip. Commit authored Jonathan (facct.py reworked from his PR#30 facct.py).

## Phase_2 impl review (2026-10-23): codex + claude both REQUEST_CHANGES HIGH — all fixed (415 pass)
- Must-fix: scores↔summary verify made BIDIRECTIONAL (set equality) + _overall recomputed from summed task counts (+raise). _outcomes overall derived from scores not copied. Tests: empty scores/dropped task/corrupted _overall all raise.
- Must-fix: join one-to-one via _index_unique (dup+missing key) + both-key-set equality. Tests: dup answer, unmatched answer.
- Must-fix: requested-edition guard now tested (Test 6:6 KJV-requested answer=KJV wording, incorrect, NOT tagged; deleting guard breaks test).
- Minors: tag:"other_edition" field added to each tagged cell; s["task"] KeyError→FacctError; evidence-immutability test (sha256 4 inputs); explicit per_model seeding.
- Real run still: denom 32, num 3, tags carry "tag" field. Fix commit authored as me.
- PHASE 3 TODO (from reviews): prose must explain zero_question_languages=['grc'] is a held-back source (TLG restricted), NOT a coverage gap.

## Phase_2 iter2: both APPROVE. Post-approval polish folded: accuracy/coverage RECOMPUTED from verified counts (not copied); n_questions cross-checked vs distinct question_ids. 417→then phase3.

## PHASE 3 COMPLETE ✓ (facct.md markdown card)
- facct.py: added CARD_PROSE block (ONE editable place, Jonathan owns wording) + report_markdown(report). Every number interpolated from report (anti-drift); _pct/_n helpers. Prose sections: census intro, zero_language_note (grc=held-back TLG not coverage gap), excluded_note, outcomes intro (accuracy-beside-coverage), counterfactual intro, claims/failure/non-conclusions/review. Embeds citations+numbers only, NO verse bodies.
- cli.py: facct writes BOTH facct.json + facct.md into run_dir by DEFAULT. --json/--md overrides validated WITHIN run_dir via _within(). Build+render BOTH before writing EITHER (both-or-neither).
- test_facct.py now 28 tests: +prose-sections, +drift-guard (flip cell in scores+summary → md number moves; 40.0% not present before), +no-fabrication/no-verse-bodies, +CLI both-files, +CLI rejects out-of-run path, +both-or-neither on bad evidence.
- Real card rendered & eyeballed (scratch): clean one-linear-read, opus overall 68.6%/85.7%, haiku 48.6%/76.9%, counterfactual table 0/17,3/15,0/0. Matches Waleed docs bar.
- README section 8 added. Suite 423 pass/1 skip. Commit author Jonathan.

## Phase_3 impl review (2026-10-23): codex + claude both REQUEST_CHANGES — all fixed (426 pass)
- Prose unified: removed _COUNTERFACTUAL_SCOPE constant; ALL reader-facing wording (scope template, labels, table headers, intros) now in CARD_PROSE. Renderer = structure+interpolation only.
- No typed figures: claims[0] rephrased to cover all 4 tasks; counterfactual intro+scope are TEMPLATES interpolated with bible count/versions from census; non_conclusions no longer says "three". Test asserts "three" absent.
- Human card: added per-text 17-row table (work/version, language, tradition, type, license); dropped confusing side-by-side table.
- Task glosses: new "The four tasks" section.
- Output safety: _within validates BOTH defaults+overrides (symlink escape), rejects run_dir itself, rejects json==md; atomic temp+os.replace both-or-neither.
- Drift guard: systematic test (every model×task×overall count/accuracy/coverage + counterfactual num/denom in card).
- Fix commit authored as me. Rebuttal committed.

## Phase_3 iter2+iter3: both REQUEST_CHANGES each round, all folded. iter3 force-advanced (max_iterations=3) with rebuttal as disposition → phase_3 ✓. All phase_3 fixes committed (atomic write_card w/ rollback, panel+correctness-rule on card, per-task correctness, evidence-alias rejection, lang names, 0/0 note).

## PORCH SEQUENCING SLIP (recovered): chained `porch next >/dev/null; porch done` after phase_3 accidentally consumed phase_4's BUILD task and ran porch done on empty phase_4 → porch jumped to phase_4 "Run 2-way consultation" at iter1 before build. RECOVERY: implemented+committed phase_4 BEFORE running the consult, so the consult reviews real committed work. Lesson: don't chain porch next/done across a phase boundary.

## PHASE 4 COMPLETE ✓ (generate+commit real card; audit .md; drift guard)
- audit.py: _AUDITED_SUFFIXES now (.json,.jsonl,.md). Origin layer still json/jsonl only (md has no source dict); .md gets CONTENT layer (restricted fingerprint scan). test_audit: test_md_card_is_content_scanned + committed-evidence filter includes .md.
- Generated runs/original-2026-10-21/facct.{json,md} via CLI. Evidence sha256 BYTE-UNCHANGED (verified before/after). audit OK (origin-only, restricted payloads absent — .md has no origin so trivially clean in CI; content layer proven by test).
- test_original_run_regression.py::test_committed_facct_card_matches_the_run — committed facct.json == fresh build_facct(RUN) (full dict). Catches a future rebaseline that moves scores/summary without regenerating the card.
- audit.py docstring + runs README updated. Suite 436 pass/1 skip; dispatcher green.
- Real card: 17 texts, 476 Q, counterfactual denom 32 / 3 other_edition. Reads clean against docs bar.

## Phase_4 iter1: BOTH APPROVE. Polish folded (card census origin audited; facct.md drift guard; panel provider note). All 4 phases ✓ → REVIEW phase.

## REVIEW phase (2026-10-24)
- Review doc written: codev/reviews/32-facct-benchmark-card-cross-edi.md (all 15 ACs met; consultation feedback per phase; deviations; lessons).
- Governance routed to COLD (HOT caps respected): arch.md gets "FAccT card + edition index" section + audit-.md note in Test gate; lessons-learned.md Process/SPIR gets the porch-chaining lesson + reuse-score-predicate lesson.
- Consult .txt + context.md files ARE committed (repo convention: spec 1 has them). .builder-* NOT tracked → leave untracked.
- PR: base main, "Part 3 of 3 of #30", "Closes #32", loop @JonathanKarr33 on provisional card wording. NO Generated-with/Co-Authored-By (architect + CLAUDE.md override the attribution reminder).

## Status
- review: committing review doc + governance + consult outputs, then push + create PR, porch done, signal PR_READY, notify architect. PR gate is HUMAN — stop & wait after.
- Phase_4: extend audit.py suffix set to scan .md + test_audit injection test; byte-digest integrity (sha256 3 evidence files before/after); GENERATE+COMMIT real card into runs/original-2026-10-21/facct.{json,md} + README line; real-run drift guard in test_original_run_regression.py. Author carry phases to Jonathan. THEN PR ("Part 3 of 3 of #30", closes #32, loop Jonathan on wording, NO Generated-with/Co-Authored-By). Commit untracked consult .txt files with PR.
- Phase3: facct.md, both files written atomically within run_dir by default, ONE prose block, every number from build data (anti-drift test == summary). Phase4: extend audit.py to .md + test, byte-digest integrity, generate+commit real card over runs/original-2026-10-21, real-run drift guard; author carry phases to Jonathan.
- NOTE: context-refresh at phase_1→2 boundary did NOT run (porch handed implement task directly, no self-refresh cmd). Context intact, ~14.7M tokens. Consult .txt files for all phases still untracked — commit with PR.
