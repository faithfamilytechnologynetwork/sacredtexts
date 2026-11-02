"""Paired tests for the claim that one accuracy number mixes different facts.

McNemar's exact test compares two tasks, or two prompts, on the same citation.
Only the pairs where the two sides disagree enter the test. Refusals are left
out, matching accuracy. Fisher exact compares two independent sets of answered
cells, such as a real verify item against a fake one.

The tail probabilities use log-gamma so a few hundred discordant pairs do not
underflow to zero. No extra dependency.
"""

from __future__ import annotations

import math


def _log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def mcnemar_p(only_a: int, only_b: int) -> float | None:
    """Two-sided exact McNemar p-value. ``only_a`` and ``only_b`` are the discordant counts."""
    n = only_a + only_b
    if n <= 0:
        return None
    target = abs(only_a - only_b)
    log_half_n = -n * math.log(2)
    p = 0.0
    for i in range(n + 1):
        if abs(2 * i - n) + 1e-9 < target:
            continue
        p += math.exp(_log_choose(n, i) + log_half_n)
    return 1.0 if p > 1 - 1e-9 else p


def negative_kind(language: str | None, asked: str | None, true_tradition: str | None) -> str:
    """What a verify-no item actually asks the model to notice.

    Cross-script donors are an alphabet check. The Talmud shown the Bible, and
    the Book of Mormon shown an encyclical, are canon checks. The reverse of
    that last pair is kept separate because it is not the same error.
    """
    if language in {"pa", "pi", "sa", "grc"}:
        return "Different script"
    if asked == "Book of Mormon" and true_tradition == "Encyclicals":
        return "Book of Mormon shown an encyclical"
    if asked == "Encyclicals":
        return "Encyclical shown the Book of Mormon"
    if asked == "Judaism":
        return "Talmud shown the Bible"
    if asked == "Islam":
        return "Qur'an shown a hadith"
    if asked == "Christianity" and language == "en":
        return "NRSV shown the Book of Mormon"
    return "Other same-script negative"


def fisher_p(correct_a: int, incorrect_a: int, correct_b: int, incorrect_b: int) -> float:
    """Two-sided Fisher exact test on two answered groups (refusals already excluded)."""
    a, b, c, d = correct_a, incorrect_a, correct_b, incorrect_b
    row1 = a + b
    row2 = c + d
    col1 = a + c
    n = row1 + row2
    if n == 0 or row1 == 0 or row2 == 0 or col1 == 0 or col1 == n:
        return 1.0
    lo = max(0, col1 - row2)
    hi = min(col1, row1)
    denom = _log_choose(n, col1)

    def log_p(k: int) -> float:
        return _log_choose(row1, k) + _log_choose(row2, col1 - k) - denom

    observed = log_p(a)
    p = 0.0
    for k in range(lo, hi + 1):
        lp = log_p(k)
        if lp <= observed + 1e-12:
            p += math.exp(lp)
    return min(1.0, p)
