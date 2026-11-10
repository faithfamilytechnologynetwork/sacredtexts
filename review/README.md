# Review

Human labels for checking the matcher (Spec 154). A reviewer who knows a text looks at a
sample of scored cells and records the true outcome. Those labels are a gold set that any
version of the matcher can be scored against.

## What is here

```text
review/samples/<sample-id>.json   a committed sample: the cells a reviewer is shown
```

## Samples

A sample is drawn from one run directory and committed. The FAccT one:

```bash
uv --project pipelines run python -m sacredbench review-sample \
  --run-dir runs/facct-2026-11-03 --seed spec-154 --per-stratum 10 \
  --out review/samples/facct-2026-11-03-k10.json
```

That gives 1,423 cells from 151 strata across 13 texts.

- **Cell.** A cell is one row of a `scores.jsonl` joined to its `answers.jsonl` row. Only
  rows with a recorded `outcome` count.
- **Text.** A cell's text is its edition folder between `<model>/base/` and `population/`,
  for example `islam/native` or `encyclicals/english`.
- **Strata.** Strata are outcome × task × text. Each stratum gives `min(N, k)` cells, in
  the order of `sha256(seed NUL cell_id)`.
- **Order.** The sample lists its cells in the order of
  `sha256(seed NUL "order" NUL cell_id)`.
- **Cell id.** A cell's id is `<run>:<model_id>:<question_id>`.
- **Contents.** Each cell carries everything needed to show and re-score it: prompt,
  expected, answer, source, and the scorer's metrics, outcome and grader path. The sample
  also records the seed, `k`, the source run, and each stratum's population and drawn
  count.

Grader path, from the recorded metrics:

- retrieve_quote / complete_unit: `exact`, `normalized`, `contained` (containment only)
  or `none`;
- cite_passage: `citation`;
- verify_source: `verdict`.

The same run, seed and `k` always give the same bytes.
`pipelines/tests/test_review_sample.py` rebuilds the committed sample from `runs/` and
compares it, so a change to `runs/` that moves the sample fails that test. If that happens
deliberately (a sanctioned rebaseline), regenerate the sample in the same PR and say so.
Labels already downloaded stay valid, because they carry their own inputs.

## Copyright

The samples include NRSV cells. NRSV is a `restricted` catalogue edition, and
`pipelines/sacredbench/audit.py` audits committed run evidence under `runs/`.

`review/` is deliberately **outside** that audit. This is the owner's ruling at the
Spec 154 spec gate (2026-11-10): counsel's position is that this research is fair use. So
the review tool includes NRSV and adds no copyright exclusion or audit machinery. This is
not an oversight. The FAccT sample's NRSV cells cite 29 distinct verses.
