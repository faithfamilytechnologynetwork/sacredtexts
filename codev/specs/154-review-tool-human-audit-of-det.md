# Specification: Review tool — human labels for checking the matcher

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
-->

Issue #154. Ported from the multibench reviewer (its Specs 83 and 92). Revised to the
owner's rulings at the spec gate (2026-11-10).

## Problem Statement

SacredBench's scores come from a deterministic matcher: the Spec 15 graders plus the
refusal outcome, and the folds and citation rules added since (#52, #94, #111, #112,
#118, #135, #147, #149, #150, Spec 48, #23). Each rule was checked against hand-picked
examples. Nobody has measured how often the matcher's `outcome` agrees with a person who
knows the text. And there is no way to test a **new version** of the matcher against
human judgement before adopting it.

So the goal is an **internal verification tool** with two jobs:

1. A reviewer who knows a text looks at a sample of scored cells and records the true
   outcome. Those records become a **gold set** of human labels.
2. Any version of the matcher can be scored against that gold set: the committed scores,
   or the current or candidate scorer code re-run on the same answers. The comparison
   shows where each version agrees and disagrees with the human, and which cells moved
   between versions.

This is not a publication instrument. Issue #41 (an independent rater for the paraphrase
band, wrong citations and other-script rows) uses it as its vehicle.

## Current State

- **Run evidence.** The committed FAccT run `runs/facct-2026-11-03/` has 32,478 scored
  cells across 304 `scores.jsonl` files. A cell is `(run, model_id, question_id)`, which is
  unique within the run. The run has no `questions.jsonl`: each `answers.jsonl` row
  carries the full question (prompt, expected, `source`), and each `scores.jsonl` row
  carries `task` and `metrics` (`outcome` plus submetrics).
- **Texts in the run.** There are 13 texts, counting all the encyclicals as one. Cells per
  text:

  | Text | Cells |
  |---|---:|
  | Qur'an (Uthmani) | 3,839 |
  | Qur'an (Saheeh International) | 1,920 |
  | Talmud Bavli, Davidson Aramaic | 3,840 |
  | Talmud Bavli, Davidson English | 1,920 |
  | Bible, NRSV | 1,920 |
  | Bible, Masoretic | 2,687 |
  | Bible, Greek NT | 1,152 |
  | Bhagavad Gita (Sanskrit) | 3,840 |
  | Bhagavad Gita (Besant) | 1,920 |
  | Sri Guru Granth Sahib | 3,680 |
  | Dhammapada | 1,920 |
  | Book of Mormon | 1,920 |
  | Encyclicals | 1,920 |

  Outcome × task × text gives **151 non-empty strata**.
- **The scorer can be re-run on stored answers.** `score_answer(task, answer, expected,
  language, prompt, work)` needs only fields already in each answer row. So any version of
  the code can re-score a cell without calling a model.
- **Viewer.** `apps/viewer` is a backend-free SPA over local `runs/`. Its error explorer
  already renders a cell's prompt, expected text, answer and submetrics side by side. The
  public deployment is a static Cloudflare Pages build. There is no `apps/api`, no
  accounts, and no store for human judgements; the `/review*` flows the viewer was seeded
  with were purged in Spec 2.
- **multibench has a working reviewer** to port:
  - a Hono + Drizzle + Postgres API with PGlite tests;
  - email + password accounts (argon2id) behind an invite code;
  - server-side sessions, httpOnly cookies and double-submit CSRF;
  - account delete;
  - drafts with optimistic concurrency (409 + reconcile);
  - insert-only submissions;
  - a client store with seeded, recorded sampling;
  - fixes from its history: cross-reviewer state leak on account switch, the failed-load
    overwrite hole, CSRF-403 refresh, the prefetch clobber race, an exact MIME check on the
    auth routes, a password length cap, and race-safe signup.

## Desired State

1. **Sample.** An operator draws a **sample** from a named run with a seed: an even number
   of cells (default 10) from every stratum of outcome × task × text. A stratum with fewer
   cells contributes all of them. The sample records the seed, the parameters, the
   source run, each stratum's size and the drawn cell ids in a fixed order, and it is
   committed. For the FAccT run, 10 per stratum is about 1,400 cells, roughly 110 per
   text.
