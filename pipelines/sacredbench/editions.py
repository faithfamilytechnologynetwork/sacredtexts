"""Agreement among the public-domain English Bibles under the scorer's fold.

This is the portability check in the manuscript: KJV, ASV, and WEB, one verse
at a time. It does not score a model.

Editions come from the Spec 32 edition index (``edition_index.load_edition_documents``),
never from ``texts/raw/*.json`` payloads directly: that routes every wording through the
same converter the audit uses and the same licence gate, so a restricted English Bible
(e.g. NABRE) is filtered before it can be compared here.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from sacredbench import catalogue as cat
from sacredbench.edition_index import load_edition_documents
from sacredbench.score import normalize

# The manuscript's portability check is the English Bible: one work, one language, several
# public-domain wordings. These select which indexed editions enter the agreement table.
BIBLE_WORK = "The Bible"
BIBLE_LANGUAGE = "en"


def edition_indexes(
    raw_root: Path = cat.RAW_ROOT,
    *,
    work: str = BIBLE_WORK,
    language: str = BIBLE_LANGUAGE,
) -> dict[str, dict[str, str]]:
    """Per-version ``{citation: folded text}`` for one work+language, from the edition index.

    Reads the non-restricted corpus through the converter (:func:`load_edition_documents`),
    never raw payload files. The index is the same-canonical-language pool, so a work has one
    indexed wording per (version, citation); versions are the catalogue's version strings
    (e.g. ``KJV``, ``ASV (1901)``, ``WEB``)."""
    indexed, _all_docs, _excluded = load_edition_documents(raw_root)
    editions: dict[str, dict[str, str]] = defaultdict(dict)
    for doc in indexed:
        if doc.work != work or doc.language != language:
            continue
        for entry in doc.entries:
            editions[doc.version][entry.citation] = normalize(entry.text)
    return dict(editions)


def agreement(indexes: dict[str, dict[str, str]]) -> dict:
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


def edition_run(raw_root: Path = cat.RAW_ROOT) -> dict:
    return agreement(edition_indexes(raw_root))


def format_editions(report: dict) -> str:
    shared = report["shared"]
    lines = [f"verses in every edition: {shared}"]
    if shared:
        lines.append(f"all editions agree: {report['all']} ({100 * report['all'] / shared:.1f}%)")
    for label, count in report["pairs"].items():
        rate = f"{100 * count / shared:.1f}%" if shared else "n/a"
        lines.append(f"{label}: {count} ({rate})")
    return "\n".join(lines)
