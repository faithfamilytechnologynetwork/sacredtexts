"""Issue #117: a decline written in the edition's language is a refusal, not a wrong answer.

A model often declines in the edition's language: Hebrew, Punjabi, Hindi, Arabic or Greek. That
happens on the native-prompt arms, which ask for that language, and on the English-prompt arms as
well (163 of the 792 registered movers), because the model answers in the edition's language
either way. Before #117 the decline cues were English, and these cells were
scored `incorrect`. ``outcomes._NATIVE_DECLINE_CUES_RAW`` adds a narrow native set. It is matched
as whole words, in the same leading window / opening sentence as the English cues, and under the
same Spec-48 assertion gate.

The oracles at the bottom re-score the committed evidence with the native cues off and on.
Exactly the cells registered in ``testdata/native_decline_movers.tsv`` move, and each moves only
from incorrect to refused. The committed ``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from sacredbench import outcomes
from sacredbench.outcomes import classify_refusal, leading_decline
from sacredbench.score import normalize, score_answer

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs"
MOVERS = Path(__file__).parent / "testdata" / "native_decline_movers.tsv"
_NEVER = re.compile(r"(?!)")

HE_REF = {"text": "בראשית ברא אלהים את השמים ואת הארץ"}
PA_REF = {"text": "ਸੋ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਅਗਮਾ ਅਗਮ ਅਪਾਰਾ"}
SA_REF = {"text": "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"}
AR_REF = {"text": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"}
GRC_REF = {"text": "Ἐν ἀρχῇ ἦν ὁ λόγος"}


# Real declines from the 2026-11-03 rerun, trimmed. Each one was scored `incorrect` before #117.
@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("אני לא יכול לספק את הטקסט המדויק מתוך מהדורת וויליאם דוידסון של התלמוד הבבלי, "
         "אך אשמח לסכם עבורך את התוכן.", HE_REF),
        ("איני יכול לספק את נוסח Yevamot 67b:1 במהדורת ויליאם דוידסון.", HE_REF),
        ("אין בידי להעתיק את נוסח מהדורת ויליאם דייווידסון.", HE_REF),
        ("מצטער, אין ביכולתי לאמת את הנוסח המדויק של עירובין צ״א ע״א במהדורת ויליאם דייווידסון.", HE_REF),
        ("אין לי גישה בזמן אמת לוודא את הנוסח המדויק של מהדורת ויליאם דייווידסון.", HE_REF),
        ("ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਇਹ ਬੇਨਤੀ ਪੂਰੀ ਨਹੀਂ ਕਰ ਸਕਦਾ।", PA_REF),
        ("ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਇਸ ਪੰਕਤੀ ਦਾ ਬਾਕੀ ਹਿੱਸਾ ਪੱਕੇ ਤੌਰ 'ਤੇ ਯਾਦ ਨਹੀਂ।", PA_REF),
        ("ਮਾਫ਼ ਕਰਨਾ, ਮੇਰੇ ਕੋਲ ਇਸ ਸੰਸਕਰਣ ਦੇ ਅੰਗ ੮੫੩:੧੩ ਦਾ ਪ੍ਰਮਾਣਿਤ ਪਾਠ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।", PA_REF),
        ("मैं इस संस्करण का पाठ हूबहू सत्यापित नहीं कर सकता।", SA_REF),
        ("मैं गीता प्रेस के पाठ का अक्षरशः पाठ सत्यापित नहीं कर पा रहा हूँ।", SA_REF),
        ("عذرًا، لا يمكنني تزويدك بنص القرآن الكريم.", AR_REF),
        ("Δεν μπορώ να αναπαράγω με ακρίβεια το κείμενο της Scrivener 1894.", GRC_REF),
    ],
)
def test_native_declines_are_refusals(answer, expected):
    assert classify_refusal(answer, "retrieve_quote", expected) is True
    assert score_answer("retrieve_quote", answer, expected)["outcome"] == "refused"


def test_verb_final_decline_is_caught_by_the_opening_sentence():
    # Punjabi puts "can't give" at the end of the sentence, past the 60-character window.
    ans = ("ਮੈਂ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਦੇ ਕਿਸੇ ਖ਼ਾਸ ਅਡੀਸ਼ਨ (ਜਿਵੇਂ ਕਿ ਸ਼੍ਰੋਮਣੀ ਗੁਰਦੁਆਰਾ ਪ੍ਰਬੰਧਕ ਕਮੇਟੀ ਵਾਲਾ "
           "ਅਡੀਸ਼ਨ) ਦੇ ਪੰਨਾ 1231 ਦਾ ਸ਼ਬਦ-ਬ-ਸ਼ਬਦ ਪਾਠ ਭਰੋਸੇ ਨਾਲ ਨਹੀਂ ਦੇ ਸਕਦਾ, ਇਸ ਲਈ ਮੈਂ ਕੋਈ "
           "ਅਨੁਮਾਨਿਤ ਪਾਠ ਲਿਖਣ ਤੋਂ ਬਚਾਂਗਾ।")
    assert leading_decline(ans) is False
    assert score_answer("retrieve_quote", ans, PA_REF)["outcome"] == "refused"


def test_native_cite_passage_decline_is_refused():
    ans = "אני לא יכול לאשר את המקום המדויק בקודקס לנינגרד לפי הציטוט הזה."
    assert score_answer("cite_passage", ans, {"citation": "Genesis 1:1"})["outcome"] == "refused"


def test_native_decline_that_still_delivers_the_reference_is_an_answer():
    ans = "אינני יכול לאמת את המהדורה, אבל הפסוק הוא: בראשית ברא אלהים את השמים ואת הארץ"
    assert score_answer("retrieve_quote", ans, HE_REF)["outcome"] == "correct"


@pytest.mark.parametrize(
    "answer",
    [
        "וְאָמַר לֹא אוּכַל כִּי חָתוּם הוּא",  # Isaiah 29:11: "I cannot, for it is sealed"
        "חָנֵּנִי יְהוָה כִּי צַר לִי",  # Psalm 31:10: "for I am in distress"
        "מצטער פטור מן הסוכה",  # Sukkah 26a: "one who is distressed is exempt from the sukkah"
        "قَالَ إِن سَأَلْتُكَ عَن شَيْءٍ بَعْدَهَا فَلَا تُصَاحِبْنِي قَدْ بَلَغْتَ مِن لَّدُنِّي عُذْرًا",  # 18:76
        "قُل لَّا أَمْلِكُ لِنَفْسِي نَفْعًا وَلَا ضَرًّا",  # Qur'an 7:188
        "إِنِّي لاَ أَسْتَطِيعُ أَنْ آخُذَ مِنَ الْقُرْآنِ شَيْئًا",  # Sunan Abi Dawud 832
        "مَثَلُ الَّذِينَ حُمِّلُوا التَّوْرَاةَ ثُمَّ لَمْ يَحْمِلُوهَا كَمَثَلِ الْحِمَارِ يَحْمِلُ أَسْفَارًا",  # 62:5
    ],
)
def test_scripture_that_reads_like_a_decline_is_not_one(answer):
    # Seeds proposed in the issue that occur in scripture are not cues: a delivered (wrong) verse
    # that contains one is an answer.
    assert classify_refusal(answer, "retrieve_quote", {"text": "unrelated reference"}) is False


@pytest.mark.parametrize(
    "answer",
    [
        "عذرًا، لا يوجد آية رقم 12 في سورة 31 (سورة السجدة).",
        'ਮਾਫ਼ ਕਰਨਾ, ਪਰ "315:44" ਦਾ ਹਵਾਲਾ ਸਪਸ਼ਟ ਨਹੀਂ ਹੈ। ਅੰਗ 315 ਦੀ 44ਵੀਂ ਪੰਕਤੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।',
    ],
)
def test_an_apology_before_a_non_existence_claim_is_a_wrong_answer(answer):
    # "Sorry, there is no verse 12 in surah 31" is a confident (wrong) claim, as in English.
    assert score_answer("retrieve_quote", answer, {"text": "unrelated reference"})["outcome"] == "incorrect"


def test_a_caveat_after_a_delivered_verse_is_not_a_decline():
    # A Masoretic verse ends in sof pasuq (׃). The caveat after it, on the same line and past the
    # leading window, is not the opening sentence, so the delivered (wrong) verse is an answer.
    ans = ("וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת "
           "עַל־פְּנֵי הַמָּיִם׃ אני לא יכול לאמת את הנוסח המדויק במהדורה הזו")
    assert leading_decline(ans) is False
    assert score_answer("retrieve_quote", ans, HE_REF)["outcome"] == "incorrect"


def test_native_cues_match_whole_words_only():
    # שאינני יכול = "since I can't …": the model goes on to deliver the text (gemma, 2026-11-03).
    ans = "מכיוון שאינני יכול להציג קובץ PDF מלא, להלן הנוסח של הדף כפי שהוא מופיע במקור."
    assert leading_decline(ans) is False
    assert leading_decline("אינני יכול להציג את הנוסח המלא.") is True


def test_native_cues_do_not_occur_in_scripture():
    # Every native cue is absent from the standardized corpus, except the two known single
    # occurrences that are kept because they carry 67 declines (see outcomes.py).
    root = REPO_ROOT / "texts" / "standardized"
    if not root.exists():
        pytest.skip("texts/standardized not built")
    pattern = outcomes._native_cue_re()
    found = set()
    for path in root.rglob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc["source"]["language"] == "en":
            continue
        for entry in doc["entries"]:
            for m in pattern.finditer(normalize(entry["text"])):
                found.add((m.group(0), entry["citation"]))
    assert found == {("איני יכול", "Bava Batra 20b:15"), ("אין בידי", "Yevamot 80b:9")}


# --- oracle over the committed evidence -----------------------------------------------------


def _registered() -> dict[tuple[str, int, str], str]:
    """(folder, row in answers.jsonl, question_id) -> task."""
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {(folder, int(row), qid): task for folder, row, qid, task in rows}
    assert len(registered) == len(rows)
    return registered


def _pre_and_post(row: dict, monkeypatch) -> tuple[dict, dict]:
    """The cell scored without the #117 native cues, and with them."""
    args = (row["task"], row["answer"] or "", row["question"]["expected"])
    language = row["question"].get("source", {}).get("language")
    post = score_answer(*args, language=language)
    with monkeypatch.context() as m:
        m.setattr(outcomes, "_native_cue_re", lambda: _NEVER)
        pre = score_answer(*args, language=language)
    return pre, post


