# Review phase — PR #62 architect integration review (round 2) rebuttals

Architect verified hands-on (58 movers re-derived, SIMs frozen, splices verbatim, 642+187 green,
audit) and relayed BOTH PR consults as REQUEST_CHANGES/HIGH with real findings. Directive: fold all
six, do not merge. All folded; one item (1) surfaced a committed-evidence rebaseline, approved by the
architect before I touched it.

## Item 1 (BLOCKING, codex) — segmentation over-credit — FIXED + witness RE-VERIFIED
`_fold_containment_pattern` allowed optional `\s*` between EVERY adjacent Arabic letter and dropped
every letter-flanked reference space, so a multiword reference could match a distinct single word
(منشر → "من شر", "ك تب" → كتب). FIX: whitespace flexibility is now CONFINED to the long-ā join
boundary — a gap is optional only when it abuts an optional-long-ā (`AA`) atom (the attested
vocative/dagger-join); elsewhere a reference space stays REQUIRED and adjacent letters stay
CONTIGUOUS. Added codex's negative tests (`test_fold_contains_rejects_distinct_segmentations`).

**RE-VERIFICATION (as directed — "surface if any drop"):** dry-run re-scored every committed answer.
The 3 `scores.jsonl` runs (tutorial/original/first-run): **1514 text cells, 0 changed.** exp-ar:
**2 cells dropped** — `retrieve_quote-317f7f727f3c` (Q27:59) sonnet+sol. Root-caused and surfaced: the
sole blocker is the `ءَآ↔آ` hamza-alef residual (#60), which the OLD over-permissive `\s*` was
accidentally bridging via the plene form — a real over-credit (right verse, wrong mechanism — the
same bridge that credits distinct segmentations). Proof: under the tightened predicate, patching ONLY
`آ→ءَآ` in the answer restores the credit. **Architect APPROVED the rebaseline.** Done: exp-ar
re-scored (2 cells correct→incorrect, en unchanged, answers-normalized byte-identical, SIM
submetrics unchanged); exp-ar 96.4%→92.9%, en stays 96.4%, one residual cross-condition flip
(Q27:59) now visible = #60, not retrieval. The 2 cells added to `HAMZA_ALEF_RESIDUAL` (en stays
credited — it wrote «ءَآللَّهُ»); `ORTHO_MOVERS` total 58→56; the exp witness pins the new 26/28 + the
single-flip identity.

## Item 2 (BLOCKING, claude) — false narrative in committed evidence — FIXED
Confirmed a SECOND residual class: verse-number sign glued to the final word (U+06DD + Arabic-Indic
digits) leaves tutorial `haiku/retrieve_quote-e2d74279aaf0` (4:176) verbatim-correct but uncredited.
With it counted, haiku-off's three Qur'an misses are ALL scorer residuals (2 hamza-alef + 1
verse-number), **0 genuine** — so the entire haiku→haiku-search Qur'an gap is artifactual. Verified by
stripping the trailing verse-number, which restores the credit. FIXED: tutorial README prose
corrected (the "only 1 genuine miss"/"~2–3 pts" claims removed — the whole gap is artifactual); the
cell pinned in `VERSE_NUMBER_RESIDUAL` with a test that also asserts the digit-strip restores credit;
`tutorialRun.test.ts` comment caveated (the accuracy ordering is surfaced, NOT a causal retrieval
claim). The digit-strip CODE fix is deferred to #60 as directed.

## Item 3 (claude) — cite_passage call site — FIXED (reverted)
`_single_citation_correct` reverted to `bounded_contains` (boundary-aware citation EQUALITY, not the
verse-length fold). No-op on committed evidence (0 Arabic citations; committed-run regression guards
stay green). Candid comment kept, pointed at #39 (design a citation-appropriate equivalence there).

## Item 4 (codex) — public-API clarity — FIXED
`fold_aware_contains` docstring states it is THE public text-retrieval containment contract;
`bounded_contains` docstring marked the legacy/equality FLOOR — used directly only for citation
equality and the `normalize`-only edition identity checks, and as the superset floor — with an
explicit "new text-retrieval analyses must use `fold_aware_contains` or they silently score the
obsolete pre-#52 semantics" warning.

## Item 5 (confirm) — stale Phase-1 docstring — CONFIRMED
The `test_arabic_orthography_fold.py` "not yet wired" docstring fix landed in `03a9443` and is in this
PR (now states the fold IS wired into the 5… now 4 call-sites as of Phase 2).

## Item 6 (notes) — #60 watch items + cross-pointer — DONE
Added to #60 (not fixed here): the U+06DD digit-strip code fix; `failureKind.ts` token arithmetic
under whitespace-flexed credits. Added the `score.py fold_arabic_orthography` → `probes.fold_arabic_letters`
cross-pointer (the probe fold is a looser, probe-only variant — kept deliberately distinct).

## Net
Full gate green after all fixes: pipelines **643 pass / 2 skip**, viewer vitest pass, audit OK. Only
committed-evidence change is the architect-approved exp-ar rebaseline (2 cells); all SIM projections
and the 3 other runs byte-stable. Advancing to re-report; HOLD at the pr gate — architect runs
`porch approve`, I merge after.
