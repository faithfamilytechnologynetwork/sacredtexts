# air-75 — Qur'an verify_source "no" donors → hadith (same script)

Issue #75 (AIR, strict). Make the Qur'an's `verify_source` "no" donor a hadith
matn (Arabic, same script, Islam tradition, different work) instead of a passage
from another tradition in another script.

## Findings
- Generator: `items/for-test/review/build_questions.py`. `add_verify_negatives`
  builds a donor pool from every tradition's `retrieve_quote` rows and, per
  `_donor_rank`, requires `donor.tradition != row.tradition`. Arabic has no
  same-script cross-tradition donor → Islam falls through to another script
  (confirmed in committed files: current Islam "no" donors are Sikhism/Judaism).
- Hadith raw is committed & public-domain: `texts/raw/Sunni Islam/hadith_from_sunnah.com_arabic_only/{bukhari,muslim,abudawud,tirmidhi,nasai,ibnmajah}.json`
  (`{hadiths:[{idInBook, arabic}]}`). `texts/standardized/` (what the issue names)
  is gitignored/not present → build from raw, mirroring `convert_hadith_sunnah`
  (citation `"{work} {idInBook}"`, version `"sunnah.com Arabic"`). All six books
  have thousands of ≥16-word entries, no HTML markup.
- Determinism constraint: Sikhism is built AFTER Islam and shares the one RNG, so
  I must keep the shared RNG consumption identical (sikhism byte-stable). Plan:
  keep the (now discarded) cross-tradition `rng.choice` for Islam to hold the
  shared stream, then override the donor with a hadith pick from an independent
  `Random(20261030)`. Islam's hadith donors depend only on that independent RNG +
  stable row order → regenerating Islam alone reproduces the full-run output.
- Test gate: `.codev/checks/test.sh` maps only apps/pipelines/runs/texts/configs
  to a lane — `items/**` runs ZERO tests. So the test lives in `pipelines/tests/`
  (triggers the pipelines lane + copyright audit).

## Plan
1. `_hadith_donors()` reads the six canonical books from raw (≥16 words).
2. `add_verify_negatives`: for Islam rows, override donor with a hadith pick;
   guard the empty-pool case so Islam can be rebuilt in isolation.
3. Regenerate only `islam/**/questions.jsonl`.
4. Update METHODOLOGY.md donor table.
5. Test in `pipelines/tests/`.

## Scope extension (architect, 2026-11-01)
- **#76 folded in**: `score.py parse_yes_no` was English-only → native-prompt verify answers
  (نعم/لا, כן/לא, ਹਾਂ/ਨਹੀਂ, हाँ/नहीं, Pali āma/na) scored refused. Added a per-language
  leading-token table (`_YES_NO_BY_LANG`), always-English + the cell's `source.language` script,
  plumbed `language` through `score_answer`. Kept the Spec 26/#23 hardening exactly (leading
  stance, same window, same label strip). **0 committed scores.jsonl cells move** — re-scored all
  4 committed runs (413 verify cells, langs ar/en/he) + full rebaseline suite green.
- **Owner-signed Islam prompt + familiarity changes** (within #75 PR): edition named "the Uthmani
  Qur'an" / "القرآن الكريم بالرسم العثماني" (no "QUL"; `edition_name` override, catalogue
  `version` metadata unchanged); new Arabic templates (verbatim); new 8-item familiarity list.
  Architect confirmed English complete_unit = shared template verb (edition-name only, option A).

## Regeneration (done, single Islam-only pass, seed 20261030)
- Regenerated ONLY `islam/**` (questions + passages); every other tradition asserted byte-stable
  (git diff touches only islam/** + methodology/review/build scripts + well_known + score.py).
- **Islam population is a near-total re-draw: 30→30 passages, only 2 in common.** Cause: the new
  familiarity list changes the pool exclusions, reshuffling the seeded draw (+ pre-existing stale
  files from script drift in 5883d6f/383323a). Deterministic (regen twice byte-identical),
  population∩familiarity empty, all pop verses ≥16 words. Architect accepted (nothing collected
  from old set; FAccT run collects Islam fresh). Documented in PR body + METHODOLOGY.
- build_review.py also stale → restored non-islam churn (buddhism/hinduism/christianity-modern
  passages.json + 05/06 READMEs) to committed; only 03-islam README + index count (7→8) kept.

## Tests
- `pipelines/tests/test_build_questions_islam_hadith.py` (#75): hadith donor pool = six books,
  Arabic ≥16 words; verify "no" rows quote a hadith (same tradition, diff work); determinism;
  no "QUL" in prompts; version metadata preserved.
- `pipelines/tests/test_score.py` (#76): per-script leading verdicts; per-script negation-evasion
  → None; native tokens only eligible for their language (Pali "na" never flips English);
  score_answer language plumbing. Full pipelines suite: 744 passed, 2 skipped.

## Round 2 (PR #78 review = REQUEST_CHANGES, 2026-11-01)
- **Parser**: native yes/no words must stand alone (then punctuation/symbol or end of window, read
  by Unicode category) — لا/לא/na are also the negation particle, so "لا أستطيع التحقق", "לא ניתן
  לאמת", "na jānāmi" stay refused. Symmetric for yes words. Danda after a nasal mark now ends the
  word (ਹਾਂ।, हाँ।). Greek ναι/όχι added. English matcher byte-identical to main. Re-scored all
  committed verify cells in memory (6 answer files, 441 cells: ar 294 / en 126 / he 21) → 0 move;
  the 14 Arabic-prompt cells (bare نعم/لا) parse exactly as the experiment's hand-mapping did.
- **Donors**: gate on the quoted passage's script (not tradition); per-row RNG
  (`HADITH_SEED|condition|sample|citation`); fail-fast restored on an empty non-Arabic pool;
  collections read from source.yaml (canonical six, Arabic), hadith JSON lazy-loaded.
- **Matn only** (owner-approved): after the LAST salawat. Surprise: sunnah.com spells the salawat
  vowelled (two mark orders) and line-broken — a plain substring missed 258 hadith and could cut at
  an earlier salawat. Now a letters-with-optional-marks regex. Pool 16,217 matns.
  Observation for owner (not acted on): 866 matns open with يَقُولُ (outside the approved
  قَالَ / أَنَّهُ قَالَ list).
- **No Qur'an wording** (owner-raised): skeleton 6-gram index + `fold_aware_contains` both
  directions. Load-bearing: with the filter off, 3/38 committed draws would carry Qur'an wording.
  Conservative: a matn containing a one-word ayah (55:1, 103:1) is skipped too.
- **Review page**: build_review renders Islam from build_questions' live EN/QURAN_AR/edition_name
  (other pages unchanged; non-Islam churn restored again). Drift test matches every committed
  Islam prompt against the page templates and asserts the committed page == current build.
- Regenerated Islam only: 38 verify-"no" rows changed vs round 1, nothing else. Full offline build:
  Islam SAME; Christianity/Judaism/Sikhism still don't reproduce (pre-existing, separate issue);
  no non-Islam question file differs from origin/main.
