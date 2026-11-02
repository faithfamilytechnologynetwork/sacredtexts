from sacredbench.claims import fisher_p, mcnemar_p, negative_kind


def test_negative_kind_splits_alphabet_checks_from_canon_checks():
    assert negative_kind("pa", "Sikhism", "Islam") == "Different script"
    assert negative_kind("pi", "Buddhism", "Judaism") == "Different script"
    assert negative_kind("en", "Book of Mormon", "Encyclicals") == "Book of Mormon shown an encyclical"
    assert negative_kind("en", "Encyclicals", "Book of Mormon") == "Encyclical shown the Book of Mormon"
    assert negative_kind("he", "Judaism", "Christianity") == "Talmud shown the Bible"
    assert negative_kind("ar", "Islam", "Islam") == "Qur'an shown a hadith"
    assert negative_kind("en", "Christianity", "The Church of Jesus Christ of Latter-Day Saints") == "NRSV shown the Book of Mormon"


def test_mcnemar_balanced_is_one():
    assert mcnemar_p(5, 5) == 1.0


def test_mcnemar_one_sided_split_is_small():
    # 10 vs 0 discordant pairs. Two-sided exact binomial: 2/1024.
    p = mcnemar_p(10, 0)
    assert p is not None
    assert abs(p - 2 / 1024) < 1e-12


def test_mcnemar_empty_is_none():
    assert mcnemar_p(0, 0) is None


def test_fisher_identical_rates_are_not_small():
    assert fisher_p(10, 10, 10, 10) == 1.0
