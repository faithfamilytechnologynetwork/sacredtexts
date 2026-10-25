"""Agreement among the public-domain English Bibles under the scorer's fold.

This is the portability check in the manuscript: KJV, ASV, and WEB, one verse
at a time. It does not score a model.
"""

from __future__ import annotations

import json
from pathlib import Path

from sacredbench.score import normalize


def _index(path: Path) -> dict[tuple, str]:
    rows = json.loads(path.read_text())
    return {
        (row["book"], int(row["chapter"]), int(row["verse"])): normalize(row["text"])
        for row in rows
    }


def agreement(indexes: dict[str, dict[tuple, str]]) -> dict:
    """Count verses present in every edition whose folded text matches."""
    names = list(indexes)
    if len(names) < 2:
        return {"shared": 0, "all": 0, "pairs": {}}
    shared = set.intersection(*(set(index) for index in indexes.values()))
    all_match = sum(
        1 for key in shared
        if len({indexes[name][key] for name in names}) == 1
    )
    pairs = {}
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            pairs[f"{left} and {right}"] = sum(
                1 for key in shared if indexes[left][key] == indexes[right][key]
            )
    return {"shared": len(shared), "all": all_match, "pairs": pairs}


def edition_run(paths: dict[str, Path]) -> dict:
    return agreement({name: _index(path) for name, path in paths.items()})


def format_editions(report: dict) -> str:
    shared = report["shared"]
    lines = [f"verses in every edition: {shared}"]
    if shared:
        lines.append(f"all editions agree: {report['all']} ({100 * report['all'] / shared:.1f}%)")
    for label, count in report["pairs"].items():
        rate = f"{100 * count / shared:.1f}%" if shared else "n/a"
        lines.append(f"{label}: {count} ({rate})")
    return "\n".join(lines)
