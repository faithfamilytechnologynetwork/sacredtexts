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

The run is the population sample: 30 passages, four tasks each. A native
edition is two files, an English prompt and a native-language prompt.
Sikhism has no English file. Buddhism is the Pali text with an English prompt.
Book of Mormon and encyclicals are extra English sets, 30 passages each.
Familiarity lists sit in sibling `familiarity/` folders and are not collected.
The panel is `items/for-test/models/openrouter.yaml`, 16 models, temperature 0,
search off. Prices are in `items/for-test/COST.md`.

```bash
python items/for-test/join_run.py --model haiku --test
python items/for-test/join_run.py --model haiku
python items/for-test/join_run.py --model haiku --tradition islam --tradition judaism
python items/for-test/join_run.py --model haiku --tradition book-of-mormon --tradition encyclicals
python items/for-test/join_run.py --model haiku --only christianity/english/population
```

`--test` calls the first 3 passages of each tradition, then the same command
without `--test` fills the rest into the same answer files. Repeat
`--tradition`. Names are the folder names: `christianity`, `judaism`, `islam`,
`sikhism`, `hinduism`, `buddhism`, `book-of-mormon`, `encyclicals`. Passing
several names to one flag is an error. `--head 9` keeps the first 9 questions
of each selected file and still stamps the full-file digest, which is how the
limited models take Buddhism.

That creates `runs/haiku/base/` and, under it, the same folders as the question
files. A finished file receives `answers.jsonl`, then `scores.jsonl`,
`summary.json`, and `summary.md`. A file with a pending cell is not scored.
Run the same command again to retry cells that failed. Finished
question-and-model pairs are not called again. `--run-dir runs/<name>` writes
a new tree instead of `runs/<model>/`. See `runs/README.md`.

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
different provider, slug, temperature, or search setting. Point `--run-dir`
at a new folder in that case.

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
`model.json` counts only the new calls. The token usage in `summary.json`
still counts a copied row, so read the spend of the new run from
`model.json`. `--carry-from runs` copies from the committed `runs/<model>/`
folders.

`score`, `analyze`, and `facct` are free. They can run on a partial answers
file. They do not call a model. The headline is the string score: a folded
match or a contained quotation is correct, a refusal is a separate outcome,
and it does not enter accuracy.

## Run Jev

Jev is a paid second pass. It does not rescore, and it does not change
`correct`. Run it only after `join_run` has written `answers.jsonl` for one
folder. The first command prints the estimate and stops. Add `--yes` to spend.

```bash
uv --project pipelines run python -m sacredbench judge \
  runs/haiku/base/christianity/english/population/answers.jsonl
uv --project pipelines run python -m sacredbench judge \
  runs/haiku/base/christianity/english/population/answers.jsonl --yes
```

The default write is next to those answers:

```text
runs/haiku/base/christianity/english/population/jev_results/judgments.jsonl
runs/haiku/base/christianity/english/population/jev_results/judgments.jsonl.manifest.json
runs/haiku/base/christianity/english/population/jev_results/cost.json
```

One Decisions call covers the cells that still need a judge. Cite and verify
are skipped. A quote or completion the string score already settled (folded
equality, or the reference contained in the answer) is skipped and is not
billed. Restricted editions are not sent. `--limit 20` caps how many cells
this invocation calls. The pre-flight estimate uses $0.00003 per cell.
`cost.json` stores the measured tokens and dollars after the call.

Each row records a wording label (`kind`) and a separate claim scale
(`theology`: accurate 0, gloss 1, distorted 2, contradicted 3, or no_claim).
Those two fields are descriptive until people apply the same labels. The
string score remains the result. The tradition name is not sent to Jev.

The same command resumes. A cell already in the sidecar is not called again.
The resolved build is part of the file. If OpenRouter resolves `jev-latest`
to a different build, the resume stops; point `--out` at a new
`judgments.jsonl`. The rubric id is `sacredbench-jev-5`. Spelling, accents,
and vowel signs are not a distorted claim, and a quotation that drops a clause
is not accurate. A file already judged under an older rubric needs its own
`--out`, such as `jev_results/judgments-v5.jsonl`.

Counts without a new call:

```bash
uv --project pipelines run python -m sacredbench judge-summary \
  runs/haiku/base/christianity/english/population/jev_results/judgments.jsonl
```

Agreement with the string score, also free. This is the check on Jev's
refusal and containment questions. It does not validate the theology scale.

```bash
uv --project pipelines run python -m sacredbench judge-agreement \
  runs/haiku/base/christianity/english/population/answers.jsonl \
  runs/haiku/base/christianity/english/population/scores.jsonl \
  runs/haiku/base/christianity/english/population/jev_results/judgments.jsonl \
  --md-out runs/haiku/base/christianity/english/population/jev_results/agreement.md
```

An edition index is optional. It adds other wordings so `other_indexed_wording`
can be chosen. It needs the questions file whose manifest carries the corpus
hash:

```bash
uv --project pipelines run python -m sacredbench judge \
  runs/haiku/base/christianity/english/population/answers.jsonl \
  --equivalence-index path/to/index.jsonl \
  --questions items/for-test/christianity/english/population/questions.jsonl \
  --yes
```

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
