# Review

Human labels for checking the matcher (Spec 154). A reviewer who knows a text looks at a
sample of scored cells and records the true outcome. Those labels are a gold set that any
version of the matcher can be scored against.

## What is here

```text
review/samples/<sample-id>.json   a committed sample: the cells a reviewer is shown
gold-<sample-id>.jsonl            a reviewer's labels, downloaded from the review tool (not committed here)
```

## The workflow, end to end

1. **Draw a sample** (an operator, once per run). `review-sample` picks cells from a run and
   writes `review/samples/<sample-id>.json`. Commit it. See [Samples](#samples).
2. **Serve it.** The review service (`apps/api`) serves one sample, named by `SAMPLE_PATH`,
   together with the review pages. To run it on your machine, follow "Local run" in
   `apps/api/README.md`.
3. **Label** (each reviewer).
   1. Open `/review`, create an account with the invite code, and tick the texts you know.
   2. Work through your pass. For each cell, pick the true outcome, following the rubric shown
      beside it. Tick **Question defect** if the expected text or the prompt is itself wrong.
      Add notes in any language.
   3. Labels save as you go. You can stop and pick up later, on any device.
4. **Download** your labels: **Download gold set** at the bottom of `/review` saves
   `gold-<sample-id>.jsonl`. Downloading twice gives the same file. See [Gold sets](#gold-sets).
5. **Compare** matcher versions against the labels, from the repo root:

   ```bash
   uv --project pipelines run python -m sacredbench review-compare gold-<sample-id>.jsonl \
     --version committed --version current
   ```

   See [Comparing matcher versions](#comparing-matcher-versions).

What a reviewer sees on each cell:

- the text and its citation, the task, and the model;
- the prompt, the expected text and the model's answer;
- the matcher's verdict, its submetrics and the grader path;
- for `verify_source`, where the passage really comes from (a "No" item quotes another text).

The review is not blind: the matcher's verdict is shown with the cell. That is the owner's
ruling at the Spec 154 spec gate, because this is a tool for checking matcher versions, not a
study of independent raters.

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
  also records the seed, `k`, the source run, each text's drawn count, and each stratum's
  population and drawn count.

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

## Gold sets

A reviewer downloads their labels as a **gold set**: a JSONL file with one row per labelled
cell, sorted by `cell_id`. Each row carries everything needed to re-score its cell, so a gold
set does not depend on any one version of the matcher.

| Field | What it holds |
|---|---|
| `format` | `1` |
| `sample_id` | the sample the cell came from |
| `cell_id`, `run`, `model_id`, `question_id` | the cell (`cell_id` is `<run>:<model_id>:<question_id>`) |
| `scores_path` | the `scores.jsonl` the cell was scored in, relative to the repo root |
| `task`, `text`, `prompt`, `expected`, `answer`, `source` | the cell, exactly as in the sample |
| `shown` | what the reviewer saw: `outcome`, `metrics`, `grader_path` |
| `label` | the human verdict: `outcome` (`correct` / `incorrect` / `refused` / `cant_judge`), `defect` (true if the question itself is wrong), `notes` |
| `rubric_version` | the rubric version the label was made under |
| `reviewer_id` | the reviewer's account id (a UUID; no email or name) |
| `labelled_at` | when the label was last changed (ISO 8601 with a time zone) |

The bytes are fixed so that the review tool and Python write the same file: one compact JSON
object per line, keys sorted at every level, non-ASCII written as is, and numbers written as
JavaScript's `JSON.stringify` writes them (`1.0` is `1`). `review_compare.dumps_gold_rows` is
the Python writer.

Loading a gold set fails loudly on an unknown `format`, a missing or unknown field, an unknown
label outcome, an `expected` without the key its task is scored on, a `scores_path` that is
not a canonical relative path (absolute, `..`, `.`, or a doubled or trailing `/`), rows out of
order, or the same reviewer labelling the same cell twice (in one file or across files).

`fixtures/review_sample.json` and `fixtures/review_gold_set.jsonl` are a small sample (10
cells: every task, in `islam/native` and `hinduism/english`) and its gold set. They are the
contract between the two writers: the pipelines tests pin them, and the review tool's download
must reproduce `review_gold_set.jsonl` byte for byte from them.

## Comparing matcher versions

Score one or more versions of the matcher against gold sets. Run from the repo root:

```bash
uv --project pipelines run python -m sacredbench review-compare gold-facct-2026-11-03-k10.jsonl \
  --version committed --version current
```

Pass several gold-set files to combine reviewers. Each `--version` is one of:

- `committed`: the run's recorded scores, read now from each row's `scores_path`;
- `current`: a re-score by the scorer code in this checkout, exactly as `sacredbench score`
  would score it with the default graders. It makes no network calls. Each row's run must
  have been scored with the default graders too (the `evaluators` in the `summary.json`
  beside its `scores_path`). Otherwise it stops with an error, because the difference
  would show as matcher movers;
- a **run directory** laid out like `runs/<run>/`, for example a copy of the run re-scored
  with `sacredbench score` on another branch. Each row's `scores_path` has its
  `runs/<run>/` prefix replaced by the directory. All the gold rows must come from one run.

For each version it prints:

- agreement with the human as `agree / n (pct)`: overall, per task, per text and per grader
  path (the path is worked out from that version's own metrics);
- for each text, how many of its judged rows came from each prompt arm (`source.condition`;
  `(none)` for a run without arms);
- every disagreement: cell id, task, text, the human outcome and the version's outcome.

`n` leaves out `cant_judge` and defect-flagged rows. They are counted on their own line,
with how many rows are both.

With two or more versions, the first is the **baseline**. Each other version lists its
**movers**, the judged cells whose outcome changed against the baseline:

- `fixed`: it now agrees with the human;
- `broken`: it agreed with the human and no longer does;
- `neither`: it agrees with the human under neither version.

So a version's agreement minus the baseline's is always `fixed` minus `broken`.

`--json <path>` also writes the same numbers as JSON (each `by_text` entry also carries its
`arms` counts). Both outputs are the same every time
for the same inputs. A missing scores file or row, a scores file with two rows for one cell,
or an unknown version stops the command with an error.

## Copyright

The samples include NRSV cells. NRSV is a `restricted` catalogue edition, and
`pipelines/sacredbench/audit.py` audits committed run evidence under `runs/`.

`review/` is deliberately **outside** that audit. This is the owner's ruling at the
Spec 154 spec gate (2026-11-10): counsel's position is that this research is fair use. So
the review tool includes NRSV and adds no copyright exclusion or audit machinery. This is
not an oversight. Of the FAccT sample's 111 NRSV cells, 105 cite 28 distinct verses. The other 6
are `verify_source` "No" items, which quote another text.
