"""Collect and score the population questions for one model.

Each question file lands in the matching folder under ``runs/<model>/base/``.
The folder is created when that file is collected. ``--run-dir`` moves the whole
run elsewhere: answers under ``<run-dir>/<model>/base/`` and the usage card at
``<run-dir>/<model>/model.json``, seeded from the committed ``runs/<model>/model.json``
when it is missing. A ``--run-dir`` run never writes into ``runs/<model>/``; pointing
it at ``runs`` itself, or inside a committed model folder, is refused. ``base`` is temperature 0
and search off, the panel in ``models/openrouter.yaml``. A file that already
has answers is resumed: finished question-and-model pairs are skipped. After
a clean collect, the same folder gets ``scores.jsonl``, ``summary.json``, and
``summary.md``.

``--test`` calls only the first 3 passages of each tradition. The answer file
is still stamped with the full question-file digest, so dropping ``--test``
later adds the remaining passages to the same file.

    python items/for-test/join_run.py --model haiku --test
    python items/for-test/join_run.py --model haiku
    python items/for-test/join_run.py --model haiku --tradition islam
    python items/for-test/join_run.py --model haiku --only sikhism/native/population
    python items/for-test/join_run.py --model haiku --run-dir runs/rerun-2026-11-03
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from dataclasses import replace
from pathlib import Path

from cost import PANEL, RUNNABLE
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "pipelines"))

from sacredbench.collect import Stopped, _existing, collect  # noqa: E402
from sacredbench.config import load_config  # noqa: E402
from sacredbench.generate import Question, load_questions  # noqa: E402

PYTHON = REPO / ".venv" / "bin" / "python"
RUNS = REPO / "runs"
# Top-level runs/ names the viewer reserves (apps/viewer/vite/runsEndpoint.ts SKIP_TOP).
RESERVED_RUN_NAMES = frozenset({"panel", "paper", "archive"})


_USAGE_LOCK = threading.Lock()
TEST_PASSAGES = 3


def resolve_run_dir(arg: str | None) -> Path:
    """Where this run writes. None is today's ``runs/``. A relative path is taken from the repo root.

    An explicit run dir may not be ``runs/`` itself or sit inside a committed model folder
    (``runs/<id>/`` with a ``base/``), so a rerun can never write into the committed archive.
    """
    if arg is None:
        return RUNS
    run_dir = Path(arg)
    if not run_dir.is_absolute():
        run_dir = REPO / run_dir
    run_dir = run_dir.resolve()
    runs = RUNS.resolve()
    if run_dir == runs:
        raise SystemExit("--run-dir must not be runs/ itself; leave it out to write the committed archive")
    if run_dir.is_relative_to(runs):
        top = run_dir.relative_to(runs).parts[0]
        if (runs / top / "base").exists() or (runs / top / "model.json").exists():
            raise SystemExit(f"--run-dir {run_dir} is inside the committed model folder runs/{top}/")
        if top in RESERVED_RUN_NAMES:
            raise SystemExit(f"--run-dir runs/{top} is reserved; the viewer does not list it as a run")
    return run_dir


def _card_path(model_id: str, run_dir: Path) -> Path:
    return run_dir / model_id / "model.json"


def seed_card(model_id: str, run_dir: Path) -> Path | None:
    """Copy the committed card's prices into a new run dir, without its collected totals."""
    dest = _card_path(model_id, run_dir)
    if dest.exists():
        return dest
    committed = _card_path(model_id, RUNS)
    if dest == committed or not committed.exists():
        return None
    card = json.loads(committed.read_text(encoding="utf-8"))
    card.pop("collected", None)
    dest.parent.mkdir(parents=True, exist_ok=True)
    _write_card(dest, card)
    return dest


def _prices(card: dict) -> tuple[float, float]:
    prices = (card.get("catalogue") or {}).get("pricing_usd_per_token") or {}
    return float(prices.get("prompt") or 0), float(prices.get("completion") or 0)


def _totals(prompt_tokens: int, completion_tokens: int, calls: int, prices: tuple[float, float]) -> dict:
    return {
        "calls": calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": round(prompt_tokens * prices[0] + completion_tokens * prices[1], 8),
    }


