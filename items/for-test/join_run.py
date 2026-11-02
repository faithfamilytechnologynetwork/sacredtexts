"""Collect and score the population questions for one model.

Each question file lands in the matching folder under ``runs/<model>/base/``.
The folder is created when that file is collected. ``base`` is temperature 0
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
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from cost import PANEL, RUNNABLE
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "pipelines"))

from sacredbench.collect import _existing, collect  # noqa: E402
from sacredbench.config import load_config  # noqa: E402
from sacredbench.generate import Question, load_questions  # noqa: E402

PYTHON = REPO / ".venv" / "bin" / "python"
TEST_PASSAGES = 3


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


def out_dir(model: str, questions: Path) -> Path:
    rel = questions.parent.relative_to(ROOT)
    return REPO / "runs" / model / "base" / rel


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
        "--only",
        action="append",
        default=[],
        help="collect only question files whose path contains this fragment; repeatable",
    )
    args = parser.parse_args()
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
    cfg = replace(cfg, models=tuple(picked))
    py = PYTHON if PYTHON.exists() else Path(sys.executable)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "pipelines")
    for questions in files:
        all_qs = load_questions(questions)
        if args.test:
            tradition = questions.relative_to(ROOT).parts[0]
            preferred = [c for c in chosen.get(tradition, []) if c in passages_in(all_qs)]
            keep = preferred[:TEST_PASSAGES] or passages_in(all_qs)[:TEST_PASSAGES]
            todo = rows_for(all_qs, set(keep))
            if not todo:
                print(f"skip {questions.relative_to(ROOT)} (none of the 3 passages are in this file)")
                continue
        else:
            todo = all_qs
        dest = out_dir(args.model, questions)
        dest.mkdir(parents=True, exist_ok=True)
        answers = dest / "answers.jsonl"
        rel = questions.parent.relative_to(ROOT)
        saved, *_ = _existing(answers)
        pending = sum(1 for q in todo if (q.id, args.model) not in saved)
        print(f"collect {rel} -> {answers.relative_to(REPO)} ({len(todo)} questions, {pending} to call)")
        bar = tqdm(total=pending, desc=str(rel), unit="call", leave=True, disable=pending == 0)

        def tick(*_a, _bar=bar) -> None:
            _bar.update(1)

        done, failed, messages = collect(
            todo, cfg, answers, on_result=tick, on_failure=tick, digest_from=all_qs,
        )
        bar.close()
        print(f"  collected {done}, pending {failed}")
        if failed:
            for msg in messages:
                print(f"  {msg}", file=sys.stderr)
            raise SystemExit(1)
        score = [
            str(py), "-m", "sacredbench", "score",
            str(answers),
            "--scores-out", str(dest / "scores.jsonl"),
            "--summary-out", str(dest / "summary.json"),
            "--summary-md", str(dest / "summary.md"),
        ]
        print(" ".join(score))
        subprocess.run(score, cwd=REPO, check=True, env=env)


if __name__ == "__main__":
    main()
