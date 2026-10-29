# Running SacredBench — handover notes for Jonathan

These are the steps to run the full benchmark end-to-end in Waleed's absence. Nothing
here requires changing code. Every command is copy-pasteable and runs from the top
folder of the project. If you have never run the pipeline before, do the
[TUTORIAL.md](TUTORIAL.md) walk-through once first — it is the same pipeline on three
texts for under a dollar, and it verifies your setup end to end.

## One-time setup

1. Clone the repo and install [uv](https://docs.astral.sh/uv/) (`brew install uv` on a
   Mac). That is the only tool the pipeline needs; `uv` fetches Python and all
   dependencies by itself on first run.
2. Get an [OpenRouter](https://openrouter.ai/) API key with ~$20 of credit (a full
   reference run costs about $13). Put it in your terminal's environment:

   ```bash
   export OPENROUTER_API_KEY=sk-or-...
   ```

   **Never commit the key or save it in a file inside the project.**

## The full reference run, step by step

**Step 1 — rebuild the local text corpus** (free, ~1 minute). The standardized texts are
deliberately not checked in; this rebuilds them from the committed raw sources. Two
restricted sources (NABRE, TLG) will be skipped unless their payloads are present
locally — that is normal and fine.

```bash
uv --project pipelines run python -m sacredbench convert
```

**Step 2 — generate the question set** (free, seconds). Defaults are the committed
protocol: original-language texts only, 28 questions per text across the four templates,
pinned seed. Name the run folder `original-YYYY-MM-DD`:

```bash
uv --project pipelines run python -m sacredbench generate texts/standardized \
  --out runs/original-2026-11-05/questions.jsonl
```

**Step 3 — collect answers from the model panel** (THE PAID STEP, ~$13, ~30–60 min).
Uses the same three-model OpenRouter panel as the reference run:

```bash
uv --project pipelines run python -m sacredbench collect \
  runs/original-2026-11-05/questions.jsonl configs/models.openrouter.yaml \
  --out runs/original-2026-11-05/answers.jsonl
```

This is **resumable**: if it exits with failed cells (network blips, rate limits), just
run the exact same command again — finished answers are never re-bought, only the
missing ones are retried.

**Step 4 — score** (free, seconds):

```bash
uv --project pipelines run python -m sacredbench score \
  runs/original-2026-11-05/answers.jsonl \
  --scores-out runs/original-2026-11-05/scores.jsonl \
  --summary-out runs/original-2026-11-05/summary.json \
  --summary-md runs/original-2026-11-05/summary.md
```

**Step 5 — build the report card** (free, seconds). Writes `facct.json` and `facct.md`
into the run folder — `facct.md` is the human-readable results report:

```bash
uv --project pipelines run python -m sacredbench facct runs/original-2026-11-05
```

**Step 6 — the deeper analyses** (free; these are the commands behind the paper's
failure-mode numbers):

```bash
uv --project pipelines run python -m sacredbench failures  runs/original-2026-11-05
uv --project pipelines run python -m sacredbench breakdown runs/original-2026-11-05
uv --project pipelines run python -m sacredbench probes    runs/original-2026-11-05
uv --project pipelines run python -m sacredbench splits    runs/original-2026-11-05
```

**Step 7 — browse the results** (optional). The viewer needs
[pnpm](https://pnpm.io/installation):

```bash
cd apps/viewer && pnpm install && pnpm dev
```

## Before committing a finished run

Run the test suite and the copyright audit from the top folder; both must pass:

```bash
uv --project pipelines run python -m pytest pipelines -q
uv --project pipelines run python -m sacredbench.audit
```

Then commit the run folder's files **by explicit path** (never `git add -A` or
`git add .` in this repo):

```bash
git add runs/original-2026-11-05/questions.jsonl \
        runs/original-2026-11-05/questions.jsonl.manifest.json \
        runs/original-2026-11-05/answers.jsonl \
        runs/original-2026-11-05/scores.jsonl \
        runs/original-2026-11-05/summary.json \
        runs/original-2026-11-05/summary.md \
        runs/original-2026-11-05/facct.json \
        runs/original-2026-11-05/facct.md
git commit -m "runs: original-2026-11-05 reference run"
```

## The rules that protect the evidence

- **Never re-run `collect` or `score` pointing at an already-committed run folder**
  (`runs/original-2026-10-21/` and the others). They are finished evidence. Every new
  run goes in a brand-new folder.
- **Never commit `texts/standardized/`** or anything derived from the restricted
  sources (NABRE, TLG). The audit in the step above enforces this — if it fails, stop
  and don't commit.
- A run's numbers come from its own folder. If a command errors, read the message —
  the pipeline is built to fail loudly with instructions rather than produce silently
  wrong numbers.

## If something breaks

Open a GitHub issue on the repo describing the command you ran and the full error
output. The test suite (`pytest` command above) passing tells you the code and corpus
on your machine are healthy; from there the usual culprits are the API key not being
exported in the current terminal, or OpenRouter credit running out mid-collect (top up
and re-run the same collect command — it resumes).