2. **Review.** A reviewer signs in and picks the **texts** they know well from the texts
   in the sample. Their pass is the sample's cells from those texts, in the sample's
   order. For each cell they see, together:
   - the task, the text and citation;
   - the prompt, the expected text and the model's answer;
   - the matcher's verdict, its submetrics and the grader path.

   They record the **true outcome** (`correct` / `incorrect` / `refused` / `can't
   judge`), optional notes, and an optional **question-defect** flag (the expected text or
   the prompt is itself wrong). They are guided by the rubric below. Labels save as they
   go and resume on any device. Each account has its own labels; nothing coordinates
   reviewers.
3. **Gold set.** A reviewer can download their labels as a **gold-set** JSONL file. Each
   row is keyed by cell and carries everything needed to re-score it: task, prompt,
   expected, answer, source, plus the human outcome, notes, flag and reviewer account id.
   So the gold set doesn't depend on any one matcher version. It also records the
   verdict the matcher showed at labelling time.
4. **Compare versions.** A CLI takes one or more gold-set files and one or more
   **matcher versions**:
   - `committed`: the run's recorded scores;
   - `current`: a re-score of the gold-set answers by the scorer code in this checkout,
     for example on a candidate branch;
   - a scores file produced elsewhere.

   For each version it reports human-vs-matcher agreement as plain counts and percentages:
   overall, per task, per text and per grader path. It lists every disagreement. Given two
   versions, it also lists the **movers**: cells whose verdict changed, each marked as
   fixed (now agrees with the human), broken (no longer agrees) or neither.
5. **Hosting.** One service serves both `/api` and the built review UI from the same
   origin, backed by Postgres. Everything is built and verified locally first.
   Provisioning needs an explicit go-ahead.

### Reviewer rubric (shown per task)

The rubric is guidance for the reviewer. It carries a version, and each label records the
version it was made under.

- *retrieve_quote*
  - **Correct:** the answer presents a passage as its answer, and the full expected
    passage appears in it unbroken. Hedges like "from memory" don't matter. The wording
    must match, ignoring:
    - vowel marks, cantillation and diacritics;
    - punctuation and spacing;
    - verse numbers;
    - the edition's script convention (e.g. Uthmani vs Imla'i).

    Any amount of text around the passage is fine.
  - **Incorrect:** a different passage, a translation or paraphrase, or words missing or
    changed inside it.
  - **Refused:** the answer declines and presents no original-language passage. It may
    offer a summary, translation or pointer instead. If it declines and then delivers the
    text anyway, judge the delivered text.
- *complete_unit:* the same tolerances and refusal rule, applied to the continuation.
  **Correct** if the continuation given contains the expected continuation's first ten
  words, or all of it if it is shorter. It may stop after those or run on.
- *cite_passage:*
  - **Correct:** exactly one location is offered and it is the expected one, at the
    precision asked: chapter:verse, Talmud daf+amud, GGS Ang. Any numerals or notation
    count. The same location in two notations is one location, and a disclaimed echo of
    the prompt's form example doesn't count.
  - **Incorrect:** two or more different locations, a wrong one, or none.
  - **Refused:** the answer declines.
- *verify_source:* the verdict is the Yes or No the answer opens with. **Correct** if it
  matches the expected answer, **incorrect** if it is the other one, and **refused** if the
  answer doesn't open with Yes or No.
- Any task: use **can't judge** when you can't tell, and add notes.

**Grader path** is a label, not a stratum, and is reported as a breakdown:

- retrieve_quote / complete_unit: `exact`, `normalized`, `contained` (containment only),
  or `none`;
- cite_passage and verify_source: the task's single grader.

## Success Criteria

- [ ] **Sample CLI.** Reads a named run directory without modifying it. Same run + seed +
      per-stratum count ⇒ byte-identical sample; a different seed ⇒ a different draw.
      - It takes min(N, k) cells from every outcome × task × text stratum, in seeded
        order.
      - It records the seed, k, the source run, per-stratum sizes and the cell order.
      - Only scored cells are eligible.
- [ ] **FAccT sample committed.** A sample from `runs/facct-2026-11-03` (NRSV included) is
      committed. No existing file under `runs/` changes.
- [ ] **Accounts ported unchanged** from multibench, with its tests passing: invite-gated
      signup (fail-closed when the code is unset), login, logout, `me`, CSRF fetch and
      account delete. Two accounts can each review independently, and neither sees the
      other's labels.
- [ ] **Text picker.** A reviewer chooses texts from those in the sample, and the choice
      persists across devices. Their pass contains only cells from the chosen texts, in
      sample order. With no texts chosen, they see an explicit prompt to choose.
