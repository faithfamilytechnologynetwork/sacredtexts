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
