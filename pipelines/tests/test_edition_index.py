"""The shared edition index (Spec 32, Phase 1).

Schema, ordering, single-wording omission, the restricted-license filter (NABRE never
appears even when its payload is present), and byte-stable / hash-sensitive export.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import dedent

from typer.testing import CliRunner

from sacredbench import catalogue as cat
from sacredbench import generate as gen
from sacredbench.cli import app
from sacredbench.edition_index import (
    cite_key,
    export_rows,
    index_documents,
    load_edition_documents,
    write_export,
)
from sacredbench.schema import Document, Entry

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parents[2]

PROV = (
    "provenance:\n"
    "  retrieved_from: example.org/repo\n"
    "  fetch_method: downloaded\n"
    '  fetch_date: "2026-01-01"\n'
)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text), encoding="utf-8")
    return path


def _bible(book: str, verses: list[tuple[int, int, str]]) -> str:
    return json.dumps([{"book": book, "chapter": c, "verse": v, "text": t} for c, v, t in verses])


def _doc(work: str, version: str, entries: list[tuple[str, str]], language: str = "en") -> Document:
    return Document(
        tradition=["T"],
        work=work,
        version=version,
        language=language,
        document_type="scripture",
        entries=[Entry(unit_type="verse", citation=c, text=t) for c, t in entries],
    )


# --- cite_key: Bible-style only ---------------------------------------------


def test_cite_key_parses_bible_and_rejects_non_bible():
    assert cite_key("Romans 3:23") == ("romans", 3, 23)
    assert cite_key("Song of Solomon 1:1") == ("song of solomon", 1, 1)
    # Arabic surah:ayah (no book token), hadith numbers, Talmud daf:line never parse to a Bible key
    assert cite_key("2:255") is None
    assert cite_key("Sahih al-Bukhari 1") is None
    assert cite_key("Berakhot 2a:1") is None


# --- export rows: schema, ordering, omission --------------------------------


def test_export_rows_schema_ordering_and_single_wording_omitted():
    docs = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "In the beginning God"), ("John 3:16", "For God so loved")]),
        _doc("The Bible", "ASV (1901)", [("Genesis 1:1", "In the beginning God"), ("John 3:16", "For God so loved it")]),
        _doc("The Bible", "WEB", [("Genesis 1:1", "In the beginning, God")]),
        _doc("Book of Mormon", "2013 edition", [("Helaman 5:21", "they were encircled about")]),
    ]
    rows = export_rows(docs)
    # Genesis 1:1 has 3 editions, John 3:16 has 2 -> both are rows; the single-edition
    # Book of Mormon verse is omitted.
    keys = [(r["work"], r["citation"], r["language"]) for r in rows]
    assert keys == [("The Bible", "Genesis 1:1", "en"), ("The Bible", "John 3:16", "en")]  # sorted
    gen_row = rows[0]
    assert [w["version"] for w in gen_row["wordings"]] == ["ASV (1901)", "KJV", "WEB"]  # sorted by version
    assert gen_row["wordings"][1] == {"version": "KJV", "text": "In the beginning God"}
    john = rows[1]
    assert [w["version"] for w in john["wordings"]] == ["ASV (1901)", "KJV"]


def test_index_documents_bucket_by_cite_and_norm():
    docs = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "In the beginning God")]),
        _doc("The Bible", "WEB", [("Genesis 1:1", "In the beginning, God")]),
    ]
    idx = index_documents(docs)
    assert len(idx.by_cite[("genesis", 1, 1)]) == 2
    # passages carry language
    assert {p.language for p in idx.passages} == {"en"}


# --- determinism + hash sensitivity -----------------------------------------


def test_export_is_byte_stable_and_hash_sensitive(tmp_path):
    docs = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "In the beginning God")]),
        _doc("The Bible", "ASV (1901)", [("Genesis 1:1", "In the beginning God")]),
    ]
    m1 = write_export(docs, [], tmp_path / "a.jsonl")
    bytes1 = (tmp_path / "a.jsonl").read_bytes()
    m2 = write_export(docs, [], tmp_path / "b.jsonl")
    bytes2 = (tmp_path / "b.jsonl").read_bytes()
    assert bytes1 == bytes2  # byte-stable on identical input
    assert m1["digest"] == m2["digest"] == hashlib.sha256(bytes1).hexdigest()[:16]
    assert m1["corpus_hash"] == gen.corpus_hash(docs)
    assert m1["row_count"] == 1

    # mutate one wording -> both hashes move
    docs2 = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "In the beginning God")]),
        _doc("The Bible", "ASV (1901)", [("Genesis 1:1", "In the beginning, God.")]),
    ]
    m3 = write_export(docs2, [], tmp_path / "c.jsonl")
    assert m3["digest"] != m1["digest"]
    assert m3["corpus_hash"] != m1["corpus_hash"]


def test_manifest_shape(tmp_path):
    docs = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "a b c d e")]),
        _doc("The Bible", "WEB", [("Genesis 1:1", "a b c d e")]),
    ]
    m = write_export(docs, ["NABRE", "TLG"], tmp_path / "idx.jsonl")
    assert set(m) == {"corpus_hash", "row_count", "digest", "excluded_restricted"}
    assert m["excluded_restricted"] == ["NABRE", "TLG"]
    manifest_on_disk = json.loads((tmp_path / "idx.jsonl.manifest.json").read_text())
    assert manifest_on_disk == m


# --- the restricted-license filter (a present payload is still excluded) -----


def _fixture_raw_with_present_restricted(root: Path) -> Path:
    """A raw tree with two public Bible editions AND a restricted edition whose payload
    is PRESENT locally, all sharing a citation."""
    raw = root / "texts" / "raw"
    _write(
        raw / "Protestant Christian" / "source.yaml",
        PROV
        + "targets:\n"
        "  - payload: kjv.json\n"
        "    converter: bible_flat\n"
        "    work: The Bible\n"
        "    version: KJV\n"
        "    language: en\n"
        "    document_type: scripture\n"
        "    tradition: [Protestant Christian]\n"
        "    license: public-domain\n"
        "    requested_as: [the KJV]\n"
        "    canonical_language: en\n"
        "  - payload: asv.json\n"
        "    converter: bible_flat\n"
        "    work: The Bible\n"
        "    version: ASV (1901)\n"
        "    language: en\n"
        "    document_type: scripture\n"
        "    tradition: [Protestant Christian]\n"
        "    license: public-domain\n"
        "    requested_as: [the ASV]\n"
        "    canonical_language: en\n",
    )
    _write(raw / "Protestant Christian" / "kjv.json", _bible("Genesis", [(1, 1, "In the beginning God")]))
    _write(raw / "Protestant Christian" / "asv.json", _bible("Genesis", [(1, 1, "In the beginning God")]))
    # A restricted fourth edition of the SAME work/citation, payload PRESENT.
    _write(
        raw / "Restricted" / "source.yaml",
        PROV
        + "targets:\n"
        "  - payload: nabre.json\n"
        "    converter: bible_flat\n"
        "    work: The Bible\n"
        "    version: NABRE\n"
        "    language: en\n"
        "    document_type: scripture\n"
        "    tradition: [Roman Catholic]\n"
        "    license: restricted\n"
        "    requested_as: [the NABRE]\n"
        "    canonical_language: en\n",
    )
    _write(raw / "Restricted" / "nabre.json", _bible("Genesis", [(1, 1, "SECRET restricted NABRE wording")]))
    # A non-canonical-language edition (English rendering of a Hebrew-canonical work):
    # language en != canonical_language he, so the pool rule must keep it OUT of the index.
    _write(
        raw / "Translation" / "source.yaml",
        PROV
        + "targets:\n"
        "  - payload: talmud_en.json\n"
        "    converter: bible_flat\n"
        "    work: Talmud Bavli\n"
        "    version: Davidson English\n"
        "    language: en\n"
        "    document_type: scripture\n"
        "    tradition: [Jewish]\n"
        "    license: public-domain\n"
        "    requested_as: [the Talmud]\n"
        "    canonical_language: he\n",
    )
    _write(raw / "Translation" / "talmud_en.json", _bible("Genesis", [(1, 1, "an english rendering")]))
    return raw


def test_cli_edition_index_writes_both_files(tmp_path):
    raw = _fixture_raw_with_present_restricted(tmp_path)
    out = tmp_path / "idx.jsonl"
    result = runner.invoke(app, ["edition-index", "--out", str(out), "--raw-root", str(raw)])
    assert result.exit_code == 0, result.output
    assert out.exists() and (tmp_path / "idx.jsonl.manifest.json").exists()
    manifest = json.loads((tmp_path / "idx.jsonl.manifest.json").read_text())
    assert manifest["excluded_restricted"] == ["NABRE"]
    assert "NABRE" in result.output  # the echo surfaces the exclusions
    # the restricted + non-canonical editions never reach the exported file
    body = out.read_text()
    assert "SECRET" not in body and "english rendering" not in body


def test_restricted_edition_never_indexed_even_when_payload_present(tmp_path):
    raw = _fixture_raw_with_present_restricted(tmp_path)
    docs, excluded = load_edition_documents(raw)
    versions = {d.version for d in docs}
    assert "NABRE" not in versions  # license filter, not payload-absence, excludes it
    assert excluded == ["NABRE"]  # named in the manifest exclusions
    # the non-canonical-language English Talmud edition is kept out by the pool rule
    assert "Davidson English" not in versions
    rows = export_rows(docs)
    serialized = json.dumps(rows, ensure_ascii=False)
    assert "NABRE" not in serialized and "SECRET" not in serialized
    assert "english rendering" not in serialized
    # the two public editions still form a sibling row
    assert rows and [w["version"] for w in rows[0]["wordings"]] == ["ASV (1901)", "KJV"]


def test_conflicting_duplicate_wording_fails_fast():
    import pytest

    from sacredbench.edition_index import EditionIndexError

    docs = [
        _doc("The Bible", "KJV", [("Genesis 1:1", "wording one")]),
        _doc("The Bible", "KJV", [("Genesis 1:1", "a DIFFERENT wording")]),  # same version, conflicts
    ]
    with pytest.raises(EditionIndexError):
        export_rows(docs)


# --- against the real committed catalogue -----------------------------------


def test_real_catalogue_indexes_bibles_and_excludes_restricted():
    raw = REPO_ROOT / "texts" / "raw"
    if not raw.exists():
        import pytest

        pytest.skip("no raw texts tree")
    docs, excluded = load_edition_documents(raw)
    versions = {(d.work, d.version) for d in docs}
    # the three public English Bibles are indexed
    assert ("The Bible", "KJV") in versions
    assert ("The Bible", "ASV (1901)") in versions
    assert ("The Bible", "WEB") in versions
    # NABRE (restricted) is not
    assert ("The Bible", "NABRE") not in versions
    assert "NABRE" in excluded
    # the canonical-language guard keeps non-canonical editions OUT of the index:
    # the English Talmud (en / canonical he) and the Papal Encyclicals (en / canonical la)
    assert ("Talmud Bavli", "William Davidson Edition - English") not in versions
    assert all(d.work != "Papal Encyclicals" for d in docs)
