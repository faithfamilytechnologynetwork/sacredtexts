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

The manifest's ``corpus_hash`` is **generate's corpus hash**, taken over every non-restricted
converted doc (translations included, before the language filter) — the same set ``generate``
hashes — so it is directly comparable to a run manifest's ``corpus_hash``: #21's consumer can
fail-fast unless the index and the run were built from the same corpus.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from sacredbench import catalogue as cat
from sacredbench import convert as conv
from sacredbench import generate as gen
from sacredbench.schema import Document


class EditionIndexError(Exception):
    pass


_CITE = re.compile(r"^(?P<book>.+?)\s+(?P<ch>\d+)\s*:\s*(?P<vs>\d+)\s*$")


@dataclass(frozen=True)
class Passage:
    tradition: str
    work: str
    version: str
    language: str
    citation: str
    text: str


# The ``by_cite`` key: (work, language, raw citation string). export_rows groups on the SAME key,
# so the in-process index and the exported file are the same grouping by construction.
LookupKey = tuple[str, str, str]  # (work, language, citation)


@dataclass
class EditionIndex:
    passages: list[Passage]
    # Keyed on (work, language, citation): work + language are IN the key, so a lookup is already
    # scoped to one work and one language. EVERY raw citation is bucketed (not only Bible-style
    # ones), so the in-process grouping is one-for-one with ``export_rows`` for every work; the
    # Bible-only scope of the counterfactual lives in its consumer (``facct._counterfactual``, via
    # ``lookup_key``), not in the index.
    by_cite: dict[LookupKey, list[Passage]]


def is_verse_citation(citation: str) -> bool:
    """True iff ``citation`` is a Bible-style ``Book chapter:verse`` — the non-Bible guard.

    Arabic ``surah:ayah`` (no book token), hadith numbers, and Talmud ``daf:line`` are not, so a
    consumer using :func:`lookup_key` never matches them to a Bible edition.
    """
    return _CITE.match(citation.strip()) is not None


def lookup_key(work: str, language: str, citation: str) -> LookupKey | None:
    """The ``by_cite`` key for a work's language edition of a Bible-style citation, else None.

    Returns None for non-verse citations, so the Spec 32 counterfactual (its only caller) never
    looks a non-Bible citation up — even though such citations ARE bucketed in the index.
    """
    return (work, language, citation) if is_verse_citation(citation) else None


def index_documents(docs: list[Document]) -> EditionIndex:
    """Build the in-process index: every passage bucketed by (work, language, citation)."""
    passages: list[Passage] = []
    by_cite: dict[LookupKey, list[Passage]] = defaultdict(list)
    for doc in docs:
        # NOTE: this collapses the tradition LIST to its first element (arch invariant:
        # "tradition is a LIST"). Fine for the edition index (it only needs edition identity),
        # but a consumer that needs tradition (e.g. the Spec 32 census) must read it from the
        # catalogue/question source, NOT from Passage.tradition.
        tradition = doc.tradition[0] if doc.tradition else "unknown"
        for entry in doc.entries:
            passage = Passage(
                tradition=tradition,
                work=doc.work,
                version=doc.version,
                language=doc.language,
                citation=entry.citation,
                text=entry.text,
            )
            passages.append(passage)
            by_cite[(doc.work, doc.language, entry.citation)].append(passage)  # every raw citation
    return EditionIndex(passages=passages, by_cite=dict(by_cite))


def load_edition_documents(
    raw_root: Path = cat.RAW_ROOT,
) -> tuple[list[Document], list[Document], list[str]]:
    """Convert the corpus from ``texts/raw/**`` and name the restricted exclusions.

    Reads raw payloads through ``convert.convert_target`` (as the audit does), never the gitignored
    ``texts/standardized/``. Returns ``(indexed_docs, all_nonrestricted_docs, excluded_restricted)``:

    - ``indexed_docs`` — the same-canonical-language editions (the question-pool rule, Spec 26); the
      index and the export rows are built from these.
    - ``all_nonrestricted_docs`` — **every** non-restricted converted doc, translations included,
      BEFORE the language filter. This is exactly the set ``generate`` hashes, so a ``corpus_hash``
      over it equals a run manifest's ``corpus_hash`` for the same corpus (what #21's consumer check
      compares).
    - ``excluded_restricted`` — sorted, de-duplicated versions of the restricted targets that would
      otherwise be eligible siblings (``language == canonical_language``): the NABRE / TLG exclusions.
    """
    sources = cat.discover_catalogue(raw_root)
    all_docs: list[Document] = []
    indexed: list[Document] = []
    for t in sorted(
        cat.select_targets(sources, include_restricted=False),
        key=lambda t: (t.work, t.version, t.language),
    ):
        docs = conv.convert_target(t.payload_paths(raw_root), t)
        all_docs.extend(docs)
        if t.language == t.canonical_language:
            indexed.extend(docs)
    excluded_restricted = sorted(
        {
            t.version
            for t in cat.all_targets(sources)
            if t.license == "restricted" and t.language == t.canonical_language
        }
    )
    return indexed, all_docs, excluded_restricted


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


