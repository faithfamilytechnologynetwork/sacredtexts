"""Write the population questions the run collects.

The list is the same one cost.py prices. Sikhism and the familiarity folders
are not included. The command refuses duplicate question ids.

    python items/for-test/join_run.py
"""

from __future__ import annotations

import json
from pathlib import Path

from cost import RUNNABLE

OUT = Path(__file__).resolve().parents[2] / "runs" / "for-test" / "questions.jsonl"


def main() -> None:
    seen: set[str] = set()
    lines: list[str] = []
    for path in RUNNABLE:
        if not path.exists():
            raise SystemExit(f"missing {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row["id"] in seen:
                raise SystemExit(f"duplicate question id {row['id']} in {path}")
            seen.add(row["id"])
            lines.append(line)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    print(f"{OUT} {len(lines)} questions from {len(RUNNABLE)} files")


if __name__ == "__main__":
    main()