def _write_card(path: Path, card: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def reconcile_usage(model_id: str, run_dir: Path) -> dict | None:
    """Rebuild collected totals from the answer files. Safe after a stopped run."""
    path = _card_path(model_id, run_dir)
    if not path.exists():
        return None
    with _USAGE_LOCK:
        card = json.loads(path.read_text(encoding="utf-8"))
        prices = _prices(card)
        prompt_tokens = completion_tokens = calls = 0
        base = path.parent / "base"
        if base.is_dir():
            for answers in base.rglob("answers.jsonl"):
                for line in answers.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if row.get("model_id") != model_id:
                        continue
                    usage = row.get("usage") or {}
                    prompt_tokens += int(usage.get("in") or 0)
                    completion_tokens += int(usage.get("out") or 0)
                    calls += 1
        card["collected"] = _totals(prompt_tokens, completion_tokens, calls, prices)
        _write_card(path, card)
        return card["collected"]


def add_usage(model_id: str, row: dict, run_dir: Path) -> dict | None:
    """Add one saved answer's tokens to model.json."""
    path = _card_path(model_id, run_dir)
    if not path.exists():
        return None
    usage = row.get("usage") or {}
    with _USAGE_LOCK:
        card = json.loads(path.read_text(encoding="utf-8"))
        prices = _prices(card)
        have = card.get("collected") or {}
        card["collected"] = _totals(
            int(have.get("prompt_tokens") or 0) + int(usage.get("in") or 0),
            int(have.get("completion_tokens") or 0) + int(usage.get("out") or 0),
            int(have.get("calls") or 0) + 1,
            prices,
        )
        _write_card(path, card)
        return card["collected"]


def load_dotenv() -> None:
    """Copy .env into the environment. sacredbench does not read that file itself."""
    path = REPO / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and name not in os.environ and value:
            os.environ[name] = value


def out_dir(model: str, questions: Path, run_dir: Path) -> Path:
    rel = questions.parent.relative_to(ROOT)
    return run_dir / model / "base" / rel


def asked_citation(q: Question) -> str:
    """The passage this row asks about. A verify ``no`` row leaves citation blank."""
    return q.source.get("citation") or ""


def passages_in(qs: list[Question]) -> list[str]:
    seen: list[str] = []
    for q in qs:
        citation = asked_citation(q)
        if citation and citation not in seen:
            seen.append(citation)
    return seen


def rows_for(qs: list[Question], keep: set[str]) -> list[Question]:
    """Rows for those passages, including a verify ``no`` that follows its passage."""
    current = ""
    out: list[Question] = []
    for q in qs:
        citation = asked_citation(q)
        if citation:
            current = citation
        if current in keep:
            out.append(q)
    return out


def test_passages(files: list[Path]) -> dict[str, list[str]]:
    """First 3 passages of each tradition, in question-file order."""
    chosen: dict[str, list[str]] = {}
    for path in files:
        tradition = path.relative_to(ROOT).parts[0]
        have = chosen.setdefault(tradition, [])
        if len(have) >= TEST_PASSAGES:
            continue
        for citation in passages_in(load_questions(path)):
            if citation not in have:
                have.append(citation)
            if len(have) >= TEST_PASSAGES:
                break
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect one model's population answers.")
    parser.add_argument("--model", required=True, help="model id from models/openrouter.yaml, such as haiku or opus")
    parser.add_argument(
        "--tradition",
        action="append",
        default=[],
        help="only this tradition: christianity, judaism, islam, sikhism, hinduism, buddhism; repeatable",
    )
    parser.add_argument("--test", action="store_true", help="only the first 3 passages of each tradition")
    parser.add_argument(
        "--head",
        type=int,
        default=None,
        help="only the first N questions of each selected file; the file digest stays the full set",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="calls in flight at once (default: concurrency in the panel file, currently 4)",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="collect only question files whose path contains this fragment; repeatable",
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        help="write under <run-dir>/<model>/ instead of runs/<model>/ (relative to the repo root), "
        "such as runs/rerun-2026-11-03",
    )
    args = parser.parse_args()
    run_dir = resolve_run_dir(args.run_dir)
    files = list(RUNNABLE)
    missing = [p for p in files if not p.exists()]
    if missing:
        raise SystemExit(f"missing {missing[0]}")
    chosen = test_passages(files) if args.test else {}
    known = sorted({p.relative_to(ROOT).parts[0] for p in files})
    if args.tradition:
        wanted = {name.casefold() for name in args.tradition}
        unknown = wanted - set(known)
        if unknown:
            raise SystemExit(f"no tradition {sorted(unknown)} (choices: {', '.join(known)})")
        files = [p for p in files if p.relative_to(ROOT).parts[0].casefold() in wanted]
    if args.only:
        files = [p for p in files if any(part in p.as_posix() for part in args.only)]
        if not files:
            raise SystemExit(f"no question file matches {args.only}")
    load_dotenv()
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is not set in the environment or .env")
    cfg = load_config(PANEL)
    picked = [m for m in cfg.models if m.id == args.model]
    if not picked:
        ids = ", ".join(m.id for m in cfg.models)
        raise SystemExit(f"no model id {args.model!r} in {PANEL} (ids: {ids})")
    if args.concurrency is not None:
        if args.concurrency < 1:
            raise SystemExit("--concurrency must be at least 1")
        cfg = replace(cfg, concurrency=args.concurrency)
    cfg = replace(cfg, models=tuple(picked))
    if run_dir != RUNS:
        seed_card(args.model, run_dir)
    reconcile_usage(args.model, run_dir)
    py = PYTHON if PYTHON.exists() else Path(sys.executable)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "pipelines")
    unfinished: list[str] = []
    for questions in files:
        all_qs = load_questions(questions)
        if args.test:
            tradition = questions.relative_to(ROOT).parts[0]
            keep = [c for c in chosen.get(tradition, []) if c in passages_in(all_qs)][:TEST_PASSAGES]
            todo = rows_for(all_qs, set(keep))
            if not todo:
                print(f"skip {questions.relative_to(ROOT)} (none of the 3 passages are in this file)")
                continue
        else:
            todo = all_qs[: args.head] if args.head else all_qs
        dest = out_dir(args.model, questions, run_dir)
        dest.mkdir(parents=True, exist_ok=True)
        answers = dest / "answers.jsonl"
        rel = questions.parent.relative_to(ROOT)
        saved, *_ = _existing(answers)
        pending = sum(1 for q in todo if (q.id, args.model) not in saved)
        shown = answers.relative_to(REPO) if answers.is_relative_to(REPO) else answers
        print(f"collect {rel} -> {shown} ({len(todo)} questions, {pending} to call)")
        bar = tqdm(total=pending, desc=str(rel), unit="call", leave=True, disable=pending == 0)

        def on_saved(row, _bar=bar, _model=args.model) -> None:
            totals = add_usage(_model, row, run_dir)
            _bar.update(1)
            if totals:
                _bar.set_postfix(usd=f"{totals['cost_usd']:.4f}", refresh=False)

        def on_failure(*_a, _bar=bar) -> None:
            _bar.update(1)

        try:
            done, failed, messages = collect(
                todo, cfg, answers, on_result=on_saved, on_failure=on_failure, digest_from=all_qs,
            )
        except Stopped as stop:
            bar.close()
            reconcile_usage(args.model, run_dir)
            print(f"\n{stop}", file=sys.stderr)
            os._exit(130)
        finally:
            bar.close()
            reconcile_usage(args.model, run_dir)
        print(f"  collected {done}, pending {failed}")
        if failed:
            for msg in messages:
                print(f"  {msg}", file=sys.stderr)
            unfinished.append(str(rel))
            continue
        score = [
            str(py), "-m", "sacredbench", "score",
            str(answers),
            "--scores-out", str(dest / "scores.jsonl"),
            "--summary-out", str(dest / "summary.json"),
            "--summary-md", str(dest / "summary.md"),
        ]
        print(" ".join(score))
        subprocess.run(score, cwd=REPO, check=True, env=env)
    if unfinished:
        raise SystemExit(f"still pending: {', '.join(unfinished)}")


if __name__ == "__main__":
    main()
