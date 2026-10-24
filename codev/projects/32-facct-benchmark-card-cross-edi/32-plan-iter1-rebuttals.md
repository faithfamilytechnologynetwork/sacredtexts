# Plan 32 — Rebuttal to plan iteration-1 reviews

Both reviewers returned **REQUEST_CHANGES / HIGH**, both verified against the real tree, and their
issues converge. **Every point accepted; none disputed.** All are plan-text fixes — the approach,
decomposition (4 phases), and ordering are sound and unchanged. I re-verified the two code facts the
fixes depend on (below). Revised plan committed as `[Spec 32] Plan with multi-agent review`.

## My verification before accepting

- `audit.py` lines 130/132 filter `f.suffix in (".json", ".jsonl")` — `.md` is genuinely skipped. →
  confirms the audit-coverage gap (codex #3, claude #3).
- `score.py` has `_contains` (line 193) **and** `_bounded_equal` (line 252); the `contains_reference`
  grader uses `_bounded_equal` (line 305). So the contract containment predicate to reuse is the
  `contains_reference` one (`_bounded_equal` over `normalize`), not a fresh `in` check. `generate.py`
  has `corpus_hash` (sha256 `[:16]`, line 465) and `question_set_digest` (`[:16]`, line 453). →
  confirms claude #1/#2 and codex #2/#4, and pins the exact helpers.

## Converged issues (both reviewers)

1. **Containment not pinned to the scoring contract** (codex #2, claude #1). *Accepted.* Phase 2 now
   promotes `score`'s `contains_reference` predicate (`_bounded_equal` over the script-aware
   `normalize`) to public and reuses it verbatim; `facct.py` defines no matcher of its own. Added a
   deliverable, an acceptance criterion, a contract-reuse test, and a Risks row.
2. **Frozen manifest fields undefined** (codex #4, claude #2). *Accepted.* Pinned in Phase 1:
   `corpus_hash = generate.corpus_hash(docs)` over all indexed same-canonical-language docs;
   `digest = sha256 hexdigest()[:16]` of the JSONL bytes; deterministic row order
   (`(work, citation, language)`); `excluded_restricted` sorted + de-duped. Added a determinism +
   hash-sensitivity acceptance criterion and test.
3. **Audit does not cover `facct.md`** (codex #3, claude #3). *Accepted.* Phase 4 now extends
   `audit.py`'s suffix set to `.md` with a `test_audit.py` test that injected restricted Markdown
   fails, and constrains the card to citations + numbers (no passage bodies). Added deliverable,
   criterion, Risks row, and a Documentation note.

## Codex-only

4. **Output safety / atomic both-files** (codex #1, overlaps claude #5). *Accepted.* Phase 3's end
   state is `sacredbench facct <run_dir>` writing **both** files into the run dir by default; any
   override is validated to resolve within the run dir; both are rendered/validated before either is
   written (both-or-neither). Added criteria + an output-safety test.
5. **Phase-4 integrity via byte digests, not `git status`** (codex #5). *Accepted.* Replaced the
   `git status` check with recorded sha256 of `answers.jsonl` / `scores.jsonl` / `summary.json`
   compared before and after generation.

## Claude-only

6. **Phase 1 text source** (claude #4). *Accepted.* Phase 1 now states the index reads `texts/raw/**`
   via `convert.convert_target` (as `audit.restricted_text_fingerprints` does), not the gitignored
   `texts/standardized/`.
7. **Markdown opt-in vs required** (claude #5). *Accepted.* Same fix as codex #1 — both files by
   default.
8. **Agreement table undecided + no real-run drift guard** (claude #6). *Accepted.* **Decision:**
   exclude the three-edition agreement table from this PR (recorded in the Executive Summary) to keep
   the one-linear-recipe docs bar. Added a committed-card drift guard in
   `test_original_run_regression.py` tying `facct.json` to `summary.json`, so a future sanctioned
   rebaseline cannot leave the card stale.

## Net

No open disagreements. The containment rule is now the contract's own predicate, the export schema is
fully pinned for #21, the committed `.md` card is genuinely inside the copyright gate, the command
writes both files atomically within the run dir, Phase-4 integrity is checked by byte digests, and the
agreement table is explicitly out of scope.
