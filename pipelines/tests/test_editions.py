"""The English-Bible agreement table, now sourced from the Spec 32 edition index."""

from sacredbench.editions import agreement, edition_indexes, edition_run


def test_agreement_counts_shared_verses_and_folded_matches():
    idx = {
        "A": {"1:1": "in the beginning", "1:2": "and the earth", "1:3": "let there be light"},
        "B": {"1:1": "in the beginning", "1:2": "and the earth was void", "1:4": "elsewhere"},
    }
    report = agreement(idx)
    assert report["shared"] == 2            # 1:1 and 1:2 are in both
    assert report["all"] == 1               # only 1:1 is folded-equal in both
    assert report["pairs"]["A and B"] == 1


def test_agreement_needs_at_least_two_editions():
    assert agreement({"only": {"1:1": "x"}}) == {"shared": 0, "all": 0, "pairs": {}}


def test_edition_indexes_are_the_public_domain_english_bibles_via_the_converter():
    editions = edition_indexes()
    # Exactly the three public-domain wordings, by their catalogue version strings — a restricted
    # English Bible (NABRE) would add a fourth version, so this also guards the licence gate.
    assert set(editions) == {"KJV", "ASV (1901)", "WEB"}
    # Each wording is the whole Bible read through the converter, not a stub.
    assert all(len(verses) > 1000 for verses in editions.values())


def test_edition_run_over_the_real_corpus():
    report = edition_run()
    assert report["shared"] > 0
    assert 0 <= report["all"] <= report["shared"]
    assert set(report["pairs"]) == {"ASV (1901) and KJV", "ASV (1901) and WEB", "KJV and WEB"}
