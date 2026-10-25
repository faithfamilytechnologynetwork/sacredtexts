### Iteration 1 Reviews
- codex: REQUEST_CHANGES — Field validation and catalogue updates are solid, but the metadata channel is not valid for all real documents and can silently overwrite cross-source conflicts.
- claude: REQUEST_CHANGES — Clean, well-tested catalogue work that hits every stated Phase-1 criterion, but the `(work, version, language)` metadata channel cannot key the encyclicals corpus — `convert_encyclicals` re-stamps work/version, so the fail-closed lookup will raise on the default generate path in Phase 2.

### Builder Response to Iteration 1
# Spec 26 Phase 1 — Rebuttal to per-phase consult (codex + claude, both REQUEST_CHANGES)

Both reviewers converged on the same two issues and both are correct. All points accepted and fixed in
`[Spec 26][Phase: implement] fix: path-based metadata channel + cross-source conflict detection`. An
architect decision that landed during the review (drop `--include-translations` entirely) resolved the
two downstream questions the reviewers raised; spec/plan updated in a companion commit.

## Blocking 1 (both) — the metadata channel cannot key the encyclicals — ACCEPTED
`convert_encyclicals` emits one `Document` per file with `work=<title>`,
`version="Vatican English text (pope, date)"` — not the target's nominal `("Papal Encyclicals",
"Vatican English", "en")`. So a `(work, version, language)`-keyed lookup resolves **zero** encyclical
documents, and (claude's sharpening) this bites the **default** run, not just a translations path: the
equality rule must read `canonical_language` to *exclude* them, so the lookup happens before exclusion.

**Fix:** replaced `metadata_for_text` (tuple lookup) with **`metadata_for_standardized_path(path,
sources)`** — path-based recovery that mirrors `license_for_standardized_path` (deepest-containing
target `standardized_dir` wins). Every encyclical file lives under the one encyclicals target directory,
so it resolves to that target's `TextMeta` regardless of the document's re-stamped `work`/`version`.
This is now the channel generation uses (fail-closed on `None`). New test
`test_metadata_for_standardized_path_resolves_by_path` writes a doc with `work="Humanae Vitae"` under the
encyclicals target dir and asserts it resolves to the encyclicals metadata (`canonical_language="la"`) —
the exact re-stamp case, plus `None` for a stray path.

## Blocking 2 (both) — `text_metadata()` silently last-wins across source files — ACCEPTED
`load_source`'s slug-agreement runs per `source.yaml`; `discover_catalogue` never cross-checks, so two
files declaring the same tuple with different metadata resolved by glob order. **Fix:** `text_metadata()`
now raises `CatalogueError` ("ambiguous metadata") on a conflicting duplicate tuple across sources, and
its docstring no longer claims slug-agreement covers this. New test
`test_text_metadata_conflicting_tuple_across_sources_fails` (two source files, same tuple, different
`requested_as`). Its role is also corrected: it is a **nominal view**, not the generation channel (the
path-based resolver is).

## Downstream questions the reviewers raised → architect decision (2026-10-20)
Both flagged that this needed an architect call before Phase 2. I raised it; the architect decided to
**drop `--include-translations` entirely** (YAGNI — canonical-language-only, full stop; excluded
targets reported in the manifest with a reason). That **moots** both:
- **Encyclicals as ~201 un-fillable one-paragraph "texts"** (claude): nothing can pull them into a
  quota run — they are excluded by the equality rule (`en != la`), full stop.
- **Talmud en/he identical `requested_as`** (claude minor): Talmud English is never generated, so the
  prompts are never indistinguishable; the identical lists stay as #27 lists them (true data about how
  people ask). Spec/plan updated to remove the flag and record exclusions in the manifest instead.

## Minors — ACCEPTED
- **slug-agreement message named all three fields regardless of which differed** (claude): now computes
  and names only the differing field(s); `test_slug_agreement_covers_canonical_language` asserts the
  narrowed `"disagree on canonical_language"`.
- **`test_first_run_question_set_digest_regenerates` is broken by *this* phase, not Phase 2** (claude):
  removing the two LDS-KJV targets orphaned a `texts/standardized/...` dir that is in the committed
  first-run manifest's `inputs`, so `filter_standardized_paths` now fail-closes on regenerate (green
  only because `texts/standardized/` is absent locally). The Phase-2 retirement rationale in the plan
  now names the Phase-1 target removal as the first cause (alongside the generator-interface change) and
  flags that it bites at Phase 6 when the corpus is rebuilt. The **re-score** half stays.
- **"papal encyclicals" lowercase renders awkwardly** (claude): moot — encyclicals are excluded.

## Net
Both blocking findings fixed with the single correct change (path-based recovery, consistent with how
`license` already travels), plus global conflict detection. The architect's flag-drop simplified the
selection contract and removed the one genuinely open design question. Full pipeline suite 336 passed.


### Iteration 2 Reviews
- codex: COMMENT — Phase 1 implementation is functionally complete; only documentation and plan wording remain inconsistent with the corrected path-based metadata design.
- claude: REQUEST_CHANGES — Both iteration-1 blockers are genuinely fixed with correct, well-tested code; the catalogue.py module docstring and four spots in the plan (incl. an unsatisfiable acceptance criterion) still assert the superseded tuple-keyed channel.

### Builder Response to Iteration 2
# Spec 26 Phase 1 — Rebuttal to iter-2 consult (codex COMMENT / claude REQUEST_CHANGES)

Both reviewers **confirmed the two iter-1 blocking fixes are correct** (path-based
`metadata_for_standardized_path` for the encyclicals re-stamp; `text_metadata()` cross-source
conflict detection). The iter-2 asks were stale documentation and test-strength, not code defects. All
actionable points accepted and applied in `[Spec 26][Phase: implement] docs/tests: point metadata docs
at the path channel; pin pool membership`.

## Accepted and fixed

- **catalogue.py module docstring still described the old `text_metadata` channel** (both reviewers).
  Rewritten: the two fields reach generation via `metadata_for_standardized_path` (by path, like
  `license`, because a tuple key can't resolve re-stamping converters); `text_metadata` is now described
  as the separate nominal conflict-detecting view. The standardized-path-convention paragraph now covers
  metadata recovery as well as license.
- **Plan Phase 1 objective / deliverable / acceptance / test-plan still asserted `text_metadata()` is
  fail-closed on an unmapped tuple** (both). Rewritten to the shipped design: `metadata_for_standardized_path`
  is the path-based, `None`-returning channel; `text_metadata()` raises only on a cross-source conflict.
- **`text_metadata()` has no production caller yet, so its guard is inert** (claude). Noted in the plan
  as a Phase-2 obligation: generation calls `text_metadata(sources)` once at the start (its sole
  production caller) and asserts per-group path-resolved agreement, so the guard fires on the real
  catalogue. Also added a line to the real-catalogue test that invokes `text_metadata(sources)` now, so
  the guard is exercised against the committed data in Phase 1.
- **`test_real_catalogue_default_pool_is_seventeen` pinned the count, not the membership** (claude).
  Now asserts the exact 17-member set of `text_key`s — "the one test standing between a typo and a
  silently different benchmark." A `canonical_language` typo (e.g. `ara`) that drops a text now fails
  loudly, which also mitigates the no-vocabulary-check soft spot.
- **`requested_as` elements not stripped** (claude). Now stripped on store, so a padded `"  KJV "` can't
  render into a prompt verbatim or skew Phase 2's seeded uniform choice.

## Accepted as noted, no code change

- **Equal-depth-disagreement raise in `metadata_for_standardized_path` is unreachable via
  `discover_catalogue`** (claude): correct — distinct sources yield distinct `source_id`s → distinct
  `standardized_dir`s, so two different dirs can't contain the same path. Kept as defence-in-depth (it
  fires for hand-built `Source` objects); not claimed as coverage.
- **No vocabulary allowlist for `canonical_language`** (claude, explicitly not a change request): there
  is no canonical language-code list in the codebase to validate against, and the exact-membership pool
  test now catches the real-data failure mode. Left as-is.
- **Lost real-data `convert_target`+`assemble` multi-shard coverage** (claude): the removed
  `test_real_lds_kjv_ot_nt_merge` was the only real multi-target-merge anchor; the merge/roundtrip
  *logic* stays covered by the synthetic export tests (verified non-vacuous). Re-adding a real anchor on
  the Talmud Aramaic target (many docs, one tuple) is a reasonable future improvement but is out of
  Phase 1's scope — flagged for the review phase.

## Net
No code defects were found in iter-2; the implementation shipped in iter-1 stands. The changes here are
documentation accuracy (catalogue docstring + plan) and two cheap test-strength improvements (exact
pool membership, invoking the conflict guard on real data), plus the Phase-2 obligation to give
`text_metadata()` a production caller. Full pipeline suite 336 passed.


### IMPORTANT: Stateful Review Context
This is NOT the first review iteration. Previous reviewers raised concerns and the builder has responded.
Before re-raising a previous concern:
1. Check if the builder has already addressed it in code
2. If the builder disputes a concern with evidence, verify the claim against actual project files before insisting
3. Do not re-raise concerns that have been explained as false positives with valid justification
4. Check package.json and config files for version numbers before flagging missing configuration
