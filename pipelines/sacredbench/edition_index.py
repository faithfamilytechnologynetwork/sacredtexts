"""Editions that share a citation — the shared cross-edition producer.

The citation/index machinery here is carried over from the cross-edition reading in
PR #30 (Jonathan Karr). It is a *shared* producer with two consumers:

- the FAccT card (Spec 32) builds its edition counterfactual from the in-process
  :class:`EditionIndex`;
- issue #21 (the passage-equivalence judge) consumes the exported JSONL + manifest.

Only same-canonical-language editions are indexed (``language == canonical_language``,
the pool rule), and ``restricted``-licensed targets are never indexed or exported, so a
restricted edition of a work already in the index (e.g. NABRE, a fourth English Bible)
can never become a sibling — even when its held-back payload is present locally. The
file export is deterministic: rows sorted by ``(work, citation, language)``, wordings
sorted by version, and rows with a single wording omitted.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from sacredbench import catalogue as cat
from sacredbench import convert as conv
from sacredbench import generate as gen
from sacredbench.schema import Document
from sacredbench.score import normalize


class EditionIndexError(Exception):
    pass


# normalize() turns an apostrophe into a space, so "Solomon's Song" is "solomon s
# song". The two KJV files name that book differently. (Carried over from PR #30.)
_BOOK_ALIAS = {
    "solomon s song": "song of solomon",
}

_CITE = re.compile(r"^(?P<book>.+?)\s+(?P<ch>\d+)\s*:\s*(?P<vs>\d+)\s*$")


@dataclass(frozen=True)
class Passage:
    tradition: str
    work: str
    version: str
    language: str
    citation: str
    text: str
    norm: str
    cite_key: tuple[str, int, int] | None
    book: str | None


@dataclass
class EditionIndex:
    passages: list[Passage]
    # NOTE: by_cite is keyed on the Bible-style (book, chapter, verse) ONLY — it carries no
    # ``work`` component, and LDS scriptures also use Book-chapter:verse citations. A consumer
    # that wants Bible editions (e.g. the Spec 32 counterfactual) must filter on
    # ``passage.work == "The Bible"``, not trust the cite-key alone.
    by_cite: dict[tuple[str, int, int], list[Passage]]
    by_norm: dict[str, list[Passage]]


def cite_key(citation: str) -> tuple[str, int, int] | None:
    """``(book, chapter, verse)`` for a Bible-style verse citation, else None.

    Book names are folded with the scorer's ``normalize`` plus the Song of Solomon
    alias, so editions that name a book differently line up. Non-``Book chapter:verse``
    citations (Arabic ``surah:ayah`` with no book, hadith numbers, Talmud ``daf:line``)
    return None and are therefore never matched to a Bible edition.
    """
    match = _CITE.match(citation.strip())
    if not match:
        return None
    book = normalize(match.group("book"))
    book = _BOOK_ALIAS.get(book, book)
    return book, int(match.group("ch")), int(match.group("vs"))


def _book_display(citation: str) -> str | None:
    match = _CITE.match(citation.strip())
    return match.group("book") if match else None


def index_documents(docs: list[Document]) -> EditionIndex:
    """Build the in-process index: passages keyed by Bible cite-key and by normalized text."""
    passages: list[Passage] = []
    by_cite: dict[tuple[str, int, int], list[Passage]] = defaultdict(list)
    by_norm: dict[str, list[Passage]] = defaultdict(list)
    for doc in docs:
        tradition = doc.tradition[0] if doc.tradition else "unknown"
        for entry in doc.entries:
            key = cite_key(entry.citation)
            passage = Passage(
                tradition=tradition,
                work=doc.work,
                version=doc.version,
                language=doc.language,
                citation=entry.citation,
                text=entry.text,
                norm=normalize(entry.text),
                cite_key=key,
                book=_book_display(entry.citation),
            )
            passages.append(passage)
            if key is not None:
                by_cite[key].append(passage)
            if passage.norm:
                by_norm[passage.norm].append(passage)
    return EditionIndex(passages=passages, by_cite=dict(by_cite), by_norm=dict(by_norm))


def load_edition_documents(raw_root: Path = cat.RAW_ROOT) -> tuple[list[Document], list[str]]:
    """Convert the indexable corpus from ``texts/raw/**`` and name the restricted exclusions.

    Reads raw payloads through ``convert.convert_target`` (as the audit does), never the
    gitignored ``texts/standardized/``. Keeps only non-restricted, same-canonical-language
    editions. Returns ``(docs, excluded_restricted)`` where ``excluded_restricted`` is the
    sorted, de-duplicated versions of the restricted targets that would otherwise be
    eligible siblings (``language == canonical_language``) — the NABRE / TLG exclusions.
    """
    sources = cat.discover_catalogue(raw_root)
    docs: list[Document] = []
    for t in sorted(
        cat.select_targets(sources, include_restricted=False),
        key=lambda t: (t.work, t.version, t.language),
    ):
        if t.language != t.canonical_language:
            continue  # original-language editions only — the question-pool rule (Spec 26)
        docs.extend(conv.convert_target(t.payload_paths(raw_root), t))
    excluded_restricted = sorted(
        {
            t.version
            for t in cat.all_targets(sources)
            if t.license == "restricted" and t.language == t.canonical_language
        }
    )
    return docs, excluded_restricted


def export_rows(docs: list[Document]) -> list[dict]:
    """The frozen export rows (one per ``(work, citation, language)`` with ≥2 wordings).

    Schema (frozen for issue #21): ``{"work", "citation", "language", "wordings":
    [{"version", "text"}, …]}`` — wordings sorted by version, single-wording rows omitted,
    rows sorted by ``(work, citation, language)``.
    """
    groups: dict[tuple[str, str, str], dict[str, str]] = {}
    for doc in docs:
        for entry in doc.entries:
            key = (doc.work, entry.citation, doc.language)
            vmap = groups.setdefault(key, {})
            # one wording per version; a second, DIFFERING wording for the same
            # (work, citation, version) is a data conflict — fail fast rather than
            # silently drop one (this producer's output is consumed by #21).
            if doc.version in vmap and vmap[doc.version] != entry.text:
                raise EditionIndexError(
                    f"conflicting wordings for {doc.work!r} {entry.citation!r} "
                    f"[{doc.version}] in {doc.language}"
                )
            vmap[doc.version] = entry.text
    rows: list[dict] = []
    for (work, citation, language), vmap in groups.items():
        if len(vmap) < 2:
            continue  # a citation with a single indexed wording is not a sibling set
        wordings = [{"version": v, "text": vmap[v]} for v in sorted(vmap)]
        rows.append({"work": work, "citation": citation, "language": language, "wordings": wordings})
    rows.sort(key=lambda r: (r["work"], r["citation"], r["language"]))
    return rows


def _serialize_rows(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def build_manifest(docs: list[Document], body: str, excluded_restricted: list[str]) -> dict:
    """The sibling ``.manifest.json`` for an export whose JSONL bytes are ``body``.

    ``corpus_hash`` = ``generate.corpus_hash`` over all indexed docs (before the
    single-wording omission); ``digest`` = sha256[:16] of the written JSONL bytes.
    """
    return {
        "corpus_hash": gen.corpus_hash(docs),
        "row_count": body.count("\n"),
        "digest": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
        "excluded_restricted": list(excluded_restricted),
    }


def write_export(docs: list[Document], excluded_restricted: list[str], out_path: Path) -> dict:
    """Write ``out_path`` (JSONL) and ``<out_path>.manifest.json``; return the manifest."""
    out_path = Path(out_path)
    body = _serialize_rows(export_rows(docs))
    manifest = build_manifest(docs, body, excluded_restricted)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    manifest_path = out_path.with_name(out_path.name + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return manifest
