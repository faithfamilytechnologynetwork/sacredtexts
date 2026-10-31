import pytest

from pathlib import Path

from sacredbench.item_sample import (
    N_PASSAGES, TASKS, Passage, draw_across_works, draw_passages, load_well_known,
    prompt_conditions, render_question,
)


def _pool(n: int, work: str = "The Bible") -> list[Passage]:
    return [Passage(citation=f"Book {i}:1", work=work) for i in range(n)]


def test_draw_is_30_and_repeatable():
    ordinary = _pool(100)
    famous = [
        Passage("John 3:16", "The Bible", weight=5),
        Passage("Genesis 1:1", "The Bible", weight=2),
        Passage("Psalm 23:1", "The Bible", weight=1),
    ]
    a = draw_passages(ordinary, famous, seed=1)
    b = draw_passages(ordinary, famous, seed=1)
    assert a == b
    assert len(a) == N_PASSAGES
    assert len(a) * len(TASKS) == 120


def test_famous_stratum_is_capped_and_not_duplicated():
    ordinary = _pool(80) + [Passage("John 3:16", "The Bible")]
    famous = [Passage("John 3:16", "The Bible", weight=100), Passage("Micah 6:8", "The Bible", weight=1)]
    rows = draw_passages(ordinary, famous, n=20, famous_share=0.25, seed=2)
    citations = [p.citation for p, _ in rows]
    assert citations.count("John 3:16") == 1
    n_famous = sum(1 for _, stratum in rows if stratum == "famous")
    assert n_famous == 2  # quota would be 5, but only two famous citations exist


def test_higher_weight_is_drawn_more_often_inside_the_famous_cap():
    famous = [Passage("John 3:16", "The Bible", weight=50), Passage("Obadiah 1:1", "The Bible", weight=0.01)]
    ordinary = _pool(40)
    hits = 0
    for seed in range(40):
        rows = draw_passages(ordinary, famous, n=4, famous_share=0.25, seed=seed)
        famous_cits = [p.citation for p, s in rows if s == "famous"]
        hits += famous_cits.count("John 3:16")
    # One famous slot per seed. The heavy citation should take most of them.
    assert hits > 30


def test_works_share_the_thirty_and_keep_their_own_famous_slot():
    ordinary = _pool(40, "The Bible") + _pool(40, "The Qur'an")
    famous = [
        Passage("John 3:16", "The Bible", weight=5),
        Passage("2:255", "The Qur'an", weight=5),
    ]
    rows = draw_across_works(ordinary, famous, n=30, seed=3)
    by_work: dict[str, int] = {}
    for passage, _ in rows:
        by_work[passage.work] = by_work.get(passage.work, 0) + 1
    assert by_work == {"The Bible": 15, "The Qur'an": 15}
    famous_works = {p.work for p, stratum in rows if stratum == "famous"}
    assert famous_works == {"The Bible", "The Qur'an"}


def test_question_names_both_languages_and_both_editions():
    text = render_question(
        "What is the text of Qur'an 2:255?",
        "ما نص الآية ٢:٢٥٥ من القرآن؟",
        canonical_language="ar",
        answer_in_english=True,
        native_version="Uthmani (QUL)",
        english_version="Saheeh International",
    )
    assert "What is the text of Qur'an 2:255?" in text
    assert "ما نص الآية" in text
    assert "Uthmani (QUL)" in text
    assert "Saheeh International" in text
    assert "can differ" in text


def test_native_answer_names_the_native_edition_only():
    text = render_question(
        "What is the text of Qur'an 2:255?",
        "ما نص الآية ٢:٢٥٥ من القرآن؟",
        canonical_language="ar",
        answer_in_english=False,
        native_version="Uthmani (QUL)",
    )
    assert "Uthmani (QUL)" in text
    assert "Saheeh" not in text


def test_english_edition_is_required_when_the_answer_is_english():
    with pytest.raises(ValueError):
        render_question(
            "What is the text?", "ما النص؟",
            canonical_language="ar", answer_in_english=True,
            native_version="Uthmani (QUL)",
        )


def test_same_verse_in_two_english_editions_stays_two_passages():
    ordinary = (
        [Passage(f"Gen {i}:1", "The Bible", version="KJV") for i in range(20)]
        + [Passage(f"Gen {i}:1", "The Bible", version="NABRE") for i in range(20)]
    )
    famous = [
        Passage("John 3:16", "The Bible", version="KJV", weight=5),
        Passage("John 3:16", "The Bible", version="NABRE", weight=5),
    ]
    rows = draw_across_works(ordinary, famous, n=10, seed=4)
    picked = {(p.version, p.citation) for p, stratum in rows if stratum == "famous"}
    assert picked == {("KJV", "John 3:16"), ("NABRE", "John 3:16")}


def test_well_known_file_names_an_edition_on_every_row():
    path = Path(__file__).resolve().parents[2] / "items" / "for-test" / "well_known.yaml"
    rows = load_well_known(path)
    assert rows
    assert all(p.version and p.citation and p.work for p in rows)
    nrsv = [p for p in rows if p.version == "NRSV" and p.citation == "John 3:16"]
    assert len(nrsv) == 1
    assert all(p.version != "KJV" for p in rows)
    talmud = next(p for p in rows if p.work == "Talmud Bavli")
    assert talmud.english_version != talmud.version


def test_english_canonical_text_has_one_prompt_condition():
    assert prompt_conditions("en") == ("en_ask_en_answer",)
    assert prompt_conditions("English") == ("en_ask_en_answer",)
    assert prompt_conditions("ar") == ("native_answer", "en_ask_en_answer")
