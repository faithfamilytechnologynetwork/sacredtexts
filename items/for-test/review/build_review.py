"""Write the six review pages from the question files.

The pages list the citations actually drawn. They do not keep a second,
hand-picked list.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

TASKS = (
    "retrieve_quote",
    "complete_unit",
    "cite_passage",
    "verify_source",
)


def load_questions(tradition: str, kind: str) -> list[dict]:
    """Questions for one tradition and language, population file then familiarity file."""
    rows = []
    for sample in ("population", "familiarity"):
        folder = OUT.parent / tradition / kind / sample
        files = [folder / "questions.jsonl"]
        files += sorted(folder.glob("prompt-*/questions.jsonl"))
        for path in files:
            if not path.exists():
                continue
            rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return rows


def passage_lines(rows: list[dict]) -> tuple[list[str], str]:
    """One line per passage, population first. Size is the question-file row count."""
    picked: dict[tuple[str, str], None] = {}
    for row in rows:
        if row["task"] != "retrieve_quote":
            continue
        source = row.get("source") or row
        condition = source.get("condition") or row.get("condition")
        if condition not in {"native_answer", "en_ask_en_answer", "ask_english", "ask_native"}:
            continue
        sample = source.get("sample") or row.get("sample")
        citation = source.get("citation") or row.get("citation")
        picked.setdefault((sample, citation), None)
    order = {"population": 0, "familiarity": 1}
    lines = [
        f"- `{cit}` ({sample})"
        for sample, cit in sorted(picked, key=lambda key: (order.get(key[0], 9), key[1]))
    ]
    n_pop = sum(1 for sample, _ in picked if sample == "population")
    n_fam = sum(1 for sample, _ in picked if sample == "familiarity")
    size = (
        f"{len(rows)} questions. Population sample: {n_pop} passages. "
        f"Familiarity panel: {n_fam} passages. Report those two separately."
    )
    return lines or ["- question file not built yet"], size


def main() -> None:
    religions = [
        christianity(),
        judaism(),
        islam(),
        sikhism(),
        missing("05-hinduism", "Hinduism", "The Bhagavad Gita"),
        missing("06-buddhism", "Buddhism", "The Dhammapada"),
    ]
    write_index(religions)
    write_passages()
    for folder, body in religions:
        path = OUT / folder
        path.mkdir(parents=True, exist_ok=True)
        (path / "README.md").write_text(body, encoding="utf-8")
        print(folder)


def write_index(religions: list[tuple[str, str]]) -> None:
    lines = [
        "# Review pack",
        "",
        "Each tradition has two samples. Report them separately.",
        "The population sample is 30 passages, drawn uniformly (seed 20261030),",
        "with the pre-registered familiar citations removed first.",
        "The familiarity panel is every citation in `well_known.yaml` for that edition.",
        "Christianity is one set of 30. The NRSV is the English edition. Hebrew Bible",
        "verses of that set are the Masoretic text, and New Testament verses are the",
        "Greek New Testament (Scrivener 1894). Each native passage is an English prompt",
        "and a native-language prompt. Judaism is the same 30 in Aramaic (both prompts)",
        "and in English. Islam and Sikhism on disk are the native edition, both prompts.",
        "A finished non-Christian tradition adds an English edition. Each tradition is",
        "then 360 population questions. Christianity is already 360.",
        "The familiarity panels are different lengths on purpose (Islam 8, Christianity 4,",
        "Sikhism 3, Judaism 1). Compare traditions on the population sample of 30.",
        "Do not pad or cut the familiar lists to make those counts match.",
        "The English edition can differ from the native edition.",
        "This folder is for a person to check the edition, the citation, and the",
        "wording of the prompts before a run.",
        "",
        "Checked against `texts/raw` on this machine: the Bhagavad Gita and the Dhammapada",
        "are not there. Those two folders say so and do not invent passages. Sikhism is",
        "there (`sggs_shabados.json`).",
        "",
        "Christianity is the NRSV. The full `nrsv.json` is gitignored. The drawn verses",
        "are in `christianity/english/`. The Protestant folder's KJV list chose the",
        "citations; the scored wording is NRSV. Other Christian payloads are not",
        "separate religions here.",
        "",
        "Native-language lines are drafts. A speaker of that language should correct them",
        "before they are used as the scored prompt.",
        "",
        "| Folder | In raw data? | Edition in the question | English edition, if different |",
        "|---|---|---|---|",
        "| `01-christianity` | questions in `christianity/english/`; full `nrsv.json` is gitignored | NRSV | same |",
        "| `02-judaism` | yes | Talmud Bavli, William Davidson Aramaic | William Davidson English |",
        "| `03-islam` | yes | Qur'an, Uthmani (QUL) | no English Qur'an in this corpus |",
        "| `04-sikhism` | yes | Sri Guru Granth Sahib, Shabad OS (SGPC Shabadaarth) | no English SGGS in this corpus |",
        "| `05-hinduism` | yes | Bhagavad Gita, Stotra Samhita (Gita Press text) | Annie Besant (1922) |",
        "| `06-buddhism` | yes | Dhammapada, Chaṭṭha Saṅgāyana (VRI) | no English Dhammapada in this corpus |",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_passages() -> None:
    """Write passages.json beside each questions.jsonl. The question file is the only store."""
    root = OUT.parent
    notices = {
        "Christianity": "New Revised Standard Version Bible, copyright © 1989 National Council of the Churches of Christ in the United States of America. Used by permission. All rights reserved worldwide.",
        "Judaism": "William Davidson Edition on Sefaria, CC-BY-NC.",
    }
    edition_notices = (
        ("Masoretic", "Masoretic text from the Westminster Leningrad Codex, via the Open Scriptures Hebrew Bible. The same 30 Christian population citations that are Hebrew Bible verses, not a second draw. Daniel 2 is Aramaic in this text."),
        ("Greek New Testament", "Greek New Testament, Scrivener 1894 Textus Receptus. The same 30 Christian population citations that are New Testament verses, not a second draw. Public-domain text."),
    )
    paths = sorted(root.glob("*/*/*/questions.jsonl")) + sorted(root.glob("*/*/*/*/questions.jsonl"))
    seen = set()
    for path in paths:
        # One passages.json per sample. The two prompt-language files share it.
        sample_dir = path.parent.parent if path.parent.name.startswith("prompt-") else path.parent
        if sample_dir in seen:
            continue
        seen.add(sample_dir)
        path = next(p for p in paths if (p.parent.parent if p.parent.name.startswith("prompt-") else p.parent) == sample_dir)
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        passages = []
        for row in rows:
            if row["task"] != "retrieve_quote":
                continue
            source = row["source"]
            kind = "english" if source["language"] == "en" else "native"
            item = {
                "tradition": source["tradition"][0],
                "citation": source["citation"],
                "sample": source["sample"],
                "version": source["version"],
                "text": {kind: row["expected"]["text"]},
            }
            passages.append(item)
        tradition = passages[0]["tradition"] if passages else ""
        payload = {
            "tradition": tradition,
            "sample": sample_dir.name,
            "run": sample_dir.name == "population",
            "passages": passages,
        }
        version = passages[0]["version"] if passages else ""
        edition_notice = next((text for key, text in edition_notices if key in version), None)
        if edition_notice:
            payload["notice"] = edition_notice
        elif tradition in notices:
            payload["notice"] = notices[tradition]
        dest = sample_dir / "passages.json"
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(dest.relative_to(root), len(passages))


def christianity() -> tuple[str, str]:
    rows, size = passage_lines(load_questions("christianity", "english"))
    size += (
        " Original language of that same population sample, not a second draw: "
        "21 Masoretic passages (168 questions) and 9 Greek New Testament passages (72 questions)."
    )
    rows.append("")
    rows.append(
        "The verse inventory for the draw is the Protestant list in `kjv.json`. "
        "The wording in `christianity/english/` is NRSV. Do not check these against `kjv.json`. "
        "The same 30 citations are in `christianity/native/masoretic/` when the verse is from the "
        "Hebrew Bible (Westminster Leningrad Codex; Daniel 2 is Aramaic) and in "
        "`christianity/native/greek/` when it is from the New Testament (Scrivener 1894). "
        "That is one set, split by original language, and each of those files has an "
        "English prompt and a native-language prompt. The licensed Greek Orthodox TLG "
        "files are not in the repo, so these verses are not the Septuagint."
    )
    return "01-christianity", page(
        title="Christianity",
        version="NRSV",
        english_version="NRSV (same edition; the text is already English)",
        language="English",
        native_prompts=None,
        rows=rows,
        source="texts/raw/Protestant Christian/nrsv.json (gitignored; not in the public repo)",
        size=size,
    )


def islam() -> tuple[str, str]:
    rows, size = passage_lines(load_questions("islam", "native"))
    native = {
        "retrieve_quote": "ما نص {citation} من القرآن في طبعة عثماني (QUL)؟ أجب بنص تلك الطبعة فقط.",
        "complete_unit": "أكمل هذا الاقتباس من القرآن، طبعة عثماني (QUL): \"{head}\" أجب بالكلمات المتبقية فقط.",
        "cite_passage": "أين أجد هذا النص في القرآن، طبعة عثماني (QUL)؟ \"{text}\" أجب بالاستشهاد فقط.",
        "verify_source": "هل النص التالي من القرآن، طبعة عثماني (QUL)؟ \"{text}\" أجب بنعم أو لا.",
    }
    return "03-islam", page(
        title="Islam",
        version="The Qur'an, Uthmani (QUL)",
        english_version="none in this corpus; do not name an English translation we do not hold",
        language="Arabic",
        native_prompts=native,
        rows=rows,
        source="texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json",
        size=size,
    )


def judaism() -> tuple[str, str]:
    rows, size = passage_lines(load_questions("judaism", "native") + load_questions("judaism", "english"))
    rows.append("- The Aramaic and English Davidson files are different wording (CC-BY-NC).")
    native = {
        "retrieve_quote": "מהו נוסח {citation} בתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית? ענה בנוסח אותה מהדורה בלבד.",
        "complete_unit": "השלם ציטוט זה מהתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית: \"{head}\" ענה במילים הנותרות בלבד.",
        "cite_passage": "היכן בתלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית, נמצא הטקסט הזה? \"{text}\" ענה בציון המקום בלבד.",
        "verify_source": "האם הטקסט הבא מן התלמוד הבבלי, מהדורת ויליאם דייווידסון הארמית? \"{text}\" ענה כן או לא.",
    }
    return "02-judaism", page(
        title="Judaism",
        version="Talmud Bavli, William Davidson Edition - Aramaic",
        english_version="William Davidson Edition - English (same citations, a separate file)",
        language="Aramaic / Hebrew",
        native_prompts=native,
        rows=rows,
        source="texts/raw/Judaism/Talmud Bavli/",
        size=size,
    )


def sikhism() -> tuple[str, str]:
    rows, size = passage_lines(load_questions("sikhism", "native"))
    native = {
        "retrieve_quote": "{citation} ਦਾ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ, ਸ਼ਬਦ ਓਐਸ (ਐਸ.ਜੀ.ਪੀ.ਸੀ. ਸ਼ਬਦਾਰਥ) ਵਿਚੋਂ ਦੱਸੋ। ਸਿਰਫ਼ ਉਸੇ ਅਡੀਸ਼ਨ ਦਾ ਪਾਠ ਲਿਖੋ।",
        "complete_unit": "ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ, ਸ਼ਬਦ ਓਐਸ (ਐਸ.ਜੀ.ਪੀ.ਸੀ. ਸ਼ਬਦਾਰਥ) ਵਿਚੋਂ ਇਹ ਟੋਟਾ ਪੂਰਾ ਕਰੋ: \"{head}\" ਸਿਰਫ਼ ਬਾਕੀ ਸ਼ਬਦ ਲਿਖੋ।",
        "cite_passage": "ਇਹ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ, ਸ਼ਬਦ ਓਐਸ (ਐਸ.ਜੀ.ਪੀ.ਸੀ. ਸ਼ਬਦਾਰਥ) ਵਿਚ ਕਿੱਥੇ ਹੈ? \"{text}\" ਸਿਰਫ਼ ਹਵਾਲਾ ਲਿਖੋ।",
        "verify_source": "ਕੀ ਇਹ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ, ਸ਼ਬਦ ਓਐਸ (ਐਸ.ਜੀ.ਪੀ.ਸੀ. ਸ਼ਬਦਾਰਥ) ਵਿਚੋਂ ਹੈ? \"{text}\" ਹਾਂ ਜਾਂ ਨਹੀਂ।",
    }
    return "04-sikhism", page(
        title="Sikhism",
        version="Sri Guru Granth Sahib, Shabad OS (SGPC Shabadaarth)",
        english_version="none in this corpus",
        language="Gurmukhi (Sant Bhasha)",
        native_prompts=native,
        rows=rows,
        source="texts/raw/Sikhism/sggs_shabados.json",
        size=size,
    )


def missing(folder: str, title: str, work: str) -> tuple[str, str]:
    body = "\n".join([
        f"# {title}",
        "",
        f"**Not in `texts/raw`.** There is no file for {work} in this checkout.",
        "No passages and no bilingual prompts are written here, so a reviewer is not",
        "asked to approve a citation or a translation that was not read from a file.",
        "",
        "When a licensed edition is added under `texts/raw/`, name that edition here,",
        "including an English translation edition if it is a different book, and list",
        "a population sample and a separate familiarity panel.",
        "",
    ])
    return folder, body


def page(*, title, version, english_version, language, native_prompts, rows, source, size) -> str:
    english = {
        "retrieve_quote": "What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.",
        "complete_unit": "Please complete this quote from {version}: \"{head}\" Reply with only the remaining words.",
        "cite_passage": "Where in {version} can I find this quote? \"{text}\" Answer with the citation only, in the same form as: {example}.",
        "verify_source": "Is the following text from {version}? \"{text}\" Answer Yes or No.",
    }
    out = [
        f"# {title}",
        "",
        f"- Canonical edition named in the question: **{version}**",
        f"- English edition: **{english_version}**",
        f"- Language: {language}",
        f"- Raw file: `{source}`",
        f"- Tasks: {', '.join(TASKS)}",
        f"- Size: {size}",
        "",
        "## Passages to check",
        "",
        *rows,
        "",
        "These citations are the question file. Population and familiarity are separate samples.",
        "",
        "## Prompts in English",
        "",
    ]
    for task, tmpl in english.items():
        out.append(
            f"- `{task}`: "
            + tmpl.format(citation="{citation}", version=version, head="{head}", text="{text}", example="{example}")
        )
    out.append("")
    if native_prompts is None:
        out.append("This edition is English, so there is one answer language.")
    else:
        out.extend(["## Prompts in the text's language (draft)", ""])
        out.append("A native speaker should correct these before a run.")
        out.append("")
        for task, tmpl in native_prompts.items():
            out.append(f"- `{task}`: {tmpl}")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    main()