def build_manifest(all_docs: list[Document], body: str, excluded_restricted: list[str]) -> dict:
    """The sibling ``.manifest.json`` for an export whose JSONL bytes are ``body``.

    ``corpus_hash`` is **generate's corpus hash** over ``all_docs`` (every non-restricted converted
    doc — the same set ``generate`` hashes), so it equals a run manifest's ``corpus_hash`` for the
    same corpus and #21's consumer can fail-fast when the index was built from a different corpus.
    ``digest`` = sha256[:16] of the written JSONL bytes.
    """
    return {
        "corpus_hash": gen.corpus_hash(all_docs),
        "row_count": body.count("\n"),
        "digest": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
        "excluded_restricted": list(excluded_restricted),
    }


def atomic_write_texts(payloads: list[tuple[Path, str]]) -> None:
    """Write several (path, text) files atomically — all or none.

    Each file is staged to a collision-safe temp (``tempfile.mkstemp`` in its own parent dir) and
    swapped into place with ``os.replace``; if a later swap fails, the already-swapped targets are
    rolled back to their prior bytes (or removed if new), and every temp/backup is cleaned up. Shared
    by the edition-index export and the FAccT card writer so there is one both-or-neither path.
    """
    staged: list[tuple[Path, Path]] = []  # (temp, final)
    try:
        for final, text in payloads:
            final.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(final.parent), prefix=final.name + ".", suffix=".tmp")
            os.close(fd)
            Path(tmp).write_text(text, encoding="utf-8")
            staged.append((Path(tmp), final))
    except BaseException:
        for tmp, _final in staged:
            tmp.unlink(missing_ok=True)
        raise

    swapped: list[tuple[Path, Path | None]] = []  # (final, backup-or-None)
    pending_backup: Path | None = None
    try:
        for tmp, final in staged:
            pending_backup = None
            if final.exists():
                fd, bak = tempfile.mkstemp(dir=str(final.parent), prefix=final.name + ".bak.")
                os.close(fd)
                shutil.copy2(final, bak)
                pending_backup = Path(bak)
            os.replace(tmp, final)
            swapped.append((final, pending_backup))
            pending_backup = None
    except BaseException:
        if pending_backup is not None:
            pending_backup.unlink(missing_ok=True)
        for final, backup in reversed(swapped):
            if backup is not None:
                os.replace(backup, final)
            else:
                final.unlink(missing_ok=True)
        for tmp, _final in staged:
            tmp.unlink(missing_ok=True)
        raise
    finally:
        for _final, backup in swapped:
            if backup is not None:
                backup.unlink(missing_ok=True)


def write_export(
    indexed_docs: list[Document],
    all_docs: list[Document],
    excluded_restricted: list[str],
    out_path: Path,
) -> dict:
    """Write ``out_path`` (JSONL rows from ``indexed_docs``) and ``<out_path>.manifest.json``.

    Both-or-neither: rows (which may raise :class:`EditionIndexError` on a conflicting duplicate) and
    the manifest (``corpus_hash`` over ``all_docs``) are built before anything is written, then both
    files are written atomically via :func:`atomic_write_texts`.
    """
    out_path = Path(out_path)
    body = _serialize_rows(export_rows(indexed_docs))
    manifest = build_manifest(all_docs, body, excluded_restricted)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=1) + "\n"
    manifest_path = out_path.with_name(out_path.name + ".manifest.json")
    atomic_write_texts([(out_path, body), (manifest_path, manifest_text)])
    return manifest
