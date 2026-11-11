# Spec 154 — iteration 1 rebuttal

Both reviewers returned REQUEST_CHANGES. I accepted every point and revised the spec in
commit 9a780cec. Below, each point is paired with what changed.

## codex

1. **Critical behaviour left unresolved** (rubric wording, NRSV, assignment, allocation,
   overlap, language grouping, batch size, topology).
   - **Changed.** The spec now has a **Defaults D1–D10** subsection. The success criteria
     are written against those defaults.
   - The rubric (D1) now defines the terms you flagged:
     - "stop early" is the #150 ten-word head;
     - "surrounding text" is any amount of text around an intact passage;
     - a conflicting yes/no follows the #23 leading stance.
   - Assignment is claim-based (D4), with batch size 25. Language grouping is D5, and
     topology is D10.
   - Two items stay as Critical open questions: NRSV, which is the architect's call
     against the issue's literal constraint, and the rubric's construct choice. Each has
     an explicit default, so planning isn't blocked.

2. **Statistical estimands wrong or ambiguous.**
   - **Changed.** There is a new **Estimands** subsection. "Precision of `correct`" is now
     separate from its complement, the false discovery rate. The `incorrect`-side measure
     is renamed **missed-credit rate**. Recall of correct and the 3×3 confusion matrix are
     reported only as population-weighted estimates.
   - `can't judge` and defect-flagged cells are excluded from every estimand and get
     their own rates.
   - The estimator is post-stratified with weights N_h/j_h, and nonresponse is handled
     under a stated missing-at-random-within-strata assumption. Strata with nothing
     judged are reported as uncovered mass and never extrapolated.
   - Intervals: Wilson for unweighted proportions; a stratified bootstrap with fixed seed
     and B = 2,000 for weighted ones. Overlap cells count once, as the mean of their
     raters, so clustering is handled.
   - Inter-rater agreement is Krippendorff's α (nominal), with `can't judge` treated as
     missing.

3. **Self-declared digest isn't a trust anchor.**
   - **Changed.** The trust chain is now: committed set → test-gated audit → digest pinned
     in the repo → digest recomputed at ingest. The test gate asserts that the pin equals
     the committed set's recomputed digest.
   - Ingest rejects any set that isn't pinned. A new test scenario covers the attack you
     describe: a tampered file that carries its own recomputed internal digest is
     rejected because it isn't pinned.
   - I didn't add a separate copyright re-validation in TypeScript. The pinned file is
     the audited file, so re-implementing the catalogue in a second language would add
     drift risk without closing a real hole.

4. **Sampling not deterministic.**
   - **Changed.** D2 now defines the stratum key (outcome, task, edition group, path) and
     lists the suspect paths by name (`contained`, `addition`, `zero_candidates`,
     `segment_mismatch`).
   - It spells out the allocation: outcome shares, a per-stratum minimum m, weights by
     path, caps with redistribution, and largest-remainder rounding with a key-order
     tie-break.
   - Order within a stratum is sha256(seed ∥ cell id). D3 defines overlap as the first
     ⌈r·n_h⌉ cells of each stratum, and D4 gives a global sha256 order for interleaving.
   - Selection probability (π_h) is kept separate from judged/assigned counts, which are
     handled by the post-stratified weights. Overlap carries no separate selection
     probability.

5. **Privacy disclosure and pseudonymisation.**
   - **Changed.** The consent text must list every published field: pseudonym, declared
     languages, verdicts, flags and notes verbatim.
   - Pseudonyms are an HMAC of the reviewer id under an operator secret, so they aren't an
     email hash (D8).
   - Each assignment snapshots the reviewer's declared languages, and the export reports
     that snapshot.

## claude

1. **The rubric contradicts Spec 48 and #23.**
   - **Changed.** This was the most important catch. D1 now follows the decided contract:
     - Spec 48 class A ("from memory: …" plus the delivered text) is judged on the
       delivered text, and only class B is `refused`;
     - verify_source takes the leading stance;
     - the completion head counts;
     - containment allows any amount of surrounding text.
   - Disagreement with the contract itself is captured by a new post-reveal
     **rubric-problem** flag and reported separately, so definitional divergence isn't
     counted as scorer error.
   - Open question 2 names Spec 48 and #23, so the architect settles the construct
     knowingly.

2. **Audit and test-gate coverage unsatisfiable; location unspecified.**
   - **Changed.** There is a new success criterion. The committed-artifact audit must
     cover the review set and every export. A change touching only review artifacts must
     run the pipelines (audit) lane in `.codev/checks/test.sh`. The viewer's run discovery
     must not list review artifacts as runs.
   - Current State now records the gap itself: `test_audit.py` scans only
     `git ls-files runs/`, and the dispatcher routes by top-level directory.
   - The physical location is left to the plan. Either of your two options satisfies the
     criterion.

3. **Account delete vs record integrity.**
   - **Changed (decided, with an option).** D9 keeps the cascade, because the issue says to
     port accounts "unchanged". Cited figures are always tied to a specific committed
     export, and the report reads only that export, so a later account delete can't
     invalidate a published number. The consent text says what delete does and doesn't
     remove.
   - Anonymize-and-retain is offered as Open Question 6, since it changes ported
     behaviour.

4. **Power, not just allocation** (non-blocking).
   - **Changed.** The Estimands section now separates citable figures (overall and
     per-task weighted precision, FDR and agreement) from descriptive breakdowns. It gives
     the Wilson half-widths and sets a target of at least 400 judged scorer-correct cells
     overall and at least 100 per task. Judged n is printed beside every figure.
     Open Question 4 asks whether the target is realistic.

5. **#41 adjudication has no criterion.**
   - **Changed.** The report must produce an adjudication worklist: every human-vs-scorer
     and overlap disagreement, plus the other-script, paraphrase and wrong-citation strata.
     Incorrect cells are now stratified by coarse failure kind, so #41's bands are
     deliberately sampled.
   - An in-tool adjudicator or third-rater role is explicitly out of scope (Open
     Question 7).

6. **Effect of the defect flag on the denominator.**
   - **Changed.** Flagged cells are excluded from every estimand, the same as
     `can't judge`, and they are listed and counted.

7. **Claim-race concurrency.**
   - **Changed.** D4 now states that a non-overlap cell is claimed at most once per set
     and that concurrent claims resolve with exactly one winner. That is a success
     criterion and has a test scenario.

8. **MVP cut.**
   - **Changed.** Desired State has a "Delivery scope" item: everything is built and
     verified locally end to end, and hosting is a separate gated step. A "Local
     end-to-end" success criterion was added.

## Also changed on my own review

- Edition language is now part of the stratum key. Without it, a pool of English-only
  reviewers would let English cells stand in for Arabic cells of the same tradition under
  post-stratification.
