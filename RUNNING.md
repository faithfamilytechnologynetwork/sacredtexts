# Running SacredBench

Run these from the top folder of the project. One OpenRouter key covers every
model. Do not commit the key.

```bash
brew install uv
export OPENROUTER_API_KEY=sk-or-...
```

Prices for the test panel are in `items/for-test/COST.md`. The old three-model
reference run is about $13.

## Test set

The run is the population sample: the same 30 passages, four tasks each.
A native edition is two files, an English prompt and a native-language prompt.
Familiarity lists are in the sibling `familiarity/` folders and are not
part of this command. The panel is 16 models, search off.

```bash
python items/for-test/join_run.py --model haiku --test
python items/for-test/join_run.py --model haiku
```

`--test` calls the first 3 passages of each tradition. The second command, without `--test`, keeps those answers and collects the rest. See `runs/README.md`.

That creates `runs/haiku/base/` and, under it, the same folders as the question
files (`christianity/english/population/`, `sikhism/native/population/`, and
the rest). Each folder receives `answers.jsonl`, then `scores.jsonl`,
`summary.json`, and `summary.md`. Run the same command again to retry cells
that failed. Add `--only sikhism/native/population` to collect one folder.

A pilot is one tradition and one model. Tradition names are `Christianity`,
`Judaism`, and `Islam`. Model ids include `haiku`, `opus`, `sol`, and
`gpt-oss-20b`.

```bash
python items/for-test/join_run.py --model haiku --only christianity/english/population
```

That answers file is only the Christianity English questions for haiku. Run
the same command without `--only` to collect the other population files.
Finished haiku rows in a folder that already has answers are skipped.

Each answer row records the model id, the OpenRouter slug, the provider,
temperature, max tokens, and the panel fingerprint (provider, model,
tools, temperature). An empty tools field means search is off. It also records `started_at`, `collected_at` (UTC), and
`duration_s` for that call, plus token `usage` when the host returns it.
There is no separate run-level clock: the run's start is the earliest
`started_at`, and its duration is the span from that to the latest
`collected_at`.

## Save and resume

Ctrl-C, a closed laptop, or a crash keeps every finished answer. A call that
had not returned is not written, and there is no error file. Run the same
command again. It prints how many calls are left and how many are already
saved.

OpenRouter runs 4 calls at once (`concurrency` in the panel file). If the
key is out of credit, the run stops, in-flight calls may finish, and the rest
are not sent. Add credit and run the same command again.

Resume stops if the question file changed, or if a model id now has a
different provider, slug, temperature, or search setting. Use a new `--out`
file in that case.

When a rebuild changed only some questions, write a new run folder and copy
the unchanged answers from the old one:

```bash
python items/for-test/join_run.py --model haiku --run-dir runs/rerun-YYYY-MM-DD --carry-from runs/rerun-2026-11-03
```

An answer is copied only when its question id and its prompt are the same,
byte for byte, and the model id still has the same provider, slug,
temperature, search setting, and max tokens. Every other question is called.
A copied row keeps its answer and times, takes the new question (so it is
scored against the new `expected`), and names its source in `carried_from`.
`model.json` counts only the new calls. `--carry-from runs` copies from the
committed `runs/<model>/` folders.

`score`, `analyze`, and `facct` are free. They can run on a partial answers
file. They do not call a model.

## Reference run

This is the older path: convert the local texts, generate 28 questions per
original-language text, collect the three models in
`configs/models.openrouter.yaml`. Use a new dated folder. Do not re-collect a
folder that is already committed.

```bash
uv --project pipelines run python -m sacredbench convert
uv --project pipelines run python -m sacredbench generate texts/standardized \
  --out runs/original-YYYY-MM-DD/questions.jsonl
uv --project pipelines run python -m sacredbench collect \
  runs/original-YYYY-MM-DD/questions.jsonl configs/models.openrouter.yaml \
  --out runs/original-YYYY-MM-DD/answers.jsonl
uv --project pipelines run python -m sacredbench score \
  runs/original-YYYY-MM-DD/answers.jsonl \
  --scores-out runs/original-YYYY-MM-DD/scores.jsonl \
  --summary-out runs/original-YYYY-MM-DD/summary.json \
  --summary-md runs/original-YYYY-MM-DD/summary.md
uv --project pipelines run python -m sacredbench facct runs/original-YYYY-MM-DD
uv --project pipelines run python -m sacredbench analyze runs/original-YYYY-MM-DD
```

The viewer, optional: `cd apps/viewer && pnpm install && pnpm dev`.

## Committing a run

```bash
uv --project pipelines run python -m pytest pipelines -q
uv --project pipelines run python -m sacredbench.audit
git add runs/original-YYYY-MM-DD/questions.jsonl \
        runs/original-YYYY-MM-DD/questions.jsonl.manifest.json \
        runs/original-YYYY-MM-DD/answers.jsonl \
        runs/original-YYYY-MM-DD/scores.jsonl \
        runs/original-YYYY-MM-DD/summary.json \
        runs/original-YYYY-MM-DD/summary.md \
        runs/original-YYYY-MM-DD/facct.json \
        runs/original-YYYY-MM-DD/facct.md \
        runs/original-YYYY-MM-DD/analysis.md
```

Do not use `git add -A`. Do not commit `texts/standardized/` or restricted
sources (NABRE, TLG). A new run gets a new folder.
