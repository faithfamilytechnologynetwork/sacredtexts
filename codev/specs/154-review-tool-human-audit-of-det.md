# Specification: Review tool — human audit of deterministic correctness scoring

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
-->

Issue #154. Ported from the multibench reviewer (its Specs 83 and 92).

## Problem Statement

Every headline number SacredBench reports comes from a deterministic scorer
(Spec 15 graders plus the refusal outcome, and the folds added since: orthography #52,
Latin diacritics #94, Talmud #149, completion head #150, citation digits #111, citation
equivalence #112/#118, GGS Ang #135, Talmud daf+amud #147). Each rule was checked against
hand-picked examples and pinned by tests. Nobody has measured how often the scorer's
`outcome` matches what a competent human reader would say about the same answer.

The gap matters most for **false positives**: cells the scorer marks `correct` that a
human would not. Containment credit (`contains_reference`) is the obvious suspect, since
an answer that buries the reference inside a long reply still scores. The scorer can also
miss in the other direction: a refusal written in Arabic, or a citation in a notation the
equivalence tables don't know. Issue #41 already asks for an independent rater for the
paraphrase band, wrong citations and other-script rows. The author audit doesn't count as
that rater.

The people affected:

- **The project owner and paper authors.** They cite accuracy figures (FAccT 2026) and
  have no measured error bar for the scorer itself.
- **Domain reviewers** (readers of Arabic, Hebrew/Aramaic, Gurmukhi, Sanskrit, Pali,
  Koine Greek, English). They need a way to look at cells and record a judgement without
  spreadsheets or repo access.
- **Future scoring work.** Every scoring-contract change is currently defended with
  hand-picked movers. A set of human labels made without seeing the scorer's verdict could
  be replayed against any later scorer.

## Current State

- **Run evidence.** The committed FAccT run `runs/facct-2026-11-03/` has **32,478 scored
  cells** across **304 `scores.jsonl` files**: 16 models × 8 tradition folders (Christianity,
  Judaism, Islam, Hinduism, Sikhism, Buddhism, Book of Mormon, encyclicals), × edition and
  prompt condition. A cell is identified by `(run, model_id, question_id)`, which is unique
  within the run (checked: 0 duplicates). Per data, not docs: this run has **no
  `questions.jsonl`**. Each `answers.jsonl` row carries the full question (prompt, expected,
  `source` with tradition/work/version/language/citation/condition), and each `scores.jsonl`
  row carries `task` and `metrics` (`outcome` plus task-specific submetrics).
- **Outcomes in that run:**

  | task | correct | incorrect | refused |
  |---|---:|---:|---:|
  | retrieve_quote | 2,427 | 3,738 | 1,834 |
  | complete_unit | 3,088 | 4,492 | 579 |
  | cite_passage | 4,812 | 3,195 | 153 |
  | verify_source | 6,838 | 968 | 354 |

  For correct text-retrieval cells, the recorded submetrics show which grader gave the
  credit: retrieve_quote 449 exact / 1,241 normalized / **737 containment-only**;
  complete_unit 1,035 / 1,383 / **670**. Among correct cite cells, 5 have
  `n_candidates = 0` and 102 have `segment_match = 0`. These are the paths most likely to
  hide false positives.
- **Languages** (edition `source.language`): en 11,520 · he 6,399 · sa 3,840 · ar 3,839 ·
  pa 3,680 · pi 1,920 · grc 1,152 · arc 128.
- **Copyright.** `pipelines/sacredbench/audit.py` (part of the test gate) fails any
  committed artifact derived from a `restricted` catalogue target. The one exception is the
  **NRSV quotation allowance**: a file may quote up to 500 distinct NRSV verses. The FAccT
  run has **1,920 NRSV cells covering only 31 distinct verses**. NABRE and the Greek
  Orthodox extracts have no allowance and are absent from committed runs.
- **Viewer.** `apps/viewer` is a backend-free SPA over local `runs/`. Its error explorer
  (`/run/$runId/model/$modelId`) already renders a cell's prompt, expected text, answer and
  submetrics side by side (`QuestionList`), and `failureKind.ts` labels how a cell failed
  (`paraphrase`, `near_copy`, `addition`, `wrong_locus`, `hedge`, …). The public deployment is
  a static Cloudflare Pages build with the run data baked in. `apps/viewer/server/` is a
  minimal Hono static host whose old `/api` reverse proxy was removed in the Spec 2 purge.
- **No review capability.** The `/review*` flows the viewer was seeded with were purged
  (Spec 2). There's no `apps/api`, no accounts, and no store for human judgements.
- **multibench has a working reviewer.** It has a Hono + Drizzle + Postgres API (PGlite
  tests); email + password accounts (argon2id) behind a shared invite code; server-side
  sessions; httpOnly cookies; double-submit CSRF; account delete; drafts with optimistic
  concurrency (409 + reconcile); insert-only immutable submissions; a client store with
  seeded `mulberry32(fnv1a(seed))` sampling, with seed and ids persisted; and a same-origin
  edge proxy to a private API on Railway, with daily Postgres backups. Its history records
  fixes this port must carry: cross-reviewer state leak on account switch, the failed-load
  overwrite hole, CSRF-403 refresh, the prefetch clobber race, an exact MIME check on
  JSON-only auth routes, a password length cap, and race-safe signup.

## Desired State

A reviewer is invited, creates an account, and declares the languages they read. They
then work through a queue of scored cells drawn at random from a committed run:

1. **Judge blind.** For each cell they see the task, the edition and citation, the prompt,
   the expected text and the model's answer, with each text rendered legibly in its own
   script and direction. They don't see the scorer's verdict, its submetrics, the failure
   kind or the model's identity. Using a short per-task rubric, they record their own
   outcome: `correct` / `incorrect` / `refused` / `can't judge`. They can add a
   question-defect flag (the expected text or prompt is wrong) and notes.
2. **Reveal.** Once the blind verdict is committed, the scorer's outcome, submetrics,
   grader path, failure kind and model are shown, along with whether the two agree. The
   blind verdict can no longer change. The reviewer can add post-reveal notes, and can
   record a revised verdict (e.g. "I misread the Hebrew"). That revision is kept alongside
   the blind verdict and never replaces it.
3. **Resume anywhere.** The queue, positions and unfinished notes persist on the server.
   The same account on another device sees the same cells in the same order. A sample
   never shifts under a reviewer.

Behind this:

- **The sampling frame is committed and citable.** A seeded, stratified **review set** is
  drawn from a named run by a CLI and committed: the seed, the source run and digests of
  its score files, stratum population sizes and inclusion probabilities, an overlap subset,
  and the cells' content. It passes the copyright audit like any committed evidence. The
  hosted service serves only cells from an ingested review set.
- **Assignment** hands each reviewer cells from the set in its seeded order, limited to
  the languages they read. The shared **overlap** cells go to every reviewer who reads
  that language, so inter-rater agreement can be measured. Every assignment is persisted
  with its time and position.
- **Results** are exported by an operator into a committed JSONL. Reviewers appear under
  pseudonyms (never email or name). An **agreement report**, built from that export alone,
  gives human-vs-scorer agreement, scorer precision (the false-positive rate) and the
  false-negative rate, broken down by task, tradition, outcome stratum and grader path,
  with confidence intervals. It also gives population-weighted estimates and inter-rater
  agreement on the overlap. The paper can cite these numbers.
- Committed run evidence is never modified. Accounts, sessions, assignments and judgements
  live in the review store. Their published form is the export.

## Success Criteria

- [ ] **Review-set builder.** A CLI reads a named run directory (read-only) and writes a
      review set. Same run + seed + allocation ⇒ byte-identical output; a different seed ⇒
      a different draw. The set records the seed, the allocation, the source run id, the
      sha256 of every score/answer file it read, each stratum's population size and
      inclusion probability, and which cells are in the overlap subset. Only scored cells
      (those with an `outcome`) are eligible. Missing cells aren't.
- [ ] **Stratified, suspect-weighted draw.** Strata are outcome × task × tradition. Within
      `correct` text-retrieval cells, the grader path (exact / normalized /
      containment-only) is also a stratum, and the suspect cite paths are covered.
      Allocation is weighted towards `correct` (false positives first), with smaller
      `incorrect` and `refused` strata so false negatives are also measured. The allocation
      is a parameter recorded in the set, not hard-coded.
- [ ] **Copyright.** No cell from a restricted-origin edition is in the set, under the rule
      settled in Open Question 2. The committed set passes `audit.py` in the test gate. The
      hosted store contains only cells ingested from a review set file produced by the CLI,
      and ingest rejects anything else (schema and digest check).
- [ ] **FAccT review set committed.** A review set drawn from `runs/facct-2026-11-03` is
      committed outside existing run evidence. `git diff` shows no change to any existing
      file under `runs/`.
- [ ] **Accounts ported unchanged.** Signup (invite-gated, fail-closed when the code is
      unset), login, logout, `me`, CSRF token fetch and account delete behave as in
      multibench, and its auth/CSRF/CORS/session tests are ported and pass. Account delete
      cascades to the reviewer's sessions, assignments, drafts and submissions.
- [ ] **Declared languages.** A reviewer can set the languages they read (chosen from the
      languages present in the active set). Assignment never hands them a cell outside
      those languages. A reviewer with no matching cells sees an explicit empty state.
- [ ] **Stable assignment.** A reviewer's assigned cells and their order survive reload,
      logout/login and a second device. Asking for more cells appends a batch and never
      reorders or replaces earlier ones. Each assignment records the set id, its position
      and the time.
- [ ] **Overlap.** Every overlap cell in a reviewer's languages is assigned to that
      reviewer, interleaved into their queue.
- [ ] **Blinding is enforced by the server.** For a given reviewer and cell, the API
      returns no scorer outcome, submetric, grader path, failure kind or model identity
      until that reviewer's blind verdict for the cell is committed. Once committed, the
      blind verdict is immutable: any attempt to change it is rejected. Post-reveal notes
      and a revised verdict are stored without touching the blind verdict.
- [ ] **Draft persistence and its fixes.** Unfinished judgements (selected verdict,
      notes) persist with optimistic concurrency, so a stale write gets 409 plus the
      current state and the client reconciles. Each multibench fix has a regression test:
      no cross-reviewer state leak on account switch or 401, a failed load never
      overwrites a saved draft, a CSRF 403 refreshes the token and retries, and a slow
      list load never clobbers a newer per-item load. Body sizes are capped.
- [ ] **Review UI in the viewer.** New viewer routes provide the sign-in/sign-up gate,
      profile (name, background, languages), queue with progress (judged / assigned,
      overlap shown), and a judging page. The judging page reuses the explorer's cell
      rendering, shows the per-task rubric, and renders Arabic, Hebrew/Aramaic and other
      scripts with correct direction (RTL) and a script-capable font. Existing viewer
      routes and tests are unaffected. The static (Cloudflare Pages) build still builds;
      there, the review routes show "review service unavailable" rather than crashing.
- [ ] **Rubric is versioned.** The per-task rubric shown to reviewers carries a version,
      and each judgement records the rubric version it was made under.
- [ ] **Export.** An operator command exports all judgements, without the database or API
      being publicly reachable and without a reviewer account, to JSONL with a stable sort
      (same store ⇒ byte-identical file). Each row has: set id and seed, cell id, reviewer
      pseudonym (stable, not reversible to email), the reviewer's declared languages,
      assignment time and position, overlap flag, rubric version, blind verdict and its
      time, the scorer's outcome, submetrics and grader path as served, any revised verdict,
      flags and notes. No emails, names or password-derived data appear in it.
- [ ] **Agreement report.** A CLI reads only an export (plus the review set it references)
      and reports, per task / tradition / outcome stratum / grader path and overall:
      n, human-vs-scorer agreement, scorer precision on `correct` (false-positive rate), the
      false-negative rate on `incorrect`, refusal agreement, and the `can't judge` rate,
      each with a Wilson 95% interval. It also reports population-weighted estimates using
      the recorded inclusion probabilities, and inter-rater agreement on the overlap
      (pairwise percent agreement and a chance-corrected coefficient). Headline agreement
      uses the blind verdict; the revision rate is reported separately. The report is
      deterministic and its numbers are pinned by a test over a synthetic export with
      hand-computed answers.
- [ ] **Test gate.** `apps/api` is registered in `.codev/checks/test.sh`, and its suite
      runs on PGlite with no external database. The Python review-set and report code runs
      in the pipelines lane.
- [ ] **Schema discipline.** Every schema change is a `drizzle-kit generate` migration
      whose SQL is committed and reviewed in the PR. `db:push` is never used.
- [ ] **Deployable, not deployed without consent.** The PR ships the deploy configuration
      and a runbook for the proposed topology. Provisioning happens only after an explicit
      human go-ahead with a cost envelope. If that's given, the post-deploy gate is: login,
      blind judge, reveal and resume across two browsers (real Safari and Chrome) through
      the one public origin; the API has no public domain; and the backup schedule is
      confirmed.

## Constraints

From the issue (no Baked Decisions section is present; these are its stated constraints):

- **Reuse the multibench review tool — do not rebuild.** Port the API (Hono + Drizzle +
  Postgres, PGlite tests) wholesale. Port accounts unchanged. Port draft persistence with
  optimistic concurrency and immutable submissions, re-keyed to the review unit. Port and
  adapt the client store, API client, auth gate, check control and progress, plus the
  seeded, recorded sampling approach. Keep the topology: one public origin, private API
  behind a same-origin edge proxy. Port the **fixes** from multibench's history, not only
  the first draft.
- **Copyright gate.** The repo is public and the tool is hosted. No cell derived from a
  `restricted` source may be served, and `audit.py` stays green.
- **Committed run evidence is read-only.** The tool never rewrites `runs/`. Review data
  lives in the review store and its export.
- **Schema changes** go `drizzle-kit generate` → review the SQL → apply. Never `db:push`.
- **Test gate.** Register `apps/api` in `.codev/checks/test.sh` alongside pipelines and the
  viewer.
- **Hosting costs money** and needs an explicit go-ahead before provisioning.
- Related: #41. This tool is the vehicle for that adjudication.

From the repo:

- `pipelines/` is the single uv project. Python CLIs run via
  `uv --project pipelines run python -m …`, and the review-set and report logic belongs
  there, beside the scorer and the audit.
- The viewer uses HeroUI v3 (provider-less), TanStack Router and Vite, and has a test
  rule against invisible text.
- **Privacy.** The repo is public. Reviewer emails, names and backgrounds stay in the
  private store, and only pseudonyms and declared languages are exported. Notes are
  exported verbatim, so signup must tell reviewers that.
- Keys and secrets (database URL, invite code) come from the environment only, never the
  SPA.

## Assumptions

- **Test-tool scale.** A handful to low tens of invited, cooperative reviewers. No
  rate-limit or email-enumeration hardening and no email transport, same as multibench.
- **Cooperative blinding.** The public viewer and the committed review set both expose
  scores, so a determined reviewer could look a verdict up. Server-side blinding protects
  the integrity of the record (the verdict really was committed before the reveal), not
  secrecy against a reviewer working against it. The report states this.
- The FAccT run `runs/facct-2026-11-03` is the first population. The builder takes any
  run directory with the same layout.
- The committed scores reflect the current scoring contract. A later rebaseline doesn't
  invalidate judgements, because the export records the scorer verdict *as served* and the
  blind label doesn't depend on any scorer.
- The multibench Railway account and workflow are available if hosting is approved.
- multibench's `apps/api` and review client at its current `main` are the port source.

## Solution Approaches

### Approach 1: Literal port — client-side sampling over opaque drafts

Keep the multibench API exactly as is. Re-key its `tradition_id` to a review-set id, and
store one opaque JSONB draft per reviewer holding `{seed, sampleIds, judgements}`. The SPA
draws each reviewer's seeded sample client-side from a baked pool index, and fetches cell
content from the viewer's static baked runs.

- **Pros:** maximum reuse, with almost no API change.
- **Cons:**
  - Cell content would come from the baked `answers.jsonl`, about 50 MB and sharded, or a
    new baked per-cell pool.
  - The scorer verdict ships to the client with the cell, so blinding is cosmetic and the
    blind-before-reveal order can't be verified.
  - Per-reviewer independent draws can't guarantee the shared overlap or avoid duplicate
    effort across reviewers.
  - Every save PUTs the whole growing draft.
  - Per-cell immutability can't be enforced.
  - The served surface is the whole run, so the copyright surface is too.
- **Risk:** low to build, but **the measurement is weak**: "the human didn't see the
  verdict first" becomes unverifiable.

### Approach 2: Committed review set + server-side assignment and per-cell judgements (recommended)

A Python CLI in `pipelines` draws a seeded, stratified, suspect-weighted review set from a
named run and commits it. It's audited like any evidence. The API ports multibench's
service, auth, sessions, CSRF, account delete, migrations, health and PGlite rig
wholesale, and adds the re-keyed review slice:

- read-only ingest of a review set, idempotent and digest-pinned;
- language-filtered, claim-based assignment from the set's seeded order, with the overlap
  interleaved;
- a cell endpoint that withholds scorer data until the blind verdict is committed;
- per-cell drafts with optimistic concurrency and insert-only submissions (the blind
  verdict, then an optional post-reveal revision).

The viewer gains review routes. They reuse the explorer's cell rendering and the ported
client store and API client (with the fixes), the auth gate, check control and progress.
An operator export, run inside the service, writes a pseudonymous JSONL. A Python report
turns it into the agreement tables.

- **Pros:**
  - The sampling frame is a committed, citable, reproducible artifact.
  - Blinding and blind-verdict immutability are server-attested.
  - Overlap and coverage are controlled.
  - The served surface is only the audited set, so the NRSV allowance is checked on that
    one file by the existing audit.
  - Sampling and statistics live next to the scorer, which knows the grader paths and
    the copyright catalogue.
  - The API stays thin.
  - The JSONL seams match the rest of the pipeline.
- **Cons:**
  - More new API surface than a literal port: ingest, assignment and per-cell judgement
    routes.
  - Two languages at the seams (Python builds and reports, TypeScript serves).
  - The review set duplicates a few MB of run content in git.
- **Risk:** moderate. Mitigated by porting the multibench auth and test rig verbatim and
  keeping the new review routes small, with their own PGlite tests.

**Variant 2b (full-pool ingest).** Ingest all 32k eligible cells and stratify on the
server. That allows re-weighting without a new set, but moves the citable sampling frame
out of git, makes the served surface the whole run, and puts statistics in TypeScript.
Not recommended.

**Assignment sub-choice.** Claim-based assignment (each non-overlap cell goes to the next
eligible reviewer in seeded order) maximises coverage with few reviewers. Its order
depends on when reviewers arrive, but every assignment is persisted. The alternative is
per-reviewer seeded permutations, multibench-style: `seed + reviewer id`, reproducible
from the seed alone, at the cost of duplicate effort. Recommended: claim-based, because
coverage is scarce. See Open Question 6.

### Approach 3: Offline sheet

Export a stratified sample to CSV or Google Sheets for reviewers to fill in.

- **Pros:** no hosting cost, no new code.
- **Cons:** no accounts, no blinding (the verdict sits in a neighbouring column or must be
  hand-hidden), poor RTL and script rendering, manual and error-prone merging, and no
  stable per-reviewer assignment. It also contradicts the issue's "reuse the multibench
  tool".
- **Risk:** low effort, but low-integrity data. Rejected. It's the fallback only if hosting
  is declined outright, and even then Approach 2 can run locally against a local Postgres.

**Recommendation: Approach 2.** It is the only option where the number the paper cites
(agreement between a blind human and the scorer) rests on an auditable record: a committed
frame, a server-attested blind-before-reveal order and a deterministic report. It keeps
every multibench piece the issue names, re-keyed only where the review unit forces it.

## Open Questions

### Critical (blocks progress)

1. **The human rubric: what "correct" means per task.** It sets what the agreement rate
   measures. Draft, for the architect to settle (tolerances mirror the benchmark's
   intended construct, not the scorer's mechanics):
   - *retrieve_quote*: **correct** if the answer delivers the requested passage in the
     named edition's wording. Vowel marks/diacritics, punctuation, spacing, verse numbers
     and orthographic convention (e.g. Uthmani vs Imla'i) don't matter, and a little
     surrounding text is fine if the whole passage is clearly given as the answer.
     **Incorrect** if it's a different passage, a translation or paraphrase, has missing or
     changed words, or is lost in a long reply that doesn't clearly offer it. **Refused** if
     it declines or says it can't provide the text, in any language, even when it offers a
     summary or translation instead.
   - *complete_unit*: **correct** if what the answer gives as the continuation matches the
     expected continuation, under the same tolerances (it may stop early or run on). This is
     the question #150 settled for the scorer, and the architect should confirm it for
     humans.
   - *cite_passage*: **correct** if it names the expected location at the precision asked
     (chapter:verse; Talmud daf+amud; GGS Ang). Any numerals or notation are fine (Arabic
     digits, Hebrew letter numerals, surah name). Two or more different locations offered
     as alternatives make it **incorrect**.
   - *verify_source*: **correct** if its committed yes/no matches the expected answer.
     **Refused** if it never commits to one.
2. **NRSV under the quotation allowance.** Read literally, "no cell derived from a
   restricted source may be served" excludes NRSV. The audit, though, permits NRSV within
   500 distinct verses per file, and the FAccT run's 1,920 NRSV cells cover only 31 verses.
   Excluding them removes the whole English-Christianity stratum. **Default in this spec:
   exclude every restricted-origin cell, NRSV included** (the literal constraint). Option:
   include NRSV and let `audit.py` enforce the allowance on the committed set.

### Important (shapes design)

3. **Hosting go-ahead and envelope.** The proposal is Railway, mirroring multibench: the
   viewer edge (the one public origin, proxying `/api`), a private API and Postgres with a
   daily backup. That's recurring spend. The public browsing viewer stays on Cloudflare
   Pages unchanged. Open: should the Railway edge serve review only, or a full baked
   viewer too? Building can proceed without the go-ahead; provisioning cannot.
4. **Allocation and set size.** Proposed default:
   - roughly 60% `correct` / 25% `incorrect` / 15% `refused`;
   - within `correct`, containment-only and the suspect cite paths are oversampled and
     exact matches get a small sanity allocation;
   - every non-empty task × tradition stratum gets a minimum;
   - total about 2,000 cells.

   All of it is a recorded parameter. Is the false-positive weighting right, and is a
   frame of that size enough for the reviewers we expect?
5. **Overlap size.** Proposed: about 10% of the set, spread across strata and interleaved
   (roughly one in ten queue positions). That's enough for inter-rater agreement per
   language where two or more reviewers read it.
6. **Assignment mode.** Claim-based (recommended, for coverage) or per-reviewer seeded
   permutation (reproducible from the seed alone)?
7. **Post-reveal revision.** Proposed: allowed, append-only, reported as a revision rate.
   Headline agreement always uses the blind verdict.
8. **Model identity hidden while judging.** Proposed: yes, to avoid brand bias, and shown
   at reveal.
9. **Export mechanism.** Proposed: an operator command run inside the API service, which
   adds no network surface. The alternative is an admin-token export endpoint behind the
   edge, which is reachable from the internet even if gated.
10. **Language options.** Proposed: Hebrew and Aramaic grouped as one "Hebrew script"
    choice, and Pali offered as its own language even though its edition is romanized.
    Should English be offered? (Proposed yes. It's the largest stratum and the easiest to
    staff.)

### Nice-to-know (optimization)

11. Finer grader-path attribution (which fold fired: orthography, Talmud, completion head,
    citation equivalence) by re-running the scorer inside the set builder, rather than
    reading only the recorded submetrics.
12. Replaying the human labels against a newer scorer, as a gold set for future scoring
    changes.
13. Deferred multibench clean-ups: `SameSite=None` → `Lax` once same-origin, and pruning
    expired sessions.
14. Batch size per "more cells" request (proposed 25).

## Test Scenarios

**Review set**

- Same run + seed + allocation produces byte-identical output twice. A changed seed
  changes the draw.
- Recorded stratum sizes equal a direct count over the run.
- Inclusion probabilities equal the allocation divided by population size.
- A run with a restricted-origin cell excludes it (fixture), and the committed set passes
  `audit.py`.
- Missing (unscored) cells are never eligible.
- A tiny stratum smaller than its minimum takes all its cells and records probability 1.
- No file under `runs/` changes (asserted by the test).

**Ingest**

- Ingesting the same set twice is a no-op.
- A tampered file (digest mismatch) or a non-set file is rejected.
- A second, different set gets a new set id and leaves the first set's cells and
  judgements untouched.

**Auth (ported)**

- Signup without an invite code, or with a wrong one, is rejected, and so is signup when
  the code is unset.
- A duplicate email is rejected (race-safe).
- A password over the cap is rejected.
- A non-JSON content type on login or signup is rejected (exact MIME essence).
- A state-changing request without CSRF gets 403. After a CSRF refresh the client retries
  and succeeds.
- Logout revokes the session. An expired session is rejected.
- Account delete cascades to everything the reviewer owns.

**Isolation**

- Reviewer A can't read or write B's assignments, drafts or submissions.
- Switching accounts in one browser leaves no residue of A's state in B's session, and
  neither does a 401.

**Assignment**

- An English-only reviewer only ever gets `en` cells.
- A reviewer whose languages match nothing sees the empty state.
- Reload, re-login and a second device show the same queue.
- Asking for more appends cells and never reorders.
- Overlap cells reach every eligible reviewer, and non-overlap cells reach one reviewer
  under claim-based assignment.
- An exhausted set gives a clear "no more cells".

**Blinding**

- Fetching a cell before its blind verdict returns no outcome, submetrics, path, kind or
  model. The same request after the blind verdict returns them.
- Changing the blind verdict after reveal is rejected.
- A post-reveal revision is stored, and the blind verdict is unchanged in the store and
  the export.

**Drafts**

- Two devices edit notes on one cell, and the stale save gets 409 plus the current state;
  the client reconciles without silent loss.
- A failed load followed by an edit doesn't overwrite the saved server draft.
- A slow list load doesn't clobber a newer per-item load.
- An oversize body gets 413.

**UI**

- The judging page shows the rubric for the cell's task.
- Arabic, Hebrew and Gurmukhi text render with the right direction (`dir`) and no
  invisible text.
- Nothing scorer-derived is in the DOM before the reveal.
- Progress counts are right with overlap.
- The static build shows "review service unavailable" with no API.

**Export and report**

- Exporting twice gives an identical file.
- The export has no email or name (asserted).
- Pseudonyms are stable across exports.
- On a synthetic export with hand-computed answers, the report's agreement, precision,
  false-negative rate, Wilson intervals, weighted estimates and inter-rater coefficient
  match exactly.
- `can't judge` cells are excluded from agreement and counted in their own rate.
- An export referencing an unknown set fails loudly.

**Non-functional**

- The `apps/api` suite runs offline on PGlite through `.codev/checks/test.sh`.
- Existing viewer and pipelines suites still pass.
- `audit.py` stays green.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Too few reviewers or judgements, so intervals are too wide to cite | High | High | Suspect-weighted strata put effort where false positives live. Wilson intervals are reported, never bare rates. Coverage is reported per stratum. Small batches lower the barrier. |
| Language gaps (no Pali or Gurmukhi reader) | High | Medium | Report per-stratum coverage explicitly. Estimates are conditional on reviewed strata, and unreviewed strata are listed, never extrapolated. |
| Rubric ambiguity drives low inter-rater agreement | Medium | High | Rubric settled at the spec gate. It's versioned, and every judgement records its version. Overlap measures agreement. `can't judge` and the defect flag avoid forced guesses. |
| Copyright exposure on a hosted public-repo tool | Low | High | The served surface is only the committed, audited set. Restricted origins are excluded per OQ2. Ingest accepts only CLI-produced sets. |
| Reviewer privacy in a public repo | Medium | High | Pseudonyms only, no email/name/background in the export (asserted by a test). Signup consent text says notes are published. |
| Blinding defeated by looking at the public viewer | Low | Medium | Cooperative-reviewer assumption, stated in the report. The server still attests blind-before-reveal order. |
| A scoring rebaseline makes recorded verdicts stale | Medium | Low | The export records the verdict as served plus score-file digests, and blind labels are scorer-independent. Replay is a follow-up (OQ12). |
| The port drifts from multibench or misses its fixes | Medium | Medium | Port from multibench `main` with its tests, and write a regression test per named fix. |
| Hosting spend or overrun | Medium | Medium | No provisioning without explicit go-ahead and an envelope. Same thin topology as multibench. |
| Loss of authoritative judgement data | Low | High | Daily Postgres backup schedule (as multibench), plus periodic committed exports. |
| Schema change applied unsafely | Low | High | Generate → review SQL → apply via the deploy-time migrator. Never `db:push`. |

## References

- Issue #154 (this), #41 (independent rater for the paraphrase band, wrong citations,
  other-script rows).
- multibench: `apps/api/README.md`; `apps/api/src/{auth,middleware,routes,schema}`;
  `apps/multibrowser/src/lib/{review.ts,reviewApi.ts}`;
  `apps/multibrowser/src/components/{ReviewAuthGate,ReviewCheckControl,ReviewProgress}.tsx`;
  `apps/multibrowser/server/index.mjs`; Specs 83 and 92; history in
  `git log -- apps/api apps/multibrowser/src/lib/review.ts` (Spec 92 fix commits a538310d,
  51aab523, 6bf07dfb, e39fe420, ca104e4b, b268d4ff, 02b59637).
- SacredBench: Spec 15 (graders + outcome), Spec 26 (original-language question set),
  Spec 48 (assertion-gated refusal), Spec 52 / #94 / #149 / #150 / #111 / #112 / #118 /
  #135 / #147 (folds and citation rules), Spec 2 (viewer purge),
  `pipelines/sacredbench/audit.py`, `apps/viewer/README.md`,
  `apps/viewer/src/lib/failureKind.ts`, `runs/README.md`.
