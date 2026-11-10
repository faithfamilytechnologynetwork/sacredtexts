# spir-154 thread — review tool (human audit of deterministic scoring)

## 2026-11-09 — specify

- No spec existed; drafted `codev/specs/154-review-tool-human-audit-of-det.md` from the issue's
  proposed defaults (to be settled at the spec gate) rather than asking clarifying questions.
- Data facts (from the real run, not docs): `runs/facct-2026-11-03` = 32,478 scored cells / 304
  score files; NO `questions.jsonl` (question embedded in each answers row); cell id
  `(run, model_id, question_id)` unique. Containment-only correct: retrieve 737, complete 670.
- Copyright wrinkle: NRSV is `restricted` but audit.py allows ≤500 distinct verses/file; the FAccT
  run's 1,920 NRSV cells cover only 31 verses. Spec defaults to the issue's literal "no restricted
  cell served" (exclude NRSV) and raises inclusion as OQ2.
- Recommended approach: committed, audited, seeded stratified **review set** (Python, pipelines)
  → API (multibench port + re-keyed review slice: ingest, claim-based language-filtered assignment
  with overlap, server-enforced blind-before-reveal, per-cell drafts + immutable submissions)
  → viewer review routes → pseudonymous committed export → Python agreement report.
- Critical OQs for the gate: the human rubric per task (draft in spec), NRSV inclusion.

## 2026-11-09 — spec consult iter 1 (codex + claude: both REQUEST_CHANGES), folded

- claude verified every factual claim exact against the run + port source.
- Folded: rubric now aligned to Spec 48 class A/B + #23 leading stance + #150 head + containment,
  with a post-reveal rubric-problem flag for contract disagreement (claude's main point);
  explicit Defaults D1–D10 (codex: settle defaults); deterministic allocation/overlap/order rules
  (sha256(seed‖cell id)); edition language added to strata (language gaps would otherwise bias
  post-stratified estimates); proper estimands (precision/FDR, missed-credit, weighted recall,
  post-stratified weights, Wilson + stratified bootstrap, Krippendorff α, uncovered mass);
  trust anchor for ingest = digest pinned in repo + recomputed; review set + exports must be wired
  into test_audit.py's scan and the dispatcher (test_audit only scans runs/ — fixtures-gap class);
  keyed (HMAC) pseudonyms + languages snapshot; account delete stays cascading (port unchanged),
  figures tied to a committed export; claim-race criterion; #41 worklist in report; local e2e scope.

## 2026-11-10 — owner rulings at spec gate (relayed by architect), spec rewritten

- Owner reframed: internal verification tool + gold set for testing matcher VERSIONS, not a
  publication instrument. Rulings: not blind; even stratified sample (outcome × task × text, k per
  stratum, default 10 ⇒ ~1,400 cells / 151 strata); reviewers pick TEXTS not languages; core
  version-comparison CLI (committed / current re-score / scores file, with movers); include NRSV, no
  copyright machinery; one reviewer base case (no overlap/claims/IRR/pseudonyms); plain counts, no
  stats; one Hono service serving /api + built UI + Postgres, no edge.
- Rewritten spec picks the max-reuse design: multibench draft re-keyed tradition→sample (one draft
  per reviewer per sample holds chosen texts + labels); gold set downloaded client-side; no cell
  tables, no server export. Not approved yet — waiting for architect to relay approval.

## 2026-11-10 — spec approved; plan drafted

- Architect relayed human approval of spec 1ee8cc12 (k=10 default stays a CLI param; hosting NOT
  approved — local only). Ran `porch approve 154 spec-approval --a-human-explicitly-approved-this`
  as instructed by the architect.
- Plan: 6 phases — (1) review-sample builder + committed FAccT sample under review/samples/,
  dispatcher maps review/ → pipelines; (2) gold-set format + review-compare CLI (committed / current
  / scores file, movers fixed/broken) with shared fixtures/ contract; (3) apps/api port re-keyed
  tradition→sample, registered in test.sh; (4) one service: /api/sample + built viewer serving +
  railway.json (not applied); (5) viewer review store/API client port + sample/rubric/gold-set libs;
  (6) /review pages + local e2e in Chrome against local Postgres (homebrew pg17 available).
- Text = edition folder between <model>/base/ and population/ (13 in FAccT; groups encyclicals and
  Masoretic he+arc with no special cases).

## 2026-11-10 — plan consult iter 1 (codex + claude both REQUEST_CHANGES), folded

- Accepted: labels carry their own rubric_version + labelled_at (stamped only on a real edit) so
  downloads are clock-free and byte-identical; body cap 8 MB in bytes (sized for 1,000-char 4-byte
  notes) + client byte guard; 413 / non-retryable 4xx is terminal (multibench retried forever);
  script-text font stack + Gurmukhi test; run-aware dir versions in review-compare; static host
  ported from the in-repo apps/viewer/server/index.mjs (not multibench's edge), viewer
  railway.json left untouched; Phase 6 split → new Phase 7 (local e2e + docs); env table.
- Rebutted claude's "audit the committed sample" — owner ruling 5 explicitly removed copyright
  audit-scan extensions (counsel: fair use). Documented in review/README + arch docs instead.

## 2026-11-10 — plan approved; phase 1 done

- Architect relayed human plan approval (56375ec4); audit-scan rebuttal stands; hosting NOT approved.
  Ran `porch approve 154 plan-approval --a-human-explicitly-approved-this` per the relay.
- Phase 1 (a70314ce + nits feb19864): `sacredbench review-sample` → review/samples/facct-2026-11-03-k10.json
  (seed `spec-154`, k=10: 1,423 cells / 151 strata / 13 texts, 2.8 MB; NRSV 111 cells / 29 verses).
  Pin test regenerates it byte-for-byte; review/ → pipelines lane in test.sh. Full pipelines suite
  green (1520 passed). Consult: codex + claude APPROVE; took claude's nits (load_sample shape checks,
  refuse --out under runs/, texts[].cells → texts[].drawn, error-path tests).
- Note for later phases: test.sh diffs COMMITTED changes vs origin/main — commit a phase before
  `porch done` or the gate tests nothing.
