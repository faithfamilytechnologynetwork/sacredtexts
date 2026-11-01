# Specification: Trim the Arabic hadith pool to the six books (Kutub al-Sittah)

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/74-*.md.
-->

## Problem Statement

The Arabic hadith pool currently carries **nine** classical collections — the *al-kutub
al-tis'a* ("the nine books"): the six canonical books plus Muwatta Malik, Musnad Ahmad, and
Sunan al-Darimi. The owner has decided (Waleed, 2026-11-01) that the benchmark's Arabic hadith
pool should be **the six canonical books** (the *Kutub al-Sittah*): Sahih al-Bukhari, Sahih
Muslim, Sunan Abi Dawud, Jami\` at-Tirmidhi, Sunan an-Nasa'i, and Sunan Ibn Majah.

The three dropped collections are the 7th–9th of the nine; Sunan al-Darimi is the least
prominent and has no English text on sunnah.com. Keeping them inflates the Arabic pool beyond
the canonical set the benchmark intends to measure and dilutes per-tradition balance.

Who is affected: anyone generating or interpreting a run of the benchmark (the Arabic hadith
pool shrinks from 9 → 6 collections, the total pool from 20 → 17 texts, and a reference-params
`generate` from 560 → 476 questions), and anyone reading the catalogue, the committed reference
run's FAccT card, or the corpus documentation.

## Current State

- `texts/raw/Sunni Islam/source.yaml` declares the Qur'an plus **nine** hadith targets; the three
  to-be-dropped payloads (`malik.json`, `ahmed.json`, `darimi.json`) are committed, tracked,
  public-domain JSON under `hadith_from_sunnah.com_arabic_only/`. The file header comment says
  "nine classical hadith collections."
- The default question pool (the rule `language == canonical_language`, non-restricted) is
  **20 texts**; after PR #73 merged (Saheeh International, an out-of-pool English Qur'an) the full
  catalogue is **27 targets**. `test_catalogue.py` pins both the target count and the exact 20-text
  pool membership set (including the three hadith); #73 updated the target-count pin to 27 while
  leaving the pool at 20.
- A reference-params `generate` over the *current* corpus produces **560 questions**
  (20 texts × 28). `test_original_run_regression.py` pins the current-corpus generation anchor
  as `ANCHOR_CORPUS_HASH = 65bb68f118d63112` and `ANCHOR_DIGEST = 93b71460742a8ecd`
  (both will be moved once by PR #73, Saheeh International, before this change — see Assumptions).
- The negative-sampling family in `generate.py` (`_family`) groups hadith by
  `document_type == "hadith_collection"` — **not** by a hardcoded list of nine — so the family
  logic is unaffected by the trim; only its explanatory comments (and a `catalogue.py` module
  docstring and a `test_generate.py` comment) say "nine."
- **The committed reference run `runs/original-2026-10-21`** was generated when the pool was a
  different 17 texts (Qur'an + all nine hadith + Talmud + three LDS works + three English Bibles;
  SGGS / Dhammapada / Gita were added later and, per Spec 50/#56, do not change a historic card).
  Its manifest lists all three to-be-removed collections in `selected_texts` (each carrying only
  `{work, version, language}`), and its committed FAccT card (`facct.json` / `facct.md`) reports
  them in the per-text census. `answers.jsonl` / `scores.jsonl` / `summary.json` for this run are
  frozen evidence and are **never** re-scored or edited.
- **FAccT rebuild behaviour today** — `build_facct(run)` recomputes the card from the manifest +
  the live catalogue. `_census` looks each selected text up in the current catalogue and
  **raises `FacctError("selected text … has no catalogue target")` if the target is absent**
  (facct.py). It is written for the *addition* case (`post_run_filter` drops later-added targets
  so a historic card stays byte-identical); the symmetric *removal* case is not handled —
  removing a selected edition makes the historic card un-rebuildable. Two tests rebuild this
  committed card and will fail once the three targets leave the catalogue:
  `test_original_run_regression.py::test_committed_facct_card_matches_the_run` (byte-equality of a
  fresh rebuild to the committed card) and
  `test_facct.py::test_real_run_census_and_counterfactual` (asserts `n_texts == 17`, the
  counterfactual denominator, etc.).
- `selected_corpus_hash` on the card is a `corpus_hash` over the raw content of only the editions
  the run selected (read from `texts/raw/**` via `load_edition_documents`). The three hadith are
  in that selected set, so deleting their payloads would also move `selected_corpus_hash` — but
  `_census` raises first, so the loud failure surfaces before that point.
- `edition_index.load_edition_documents` simply iterates the catalogue's non-restricted targets;
  a removed target is no longer iterated, and hadith (single-wording, non-verse citations) never
  enter the Bible-scoped edition counterfactual, so the edition-index export is otherwise
  unaffected by the trim.

## Desired State

- The catalogue's Sunni Islam source declares **six** hadith collections (the Kutub al-Sittah)
  plus the Qur'an; the three dropped payloads are removed from the repository; the source header
  comment reads "six."
- The default pool is **17 texts** and the catalogue **24 targets** (27 post-#73 minus the three
  dropped hadith); `test_catalogue.py` pins the new counts and the new 17-text membership set
  (Muwatta Malik, Musnad Ahmad, Sunan al-Darimi absent).
- A reference-params `generate` over the trimmed corpus produces **476 questions** (17 × 28);
  `ANCHOR_CORPUS_HASH` and `ANCHOR_DIGEST` are re-pinned **once** from a fresh `generate` over the
  post-#73, post-trim corpus, following the documented re-pin procedure.
- The committed reference run's frozen evidence (`answers`/`scores`/`summary`/`manifest`) is
  untouched. The FAccT-card rebuild path behaves **honestly and loudly** when a historic run
  selected an edition the catalogue no longer contains: it is clear that the card cannot be
  reconstructed (its source editions are gone), rather than silently producing a card for a
  corpus that no longer exists. The two tests that rebuild the committed card are updated to
  codify this behaviour, and the committed `facct.json` / `facct.md` are preserved (byte-pin holds
  on the files; the rebuild expectation is re-expressed, with the reason stated in a test comment).
- Explanatory comments/docstrings that say "nine hadith collections" are corrected to "six" in
  `source.yaml`, `generate.py`, `catalogue.py`, and `test_generate.py`. Any corpus-count prose in
  `texts/README.md` / `CODE_WALKTHROUGH.md` / arch notes that enumerates the hadith count or the
  pool/target totals is corrected (none was found referencing "nine hadith" at spec time; the
  implementer re-greps and updates whatever is live).
- The copyright audit and the full test suite pass on the trimmed corpus.

## Success Criteria

- [ ] `texts/raw/Sunni Islam/source.yaml` contains exactly six hadith targets (Bukhari, Muslim,
      Abi Dawud, Tirmidhi, Nasa'i, Ibn Majah) plus the Qur'an; no Muwatta Malik / Musnad Ahmad /
      Sunan al-Darimi target remains; the header comment says "six."
- [ ] `malik.json`, `ahmed.json`, and `darimi.json` are removed from
      `texts/raw/Sunni Islam/hadith_from_sunnah.com_arabic_only/` and are no longer tracked by git.
- [ ] `test_catalogue.py` asserts `len(targets) == 24` and a 17-text pool membership set without
      the three dropped collections; its docstring/name reflect "seventeen."
- [ ] A reference-params `generate` over the trimmed corpus yields **476** questions across **17**
      texts; `ANCHOR_CORPUS_HASH` and `ANCHOR_DIGEST` in `test_original_run_regression.py` are
      re-pinned once from that fresh generate (not guessed), from the post-#73 merged base.
- [ ] The committed reference run's `answers.jsonl`, `scores.jsonl`, `summary.json`, and
      `questions.jsonl.manifest.json` are byte-for-byte unchanged.
- [ ] The committed `runs/original-2026-10-21/facct.json` and `facct.md` are byte-for-byte
      unchanged.
- [ ] `build_facct` on a run whose selected edition is absent from the catalogue fails **loudly
      and specifically** (names the missing edition(s); does not produce a misleading card and does
      not silently drop the row). The two committed-card rebuild tests
      (`test_committed_facct_card_matches_the_run`, `test_real_run_census_and_counterfactual`) are
      updated to assert this behaviour, each with a comment stating why.
- [ ] No "nine hadith" (or equivalent stale count) wording remains in `source.yaml`,
      `generate.py`, `catalogue.py`, `test_generate.py`, or any live doc/arch note.
- [ ] The copyright audit (`audit.py`, via `.codev/checks/test.sh`) and the full `pipelines` test
      suite pass; `apps/viewer` is unaffected.

## Constraints

**Baked Decisions (from issue #74 — fixed; do not relitigate):**

- Owner decision (Waleed, 2026-11-01): the Arabic hadith pool is **the six canonical books** —
  Sahih al-Bukhari, Sahih Muslim, Sunan Abi Dawud, Jami\` at-Tirmidhi, Sunan an-Nasa'i, Sunan
  Ibn Majah. **Muwatta Malik, Musnad Ahmad, and Sunan al-Darimi leave the catalogue.**
- `texts/raw/Sunni Islam/source.yaml`: remove the three targets; delete the three payloads
  (`malik.json`, `ahmed.json`, `darimi.json`); update the header comment ("nine" → "six").
- Pool 20 → 17 texts; reference-params `generate` 560 → 476 questions. Re-pin **both**
  `ANCHOR_CORPUS_HASH` and `ANCHOR_DIGEST` per the documented procedure; update the catalogue
  membership pin in `test_catalogue.py` (target count and pool set).
- The committed reference run asked questions on all nine collections. **Committed run evidence is
  never edited.** Verify the FAccT card / `edition_index` / analysis-layer behaviour when a run's
  selected edition is no longer in the catalogue (`selected_corpus_hash`, the as-of-run census —
  see #56) and make that path **fail loudly or degrade honestly**, with the committed card's
  byte-pin either still holding or re-pinned with the reason stated in the test comment.
- Docs: `texts/README.md`, `CODE_WALKTHROUGH.md` / arch notes that say "nine hadith collections."
- **Not in scope**: English hadith (AhmedBaset/hadith-json; separate decision); `items/for-test/`
  (Jonathan's FAccT run set is Qur'an-only; unaffected).
- **Ordering**: land **after** PR #73 (Saheeh International) merges — both move
  `ANCHOR_CORPUS_HASH`; branch from the merged main and re-pin once.

**Other constraints:**

- The three dropped payloads are public-domain and currently committed; removal is a `git rm` of
  tracked files, not merely a gitignore change.
- Anchor re-pinning must come from a real `generate`, never a guessed hash.
- Never re-run `collect` / `score` / `generate` over the committed run evidence; any
  regeneration writes to tmp paths only (per lessons-critical).

## Assumptions

- **PR #73 has merged** (main at `493f700`, 27 catalogue targets): it moved `ANCHOR_CORPUS_HASH`
  to `de2c8679cbde3cf5` with `ANCHOR_DIGEST` unchanged at `93b71460742a8ecd` (Saheeh International
  is an English Qur'an — `language == en`, `canonical_language == ar` — so it is outside the
  original-language pool and did not change the question set or the pool count). Implementation
  merges origin/main into this branch and re-pins both anchors once from that base. (Architect
  confirmation, 2026-11-01.)
- Removing three in-pool hadith texts changes both the corpus hash and the question-set digest, so
  **both** anchors move with this change (unlike #73, which moved only the corpus hash).
- The committed manifest's `selected_texts` entries carry only `{work, version, language}` (no
  tradition / document_type / license) — verified at spec time — so a historic card cannot be
  rebuilt in place from the manifest alone once the catalogue targets and payloads are gone.
- `_family` keys hadith grouping on `document_type`, not a count, so pool/negative-sampling
  behaviour needs no logic change — only comment corrections.

## Solution Approaches

The only genuinely open design question is the FAccT-card behaviour when a historic run selected
an edition the catalogue no longer contains. Everything else (edit `source.yaml`, `git rm` the
payloads, re-pin anchors, update the catalogue membership test, fix comments) is mechanical and
fixed by the baked decisions.

### Approach 1: Fail loudly, freeze the historic card (RECOMMENDED)

Make `build_facct` / `_census` fail with a **specific, actionable** error when a run's selected
edition is absent from the catalogue — naming the missing edition(s) and explaining that the
historic card cannot be rebuilt because its source editions were removed (reference #74). Leave
the committed `facct.json` / `facct.md` byte-for-byte unchanged as the honest frozen record of
what the run reported. Re-express the two rebuild tests to assert the loud failure (and preserve
the committed card bytes), each with a comment stating the reason.

- **Trade-offs**: Honest — you genuinely cannot reconstruct a card whose source editions' content
  is gone (`selected_corpus_hash` is unrecomputable and the census's per-text metadata is
  unrecoverable from the manifest). Respects "committed run evidence is never edited": the card
  files are untouched (byte-pin holds). Smallest blast radius. The cost is that the historic run's
  card becomes a one-way, un-rebuildable artifact, and the arch note's "rebuild the committed
  FAccT card on a sanctioned update" guidance must gain a carve-out for removals.
- **Risk/complexity**: Low. One focused error path + two test updates. No new data carried, no
  frozen evidence edited.

### Approach 2: Degrade honestly, keep the card rebuildable and byte-identical

Teach `_census` to treat a removed selected edition like `post_run_filter` treats an added one —
reconstruct the missing per-text row from a historic source so the census stays byte-identical —
and special-case `selected_corpus_hash` so it does not move when a selected payload is gone.

- **Trade-offs**: Keeps the card rebuildable, but the manifest carries no tradition / license /
  document_type for the removed texts, so the metadata must be snapshotted out-of-band (a frozen
  fixture or the test), and the raw content is deleted so `selected_corpus_hash` can only be
  "preserved" by special-casing — i.e. the card would assert a corpus hash it can no longer derive
  from the corpus. This fabricates continuity for a corpus that no longer exists and conflicts
  with the baked decision to delete the payloads.
- **Risk/complexity**: High. New out-of-band state, a dishonest hash carve-out, larger surface,
  and it fights the issue's explicit "delete the three payloads."

**Recommendation: Approach 1.** It is the honest behaviour, keeps committed evidence untouched,
and has the smallest footprint. (Surfaced to the architect as an FYI, since it makes the historic
card un-rebuildable — a mild one-way door — but it is fully authorized by the issue's "fail loudly
or degrade honestly" + "committed run evidence is never edited.")

## Open Questions

- **Important** — Confirm Approach 1 (fail-loudly + freeze) over Approach 2 (degrade). Recommended
  and authorized by the issue framing; raised to the architect as an FYI, not a blocker.
- **Nice-to-know** — Whether the arch note instructing "rebuild the committed FAccT card on a
  sanctioned corpus update" should gain an explicit removal carve-out now, or be deferred to a
  governance-docs pass. (Leaning: add a one-line carve-out with this change.)

## Test Scenarios

- **Catalogue membership** — `discover_catalogue` on the trimmed corpus yields 23 targets and a
  17-text pool with exactly the six canonical hadith books (no Malik / Ahmad / Darimi).
  (`test_catalogue.py`, updated.)
- **Generation invariance / re-pin** — a reference-params `generate` over the post-#73, post-trim
  corpus reproduces the newly pinned `ANCHOR_CORPUS_HASH` / `ANCHOR_DIGEST` and 476 questions;
  the committed manifest's own `question_set_digest` pin (`de65959a99dea9b3`) is unchanged.
  (`test_original_run_regression.py`.)
- **Scoring invariance (unchanged)** — re-scoring the committed `answers.jsonl` still reproduces
  the committed `scores.jsonl` byte-for-byte (removal touches neither).
- **FAccT loud failure** — `build_facct(runs/original-2026-10-21)` raises a `FacctError` naming
  the removed edition(s); the committed `facct.json` / `facct.md` are unchanged on disk.
- **FAccT addition still byte-identical** — `post_run_filter` still drops a later-added target so
  an unrelated addition would not change a historic card (regression guard stays green).
- **Audit / suite** — the copyright audit and the full `pipelines` suite pass on the trimmed
  corpus; `apps/viewer` tests unaffected.
- **No stale wording** — a grep for "nine hadith" (and the stale pool/target counts) over code and
  live docs returns nothing.

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Landing before #73 merges → anchors re-pinned from the wrong base, double churn | Medium | Medium | Gate implementation on #73 merge; branch from merged main; re-pin once (per issue ordering + architect note). |
| Guessing an anchor hash instead of computing it | Low | High | Re-pin strictly from a real `generate`; never hand-write a hash. |
| Accidentally editing committed run evidence (facct/answers/scores) | Low | High | Treat `runs/original-2026-10-21/**` as read-only; assert byte-equality in tests; regenerate only to tmp. |
| A second `build_facct` consumer (beyond the two known tests) breaks unseen | Low | Medium | Re-grep `build_facct` / `facct` call sites during implementation; the loud error is self-describing. |
| `git rm` of the payloads leaves a dangling gitignore or stale reference | Low | Low | Verify `git ls-files` shows the payloads gone and no source.yaml target points at them. |
| Stale "nine" wording missed in some doc/arch note | Medium | Low | Re-grep across code + docs for "nine" / stale counts before finishing. |

## References

- Issue #74 — Corpus: trim the Arabic hadith pool to the six books (Kutub al-Sittah).
- PR #73 — Saheeh International English Qur'an (QUL); merges first, moves `ANCHOR_CORPUS_HASH`.
- Spec 26 — original-language-only question set (the `language == canonical_language` pool rule).
- Spec 32 / #56 — FAccT benchmark card; as-of-run census and `post_run_filter`.
- `codev/resources/arch-critical.md` — texts/catalogue, pipeline, run-evidence, test-gate facts.
- `codev/resources/lessons-critical.md` — "never re-run collect/score/generate over committed
  evidence"; "derive formats from real data"; sanctioned-rebaseline discipline.
