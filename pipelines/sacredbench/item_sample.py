"""Draw a fixed-size item list without letting famous passages take the whole sample.

The headline set is 30 passages x 4 task types = 120 questions (one question per
task per passage). A uniform draw treats John 3:16 like an obscure verse. Models
have seen the famous ones far more often, so a uniform set understates that
familiarity and a famous-only set measures memory of a handful of lines.

The draw is two strata, from one seed:

- ``famous_share`` of the passages (default a quarter) come from a declared
  widely-quoted list, weighted inside that list so John 3:16 can be more likely
  than a less-quoted "famous" line, but only inside this capped stratum.
- The rest are a uniform sample of everything else.

The 30 are split across editions first, so one edition cannot take every slot.
Inside each edition the famous cap still applies, and a citation is used once.
Each picked passage is then asked as all four tasks. The stratum is stored on
the row so a later table can report famous and ordinary accuracy separately.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

N_PASSAGES = 30
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
FAMOUS_SHARE = 0.25


@dataclass(frozen=True)
class Passage:
    citation: str
    work: str
    version: str = ""
    weight: float = 1.0
    # English edition to name when the answer is English. Empty when this row
    # is already that English edition. May differ from ``version``.
    english_version: str = ""

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.work, self.version, self.citation)


def draw_passages(
    ordinary: list[Passage],
    famous: list[Passage],
    *,
    n: int = N_PASSAGES,
    famous_share: float = FAMOUS_SHARE,
    seed: int = 20261030,
) -> list[tuple[Passage, str]]:
    """Return ``(passage, stratum)`` pairs, ``stratum`` is ``famous`` or ``ordinary``.

    Famous citations are removed from the ordinary pool so a verse cannot be
    drawn twice. If the famous list is shorter than its quota, the shortfall
    is filled from the ordinary pool.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    if not 0.0 <= famous_share <= 1.0:
        raise ValueError("famous_share must be between 0 and 1")
    famous_ids = {p.key for p in famous}
    ordinary = [p for p in ordinary if p.key not in famous_ids]
    rng = random.Random(seed)
    n_famous = min(len(famous), int(round(n * famous_share)))
    n_ordinary = n - n_famous
    if len(ordinary) < n_ordinary:
        raise ValueError(
            f"ordinary pool {len(ordinary)} is smaller than the ordinary quota {n_ordinary}"
        )
    picked_famous = _weighted_without_replacement(famous, n_famous, rng)
    picked_ordinary = _uniform_without_replacement(ordinary, n_ordinary, rng)
    rows = [(p, "famous") for p in picked_famous] + [(p, "ordinary") for p in picked_ordinary]
    rng.shuffle(rows)
    return rows


def _uniform_without_replacement(pool: list[Passage], k: int, rng: random.Random) -> list[Passage]:
    ordered = sorted(pool, key=lambda p: p.key)
    rng.shuffle(ordered)
    return ordered[:k]


def _weighted_without_replacement(pool: list[Passage], k: int, rng: random.Random) -> list[Passage]:
    """One key per item, ``u ** (1/weight)``; the k largest keys win. A higher
    weight pushes the key toward 1, so it is more likely. Weight 0 is never
    drawn. Deterministic for ``rng``."""
    if k == 0:
        return []
    keyed: list[tuple[float, str, str, str, Passage]] = []
    for p in pool:
        if p.weight <= 0:
            continue
        u = rng.random()
        key = (max(u, 1e-12)) ** (1.0 / p.weight)
        keyed.append((key, p.work, p.version, p.citation, p))
    keyed.sort(reverse=True)
    return [row[4] for row in keyed[:k]]


# Question language, then answer language. An English-canonical text (Roman
# Catholic editions in this corpus) collapses to one condition: asking it in
# "native" and in English is the same prompt.
# The English-question and native-question rows both expect the native edition,
# so they are one scored item. The English-answer row is the second item.
NATIVE_ANSWER = "native_answer"
EN_ASK_EN = "en_ask_en_answer"


def prompt_conditions(canonical_language: str) -> tuple[str, ...]:
    """The conditions to emit for one passage. English-native texts get one."""
    if _is_english(canonical_language):
        return (EN_ASK_EN,)
    return (NATIVE_ANSWER, EN_ASK_EN)


def _is_english(language: str) -> bool:
    return language.lower() in {"en", "eng", "english"}


def render_question(
    english: str,
    native: str | None,
    *,
    canonical_language: str,
    answer_in_english: bool,
    native_version: str,
    english_version: str | None = None,
) -> str:
    """The user message for one question.

    Anthropic, OpenAI, and Gemini text calls have no language argument, so the
    language and the edition are written here. ``collect`` sends this string
    as the only user message.

    A non-English text includes the question in both languages. The native
    edition and, when the answer is English, the English edition are both
    named. Those editions can differ (Uthmani Arabic versus an English
    translation). An English-canonical text names its one edition.
    """
    if not native_version.strip():
        raise ValueError("native_version is required")
    if _is_english(canonical_language):
        return (
            f"{english} Use the {native_version} edition. "
            "Answer in English, with nothing else."
        )
    if not native or not native.strip():
        raise ValueError("a non-English text needs the question in its own language too")
    if answer_in_english:
        if not english_version or not english_version.strip():
            raise ValueError("an English answer needs english_version, which may differ from the native edition")
        edition = (
            f"Answer in English from the {english_version} edition. "
            f"That English edition is a translation and can differ from the {native_version} edition."
        )
    else:
        edition = f"Answer in the language of {native_version}, using that edition."
    return f"{english}\n{native}\n{edition}"


def draw_across_works(
    ordinary: list[Passage],
    famous: list[Passage],
    *,
    n: int = N_PASSAGES,
    famous_share: float = FAMOUS_SHARE,
    seed: int = 20261030,
) -> list[tuple[Passage, str]]:
    """Give each work an equal share of ``n``, then draw inside that share.

    Remainder slots go to works in sorted name order. A work with too small a
    pool raises, rather than quietly handing its slots to another work.
    """
    editions = sorted({(p.work, p.version) for p in ordinary} | {(p.work, p.version) for p in famous})
    if not editions:
        raise ValueError("no works to draw from")
    if n < len(editions):
        raise ValueError(f"n={n} is smaller than the number of editions ({len(editions)})")
    base, extra = divmod(n, len(editions))
    rows: list[tuple[Passage, str]] = []
    for i, (work, version) in enumerate(editions):
        quota = base + (1 if i < extra else 0)
        rows.extend(draw_passages(
            [p for p in ordinary if (p.work, p.version) == (work, version)],
            [p for p in famous if (p.work, p.version) == (work, version)],
            n=quota, famous_share=famous_share, seed=seed + i,
        ))
    return rows


def load_well_known(path: Path) -> list[Passage]:
    """Read ``well_known.yaml``. Every item must name a work, edition, and citation."""
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("items") or []
    passages: list[Passage] = []
    for i, raw in enumerate(items, start=1):
        work, version, citation = raw.get("work"), raw.get("version"), raw.get("citation")
        if not (work and version and citation):
            raise ValueError(f"{path}:{i} needs work, version, and citation")
        passages.append(Passage(
            citation=str(citation), work=str(work), version=str(version),
            weight=float(raw.get("weight") or 1),
            english_version=str(raw.get("english_version") or ""),
        ))
    return passages