def _moves(score_files: list[Path], monkeypatch):
    """Yield ((folder, row, question_id), task, committed metrics, pre, post) for every cell #117
    moves."""
    pattern = outcomes._native_cue_re()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        committed = [json.loads(l) for l in scores.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(answers) == len(committed), folder  # score_file keeps row order, so pair by position
        for i, (row, old) in enumerate(zip(answers, committed)):
            assert row["question_id"] == old["question_id"], folder
            answer = row["answer"] or ""
            if answer.isascii() or not pattern.search(normalize(answer)):
                continue  # no native cue anywhere (every cue is non-ASCII): the cell cannot move
            pre, post = _pre_and_post(row, monkeypatch)
            if pre != post:
                yield (folder, i, row["question_id"]), row["task"], old["metrics"], pre, post


def _assert_incorrect_to_refused(key, committed: dict, pre: dict, post: dict) -> None:
    assert (pre["outcome"], post["outcome"]) == ("incorrect", "refused"), key
    changed = {k for k in pre.keys() | post.keys() if pre.get(k) != post.get(k)}
    assert changed == {"outcome"}, (key, changed)
    assert committed["outcome"] != "correct", key  # no committed credit is lost


def test_registered_mover_counts():
    by_kind = Counter()
    for (folder, _, _), task in _registered().items():
        where = folder if folder.startswith("archive/") else folder.split("/")[2]
        by_kind[(where, task)] += 1
    assert by_kind == {
        ("judaism", "retrieve_quote"): 255, ("judaism", "complete_unit"): 36, ("judaism", "cite_passage"): 37,
        ("sikhism", "retrieve_quote"): 254, ("sikhism", "complete_unit"): 34, ("sikhism", "cite_passage"): 30,
        ("hinduism", "retrieve_quote"): 112, ("hinduism", "complete_unit"): 6, ("hinduism", "cite_passage"): 12,
        ("christianity", "retrieve_quote"): 9, ("christianity", "complete_unit"): 3,
        ("islam", "retrieve_quote"): 1, ("islam", "complete_unit"): 1, ("islam", "cite_passage"): 1,
        ("archive/original-2026-10-21", "complete_unit"): 1,
    }


def test_committed_cells_move_only_as_registered(monkeypatch):
    registered = _registered()
    score_files = sorted([*RUNS.glob("*/base/**/scores.jsonl"), *RUNS.glob("archive/*/scores.jsonl")])
    if not score_files:
        pytest.skip("runs/ evidence not present")
    seen = set()
    for key, task, committed, pre, post in _moves(score_files, monkeypatch):
        assert key in registered, f"{key} moved but is not registered"
        assert registered[key] == task, key
        _assert_incorrect_to_refused(key, committed, pre, post)
        seen.add(key)
    assert seen == set(registered), f"registered cells that did not move: {sorted(set(registered) - seen)[:5]}"


def test_rerun_moves_only_incorrect_to_refused(monkeypatch):
    # The 2026-11-03 rerun is not committed; check it when it is present locally.
    score_files = sorted((RUNS / "rerun-2026-11-03").glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/rerun-2026-11-03 not present")
    moved = 0
    for key, _, committed, pre, post in _moves(score_files, monkeypatch):
        _assert_incorrect_to_refused(key, committed, pre, post)
        moved += 1
    assert moved
