"""Rebuild the review question files from texts/raw.

Each file has a uniform population sample of 30 and a separate familiarity
panel (every citation in well_known.yaml). Sikh citations are Ang N:k in
reading order. Within each sample, half of the verify_source rows quote a
different work and expect "no".
"""

from __future__ import annotations

import hashlib
import html
import json
import random
import re
import urllib.parse
import urllib.request
from pathlib import Path

from sacredbench.convert import _SGGS_ANG_ERRATA, clean_sggs_line
from sacredbench.generate import split_quote
from sacredbench.item_sample import Passage, draw_passages, load_well_known

REVIEW = Path(__file__).resolve().parent
RAW = Path(__file__).resolve().parents[3] / "texts" / "raw"
TAG = re.compile(r"<[^>]+>")
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
MIN_WORDS = 16

# The six canonical hadith collections (Kutub al-Sittah), Arabic from sunnah.com.
# These are the Qur'an's same-script "no" donors (issue #75). (file, work) mirrors
# texts/raw/Sunni Islam/source.yaml; #74 trims Malik/Ahmad/Darimi from the catalogue.
HADITH_COLLECTIONS = (
    ("bukhari.json", "Sahih al-Bukhari"),
    ("muslim.json", "Sahih Muslim"),
    ("abudawud.json", "Sunan Abi Dawud"),
    ("tirmidhi.json", "Jami` at-Tirmidhi"),
    ("nasai.json", "Sunan an-Nasa'i"),
    ("ibnmajah.json", "Sunan Ibn Majah"),
)
HADITH_VERSION = "sunnah.com Arabic"

EN = {
    "retrieve_quote": "What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.",
    "complete_unit": 'Complete this quotation from {version}: "{head}" Reply with only the remaining words.',
    "cite_passage": 'Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.',
    "verify_source": 'Is the following text from {version}? "{text}" Answer Yes or No.',
}


# English display names the model sees in a prompt, overriding the default
# "the {version} edition". The catalogue `version` string is unchanged in each
# question's source metadata; only the prompt wording changes. The Qur'an is named
# "the Uthmani Qur'an" (no "QUL"), owner-signed 2026-11-01 (issue #75).
_EDITION_DISPLAY = {"Uthmani (QUL)": "the Uthmani Qur'an"}


def edition_name(name: str) -> str:
    if name in _EDITION_DISPLAY:
        return _EDITION_DISPLAY[name]
    if "edition" in name.lower():
        return name
    return f"the {name} edition"


def famous_passages(work: str, version: str) -> list[Passage]:
    path = REVIEW.parents[0] / "well_known.yaml"
    return [p for p in load_well_known(path) if p.work == work and p.version == version]


def population_draw(pool: list[Passage], famous: list[Passage], *, seed: int) -> list[Passage]:
    """Thirty passages, uniform, with the pre-registered familiar citations removed.

    The familiar list is reported as its own panel. Leaving it inside this draw,
    or reserving a quarter of the draw for it, would bias the population estimate
    toward lines models have memorized, and that bias is larger for some traditions
    than others.
    """
    famous_ids = {p.citation for p in famous}
    eligible = [p for p in pool if p.citation not in famous_ids]
    return [p for p, _ in draw_passages(eligible, [], n=30, famous_share=0, seed=seed)]


def clean_html(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub("", s))).strip()


def split_words(text: str) -> tuple[str, str]:
    return split_quote(text)


