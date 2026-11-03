# bugfix-117 — native-language refusal cues

## Investigate (2026-11-03)

**Reproduced.** Read-only sweep of `runs/rerun-2026-11-03` (main checkout; re-scoring the committed
answers with the code at 7567318 reproduces the committed `scores.jsonl` exactly — 0 mismatches).
Using the issue's seed cues at an 80-char window: 568 text-retrieval cells + 77 cite_passage cells
currently `incorrect` open with a native decline (he 258, pa 282, hi 10, ar 9, el 9). The counts are
a little above the issue's 522 because my seed list was slightly broader.

**Root cause.** `outcomes._DECLINE_CUES_RAW` is English-only (plus one stray `क्षमा करें`).
`leading_decline` / `first_sentence_decline` therefore never fire on a Hebrew/Gurmukhi/Devanagari/
Arabic/Greek decline. `classify_refusal` returns False, so `_with_outcome` stamps `incorrect`.
The module docstring admits this.

**Seeds that must NOT be adopted.** I counted word-bounded hits in `texts/standardized/` (190k
non-English entries):
- `לא אוכל` ×25 (Talmud; also לֹא אוּכַל in the Hebrew Bible)
- `מצטער` ×35 (Talmudic "is distressed")
- `צר לי` ×2
- `לא יכילנא` ×4
- `איני יכולה` ×4
- `عذرا` ×11 (Qur'an 18:76, 77:6)
- `آسف`→`اسف` ×4. Unbounded, it also matches inside `أَسْفَارًا` in a delivered verse.
- `لا أستطيع` ×18 (hadith)
- `لا أملك` ×17 (Qur'an 7:188 …)

Bare apologies also open confident non-existence claims ("عذرًا، لا يوجد آية رقم 12…", "ਮਾਫ਼ ਕਰਨਾ,
ਪਰ 315:44 … ਮੌਜੂਦ ਨਹੀਂ"). Existing doctrine scores those as wrong answers, not declines. So: no
bare apologies. Instead I use apology + first person ("ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ/ਮੈਂ/ਮੇਰੇ ਕੋਲ"). That is the
SOV analogue of the English `i'm sorry, but i don't/can't`, where the negation comes last.
Pali (`na jānāmi` is a canonical phrase): the rerun has no native-script Pali declines, so no
Pali cues.

**Matching must be word-bounded** (`(?<!\S)cue(?!\S)` on the normalized text). Substring matching
lets `اسف` fire inside `اسفارا`. Bounding also keeps `שאינני יכול` ("since I can't … here is the
text", gemma, which delivers the text) out.

**SOV declines need the first-sentence path.** In Punjabi/Hindi the inability verb comes at the end
of the sentence, often past the 60-char window: 195 of the moved cells match only via
`first_sentence_decline`. The issue's 80-char sweep would have missed them.

**Simulated fix** (monkeypatched, read-only): 638 text-retrieval + 88 cite_passage cells move. Every
one goes `incorrect → refused`; none go `correct →` anything, and none go `refused →` anything.
Moves by language: pa 354, he 339, sa 20, grc 9, ar 3, arc 1. The highest token_f1 among moved
cells is 0.48. The top-overlap movers decline and then give a substitute: another edition's text
("the standard Vilna text is roughly: …", Textus Receptus instead of Scrivener). The English
Spec-48 assertion frames (`_ASSERT_INTRO`) don't parse Hebrew/Greek framing, so these strand as
`refused`. That is the spec's "favour refused when unsure" fallback. I'm flagging it as the known
boundary.

**Residual corpus collisions accepted.** `איני יכול` (Bava Batra 20b:15, "איני יכול לישן") and
`אין בידי` (Yevamot 80b:9) each occur once in the Talmud. Together they carry 67 genuine declines
in the rerun (`איני יכול` 51, `אין בידי` 16). A collision needs the model to deliver a *non-matching*
copy of exactly those words inside the leading window/first sentence. I'll document it rather than
drop the cues.

**Scope.** One file of logic (`outcomes.py`: a native cue tuple + bounded matcher wired into the two
existing predicates), a regression test, and doc updates. Well under 300 LOC.

Merged origin/main twice per architect (#85 b8b63bf, #111 1d9812c) before any code change.

## Fix (2026-11-03)

- `outcomes.py`: new `_NATIVE_DECLINE_CUES_RAW` (Hebrew, Gurmukhi, Devanagari, Arabic, modern
  Greek), compiled once into a whole-word regex (`_native_cue_re`). It is wired into the existing
  `leading_decline` (60-char window) and `_has_cue` (opening sentence). The English list and its
  substring matching are unchanged; `क्षमा करें` stays where it was. Same Spec-48 gate.
  Docstring caveat replaced; arch.md refusal paragraph updated.
- Final pre/post oracle (native cues off vs on, real code). Every move is `incorrect → refused`;
  only the `outcome` field changes; nothing moves `correct →`:
  - rerun-2026-11-03 (local, uncommitted): 724 (636 text-retrieval + 88 cite_passage)
  - committed 2026-11-02 run (`runs/*/base`): 791
  - archive: 1 (original-2026-10-21 haiku complete_unit — "not sure … can't confirm the
    continuation. A reasonable guess is: «…»"; the English rule refuses the English equivalent too)
- No rebaseline. The 792 committed movers are registered in `tests/testdata/native_decline_movers.tsv`
  (session fixture `native_decline_movers` in conftest). The guards that re-derive committed
  outcomes now expect those cells to read `refused`: #111's cite oracle, the original-run byte
  re-score, and the Spec-48 refused-set gate.
- `test_native_refusal_cues.py`: 15 cases fail on the pre-fix code; 11 narrowness guards pass both
  ways. The corpus guard (pins the two Talmud collisions) and the rerun oracle run only where
  `texts/standardized` / the rerun exist. Against the main checkout all 29 pass (corpus guard ~37s).
- Known boundary for the architect: the Spec-48 assertion frames are English, so a native-language
  decline followed by a reconstruction ("the standard Vilna text is roughly: …") strands as
  `refused`. Highest token_f1 among the rerun movers is 0.48.
- Side note (not mine): in the main checkout, `test_regenerating_original_run_reproduces_digest`
  fails because the local `texts/standardized/Sunni Islam/musnad-ahmad…` dir predates #74's trim.

## PR #123 + CMAP (2026-11-03)

- Full suite on the tree merged with origin/main (00de30f): 1029 passed, 4 skipped. PR #123 opened.
- First consult attempt didn't review: no project was auto-detected ("Multiple projects found"). Re-ran with
  `--issue 117 --project-id bugfix-117`.
- Gemini: APPROVE, no issues.
- Codex: COMMENT. `first_sentence_decline` split only on `[.!?।\n]`, so a native terminator wasn't a
  sentence end. Probe over 65,878 cells (committed + archive + rerun), current splitter vs extended:
  - adding `׃ ؟ ۔` and U+037E changes zero outcomes on either path, so the registry is unchanged
  - adding ASCII `;` flips one committed English-path cell, refused→incorrect, so it stays out
  Adopted the native terminators. Guard test: a Masoretic verse ending in sof pasuq, then a native caveat
  past the window, is `incorrect` (was `refused` with the old splitter). Suite: 1030 passed, 4 skipped.