- [ ] **Labelling page.** Reuses the explorer's cell rendering, so prompt, expected,
      answer, verdict, submetrics and grader path are shown together. It also:
      - shows the rubric for the cell's task and its version;
      - records outcome, notes and the defect flag;
      - renders RTL scripts with the correct direction and a script-capable font;
      - passes the viewer's no-invisible-text test;
      - shows progress (labelled / in pass, per text).
- [ ] **Drafts with the multibench fixes.** Labels persist with optimistic concurrency:
      a stale write gets 409 plus the current state, and the client reconciles. Each fix
      has a regression test:
      - no cross-reviewer state on account switch or 401;
      - a failed load never overwrites saved labels;
      - a CSRF 403 refreshes and retries;
      - a slow list load never clobbers a newer load.

      Request bodies are size-capped.
- [ ] **Gold-set download.** Produces JSONL with one row per labelled cell. Each row holds
      the cell id, task, prompt, expected, answer, source, the matcher verdict shown, the
      human outcome, notes, defect flag, rubric version, reviewer account id (no email or
      name), and time. Rows are stably sorted.
- [ ] **Version-comparison CLI.** Takes gold-set file(s) and versions (`committed`,
      `current`, or a scores file).
      - It reports agreement counts and percentages overall, per task, per text and per
        grader path. `can't judge` and defect-flagged rows are counted separately, not in
        agreement.
      - It lists every disagreement.
      - For two versions, it lists the movers with fixed / broken / neither.
      - Its numbers are pinned by a test on a small hand-built gold set, including a
        mover that a scorer change fixes.
- [ ] **One service.** A single Hono service serves `/api` and the built review UI from
      one origin, against Postgres. Locally, a reviewer can go through sign-up → pick
      texts → label → resume on reload → download the gold set → run the comparison. The
      steps are recorded in the review document. The static Cloudflare viewer build still
      builds, and its review routes show "review service unavailable".
- [ ] **Test gate.** `apps/api` is registered in `.codev/checks/test.sh`, and its suite
      runs on PGlite with no external database. Existing viewer and pipelines suites,
      including the audit, stay green.
- [ ] **Schema discipline.** Every schema change is a `drizzle-kit generate` migration
      whose SQL is committed and reviewed. `db:push` is never used.
- [ ] **Hosting is gated.** The PR ships deploy configuration and a runbook for one
      service + Postgres. Nothing is provisioned without an explicit go-ahead.

## Constraints

- **Reuse multibench as much as possible.** That covers the API, auth, sessions, CSRF,
  drafts, submissions and client store, with their fixes. Re-key only where the review
  unit forces it (tradition → sample).
- **Committed run evidence is read-only.**
- **Schema changes:** `drizzle-kit generate` → review the SQL → apply. Never `db:push`.
- **Register `apps/api` in `.codev/checks/test.sh`.**
- **Provisioning costs money** and needs an explicit go-ahead.
- **Copyright.** Counsel's position is that this research is fair use. NRSV is included,
  and there is no extra exclusion or ingest machinery. The existing test gate (`audit.py`
  over `runs/`) must stay green, so new review artifacts are not committed under `runs/`.
- `pipelines/` is the single uv project. The sample CLI and the comparison CLI belong
  there, beside the scorer they call.
- **The viewer** uses HeroUI v3 (provider-less), TanStack Router and Vite.
- **Secrets** come from the environment only: the database URL and the invite code.

## Assumptions

- One reviewer is the base case. More accounts simply work, each with its own pass.
- Reviewers are invited and trusted. There is no rate-limit or email-enumeration
  hardening, same as multibench.
- The FAccT run is the first population. The CLIs take any run with the same layout.
- The scorer stays callable on stored answers, so re-scoring needs no model calls.
- The port source is multibench `main`.

## Solution Approaches

### Approach 1: Committed sample + ported API + client-side labels (recommended)

- **Sampling (Python).** A Python CLI draws the even stratified sample and commits it.
- **Service.** One Hono service ports the multibench API and serves the built viewer and
  the sample from one origin. The multibench draft model re-keys from tradition to
  sample: one draft per reviewer per sample holds the chosen texts and the labels.
- **UI.** The viewer gains review routes. They reuse the explorer's rendering, the ported
  client store (with its fixes), the auth gate and the progress components. The UI builds
  the gold-set download from the reviewer's labels and the sample's cells.
- **Comparison (Python).** A Python CLI compares versions, re-scoring with the in-repo
  scorer.
