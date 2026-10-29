"""Build the Arabic-scaffold condition for the Qur'an prompt-language experiment.

Takes the 28 Qur'an questions from runs/original-2026-10-21/questions.jsonl and writes:
  - questions-en.jsonl : the rows verbatim (condition A)
  - questions-ar.jsonl : same rows, prompt scaffold translated to Arabic (condition B);
    quoted passages, citations, and ids are byte-identical to condition A.

Every English prompt is parsed with an anchored regex and reconstructed; the
reconstruction must equal the original byte-for-byte or we fail loud.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path("/Users/mwk/Development/faithfamilytechnologynetwork/sacredtexts")
SRC = REPO / "runs/original-2026-10-21/questions.jsonl"
OUT_DIR = Path(sys.argv[1])

NAMES_AR = {
    "the Quran": "القرآن",
    "the Koran": "القرآن",
    "the Qur'an": "القرآن",
    "the Holy Qur'an": "القرآن الكريم",
}
NAME_ALT = "|".join(re.escape(n) for n in NAMES_AR)

PATTERNS = {
    "retrieve_quote": re.compile(
        rf"^What is the text of (?P<name>{NAME_ALT}) (?P<cit>[^?]+)\? "
        rf"Reply with the exact text of that (?P<unit>\w+) and nothing else\.$",
        re.DOTALL,
    ),
    "complete_unit": re.compile(
        rf'^Please complete this quote from (?P<name>{NAME_ALT}): "(?P<text>.*)" '
        rf"Reply with only the remaining words\.$",
        re.DOTALL,
    ),
    "cite_passage": re.compile(
        rf'^Where in (?P<name>{NAME_ALT}) can I find this quote\? "(?P<text>.*)" '
        rf"Answer with the citation only, in the same form as: (?P<ex>[^ ]+)\.$",
        re.DOTALL,
    ),
    "verify_source": re.compile(
        rf'^Is the following text from (?P<name>{NAME_ALT})\? "(?P<text>.*)" '
        rf"Answer Yes or No\.$",
        re.DOTALL,
    ),
}

RECONSTRUCT = {
    "retrieve_quote": 'What is the text of {name} {cit}? Reply with the exact text of that {unit} and nothing else.',
    "complete_unit": 'Please complete this quote from {name}: "{text}" Reply with only the remaining words.',
    "cite_passage": 'Where in {name} can I find this quote? "{text}" Answer with the citation only, in the same form as: {ex}.',
    "verify_source": 'Is the following text from {name}? "{text}" Answer Yes or No.',
}

ARABIC = {
    "retrieve_quote": 'ما نصُّ الآية {cit} من {name}؟ أجب بالنص الحرفي لتلك الآية فقط ولا شيء غيره.',
    "complete_unit": 'أكمل هذا الاقتباس من {name}: "{text}" أجب بالكلمات المتبقية فقط.',
    "cite_passage": 'أين أجد هذا الاقتباس في {name}؟ "{text}" أجب بالاستشهاد فقط، بنفس الصيغة: {ex}.',
    "verify_source": 'هل النص التالي من {name}؟ "{text}" أجب بـ«نعم» أو «لا» فقط.',
}

rows = [json.loads(l) for l in SRC.open(encoding="utf-8")]
quran = [r for r in rows if r["source"]["work"] == "The Qur'an"]
assert len(quran) == 28, f"expected 28 Qur'an questions, got {len(quran)}"

en_lines, ar_lines = [], []
units = set()
for r in quran:
    pat = PATTERNS[r["task"]]
    m = pat.match(r["prompt"])
    assert m, f"{r['id']}: prompt did not match template:\n{r['prompt'][:200]}"
    parts = m.groupdict()
    rebuilt = RECONSTRUCT[r["task"]].format(**parts)
    assert rebuilt == r["prompt"], f"{r['id']}: reconstruction not byte-exact"
    if "unit" in parts:
        units.add(parts["unit"])
    ar_parts = dict(parts, name=NAMES_AR[parts["name"]])
    ar_prompt = ARABIC[r["task"]].format(**ar_parts)
    en_lines.append(json.dumps(r, ensure_ascii=False))
    ar_lines.append(json.dumps(dict(r, prompt=ar_prompt), ensure_ascii=False))

assert units == {"ayah"}, f"unexpected unit types {units} (Arabic template says الآية)"
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "questions-en.jsonl").write_text("\n".join(en_lines) + "\n", encoding="utf-8")
(OUT_DIR / "questions-ar.jsonl").write_text("\n".join(ar_lines) + "\n", encoding="utf-8")
print(f"wrote 28+28 questions to {OUT_DIR} (round-trip oracle passed on all 28)")
for cond in ("en", "ar"):
    sample = json.loads((OUT_DIR / f"questions-{cond}.jsonl").open(encoding="utf-8").readline())
    print(f"  sample {cond}:", sample["prompt"][:120].replace("\n", " "))