def rows_for(items, *, tradition, version, native_tmpl, english_version=None, english_native_tmpl=None):
    citations = [passage.citation for passage, _, _, _ in items]
    out = []
    for passage, sample, native, english in items:
        head, rest = split_words(native)
        example = next(c for c in citations if c != passage.citation)
        fields = {
            "citation": passage.citation, "version": edition_name(version),
            "head": head, "text": native, "example": example,
        }
        en_q = {k: EN[k].format(**fields) for k in TASKS}
        nat_q = {k: native_tmpl[k].format(**fields) for k in TASKS}
        expected = {
            "retrieve_quote": {"text": native},
            "complete_unit": {"text": rest, "full_text": native},
            "cite_passage": {"citation": passage.citation},
            "verify_source": {
                "answer": "yes", "true_tradition": tradition,
                "true_version": version, "true_citation": passage.citation,
            },
        }
        base = {
            "tradition": tradition,
            "citation": passage.citation,
            "sample": sample,
            "stratum": "famous" if sample == "familiarity" else "ordinary",
            "version": version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            # Two calls, not one bilingual prompt. The English call still says which
            # language to answer in. The native call is only the native-language question.
            out.append({
                **base, "task": task, "condition": "ask_english",
                "prompt": f"{en_q[task]}\nAnswer in the language of {edition_name(version)}.",
                "expected": expected[task],
            })
            out.append({
                **base, "task": task, "condition": "ask_native",
                "prompt": nat_q[task],
                "expected": expected[task],
            })
        if english is None:
            continue
        head_e, rest_e = split_words(english)
        fields_e = {
            "citation": passage.citation, "version": edition_name(english_version),
            "head": head_e, "text": english, "example": example,
        }
        en_q2 = {k: EN[k].format(**fields_e) for k in TASKS}
        nat_q2 = {k: english_native_tmpl[k].format(**fields_e) for k in TASKS}
        expected_e = {
            "retrieve_quote": {"text": english},
            "complete_unit": {"text": rest_e, "full_text": english},
            "cite_passage": {"citation": passage.citation},
            "verify_source": {
                "answer": "yes", "true_tradition": tradition,
                "true_version": english_version, "true_citation": passage.citation,
            },
        }
        for task in TASKS:
            if task == "complete_unit" and not rest_e.strip():
                continue
            # One English question. The edition name is already in that line.
            prompt = en_q2[task]
            out.append({
                **base, "task": task, "condition": "en_ask_en_answer",
                "english_version": english_version, "prompt": prompt, "expected": expected_e[task],
            })
    return out


def islam() -> list[dict]:
    quran = json.loads((RAW / "Sunni Islam" / "quran_uthmani_from_qul.json.json").read_text())
    famous_rows = famous_passages("The Qur'an", "Uthmani (QUL)")
    famous_cit = {p.citation: p for p in famous_rows}
    ordinary, famous = [], []
    for key, row in quran.items():
        text = row["text"].strip()
        if len(text.split()) >= MIN_WORDS:
            passage = famous_cit.get(key) or Passage(key, "The Qur'an", "Uthmani (QUL)")
            ordinary.append((passage, text))
        elif key in famous_cit:
            famous.append((famous_cit[key], text))
    missing = set(famous_cit) - set(quran)
    if missing:
        raise SystemExit(f"Qur'an famous citations missing from QUL: {sorted(missing)}")
    drawn = population_draw([p for p, _ in ordinary], famous_rows, seed=20261030)
    text = {p.citation: t for p, t in ordinary + famous}
    # Owner-signed Arabic templates (Waleed, native Arabic speaker, 2026-11-01). "رسم" is
    # orthography not a print run ("طبعة"), "النص" for revelation, "رقم السورة والآية" for the
    # reference, and a closing "فقط" because Arabic-prompted models tend to open with a preamble
    # before the verdict (see METHODOLOGY.md).
    ar = {
        "retrieve_quote": "ما نص الموضع {citation} في القرآن الكريم بالرسم العثماني؟ أجب بالنص المطابق لهذه النسخة فقط، دون أي زيادة.",
        "complete_unit": 'أكمل هذا النص من القرآن الكريم بالرسم العثماني: "{head}" أجب بالكلمات المتبقية فقط.',
        "cite_passage": 'أين ورد هذا النص في القرآن الكريم بالرسم العثماني؟ "{text}" أجب برقم السورة والآية فقط، بالصيغة نفسها: {example}.',
        "verify_source": 'هل النص التالي من القرآن الكريم بالرسم العثماني؟ "{text}" أجب بـ«نعم» أو «لا» فقط.',
    }
    items = [(p, "population", text[p.citation], None) for p in drawn]
    items += [(famous_cit[c], "familiarity", text[c], None) for c in famous_cit]
    return rows_for(items, tradition="Islam", version="Uthmani (QUL)", native_tmpl=ar)


def sikhism() -> list[dict]:
    lines = json.loads((RAW / "Sikhism" / "sggs_shabados.json").read_text())["lines"]
    prev_ang, k = 0, 0
    pool = []
    for rec in lines:
        ang = rec["ang"]
        if rec.get("id") in _SGGS_ANG_ERRATA:
            _upstream, correct = _SGGS_ANG_ERRATA[rec["id"]]
            ang = correct
        k = k + 1 if ang == prev_ang else 1
        prev_ang = ang
        text = clean_sggs_line(rec["data"])
        if text:
            pool.append((f"Ang {ang}:{k}", text))
    text = dict(pool)
    famous = famous_passages("Sri Guru Granth Sahib", "Shabad OS (SGPC Shabadaarth)")
    missing = {p.citation for p in famous} - set(text)
    if missing:
        raise SystemExit(f"SGGS famous citations missing: {sorted(missing)}")
    ordinary = [
        Passage(cit, "Sri Guru Granth Sahib", "Shabad OS (SGPC Shabadaarth)")
        for cit, body in pool
        if len(body.split()) >= MIN_WORDS
    ]
    drawn = population_draw(ordinary, famous, seed=20261030)
    pa = {
        "retrieve_quote": "{citation} ਦਾ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਵਿਚੋਂ ਦੱਸੋ। ਸਿਰਫ਼ ਉਸੇ ਅਡੀਸ਼ਨ ਦਾ ਪਾਠ ਲਿਖੋ।",
        "complete_unit": 'ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਵਿਚੋਂ ਇਹ ਟੋਟਾ ਪੂਰਾ ਕਰੋ: "{head}" ਸਿਰਫ਼ ਬਾਕੀ ਸ਼ਬਦ ਲਿਖੋ।',
        "cite_passage": 'ਇਹ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਵਿਚ ਕਿੱਥੇ ਹੈ? "{text}" ਸਿਰਫ਼ ਹਵਾਲਾ ਲਿਖੋ, ਇਸ ਰੂਪ ਵਿਚ: {example}.',
        "verify_source": 'ਕੀ ਇਹ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਵਿਚੋਂ ਹੈ? "{text}" ਹਾਂ ਜਾਂ ਨਹੀਂ।',
    }
    items = [(p, "population", text[p.citation], None) for p in drawn]
    items += [(p, "familiarity", text[p.citation], None) for p in famous]
    return rows_for(items, tradition="Sikhism", version="Shabad OS (SGPC Shabadaarth)", native_tmpl=pa)


def judaism() -> list[dict]:
    root = RAW / "Judaism" / "Talmud Bavli"
    pairs = []
    for he_path in sorted(root.glob("* - he - William Davidson Edition - Aramaic.json")):
        tract = he_path.name.split(" - he - ")[0]
        en_path = root / f"{tract} - en - William Davidson Edition - English.json"
        if not en_path.exists():
            continue
        he = json.loads(he_path.read_text())["text"]
        en = json.loads(en_path.read_text())["text"]
        if len(he) != len(en):
            raise SystemExit(f"{tract}: Aramaic has {len(he)} sections, English has {len(en)}")
        for i, (sec_h, sec_e) in enumerate(zip(he, en)):
            if not sec_h or not sec_e:
                continue
            daf = (i // 2) + 1
            side = "a" if i % 2 == 0 else "b"
            # A daf side can end with one extra segment in one edition. Pair only
            # the shared indexes. An unpaired tail has no wording in the other edition.
            paired = min(len(sec_h), len(sec_e))
            for n, (a, b) in enumerate(zip(sec_h[:paired], sec_e[:paired]), start=1):
                if not isinstance(a, str) or not isinstance(b, str):
                    continue
                ha, eb = clean_html(a), clean_html(b)
                if len(ha.split()) >= MIN_WORDS and len(eb.split()) >= MIN_WORDS:
                    pairs.append((f"{tract} {daf}{side}:{n}", ha, eb))
                    break
    text = {c: (h, e) for c, h, e in pairs}
    famous = famous_passages("Talmud Bavli", "William Davidson Edition - Aramaic")
    missing = {p.citation for p in famous} - set(text)
    if missing:
        raise SystemExit(f"Talmud famous citations missing: {sorted(missing)}")
    ordinary = [
        Passage(c, "Talmud Bavli", "William Davidson Edition - Aramaic")
        for c in text
    ]
    drawn = population_draw(ordinary, famous, seed=20261030)
    he = {
        "retrieve_quote": "מהו נוסח {citation} בתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית? ענה בנוסח אותה מהדורה בלבד.",
        "complete_unit": 'השלם ציטוט זה מהתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית: "{head}" ענה במילים הנותרות בלבד.',
        "cite_passage": 'היכן בתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית, נמצא הטקסט הזה? "{text}" ענה בציון המקום בלבד, בצורה: {example}.',
        "verify_source": 'האם הטקסט הבא מן התלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית? "{text}" ענה כן או לא.',
    }
    he_en = {
        "retrieve_quote": "מהו הנוסח האנגלי של {citation} בתלמוד הבבלי, מהדורת ויליאם דייווידסון האנגלית? ענה בנוסח אותה מהדורה בלבד.",
        "complete_unit": 'השלם ציטוט זה מהתלמוד הבבלי, מהדורת ויליאם דייווידסון האנגלית: "{head}" ענה במילים הנותרות בלבד.',
        "cite_passage": 'היכן בתלמוד הבבלי, מהדורת ויליאם דייווידסון האנגלית, נמצא הטקסט הזה? "{text}" ענה בציון המקום בלבד, בצורה: {example}.',
        "verify_source": 'האם הטקסט הבא מן התלמוד הבבלי, מהדורת ויליאם דייווידסון האנגלית? "{text}" ענה כן או לא.',
    }
    items = [(p, "population", *text[p.citation]) for p in drawn]
    items += [(p, "familiarity", *text[p.citation]) for p in famous]
    rows = rows_for(
        items, tradition="Judaism", version="William Davidson Edition - Aramaic",
        native_tmpl=he, english_version="William Davidson Edition - English",
        english_native_tmpl=he_en,
    )
    note = "William Davidson Edition on Sefaria, CC-BY-NC. Attribute Sefaria and the William Davidson Edition."
    for row in rows:
        row["license"] = note
    return rows


NOTICE = (
    "Scripture quotations are from the New Revised Standard Version Bible, "
    "copyright © 1989 National Council of the Churches of Christ in the United States of America. "
    "Used by permission. All rights reserved worldwide."
)
_PSALM_HEAD = re.compile(r"^Psalm\s+\d+\s+\d+\s+")
_OREMUS_BOOK = {"Psalms": "Psalm", "Song of Solomon": "Song of Songs"}


def fetch_nrsv(citation: str) -> str:
    """One verse from oremus's NRSV. The draw uses the Protestant citation list; this is the wording."""
    book, ref = citation.rsplit(" ", 1)
    query = f"{_OREMUS_BOOK.get(book, book)} {ref}"
    url = "https://bible.oremus.org/?version=nrsv&passage=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "academic-nrsv-draw"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    match = re.search(r'class="bibletext">(.*?)</div>', raw, re.S)
    if not match:
        raise SystemExit(f"no NRSV text for {citation}")
    chunk = re.sub(r"<[^>]+>", " ", match.group(1))
    chunk = html.unescape(re.sub(r"\s+", " ", chunk)).strip()
    chunk = re.sub(r"^\d+\s*", "", chunk).strip(" “”\"")
    chunk = _PSALM_HEAD.sub("", chunk)
    if not chunk:
        raise SystemExit(f"empty NRSV text for {citation}")
    return chunk


def christianity() -> list[dict]:
    """Seeded draw over the Protestant verse list. Wording is NRSV, not KJV."""
    kjv = json.loads((RAW / "Protestant Christian" / "kjv.json").read_text())
    famous = famous_passages("The Bible", "NRSV")
    famous_ids = {p.citation for p in famous}
    ordinary = []
    for row in kjv:
        citation = f"{row['book']} {row['chapter']}:{row['verse']}"
        if len(row["text"].split()) >= MIN_WORDS:
            ordinary.append(Passage(citation, "The Bible", "NRSV"))
    missing = famous_ids - {f"{r['book']} {r['chapter']}:{r['verse']}" for r in kjv}
    if missing:
        raise SystemExit(f"NRSV famous citations missing from the Protestant verse list: {sorted(missing)}")
    drawn = population_draw(ordinary, famous, seed=20261030)
    panel = list(drawn) + list(famous)
    verses = {p.citation: fetch_nrsv(p.citation) for p in panel}
    version = "the New Revised Standard Version (NRSV)"
    citations = [p.citation for p in panel]
    rows = []
    for passage in panel:
        sample = "population" if passage in drawn else "familiarity"
        text = verses[passage.citation]
        head, rest = split_words(text)
        example = next(c for c in citations if c != passage.citation)
        base = {
            "tradition": "Christianity", "citation": passage.citation,
            "sample": sample,
            "stratum": "famous" if sample == "familiarity" else "ordinary",
            "version": "NRSV", "condition": "en_ask_en_answer", "copyright": NOTICE,
        }
        specs = [
            ("retrieve_quote", f"What is the text of {passage.citation} in {version}? Reply with the exact text of that edition and nothing else.", {"text": text}),
            ("complete_unit", f'Please complete this quote from {version}: "{head}" Reply with only the remaining words.', {"text": rest, "full_text": text}),
            ("cite_passage", f'Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.', {"citation": passage.citation}),
            ("verify_source", f'Is the following text from {version}? "{text}" Answer Yes or No.', {
                "answer": "yes", "true_tradition": "Christianity", "true_version": "NRSV",
                "true_language": "en", "true_citation": passage.citation,
            }),
        ]
        for task, prompt, expected in specs:
            if task == "complete_unit" and not rest.strip():
                continue
            rows.append({**base, "task": task, "prompt": prompt, "expected": expected})
    return rows


def _script(text: str) -> str:
    for ch in text:
        o = ord(ch)
        if 0x0590 <= o <= 0x05FF:
            return "he"
        if 0x0600 <= o <= 0x06FF:
            return "ar"
        if 0x0900 <= o <= 0x097F:
            return "sa"
        if 0x0A00 <= o <= 0x0A7F:
            return "pa"
        if 0x0370 <= o <= 0x03FF:
            return "grc"
    return "lat"


_NT = {
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
}


def _donor_rank(row: dict, donor: dict) -> int:
    """0 is the nearest same-language other work. 2 is a different script."""
    row_script = _script(row["expected"]["text"] if row["task"] == "retrieve_quote" else row["prompt"])
    donor_script = _script(donor["expected"]["text"])
    if donor["tradition"] == row["tradition"] or donor_script != row_script:
        return 2
    version = donor.get("version", "")
    if row["tradition"] == "Judaism" and row_script == "he" and "Masoretic" in version:
        return 0
    if row["tradition"] == "Judaism" and row.get("condition") == "en_ask_en_answer" and version == "NRSV":
        book = donor["citation"].rsplit(" ", 1)[0]
        return 0 if book not in _NT else 2
    if row["tradition"] == "Christianity" and "Masoretic" in row.get("version", "") and donor["tradition"] == "Judaism":
        return 0
    if row["tradition"] == "Christianity" and row.get("condition") == "en_ask_en_answer" and donor.get("work") == "Book of Mormon":
        return 0
    return 1


def _hadith_donors() -> list[dict]:
    """Every >=16-word hadith in the six canonical collections, as donor rows.

    Shaped like a ``retrieve_quote`` donor (``tradition``/``version``/``citation``
    + ``expected.text``) so ``add_verify_negatives`` can use them directly. Citation
    and version mirror ``convert_hadith_sunnah`` so a "no" item records the same
    ``true_version``/``true_citation`` the standardized corpus would.
    """
    donors: list[dict] = []
    for filename, work in HADITH_COLLECTIONS:
        data = json.loads((RAW / "Sunni Islam" / "hadith_from_sunnah.com_arabic_only" / filename).read_text())
        for h in data["hadiths"]:
            text = (h.get("arabic") or "").strip()
            if len(text.split()) < MIN_WORDS:
                continue
            donors.append({
                "tradition": "Islam",
                "work": work,
                "version": HADITH_VERSION,
                "citation": f"{work} {h['idInBook']}",
                "expected": {"text": text},
            })
    if not donors:
        raise SystemExit("no hadith donors found for the Qur'an verify_source 'no' items")
    return donors


def add_verify_negatives(by_name: dict[str, list[dict]]) -> None:
    """Half of each condition's verify_source rows quote a different work.

    The donor is the same script as the passage being checked, and a nearer
    work when this corpus has one. A different tradition in another script is
    the fallback for a language that has only one work. For the Qur'an, whose
    only same-script neighbours are the hadith collections, the donor is a
    hadith matn (same script, same tradition, different work) so the item is a
    real "Qur'an or hadith?" judgement rather than an alphabet test (issue #75).
    """
    donors = []
    for rows in by_name.values():
        for row in rows:
            if row["task"] == "retrieve_quote" and row["condition"] in {"ask_english", "ask_native", "en_ask_en_answer"}:
                donors.append(row)
    rng = random.Random(20261030)
    # Islam draws from its own pool with an independent RNG, so Islam can be rebuilt
    # in isolation and the shared `rng` stream stays byte-stable for traditions built
    # after Islam (e.g. Sikhism).
    hadith_donors = _hadith_donors()
    hadith_rng = random.Random(20261030)
    for rows in by_name.values():
        groups: dict[tuple[str, str], list[dict]] = {}
        for row in rows:
            if row["task"] == "verify_source":
                groups.setdefault((row["condition"], row["sample"]), []).append(row)
        for group in groups.values():
            group.sort(key=lambda r: r["citation"])
            flip = group[: len(group) // 2]
            for row in flip:
                ranked = [d for d in donors if d["tradition"] != row["tradition"]]
                best = min((_donor_rank(row, d) for d in ranked), default=2)
                pool = [d for d in ranked if _donor_rank(row, d) == best] or ranked
                # The cross-tradition draw advances the shared RNG even for Islam (whose
                # result is replaced below), keeping later traditions' draws unchanged.
                donor = rng.choice(pool) if pool else None
                if row["tradition"] == "Islam":
                    donor = hadith_rng.choice(hadith_donors)
                text = donor["expected"]["text"]
                row["expected"] = {
                    "answer": "no",
                    "true_tradition": donor["tradition"],
                    "true_version": donor["version"],
                    "true_citation": donor["citation"],
                }
                lines = row["prompt"].split("\n")
                for i, line in enumerate(lines):
                    a = line.find('"')
                    b = line.find('"', a + 1) if a != -1 else -1
                    if a != -1 and b != -1:
                        lines[i] = line[: a + 1] + text + line[b:]
                row["prompt"] = "\n".join(lines)


_RUN_META = {
    "Christianity": ("The Bible", "en", "scripture"),
    "Judaism": ("Talmud Bavli", "he", "talmud"),
    "Islam": ("The Qur'an", "ar", "scripture"),
    "Sikhism": ("Sri Guru Granth Sahib", "pa", "scripture"),
}


def _collect_row(row: dict) -> dict:
    work, language, document_type = _RUN_META[row["tradition"]]
    asked = row.get("english_version") or row["version"]
    if row["condition"] == "en_ask_en_answer":
        language = "en"
    expected = row["expected"]
    citation = row["citation"]
    if row["task"] == "verify_source" and expected.get("answer") == "no":
        citation = ""
    source = {
        "tradition": [row["tradition"]],
        "work": work,
        "version": asked,
        "language": language,
        "document_type": document_type,
        "citation": citation,
        "requested_as": asked,
        "sample": row["sample"],
        "condition": row["condition"],
    }
    # The prompt is part of the id. A verify "no" row clears its citation, so the
    # citation alone would give every negative the same id.
    ident = "|".join([
        row["tradition"], row["sample"], row["condition"], row["task"], row["citation"], row["prompt"],
    ])
    return {
        "id": hashlib.sha256(ident.encode()).hexdigest()[:16],
        "task": row["task"],
        "prompt": row["prompt"],
        "expected": expected,
        "source": source,
    }


def _language_dir(row: dict) -> Path:
    """christianity/english/population, judaism/native/familiarity, and so on.

    English-only traditions have no native folder. ``population`` is the 30
    passages the run uses. ``familiarity`` is the separate pre-registered list.
    """
    tradition = row["source"]["tradition"][0].lower()
    kind = "english" if row["source"]["language"] == "en" else "native"
    sample = row["source"].get("sample") or "population"
    base = REVIEW.parent / tradition / kind / sample
    prompt_lang = {"ask_english": "prompt-english", "ask_native": "prompt-native"}.get(row["source"].get("condition"))
    return base / prompt_lang if prompt_lang else base


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(path.relative_to(REVIEW.parent), len(rows))


def place_questions(rows: list[dict]) -> None:
    """One folder per tradition, then english or native. Christianity is english only."""
    grouped: dict[Path, list[dict]] = {}
    for row in rows:
        grouped.setdefault(_language_dir(row), []).append(row)
    for path, group in sorted(grouped.items()):
        _write_jsonl(path / "questions.jsonl", group)


def export_questions(built: dict[str, list[dict]]) -> None:
    """Write each tradition under english or native, then population or familiarity.

    There is no second copy under review/. Sikhism is included. Scoring keeps
    Gurmukhi vowel signs.
    """
    rows = [_collect_row(row) for group in built.values() for row in group]
    place_questions(rows)


def main() -> None:
    built = {
        "christianity": christianity(),
        "judaism": judaism(),
        "islam": islam(),
        "sikhism": sikhism(),
    }
    add_verify_negatives(built)
    export_questions(built)


if __name__ == "__main__":
    main()
