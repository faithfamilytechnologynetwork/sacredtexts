# Specification: Review tool — human audit of deterministic correctness scoring

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
-->

Issue #154. Ported from the multibench reviewer (its Specs 83 and 92).

## Problem Statement

Every headline number SacredBench reports comes from a deterministic scorer:
Spec 15 graders plus the refusal outcome, and the folds and citation rules added since
(orthography #52, Latin diacritics #94, Talmud #149, completion head #150, citation digits
#111, citation equivalence #112/#118, GGS Ang #135, Talmud daf+amud #147, assertion-gated
refusal Spec 48, leading-stance verify #23). Each rule was checked against hand-picked
examples and pinned by tests. Nobody has measured how often the scorer's `outcome`
matches what a competent human reader would say about the same answer.

The gap matters most for **false positives**: cells the scorer marks `correct` that a
human would not. Containment credit (`contains_reference`) is the obvious suspect, since
an answer that carries the reference inside a long reply still scores. The scorer can
also miss in the other direction: a refusal written in Arabic, or a citation in a notation
the equivalence tables don't know. Issue #41 already asks for an independent rater for the
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
  hide false positives. `pipelines/sacredbench/failure_kind.py`, which has parity with the
  viewer's `failureKind.ts`, labels a containment-only correct cell `addition` when the
  answer runs at least eight tokens past the reference, and labels incorrect cells
  (`paraphrase`, `other_script`, `near_copy` family, `omission`, `wrong_passage`, `hedge`,
  `wrong_locus`, `no_citation`, `wrong_verdict`).
- **Languages** (edition `source.language`): en 11,520 · he 6,399 · sa 3,840 · ar 3,839 ·
  pa 3,680 · pi 1,920 · grc 1,152 · arc 128.
- **Copyright.** `pipelines/sacredbench/audit.py` fails any committed artifact derived from
  a `restricted` catalogue target. The one exception is the **NRSV quotation allowance**:
  a file may quote up to 500 distinct NRSV verses. The FAccT run has **1,920 NRSV cells
  covering only 31 distinct verses**. They make up the whole English-Christianity
  population. NABRE and the Greek Orthodox extracts have no allowance and are absent from
  committed runs. In the test gate, `test_audit.py` audits only `git ls-files runs/`, and
  `.codev/checks/test.sh` maps a change to a lane only by its top-level directory. So a
  committed artifact in a new top-level directory would be audited by nothing and would
  trigger no tests.
- **Viewer.** `apps/viewer` is a backend-free SPA over local `runs/`. Its error explorer
  (`/run/$runId/model/$modelId`) already renders a cell's prompt, expected text, answer and
  submetrics side by side (`QuestionList`). The public deployment is a static Cloudflare
  Pages build with the run data baked in. `apps/viewer/server/` is a minimal Hono static
  host whose old `/api` reverse proxy was removed in the Spec 2 purge.
- **No review capability.** The `/review*` flows the viewer was seeded with were purged
  (Spec 2). There's no `apps/api`, no accounts, and no store for human judgements.
- **multibench has a working reviewer.** It has a Hono + Drizzle + Postgres API (PGlite
  tests); email + password accounts (argon2id) behind a shared invite code; server-side
  sessions; httpOnly cookies; double-submit CSRF; account delete (cascading); drafts with
  optimistic concurrency (409 + reconcile); insert-only immutable submissions; a client
  store with seeded sampling, with seed and ids persisted; and a same-origin edge proxy to
  a private API on Railway, with daily Postgres backups. Its history records fixes this
  port must carry: cross-reviewer state leak on account switch, the failed-load overwrite
  hole, CSRF-403 refresh, the prefetch clobber race, an exact MIME check on JSON-only auth
  routes, a password length cap, and race-safe signup.

## Desired State

A reviewer is invited, creates an account, and declares the languages they read. They
then work through a queue of scored cells drawn at random from a committed run:

1. **Judge blind.** For each cell they see the task, the edition and citation, the prompt,
   the expected text and the model's answer, with each text rendered legibly in its own
   script and direction. They don't see the scorer's verdict, its submetrics, the
   grader path, the failure kind or the model's identity. Using the per-task rubric
   (below), they record their own verdict: `correct` / `incorrect` / `refused` /
   `can't judge`. They can add a **question-defect** flag (the expected text or prompt is
   itself wrong) and notes.
2. **Reveal.** Once the blind verdict is committed, the scorer's outcome, submetrics,
   grader path, failure kind and model are shown, along with whether the two agree. The
   blind verdict can no longer change. The reviewer can record a **revised verdict**
   (e.g. "I misread the Hebrew"), a **rubric-problem** flag (the rubric itself gives the
   wrong answer for this cell) and post-reveal notes. All of these are kept beside the
   blind verdict and never replace it.
3. **Resume anywhere.** The queue, positions and unfinished notes persist on the server.
   The same account on another device sees the same cells in the same order. A sample
   never shifts under a reviewer.

Behind this:

- **The sampling frame is committed and citable.** A seeded, stratified **review set** is
  drawn from a named run by a CLI and committed: seed, allocation, source run, file
  digests, stratum sizes, selection probabilities, overlap subset, and the cells' content.
  It is audited and test-gated like run evidence, and its digest is pinned in the repo. The
  hosted service serves only cells from a pinned, ingested review set.
- **Assignment** hands each reviewer cells from the set in its seeded order, limited to
  the languages they read. Shared **overlap** cells go to every reviewer who reads that
  language. Every assignment is persisted with its time, position and the reviewer's
  languages at that moment.
- **Results** are exported by an operator into a committed JSONL that uses keyed
  pseudonyms, never email or name. An **agreement report**, built only from that export
  and its review set, gives the estimands defined below with intervals. The cited numbers
  are always tied to one specific committed export.
- Committed run evidence is never modified. Accounts, sessions, assignments and judgements
  live in the review store. Their published form is the export.
- **Delivery scope.** Everything is built and verified **locally end to end** (service
  against a local Postgres; PGlite in tests). Provisioning the hosted deployment is a
  separate step, gated on an explicit go-ahead.

### Defaults (proposed by the issue; confirm or change at the spec gate)

The success criteria are written against these. Changing one at the gate changes only its
parameter or rule, not the architecture.

**D1. Reviewer rubric (versioned, shown per task).** It encodes the benchmark contract the
project already decided deliberately: Spec 48's assertion gate, #23's leading stance,
#150's completion head, and containment. So agreement measures whether the scorer
implements that contract, not whether the contract is right. Disagreement with the
contract itself is captured separately by the post-reveal rubric-problem flag.

- *retrieve_quote*
  - **Correct:** the answer presents a passage as its answer (hedges like "from memory" or
    "I may be misremembering" don't matter), and the full expected passage appears in it
    unbroken. The wording must match, ignoring:
    - vowel marks, cantillation and diacritics;
    - punctuation and spacing;
    - verse numbers and markers;
    - the edition's script convention (e.g. Uthmani vs Imla'i).

    Any amount of other text around it (a heading, the citation, a translation,
    commentary, neighbouring verses) is fine.
  - **Incorrect:** the passage presented is not the expected one. That covers a different
    passage, a translation or paraphrase, words missing or changed inside it, or only part
    of it.
  - **Refused:** the answer declines and presents no original-language passage as its
    answer. It may offer a summary, a translation, a pointer, or nothing. If it declines
    and then delivers the text anyway, judge the delivered text.
- *complete_unit:* the same tolerances and refusal rule, applied to the continuation.
  **Correct** if the text the answer gives as the continuation contains the expected
  continuation's first ten words, or all of it if it is shorter (the #150 head). It may
  stop after those or run on. **Incorrect** otherwise.
- *cite_passage:*
  - **Correct:** exactly one location is offered, and it is the expected one at the
    precision asked: chapter:verse, Talmud daf+amud, GGS Ang. Any numerals or notation
    count (Arabic-Indic digits, Hebrew letter numerals, surah names). The same location
    restated in two notations is one location, and an echo of the prompt's form example
    that the answer disclaims doesn't count.
  - **Incorrect:** a different location, two or more different locations offered as
    alternatives, or no location.
  - **Refused:** the answer declines to give a location.
- *verify_source:* the verdict is the answer's **leading stance**, the Yes or No it opens
  with in its first sentence. **Correct** if that matches the expected answer,
  **incorrect** if it is the other one, and **refused** if the answer doesn't open with
  Yes or No (even if it says one later).
- Any task: use **can't judge** when you can't read the script well enough or the cell is
  unintelligible.

**D2. Strata and allocation.** A stratum is (scorer outcome, task, edition group, path).

- **Edition group** is the run's tradition folder × the edition language. Encyclicals
  count as one group.
- **Path** depends on the scorer's outcome:
  - correct retrieve/complete: `exact` / `normalized` / `contained` / `addition`;
  - correct cite: `standard` / `zero_candidates` (n_candidates = 0) / `segment_mismatch`
    (segment_match = 0);
  - correct verify: `expected_yes` / `expected_no`;
  - incorrect retrieve/complete: `near` (diacritic_only / edition_variant / near_copy /
    omission) / `paraphrase` / `other_script` / `wrong_passage`;
  - incorrect cite: `hedge` / `wrong_locus` / `no_citation`;
  - incorrect verify: `wrong_verdict`;
  - refused: none.

The review-set size is B (default 2,000). It is split by outcome shares (default 60%
correct / 25% incorrect / 15% refused). Within an outcome:

- every non-empty stratum first gets min(N_h, m) cells (default m = 3);
- the remainder is shared in proportion to N_h × w_path, where suspect paths
  (`contained`, `addition`, `zero_candidates`, `segment_mismatch`) weigh 4, `exact`
  weighs 0.25, and everything else weighs 1;
- each stratum is capped at N_h, and any overflow is redistributed;
- rounding is largest-remainder, with ties broken by stratum key order.

Within a stratum, cells are taken in order of sha256(seed ∥ cell id), which is
independent of file-read order. Each stratum's selection probability π_h = n_h / N_h is
recorded. All parameters are recorded in the set.

**D3. Overlap.** In each stratum, the first ⌈r × n_h⌉ selected cells (default r = 10%) are
overlap cells. They are ordinary set cells, so they carry no separate selection
probability.

**D4. Queue order and assignment.**

- **Global order:** the set has one global order, by sha256(seed ∥ "order" ∥ cell id), so
  overlap cells are spread through it at random.
- **Batches:** a reviewer asking for a batch (default 25 cells) gets the next cells in
  global order that are in their languages. Overlap cells are always included.
  Non-overlap cells are included only if no one has claimed them yet (claim-based).
- **Concurrency:** a non-overlap cell can be claimed at most once per set, and concurrent
  claims resolve with exactly one winner.
- **Stability:** assignments are never released or reordered.
- **Why claim-based:** coverage is scarce. The set's global order is random, so the
  claimed cells in any language are a random subsample of the set's cells in that
  language.

**D5. Languages.**

- The choices are the edition languages present in the set, labelled for humans.
  Hebrew (`he`) and Aramaic (`arc`) form one "Hebrew script" choice. Pali (`pi`) is its
  own choice although its edition is romanized. English is offered.
- A change of declared languages affects only later batches. Each assignment snapshots
  the declared languages.

**D6. Blinding scope.** Hidden until the blind verdict: outcome, all submetrics, grader
path, failure kind and model identity.

**D7. Copyright.** By default every cell from a restricted-origin edition is excluded,
**NRSV included**. That is the issue's literal constraint; see Open Question 1.

**D8. Export and pseudonyms.**

- The export runs as an operator command inside the API service, which adds no network
  surface and needs no reviewer account.
- A reviewer pseudonym is a keyed hash (HMAC) of the reviewer id under an operator secret
  held in the service environment. It is stable across exports, not derived from email,
  and not dictionary-attackable.
- The export carries no cell text. It references set cells by id.

**D9. Account delete.** Ported unchanged: it cascades. A published figure is tied to a
specific committed export, so it stays reproducible from that file after a later account
delete. Signup consent states this.

**D10. Hosting topology.** Railway, mirroring multibench:

- a viewer edge service that is the one public origin, serving the viewer build and
  proxying `/api` over the private network;
- a private API with no public domain;
- Postgres with a daily backup schedule.

The public browsing viewer stays on Cloudflare Pages, unchanged. The review routes don't
depend on run data being served.

### Estimands (what the report computes)

Notation: S is the scorer outcome as served, and H is the human's blind verdict, each in
{correct, incorrect, refused}.

- **Excluded cells.** `can't judge` and question-defect-flagged cells are excluded from
  every estimand. Each has its own rate per stratum, and both are listed.
- **Agreement**: P(H = S).
- **Precision of `correct`**: P(H = correct | S = correct). Its complement, the **false
  discovery rate**, is the false-positive headline.
- **Missed-credit rate**: P(H = correct | S = incorrect).
- **Refusal precision**: P(H = refused | S = refused).
- **Weighted estimands.** Recall of correct, P(S = correct | H = correct), is reported only
  as a population-weighted estimate. So is the full 3 × 3 confusion matrix, which is also
  shown as unweighted counts.
- **Overlap cells** count once in human-vs-scorer estimands. Each such cell's value is the
  mean of its raters' indicators.
- **Weighting is post-stratified.** A judged cell in stratum h has weight N_h / j_h, where
  j_h is the number of judged, non-excluded cells there. This is unbiased under
  missing-at-random within strata. A stratum with j_h = 0 is **uncovered**: its population
  share is reported as uncovered mass, and weighted estimates describe the covered
  population only, never extrapolated.
- **Intervals.**
  - Unweighted per-stratum and per-breakdown proportions get Wilson 95% intervals.
  - Weighted estimates get a stratified bootstrap 95% percentile interval: resample
    judged cells within each stratum, with a fixed seed and 2,000 replicates.
- **Inter-rater agreement.** Over overlap cells with two or more ratings, the report gives
  Krippendorff's α (nominal; `can't judge` treated as missing) with a bootstrap interval,
  plus pairwise raw agreement, overall and per language.
- **Headline vs secondary.** Headline figures use the blind verdict. A secondary line uses
  the final verdict (the revision if present), and the revision rate is reported.
- **Citable vs descriptive.** Citable: the overall and per-task weighted precision, false
  discovery rate and agreement. Per tradition, per path and per stratum are descriptive.
  A Wilson half-width is about ±2.9 pp at p = 0.9 with n = 400, and about ±5.9 pp with
  n = 100. So the working target is at least 400 judged scorer-`correct` cells overall and
  at least 100 per task. The report prints the judged n beside every figure.
- **Adjudication worklist (#41).** The report lists every human-vs-scorer disagreement and
  every overlap disagreement (cell id, verdicts, flags, notes). It also lists the
  other-script, paraphrase and wrong-citation strata's verdicts, for the owner to
  adjudicate.

## Success Criteria

- [ ] **Review-set builder.** A CLI reads a named run directory read-only and writes a
      review set under the D2–D4 rules.
      - Same run + seed + parameters ⇒ byte-identical output; a different seed ⇒ a
        different draw.
      - The set records:
        - seed and all parameters;
        - source run id;
        - sha256 of every score/answer file read;
        - per stratum: key, N_h, n_h, π_h;
        - overlap membership;
        - global order;
        - the set's canonical digest.
      - Only scored cells (with an `outcome`) are eligible.
      - Restricted-origin cells are excluded per D7.
- [ ] **FAccT review set committed and pinned.** A set drawn from `runs/facct-2026-11-03`
      is committed and its digest is pinned in the repo. `git diff` shows no change to any
      existing file under `runs/`.
- [ ] **Committed review artifacts are gated.** The test gate's committed-artifact audit
      covers the review set and every committed export, and they pass `audit.py`. The gate
      also asserts that the pinned digest equals the committed set's recomputed digest.
      A change touching only review artifacts runs the pipelines lane (the audit) in
      `.codev/checks/test.sh`. The viewer's run discovery doesn't list review artifacts as
      runs.
- [ ] **Trusted ingest.** The API ingests a set only if its recomputed canonical digest
      equals a pinned digest. Re-ingesting it is a no-op. A different set gets a new set
      id and never alters an earlier set's cells or judgements. Anything else is
      rejected.
- [ ] **Accounts ported unchanged.** Signup (invite-gated, fail-closed when the code is
      unset), login, logout, `me`, CSRF fetch and account delete (cascading) behave as in
      multibench, and its auth/CSRF/CORS/session/health tests are ported and pass. The
      signup consent text says what is published: pseudonym, declared languages, verdicts,
      flags and notes verbatim. It also says what account delete does and doesn't remove
      (D9).
- [ ] **Profile and languages.** A reviewer sets name, background and languages (D5).
      Assignment never hands them a cell outside the languages declared at assignment
      time. A reviewer with no matching cells sees an explicit empty state.
- [ ] **Stable, race-safe assignment.** The queue and its order survive reload,
      logout/login and a second device. "More cells" appends a batch and never reorders.
      Each assignment records set id, position, time and the languages snapshot. A
      non-overlap cell is claimed at most once, even under concurrent requests. Every
      overlap cell in a reviewer's languages is assigned to them. An exhausted set reports
      "no more cells".
- [ ] **Server-enforced blinding.** Before a reviewer's blind verdict on a cell is
      committed, no API response to that reviewer for that cell contains any D6 field.
      After it, the cell's response includes them. A committed blind verdict is immutable,
      and changes are rejected. The revised verdict, rubric-problem flag and post-reveal
      notes are stored without touching it.
- [ ] **Drafts with the multibench fixes.** Unfinished judgements persist with optimistic
      concurrency: a stale write gets 409 plus the current state, and the client
      reconciles. Each named fix has a regression test:
      - no cross-reviewer state on account switch or 401;
      - a failed load never overwrites a saved draft;
      - a CSRF 403 refreshes and retries;
      - a slow list load never clobbers a newer per-item load.

      Request bodies are size-capped. Submissions are insert-only.
- [ ] **Review UI.** New viewer routes:
      - **sign-in/sign-up gate;**
      - **profile;**
      - **queue** with progress (judged / assigned, overlap marked);
      - **judging page** that reuses the explorer's cell rendering. It shows the D1
        rubric for the task, renders RTL scripts with the correct direction and a
        script-capable font, keeps scorer-derived content out of the DOM until reveal,
        and passes the viewer's no-invisible-text rule.

      Existing routes and tests are unaffected. The static Cloudflare build still builds,
      and its review routes show "review service unavailable" instead of crashing.
- [ ] **Versioned rubric.** The rubric carries a version, and each judgement records the
      version shown.
- [ ] **Export.** The D8 operator command writes JSONL, stably sorted (same store ⇒
      byte-identical file). Each row has:
      - set id and seed, cell id, stratum key;
      - pseudonym and the languages snapshot;
      - assignment position and time, overlap flag;
      - rubric version;
      - blind verdict and time;
      - the scorer outcome, submetrics, path and failure kind as served;
      - revised verdict, flags and notes.

      No email, name, background or credential-derived data appears (asserted by a test).
- [ ] **Agreement report.** A CLI reads an export plus the set it references and computes
      every estimand above, with intervals, the excluded and uncovered rates, judged n
      beside each figure, and the adjudication worklist. It is deterministic. Its numbers
      are pinned by a test over a synthetic export and set with hand-computed answers,
      including a weighted case, an uncovered stratum and an overlap split. An export
      naming an unknown set fails loudly.
- [ ] **Test gate.** `apps/api` is registered in `.codev/checks/test.sh`, and its suite
      runs on PGlite with no external database. The Python builder and report run in the
      pipelines lane.
- [ ] **Schema discipline.** Every schema change is a `drizzle-kit generate` migration
      whose SQL is committed and reviewed in the PR. `db:push` is never used.
- [ ] **Local end-to-end.** The runbook covers running the service against a local
      Postgres and walks one reviewer through sign-up → judge → reveal → resume →
      export → report, with the steps recorded in the review document.
- [ ] **Deployable, not deployed without consent.** The PR ships the D10 deploy
      configuration and runbook. Provisioning only follows an explicit human go-ahead
      with a cost envelope. If that's given, the post-deploy gate is:
      - login, blind judge, reveal and resume across real Safari and Chrome through the
        one public origin;
      - the API has no public domain;
      - the backup schedule is confirmed;
      - the pinned set is ingested.

## Constraints

From the issue (no Baked Decisions section is present; these are its stated constraints):

- **Reuse the multibench review tool — do not rebuild.**
  - Port the API (Hono + Drizzle + Postgres, PGlite tests) wholesale.
  - Port accounts unchanged.
  - Port draft persistence with optimistic concurrency and immutable submissions,
    re-keyed to the review unit.
  - Port and adapt the client store, API client, auth gate, check control and progress,
    plus the seeded, recorded sampling approach.
  - Keep the topology: one public origin, private API behind a same-origin edge proxy.
  - Port the **fixes**, not only the first draft.
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

- `pipelines/` is the single uv project. The review-set builder and the report belong
  there, beside the scorer, `failure_kind.py` and the audit.
- The viewer uses HeroUI v3 (provider-less), TanStack Router and Vite, and has a test
  rule against invisible text.
- A new committed-artifact location must be wired into both the audit scan and the test
  dispatcher. That is the `fixtures/` gap lesson recorded in `lessons-critical`.
- **Privacy.** The repo is public. Emails, names and backgrounds stay in the private
  store.
- Secrets come from the environment only, never the SPA. That covers the database URL,
  the invite code and the pseudonym key.

## Assumptions

- **Test-tool scale.** A handful to low tens of invited, cooperative reviewers. No
  rate-limit or email-enumeration hardening and no email transport, same as multibench.
- **Cooperative blinding.** The public viewer and the committed review set both expose
  scores, so a determined reviewer could look a verdict up. Server-side blinding protects
  the integrity of the record (the verdict really was committed before the reveal), not
  secrecy against a reviewer working against it. The report states this.
- **Missing-at-random within strata.** Assigned-but-unjudged cells are assumed to be
  missing at random within their stratum. The global order is random and there's no skip
  (only `can't judge`, which is recorded), so this is plausible. The report states it.
- The FAccT run `runs/facct-2026-11-03` is the first population. The builder takes any
  run directory with the same layout.
- A later rebaseline doesn't invalidate judgements. The export records the scorer
  verdict *as served*, and the blind label doesn't depend on any scorer.
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

A Python CLI in `pipelines` draws the D2–D4 review set from a named run. The set is
committed, audited and pinned. The API ports multibench's service, auth, sessions, CSRF,
account delete, migrations, health and PGlite rig wholesale, and adds the re-keyed review
slice:

- pinned, idempotent ingest;
- language-filtered, claim-based assignment with the overlap interleaved;
- a cell endpoint that withholds D6 fields until the blind verdict is committed;
- per-cell drafts with optimistic concurrency and insert-only submissions (the blind
  verdict, then optional post-reveal records).

The viewer gains review routes. They reuse the explorer's cell rendering and the ported
client store and API client (with the fixes), the auth gate, check control and progress.
An operator export writes pseudonymous JSONL. A Python report computes the estimands.

- **Pros:**
  - The sampling frame is a committed, citable, reproducible artifact with a trust chain
    (git → test-gated audit → pinned digest → recomputed at ingest).
  - Blinding and blind-verdict immutability are server-attested.
  - Overlap and coverage are controlled.
  - The served surface is only the audited set.
  - Sampling and statistics live next to the scorer and `failure_kind.py`, which already
    know the grader paths.
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

**Assignment sub-choice.** Claim-based (D4) maximises coverage with few reviewers. Its
order depends on when reviewers arrive, but every assignment is persisted. The
alternative is per-reviewer seeded permutations, multibench-style: reproducible from seed
and reviewer id alone, at the cost of duplicate effort. Recommended: claim-based.

### Approach 3: Offline sheet

Export a stratified sample to CSV or Google Sheets for reviewers to fill in.

- **Pros:** no hosting cost, no new code.
- **Cons:** no accounts, no blinding (the verdict sits in a neighbouring column or must be
  hand-hidden), poor RTL and script rendering, manual and error-prone merging, and no
  stable per-reviewer assignment. It also contradicts the issue's "reuse the multibench
  tool".
- **Risk:** low effort, but low-integrity data. Rejected. If hosting is declined,
  Approach 2 still runs locally.

**Recommendation: Approach 2.** It is the only option where the number the paper cites
(agreement between a blind human and the scorer) rests on an auditable record: a committed,
pinned frame, a server-attested blind-before-reveal order and a deterministic report. It
keeps every multibench piece the issue names, re-keyed only where the review unit forces
it.

## Open Questions

### Critical (blocks progress)

1. **NRSV under the quotation allowance (D7).** Read literally, "no cell derived from a
   restricted source may be served" excludes NRSV. The audit, though, permits NRSV within
   500 distinct verses per file, and the FAccT run's 1,920 NRSV cells cover only 31
   verses. Excluding them removes the entire English-Christianity population from the
   audit. Default: **exclude**. Option: include NRSV, with `audit.py` enforcing the
   allowance on the committed set.
2. **Rubric (D1).** It aligns human judgement with the decided contract (Spec 48 class A
   is scored, class B is refused; verify takes the leading stance; the completion head
   counts; containment allows any surrounding text), and records contract disagreement
   through the rubric-problem flag. Is that the measurement wanted? The alternative is a
   rubric-free "is it really correct" judgement, where the report must then separate
   definitional divergence from scorer error.

### Important (shapes design)

3. **Hosting go-ahead and envelope (D10).** Recurring Railway spend for the edge, the
   private API and Postgres. Building proceeds without it; provisioning does not.
4. **Allocation (D2) and set size.** Are 60/25/15, m = 3, suspect weight 4 and B = 2,000
   right? Is the false-positive target of at least 400 judged scorer-correct cells (at
   least 100 per task) realistic for the expected reviewer pool?
5. **Overlap rate (D3)**, default 10%.
6. **Account delete (D9).** Keep the ported cascade, with figures tied to a committed
   export? Or anonymize-and-retain judgements? The latter changes ported behaviour.
7. **Overlap adjudication.** In scope: the report's worklist. Out of scope: an adjudicator
   role or third-rater tie-break in the tool. Is that enough for #41?

### Nice-to-know (optimization)

8. Finer path attribution (which fold fired) by re-running the scorer inside the set
   builder.
9. Replaying human labels against a newer scorer, as a gold set for future scoring
   changes.
10. Deferred multibench clean-ups: `SameSite=None` → `Lax` once same-origin, and pruning
    expired sessions.
11. Whether the Railway review origin should also serve a baked browsing viewer.

## Test Scenarios

**Review set**

- Same inputs give byte-identical output, and a changed seed changes the draw.
- N_h equals a direct count over the run.
- The D2 allocation on a fixture with known N_h gives the hand-computed n_h, including the
  minimums, caps, redistribution and a largest-remainder tie.
- π_h = n_h / N_h.
- Overlap is the first ⌈r × n_h⌉ cells per stratum.
- Restricted-origin fixture cells are excluded.
- Missing (unscored) cells are never eligible.
- No file under `runs/` changes.
- The committed set passes `audit.py`, and its digest equals the pin.

**Ingest**

- Ingesting the pinned set twice is a no-op.
- A one-byte tamper with a self-recomputed internal digest is rejected, because it isn't
  pinned.
- A second pinned set gets a new id and leaves the first untouched.

**Auth (ported)**

- Signup without an invite code, or with a wrong one, is rejected, and so is signup when
  the code is unset.
- Concurrent duplicate signups yield one account.
- A password over the cap is rejected.
- A non-JSON content type on login or signup is rejected (exact MIME essence).
- A state-changing request without CSRF gets 403. After a CSRF refresh the client retries
  and succeeds.
- Logout revokes the session. An expired session is rejected.
- Account delete cascades.

**Isolation**

- Reviewer A can't read or write B's assignments, drafts or submissions.
- Switching accounts in one browser leaves no residue of A in B's session, and neither
  does a 401.

**Assignment**

- An English-only reviewer only gets `en` cells.
- A "Hebrew script" reviewer gets `he` and `arc`.
- A reviewer with no match sees the empty state.
- Changing languages affects only the next batch.
- Reload, re-login and a second device show the same queue.
- "More cells" appends.
- Two concurrent batch requests never claim the same non-overlap cell.
- Overlap cells reach every eligible reviewer.
- An exhausted set says "no more cells".

**Blinding**

- Before the blind verdict, the cell response has no D6 field (asserted across every
  review endpoint). After it, the D6 fields are present.
- Changing the blind verdict after reveal is rejected.
- A revision is stored, and the blind verdict is unchanged in the store and the export.

**Drafts**

- Two devices edit one cell's notes. The stale save gets 409 plus the current state, and
  the client reconciles without silent loss.
- A failed load followed by an edit doesn't overwrite the server draft.
- A slow list load doesn't clobber a newer per-item load.
- An oversize body gets 413.

**UI**

- The judging page shows the task's rubric and its version.
- Arabic, Hebrew and Gurmukhi render with the correct `dir`, and no invisible text.
- No scorer-derived text is in the DOM before reveal.
- Progress is right with overlap.
- The static build shows "review service unavailable".

**Export and report**

- Exporting twice is identical.
- No email, name or background appears (asserted).
- Pseudonyms are stable across exports and differ under a different key.
- A synthetic export and set give hand-computed values for every estimand: Wilson and
  bootstrap intervals, the weighted estimate, uncovered mass, overlap mean-of-raters,
  Krippendorff's α, and the excluded rates.
- An unknown set fails loudly.

**Non-functional**

- The `apps/api` suite runs offline on PGlite through `.codev/checks/test.sh`.
- A review-artifact-only change runs the audit lane.
- Existing viewer and pipelines suites pass.
- `audit.py` stays green.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Too few judgements for citable intervals | High | High | Suspect-weighted strata. A stated target (≥400 scorer-correct overall, ≥100 per task). Judged n printed beside every figure. Citable and descriptive breakdowns separated. Small batches. |
| Language gaps (no Pali or Gurmukhi reader) | High | Medium | Language is part of the stratum (edition group). Uncovered mass is reported, never extrapolated. |
| The rubric diverges from the contract, so the agreement rate measures definitions rather than scorer error | Medium | High | D1 encodes Spec 48, #23 and #150 explicitly. The rubric-problem flag captures contract disagreement separately. Settled at the gate (OQ2). |
| Rubric ambiguity drives low inter-rater agreement | Medium | High | Versioned rubric, recorded per judgement. Overlap with Krippendorff's α. `can't judge` and the defect flag avoid forced guesses. |
| Copyright exposure on a hosted public-repo tool | Low | High | Served surface is only the pinned, audited set. Restricted origins are excluded per D7. Trusted ingest. |
| Review artifacts escape the gate (`fixtures/`-gap class) | Medium | High | A success criterion wires the set and exports into the audit scan and the dispatcher, with a test. |
| Reviewer privacy in a public repo | Medium | High | Keyed pseudonyms. No email, name or background in the export (test-asserted). Consent text lists every published field. |
| Blinding defeated via the public viewer | Low | Medium | Cooperative-reviewer assumption, stated in the report. The server still attests blind-before-reveal order. |
| Account delete after publication | Low | Medium | Figures are tied to a committed export (D9). Consent text. OQ6. |
| A scoring rebaseline makes recorded verdicts stale | Medium | Low | The export records the verdict as served plus file digests. Blind labels are scorer-independent (OQ9). |
| Claim race double-assigns | Low | Medium | One claim per cell, enforced by the database. A concurrency test. |
| The port misses multibench fixes | Medium | Medium | Port from `main` with its tests, and write a regression test per named fix. |
| Hosting spend | Medium | Medium | No provisioning without a go-ahead and an envelope. Thin topology. |
| Loss of judgement data | Low | High | Daily backups, plus periodic committed exports. |
| An unsafe schema change | Low | High | Generate → review SQL → apply via the deploy-time migrator. Never `db:push`. |

## References

- Issue #154 (this), #41 (independent rater for the paraphrase band, wrong citations,
  other-script rows).
- multibench: `apps/api/README.md`; `apps/api/src/{auth,middleware,routes,schema}`;
  `apps/multibrowser/src/lib/{review.ts,reviewApi.ts}`;
  `apps/multibrowser/src/components/{ReviewAuthGate,ReviewCheckControl,ReviewProgress}.tsx`;
  `apps/multibrowser/server/index.mjs`; Specs 83 and 92; Spec 92 fix commits a538310d,
  51aab523, 6bf07dfb, e39fe420, ca104e4b, b268d4ff, 02b59637.
- SacredBench: Spec 15 (graders + outcome), Spec 26, Spec 48 (assertion-gated refusal,
  class A/B), Spec 52 / #94 / #149 / #150 / #111 / #112 / #118 / #135 / #147, #23
  (leading-stance verify), Spec 2 (viewer purge); `pipelines/sacredbench/audit.py`,
  `pipelines/tests/test_audit.py`, `pipelines/sacredbench/failure_kind.py`,
  `.codev/checks/test.sh`, `apps/viewer/README.md`, `runs/README.md`.
