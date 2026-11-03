"""Issue #118: echoing the prompt's form example is not a second citation.

Every cite_passage prompt ends "Answer with the citation only, in the same form as: Dhammapada 184."
Models often name their locus and disclaim the example ("Dhammapada 74, not Dhammapada 184"). The
example was counted as a second distinct candidate, so a correct answer scored as a hedge. The scorer
now reads the example from the prompt (``example_citation``) and drops its echo when another citation
is present. An answer whose only citation is the example still named a (wrong) locus and keeps it.

The oracle re-scores the committed 2026-11-02 answers: the only cells that move past #112 are those
registered by identity in ``testdata/citation_example_echo_movers.tsv``. Read-only.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.citations import score_citation
from sacredbench.score import example_citation, score_answer, score_file

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "runs"
MOVERS = Path(__file__).parent / "testdata" / "citation_example_echo_movers.tsv"


@pytest.mark.parametrize(
    ("prompt", "example"),
    [
        ('Where is this? "And they…" Answer with the citation only, in the same form as: Ezekiel 23:16.', "Ezekiel 23:16"),
        (
            'Where is this? "Μετὰ δὲ…" Answer with the citation only, in the same form as: John 8:41. '
            "Answer in the language of the Greek New Testament (Scrivener 1894).",
            "John 8:41",
        ),
        (
            'Where is this? "…פוסק:" Answer with the citation only, in the same form as: Gittin 40a:1.\n'
            "Answer in the language of the William Davidson Aramaic edition of the Babylonian Talmud.",
            "Gittin 40a:1",
        ),
        ('היכן נמצא הטקסט הזה? "…פוסק:" ענה בציון המקום בלבד, בצורה: Gittin 40a:1.', "Gittin 40a:1"),
        ('أين هذا النص؟ "…شَدِيدٍ" أجب برقم السورة والآية فقط، بالصيغة نفسها: 6:122.', "6:122"),
        ('यह उद्धरण कहाँ है? "द्यूतं…" केवल संकेत लिखें, इस रूप में: 17:13।', "17:13"),
        ('Kattha ayaṃ pāṭho? "Khantī…" Ṭhānam eva vissajjehi, iminā ākārena: Dhammapada 144.', "Dhammapada 144"),
        ('ਇਹ ਪਾਠ ਕਿੱਥੇ ਹੈ? "ਪਰਾਈ…" ਸਿਰਫ਼ ਹਵਾਲਾ ਲਿਖੋ, ਇਸ ਰੂਪ ਵਿਚ: Ang 1231:12.', "Ang 1231:12"),
        ('Where is this? "…" Answer with the citation only, in the same form as: Deus caritas est, para. 36.', "Deus caritas est, para. 36"),
        ("Where is the verse about love in 1 John 4:8?", None),  # no quoted passage
        ('Where is this? "…" Answer with the citation only.', None),  # no example
    ],
)
def test_example_citation(prompt, example):
    assert example_citation(prompt) == example


def test_every_committed_cite_prompt_has_an_example_other_than_the_answer():
    paths = sorted((REPO / "items/for-test").rglob("questions.jsonl"))
    assert paths
    n = 0
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            q = json.loads(line)
            if q["task"] == "cite_passage":
                example = example_citation(q["prompt"])
                assert example is not None and example != q["expected"]["citation"], (path, q["id"])
                n += 1
    assert n > 500


def _cite(answer: str, citation: str, example: str | None) -> dict:
    prompt = f'Where is this? "…" Answer with the citation only, in the same form as: {example}.' if example else None
    return score_answer("cite_passage", answer, {"citation": citation}, prompt=prompt)


@pytest.mark.parametrize(
    ("answer", "citation", "example"),
    [
        ('Dhammapada 74. **Dhammapada 184** is: "Khantī paramaṃ tapo…"', "Dhammapada 74", "Dhammapada 184"),
        ("Na. Ayaṃ pāṭho **Dhammapada 76**. Dhammapada 184 pana evaṃ ārabhati: …", "Dhammapada 76", "Dhammapada 184"),
        ("This quote is from the Dhammapada, not Dhammapada 184 necessarily, but it is Dhammapada 337", "Dhammapada 337", "Dhammapada 184"),
        ("Exodus 28:43 אינו המקום הנכון; הטקסט הזה הוא 1 Samuel 31:6", "1 Samuel 31:6", "Exodus 28:43"),
        ('सही संकेत: **12:7** — आपने "10:36" लिखा है', "12:7", "10:36"),
        ("The requested form is Megillah 23b:3.\n\n**Bekhorot 2a:1**", "Bekhorot 2a:1", "Megillah 23b:3"),
        ("Πράξεις 24:1 — όχι John 8:41", "Acts 24:1", "John 8:41"),  # with #112 notation
    ],
)
def test_echoing_the_example_beside_the_answer_is_not_a_hedge(answer, citation, example):
    scored = _cite(answer, citation, example)
    assert (scored["outcome"], scored["n_candidates"]) == ("correct", 1)
    assert _cite(answer, citation, None)["outcome"] == "incorrect"  # pre-#118: the echo was a second candidate


def test_an_answer_that_is_only_the_example_is_a_wrong_locus():
    assert _cite("Dhammapada 184", "Dhammapada 74", "Dhammapada 184") == {
        "correct": 0, "n_candidates": 1, "outcome": "incorrect",
    }


def test_an_echo_beside_a_wrong_locus_is_that_wrong_locus():
    assert _cite("Dhammapada 75, not Dhammapada 184", "Dhammapada 74", "Dhammapada 184")["n_candidates"] == 1


def test_two_real_citations_are_still_a_hedge():
    scored = _cite("Dhammapada 74 or Dhammapada 75 (not Dhammapada 184)", "Dhammapada 74", "Dhammapada 184")
    assert (scored["correct"], scored["n_candidates"]) == (0, 2)


@pytest.mark.parametrize("ordinal", ["1", "First", "Second", "Third", "I", "II", "III", "first", "ii"])
def test_a_numbered_book_is_not_an_echo_of_its_namesake(ordinal):
    scored = _cite(f"John 1:1 or {ordinal} John 3:16", "John 1:1", "John 3:16")
    assert (scored["correct"], scored["n_candidates"]) == (0, 2)


def test_the_plain_namesake_is_still_an_echo():
    assert _cite("John 1:1, not John 3:16", "John 1:1", "John 3:16")["outcome"] == "correct"


def test_the_example_offered_as_an_alternative_is_still_dropped():
    # The example is a different entry by construction, so offering it cannot raise the hit rate
    # the anti-hedge guards; disclaimers and alternatives are not told apart (score.py SCOPE).
    assert _cite("Dhammapada 74 or Dhammapada 184", "Dhammapada 74", "Dhammapada 184")["outcome"] == "correct"


def test_score_file_reads_the_example_from_the_question_prompt(tmp_path):
    row = {
        "question_id": "q1", "model_id": "m1", "task": "cite_passage", "question_set_digest": "d",
        "answer": "Dhammapada 74, not Dhammapada 184",
        "question": {
            "expected": {"citation": "Dhammapada 74"},
            "prompt": 'Where is this? "…" Answer with the citation only, in the same form as: Dhammapada 184.',
        },
    }
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(row) + "\n", encoding="utf-8")
    score_file(answers, tmp_path / "scores.jsonl")
    scored = json.loads((tmp_path / "scores.jsonl").read_text(encoding="utf-8"))
    assert scored["metrics"]["outcome"] == "correct"


# --- oracle over the committed 2026-11-02 run ----------------------------------------------------


def _registered() -> dict[tuple[str, int, str], tuple[str, int, int]]:
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {(f, int(r), q): (kind, int(old_n), int(new_n)) for f, r, q, kind, old_n, new_n in rows}
    assert len(registered) == len(rows)
    return registered


def test_registered_mover_counts():
    by_kind = Counter(kind for kind, _, _ in _registered().values())
    assert by_kind == {"credited": 69, "fewer_candidates": 45}


def test_committed_cite_passage_cells_move_only_as_registered():
    registered = _registered()
    score_files = sorted(RUNS.glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    seen: set[tuple[str, int, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, row in enumerate(answers):
            if row["task"] != "cite_passage":
                continue
            question = row["question"]
            citation = question["expected"]["citation"]
            before = score_citation(row["answer"], citation)  # #112 without the example
            after = score_citation(row["answer"], citation, example_citation(question["prompt"]))
            key = (folder, i, row["question_id"])
            if key not in registered:
                assert after == before, f"{key} moved but is not registered"
                continue
            seen.add(key)
            kind, old_n, new_n = registered[key]
            assert (before["n_candidates"], after["n_candidates"]) == (old_n, new_n), key
            assert (before["correct"], after["correct"]) == ((0, 1) if kind == "credited" else (0, 0)), key
    assert seen == set(registered), f"registered cells missing from runs/: {sorted(set(registered) - seen)[:5]}"