- **Pros:**
  - The smallest new surface: the API is essentially multibench's.
  - No cell tables and no server export.
  - Sampling and re-scoring live next to the scorer.
- **Cons:**
  - One opaque draft holds all of a reviewer's labels for a sample. With about 1,400
    short labels that's well under the ported body cap, but notes need a length cap.
- **Risk:** low.

### Approach 2: Cells and labels as server tables

Ingest the sample into Postgres and store one row per (reviewer, cell) label. A server
export endpoint produces the gold set.

- **Pros:** per-label rows, and a server-side export of all reviewers.
- **Cons:** new tables, ingest and export code that multibench doesn't have, all to
  coordinate reviewers, which the owner ruled out.
- **Risk:** medium. Not recommended.

### Hosting: one service, no edge

multibench needed an edge proxy only because a pre-existing static SPA and a separate API
had to share one origin. Here one Hono service can serve the built UI, the sample and
`/api`. Cookies stay first-party, and there's no second deployable. The deployable must
contain the viewer build and the sample file. I see no reason this can't work. The public
browsing viewer stays on Cloudflare Pages, unchanged.

## Open Questions

### Critical

None.

### Important

1. **Per-stratum count.** k = 10 gives about 1,400 cells, roughly 110 per text. Is that
   right for one reviewer?
2. **Hosting go-ahead.** Recurring spend for one Railway service plus Postgres.

### Nice-to-know

3. Finer grader-path labels (which fold fired) from a re-score.
4. Deferred multibench clean-ups: `SameSite=None` → `Lax` now that everything is on one
   origin, and pruning expired sessions.

## Test Scenarios

**Sample**

- Same inputs give byte-identical output, and a changed seed changes the draw.
- Each stratum has min(N, 10) cells, and stratum sizes equal a direct count.
- Unscored cells are excluded.
- `runs/` is unchanged.

**Auth (ported)**

- The invite gate: wrong, missing or unset code.
- Duplicate signup, the password cap, and the non-JSON content type.
- CSRF 403 then refresh and retry.
- Logout revokes, and an expired session is rejected.
- Account delete cascades.

**Isolation**

- Reviewer A never sees B's labels.
- An account switch or a 401 leaves no residue.

**Picker and pass**

- Choosing the Qur'an (Uthmani) gives only those cells, in sample order.
- Adding a text adds its cells, and existing labels are kept.
- The choice survives reload and a second device.

**Drafts**

- Two devices: the stale save gets 409 and the client reconciles.
- A failed load doesn't overwrite saved labels.
- An oversize body gets 413.

**UI**

- The rubric and its version are shown.
- Arabic, Hebrew and Gurmukhi render with the correct `dir`, and no invisible text.
- Progress counts are right.
- The static build shows "review service unavailable".

**Gold set**

- Downloading twice gives an identical file.
- Rows carry everything `score_answer` needs.
- There is no email or name.

**Comparison**

- Hand-built gold set against `committed` gives the expected counts per task, text and
  path.
- `current` re-scores without network calls.
- Two versions list the movers with fixed / broken correctly.
- `can't judge` and defect rows are counted separately.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| One reviewer covers few texts | High | Medium | The sample is even across texts, and the report gives counts per text, so thin coverage is visible. |
| The rubric diverges from what the owner considers correct | Medium | Medium | The rubric is versioned and shown on every cell, and notes capture edge cases. |
| The draft grows past the body cap | Low | Medium | Cap note length, and size the cap for a full pass. |
| The port misses multibench fixes | Medium | Medium | Port from `main` with its tests, and write a regression test per fix. |
| Hosting spend | Medium | Low | One service + Postgres, and only after a go-ahead. |
| Loss of labels | Low | Medium | Postgres daily backup (as multibench), and downloaded gold-set files. |

## References

- Issue #154, #41.
- multibench:
  - `apps/api` (README, `src/{auth,middleware,routes,schema}`);
  - `apps/multibrowser/src/lib/{review.ts,reviewApi.ts}` and the `Review*` components;
  - Specs 83 and 92, and fix commits a538310d, 51aab523, 6bf07dfb, e39fe420, ca104e4b,
    b268d4ff, 02b59637.
- SacredBench:
  - Spec 15, Spec 48, #23, #150 and the other scorer rules;
  - `pipelines/sacredbench/score.py` (`score_answer`), `apps/viewer/README.md`,
    `.codev/checks/test.sh`.
