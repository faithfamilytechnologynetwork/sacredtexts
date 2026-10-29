# lessons-learned.md — Engineering Wisdom (COLD / reference)

On-demand reference. The always-injected subset lives in `lessons-critical.md`.
Seeded from Spec 1 (Phase 1 benchmark).

## Scoring & evaluation

- **Refusal is decided by ASSERTION, not by the presence of a disclaimer (Spec 48).** The search-arm
  false-positive fix: a leading-decline text-retrieval answer that then *delivers* the passage in an
  unfoldable vocalization ("I couldn't find the exact edition… from memory it is: «script»") is an
  answer, not a refusal. The rule is **assertion-only** — a positive identity frame ("the <unit>
  is/reads/starts: <payload>" or "my best reconstruction … is: …") flips `refused → incorrect`; it is
  NOT conjunctive ("assertion AND no disclaimer" is falsified by an A cell that disclaims only the
  *segment number*). **Payload detection is script-NEUTRAL** — the target script is derived from the
  question's expected text via `unicodedata` (`_script_families`), NOT a Hebrew/Arabic/Greek allowlist:
  a canonical Latin tradition (KJV, LDS) or any new script (Gurmukhi, Cyrillic) is handled with zero
  core-code edits, honouring the "traditions are drop-in data" invariant (the allowlist was an
  invariant violation of the #50-Gurmukhi class, caught at PR review). A **non-Latin** payload is
  self-signalling (the script shift from English prose IS the "here is the text" marker); a
  **Latin/ASCII** payload has no shift, so it additionally requires an explicit introducer (colon /
  dash / quote) — else "the line is about…" / "the text is also available at…" is continuation prose,
  not a delivery (this over-fire bit two first-run cells before the introducer guard). Footguns
  banked: (1) a bare "from memory" substring appears in 147 genuinely-refused cells — match the
  positive frame, never a bare substring; (2) the negation + non-identity guard must span from the
  assertion frame THROUGH the payload's sentence (catches "…is not reliable; the adjacent text is:"
  BEFORE the payload and "the line is: <payload>, but a different line" AFTER it), while excluding an
  earlier leading-decline sentence; (3) INTRO requires the payload to IMMEDIATELY follow the frame (no
  intervening words), else a distant same-sentence script run ("…segment 7 is probably either X or
  the follow-up question, «script»") over-fires; (4) a global **refusal-to-deliver** disqualifier
  ("don't want to give/guess", "fabricat") keyed on refusal-of-delivery (not identity-disclaimers)
  stops the intro regex catching a genuine "I won't give a fabricated version" refusal. The
  discriminator for A-vs-B is a *vocalization/edition-only* disclaimer (A) vs a *passage-identity*
  disclaimer (B); a URL pointer is NOT a B marker. The A/B taxonomy deliberately diverges from the Jev
  rubric (#47 grader identity) — re-align in `sacredbench-jev-2`.

- **Refusal is an OUTCOME, not a wrong answer — don't let a strict headline conflate it
  with fabrication.** `correct = normalize(answer) == normalize(expected)` alone marks both an
  honest refusal and a confident fabrication 0 (first run: gpt-oss-20b mostly refuses, gemma/llama
  fabricate — same score, opposite behaviour). Spec 15 makes this a first-class `outcome` ∈
  correct/incorrect/refused: a declined cell is `refused` and **excluded from accuracy**
  (`accuracy = correct/(correct+incorrect)`), with **coverage** (how often it answered) reported
  beside every accuracy so a high-accuracy/low-coverage model isn't misread (opus 100%/cov66% vs
  opus-search 92%/cov80%). Detection is deterministic: a leading decline cue AND the reference not
  delivered — **unless** a positive delivery assertion fires past the decline (Spec 48 escape, so a
  from-memory / best-reconstruction delivery is scored, not refused). `token_f1` is a diagnostic,
  never the refusal detector.
- **Citation scoring must resist containment and false-negatives.** A single-candidate
  boundary-equality check (multi-candidate hedge → 0), with the extractor chosen by the
  ground-truth citation *shape*, and spans asserting the expected citation collapsed to
  one, took 5 consult rounds to get right. Containment is gameable; a numeric-only or
  greedy-paragraph extractor regresses correct answers.
- **Non-Latin fairness = delete marks, don't let punctuation split letters.** The
  original `normalize()` ran its `[^\w\s]`→space pass *before* handling diacritics, so
  Arabic harakat / Hebrew niqqud split each vocalised word into single letters
  (token_f1→0). Fix: strip combining marks + tatweel and fold alef-wasla→alef /
  maqaf→space *first*; derive the mark set from the **real** QUL data (annotation marks
  run well past basic harakat — U+06D6–U+06ED, superscript alef U+0670, …, many mid-word),
  not from a spec. Pin a Latin byte-for-byte invariance snapshot: an over-eager global
  delete (e.g. soft-hyphen) silently regresses committed English answers.
- **A containment headline rescues correct-but-wrapped retrieval — adopt it as a deliberate
  contract change, don't report it on the side.** A web-search model returns the exact quote *plus*
  a citation/URL/caveat; under "the quote and nothing else" it scored 0, so the strict headline
  looked flat/down while the model retrieved *more* correct scripture. Spec 15 adopts
  `correct = normalized OR contains_reference` for the text-retrieval tasks (containment confined to
  them — provenance anti-evasion intact), so the lift sits in the accuracy column. The reliable
  signal is **word-bounded containment of the normalised reference**, not `token_f1` (a short quote
  diluted by an English caveat lands ~0.45). Caveat: containment has **no anti-hedge rule** (unlike
  `cite_passage`/`identify_source`), so a verse that is the model's secondary hedge guess still
  counts correct — document the few such cells rather than special-casing them.
- **Real orthographic variance needed a fold — but in the containment predicate, not `normalize()`.**
  A correct āyah comes back in a *different* orthography (Uthmani↔Imla'i: dagger-alif ـٰ vs full
  alef, dotless ى vs dotted ي, standalone hamza ء, hamzat-wasl ٱ; plus pure Unicode-encoding
  variance U+06E1 vs U+0652, tanwīn codepoints) — present in search-OFF answers too, so *not* a tool
  artifact. Spec 15 first shipped the additive `contains_reference` submetric rather than touch
  `normalize()`. **Spec 52** then made the Uthmani↔Imla'i equivalence real by folding it inside the
  containment predicate (`fold_aware_contains`/`score_normalize`), NOT in `normalize()` — the long-ā
  alef is matched as OPTIONAL (`ا?`) because Imla'i writes it for the plene class (الكتاب) but omits
  it for the defective class (هذا/ذلك/الرحمن), so a context-free `dagger→alef` fold is provably wrong
  (it un-credits the defective class — the trap a competing #52 PR fell into). `normalize()` and every
  equality submetric stay byte-stable (Latin invariance, the generation ANCHOR digest, and the
  copyright audit untouched); only `contains_reference`/`correct`/`outcome` move, via a sanctioned
  oracle-witnessed rebaseline. Residual not folded: word-initial hamza-alef ءَا ↔ alef-madda آ
  (e.g. Q14:34), logged as a known limitation.
- **A scoring-contract change is a SANCTIONED, evidenced rebaseline — not a forbidden re-score.**
  The byte-for-byte re-score guards exist to catch an *accidental* disturbance of committed numbers;
  a deliberate contract change (containment headline, refused outcome) reshapes `scores.jsonl` on
  purpose. Do it **once, with a durable projection-SHA oracle + an exact pre-registered flip/refused
  set** (`test_contains_reference_rebaseline.py`) so a reviewer can see only the intended fields
  moved, preserve `panel`/`usage` verbatim (a keyless re-score nulling them is the scar), and surface
  the moved numbers to the architect before writing prose. Spec 15 did exactly two such rebaselines.

- **A marker baked into an identity string to force non-collision orphans the
  pre-existing bare rows.** Spec 8 encoded tool-use into `panel.model`
  (`[no-tools]`/`[web_search]`) to keep search-on/off distinct *without* a viewer change;
  but the marked key could then never collide with an earlier run's bare
  `claude-haiku-5-5`, so a stale row sat beside it forever. Promote the dimension to a
  real field (`panel.tools`) and have the consumer's standings key incorporate it
  (`(provider, model, tools)`) so same-model/same-tools rows dedupe and legacy bare rows
  become supersedable (Spec 11, Approach B — the shape Spec 8 deferred). Lesson: don't
  encode a new identity dimension as a string marker to dodge a consumer change; the
  marker you add to separate two arms also wrongly separates two runs that should merge.

## Live runs & providers

- **Reasoning models can return empty content** when `max_tokens` is exhausted by
  hidden reasoning (gpt-oss-20b at 1024 → empty; 4096 fixed it). Budget output tokens
  per model; the resumable `collect` then fills the stragglers without re-paying.
- **…and some cells stay empty even at an adequate `max_tokens`** (gpt-oss-20b via
  OpenRouter, Spec 26 run: ~28 empties on pass 1 at 4096; all but one recovered over
  retries, one Talmud-Aramaic `cite_passage` cell stayed empty across ~15 attempts). A
  persistent empty is a **missing cell** (stays pending — never a blank answer row), not a
  refusal; `score --questions --config` reports it as `miss N`. Don't loop `collect`
  indefinitely chasing it; document the residual and move on.
- **A smoke cost-extrapolation is ~2× low for reasoning-heavy models + retries** (Spec 26:
  $6.4 projected vs $12.9 actual — gpt-oss-20b emitted ~786K output tokens and needed 5
  retry passes). Gate with headroom, measure actuals against the provider credit balance
  (not per-token prices — an OpenRouter/unpriced run has none), and re-check the balance
  mid-run against a floor.
- **Keep a budgeted live smoke in the loop** — mocking the provider seam hides
  live-only failures; the smoke caught the empty-output mode before the full run.
- **Validate model slugs against the provider's own catalogue** (OpenRouter
  `/models`) before a run, rather than guessing.
- **A server-side tool (e.g. Anthropic `web_search`) must be part of panel identity and
  fail loud, not silent.** Bake the `tools` setting into the panel fingerprint and the
  emitted `panel.model` so on/off never collapse into one row; pin the tool version
  (`web_search_20250305`) and a `max_uses`; and treat any non-terminal `stop_reason`
  (`max_tokens`, `pause_turn`) as a hard error — a silent retry over a per-request-billed
  tool re-bills forever and the cell never converges. Such a run is **unpriced** (web
  search bills per request, uncaptured in in/out tokens) — never invent a cost.

## Evidence & copyright

- **Write run evidence to a fresh `runs/<id>/`; never re-run `collect`/`score`/
  `generate` over committed evidence** — `collect` resume-skips all cells (zero calls)
  and a keyless `score` overwrites the committed panel proof with nulls. (Promoted to
  `lessons-critical.md`.)
- **Origin is the enforceable copyright proxy in CI/clone** (restricted payloads are
  never committed, so there's nothing to content-match against); a content-fingerprint
  layer adds value only when the held-back payloads are present locally.
- **Make committed evidence self-describing** (a run `README.md`): a standalone reader
  must not misread `0%` as inability when it is refusal.
- **Model answers are committed as collected — no manual clearance/redaction pass.**
  Binding project policy (human ruling, Spec 8): a web-search model may incidentally echo
  copyrighted translation text in an answer; the maintainers treat that as fair use for
  academic benchmarking, and answers are never truncated or edited (the explorer shows
  them verbatim). The **automated `audit` gate remains the enforcement line** — it still
  blocks any committed artifact derived from a *restricted* source — but there is no human
  copyright-clearance step over collected answers. Don't reintroduce one.

## Process / SPIR

- **The strongest consults re-run the pipeline**, not just read it — codex caught the
  collect-into-committed and keyless-overwrite bugs by executing TUTORIAL verbatim;
  tests did not. Prefer a consult environment that can execute.
- **Disposition every consult finding explicitly** (Addressed / Rebutted / N/A),
  including non-blocking COMMENTs, so nothing is silently dropped between iterations.
- **Derive formats from the real reference data, not its docs** (BoM heading-as-verse,
  encyclical `paragraph: null`, Talmud daf offsets).
- **A sanctioned rebaseline's deliverable includes every HUMAN-READABLE figure in the run dir**, not
  only the machine artifacts (Spec 48: two full phase_2 consult rounds were spent on the run
  `README.md` publishing pre-fix numbers + an *inverted* caveat after `summary.json`/`scores.jsonl`
  moved). Enumerate and diff the README, `facct.{json,md}`, and any prose against the regenerated
  summary, and sync them in the **same commit** as the rebaseline. (Keep deliberately-pre-fix
  evidence like `jev_agreement.{json,md}` untouched, but add a "superseded — read counts from
  `summary.json`" pointer in the dir's README so the stale figure isn't cited as current.)
- **`porch rollback <id> plan` REPLAYS the old plan's iteration history — it does not reset the
  counter.** After a rollback, each `porch done` bumps the iteration (2→3…) and `porch next` returns
  "Fix issues from iteration N" with **no consult task**, because the old plan's iterN review files
  still exist on disk. Net trap: a freshly re-scoped plan can advance plan→implement **without a
  fresh multi-agent consult**. Mitigation (Spec 15): run a manual `consult` (codex+claude) over the
  re-scoped plan, commit its outputs + a rebuttal, and fold the findings before implementing — don't
  trust the replayed green. Also note porch's implement loop has a `max_iterations` safety ceiling
  (3) that **force-advances** a phase that keeps drawing REQUEST_CHANGES, recording the last rebuttal
  as the disposition — fine when the residual is a documented out-of-scope item, but verify that's
  what happened rather than assuming the phase passed cleanly.
- **Don't chain `porch next` and `porch done` across a phase boundary in one shell line.** A
  `porch next >/dev/null; porch done` run right after a phase closed consumed (and discarded) the
  NEXT phase's build task, then `porch done` marked that phase "build complete" on an empty
  implementation — porch jumped straight to its 2-way consult. Recoverable (implement and commit the
  real work before running the consult, so it reviews real code), but run porch one command at a
  time at a boundary and read each result (Spec 32).
- **An analysis/visualisation stage reuses the scoring contract's own predicates, never a second
  copy.** The FAccT card's edition counterfactual calls `score.bounded_contains` + `score.normalize`
  (the public `contains_reference` predicate, promoted from the private `_bounded_equal`) rather than
  a fresh `in` check — one containment definition, tested to agree with the scorer, so the card can't
  drift from the headline (Spec 32, echoing Spec 15's single-refusal-definition discipline).

## Map
- (This cold archive pairs with `lessons-critical.md`'s hot tier; demote hot entries
  here as that file approaches its cap.)
