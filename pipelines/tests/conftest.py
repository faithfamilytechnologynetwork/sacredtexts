"""Synthetic fixtures. Real-SHAPE (verified against catholic_text_json) but
synthetic TEXT — no copyrighted translation is committed to this public repo."""

from __future__ import annotations

from pathlib import Path

import pytest

from sacredbench.schema import Document, Entry

LONG = (
    "And in the first days the keeper of the orchard planted twelve trees upon "
    "the eastern slope and watered each one at morning and at evening without fail"
)
LONG2 = (
    "Blessed is the traveller who shares bread with the stranger at the gate, "
    "for the road remembers every kindness shown beneath the open sky"
)


def make_doc(
    work: str = "Book of Orchards", n: int = 30, version: str = "Test Edition",
    tradition: list[str] | None = None,
) -> Document:
    entries = [
        Entry(
            unit_type="verse",
            citation=f"{work} 1:{i}",
            text=f"{LONG if i % 2 else LONG2} (unit {i} of {work.lower()})",
        )
        for i in range(1, n + 1)
    ]
    return Document(
        tradition=tradition or ["testfaith"],
        work=work,
        version=version,
        language="en",
        document_type="scripture",
        entries=entries,
    )


@pytest.fixture
def two_work_docs() -> list[Document]:
    return [make_doc("Book of Orchards"), make_doc("Book of Roads")]


# The real nabre.json is a TOP-LEVEL LIST of book objects (one file, many books);
# verse text can embed heading strings, which are kept verbatim.
NABRE_SHAPE = [
    {
        "book": "1Orchards",
        "chapters": [
            {
                "chapter": 1,
                "verses": [
                    {"verse": 1, "text": "Preamble. The Making of Orchards " + LONG},
                    {"verse": 2, "text": LONG2},
                    {"verse": 3, "text": ""},
                ],
            },
            {"chapter": 2, "verses": [{"verse": 1, "text": LONG}]},
        ],
    },
    {"book": "2Orchards", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": LONG2}]}]},
]

ENCYCLICAL_SHAPE = {
    "type": "papalEncyclical",
    "pope": "Test Pope",
    "title": "De Testibus",
    "publicationDate": "1900-01-01",
    "vaticanUrl": "https://example.org/de-testibus",
    "language": "en",
    "paragraphs": [
        {"paragraph": None, "text": LONG},
        {"paragraph": 2, "text": LONG2},
        {"paragraph": None, "text": "  "},
    ],
}


@pytest.fixture(scope="session")
def native_decline_movers() -> set[tuple[str, int, str]]:
    """Issue #117: committed cells that native-script decline cues move from incorrect to refused,
    as (run folder under runs/, 0-based row in answers.jsonl, question_id). The committed
    scores.jsonl are not rewritten, so a guard that re-derives committed outcomes expects these
    cells to read `refused`. Registry: testdata/native_decline_movers.tsv."""
    path = Path(__file__).parent / "testdata" / "native_decline_movers.tsv"
    rows = [l.split("\t") for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return {(folder, int(row), qid) for folder, row, qid, _ in rows}
