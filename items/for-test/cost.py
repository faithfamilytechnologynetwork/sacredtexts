"""Price the OpenRouter panels for the population question files.

The earlier ~$70 and ~$14 figures were for the committed 476-question run.
This run has a different number of questions, so those dollar amounts do not
apply. Token rates are the measured tokens per call from that run
(runs/original-2026-10-21/summary.md), scaled by this run's question count.
gpt-oss-20b keeps its own output rate, which was much longer. Every other
model uses the mean output of haiku and opus on that run. A second total
prices every model as if it wrote as much as gpt-oss-20b.

Prices are OpenRouter's current prompt and completion rates. Search is off,
so the web-search fee is not included.

    python items/for-test/cost.py

Writes COST.md next to this file.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNNABLE = (
    ROOT / "christianity" / "english" / "population" / "questions.jsonl",
    ROOT / "judaism" / "native" / "population" / "questions.jsonl",
    ROOT / "judaism" / "english" / "population" / "questions.jsonl",
    ROOT / "islam" / "native" / "population" / "questions.jsonl",
)
PANEL = ROOT / "models" / "openrouter.yaml"
SUBSET = ROOT / "models" / "openrouter-subset.yaml"
OUT = ROOT / "COST.md"
# Population files on disk. Sikhism is written and is not in the collect join.
WRITTEN = (
    ("Christianity", [ROOT / "christianity" / "english" / "population" / "questions.jsonl"]),
    ("Judaism", [
        ROOT / "judaism" / "native" / "population" / "questions.jsonl",
        ROOT / "judaism" / "english" / "population" / "questions.jsonl",
    ]),
    ("Islam", [ROOT / "islam" / "native" / "population" / "questions.jsonl"]),
    ("Sikhism", [ROOT / "sikhism" / "native" / "population" / "questions.jsonl"]),
)
# Finished population design: 30 passages × 4 tasks per edition.
# Christianity stays one English edition (120). Every other tradition is two
# editions, native and English (240), the way Judaism is asked twice.
ONE_EDITION = 30 * 4
TWO_EDITIONS = ONE_EDITION * 2
MODELS_URL = "https://openrouter.ai/api/v1/models"

# Measured on the committed 476-question run, 3 models, search off.
COMMITTED_QUESTIONS = 476
COMMITTED_IN = {"haiku": 100_164, "opus": 100_164, "gpt-oss-20b": 93_811}
COMMITTED_OUT = {"haiku": 280_123, "opus": 212_214, "gpt-oss-20b": 796_291}

IN_PER_QUESTION = sum(COMMITTED_IN.values()) / (len(COMMITTED_IN) * COMMITTED_QUESTIONS)
CLOSED_OUT_PER_QUESTION = (COMMITTED_OUT["haiku"] + COMMITTED_OUT["opus"]) / (2 * COMMITTED_QUESTIONS)
VERBOSE_OUT_PER_QUESTION = COMMITTED_OUT["gpt-oss-20b"] / COMMITTED_QUESTIONS


def load_panel(path: Path) -> list[dict]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data["models"])


def question_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def six_traditions() -> list[tuple[str, int, str]]:
    """Finished population counts. Christianity is one edition. The rest are two.

    Christianity and Judaism are already at those counts. A mismatch means the
    question files changed and this table would be describing a different set.
    """
    on_disk = {name: sum(question_count(path) for path in paths) for name, paths in WRITTEN}
    if on_disk["Christianity"] != ONE_EDITION:
        raise SystemExit(f"Christianity population file has {on_disk['Christianity']} questions, expected {ONE_EDITION}")
    if on_disk["Judaism"] != TWO_EDITIONS:
        raise SystemExit(f"Judaism population files have {on_disk['Judaism']} questions, expected {TWO_EDITIONS}")
    rows = [
        ("Christianity", ONE_EDITION, "English only, counted from the question file"),
        ("Judaism", TWO_EDITIONS, "both editions counted from the question files"),
    ]
    for name in ("Islam", "Sikhism"):
        have = on_disk[name]
        rows.append((
            name,
            TWO_EDITIONS,
            f"{have} on disk; 240 once the English edition is added",
        ))
    for name in ("Hinduism", "Buddhism"):
        rows.append((name, TWO_EDITIONS, "estimated: native and English, 30 passages, 4 tasks"))
    return rows


def live_prices(slugs: list[str]) -> dict[str, dict[str, float]]:
    raw = urllib.request.urlopen(
        urllib.request.Request(MODELS_URL, headers={"User-Agent": "items-for-test-cost"}),
        timeout=60,
    ).read()
    catalog = {row["id"]: row for row in json.loads(raw)["data"]}
    missing = [slug for slug in slugs if slug not in catalog]
    if missing:
        raise SystemExit(f"OpenRouter has no price for {missing}")
    prices = {}
    for slug in slugs:
        pricing = catalog[slug]["pricing"]
        prices[slug] = {
            "prompt": float(pricing["prompt"]),
            "completion": float(pricing["completion"]),
        }
    return prices


def money(amount: float) -> str:
    return f"${amount:,.2f}"


def rate(per_token: float) -> str:
    return f"{per_token * 1_000_000:.4f}"


def output_per_question(model_id: str) -> float:
    if model_id == "gpt-oss-20b":
        return VERBOSE_OUT_PER_QUESTION
    return CLOSED_OUT_PER_QUESTION


def price_panel(panel: list[dict], prices: dict, n: int) -> tuple[list[str], float, float]:
    in_tokens = IN_PER_QUESTION * n
    lines = [
        "| id | Model | Input USD / 1M | Output USD / 1M | This run | If output matches gpt-oss-20b |",
        "|---|---|---:|---:|---:|---:|",
    ]
    base = 0.0
    verbose = 0.0
    for model in panel:
        slug = model["model"]
        price = prices[slug]
        input_cost = in_tokens * price["prompt"]
        output_cost = output_per_question(model["id"]) * n * price["completion"]
        verbose_cost = input_cost + VERBOSE_OUT_PER_QUESTION * n * price["completion"]
        total = input_cost + output_cost
        base += total
        verbose += verbose_cost
        lines.append(
            f"| `{model['id']}` | `{slug}` | {rate(price['prompt'])} | {rate(price['completion'])} | "
            f"{money(total)} | {money(verbose_cost)} |"
        )
    return lines, base, verbose


def main() -> None:
    n = sum(question_count(path) for path in RUNNABLE)
    traditions = six_traditions()
    n_complete = sum(count for _, count, _ in traditions)
    panel = load_panel(PANEL)
    subset = load_panel(SUBSET)
    slugs = [model["model"] for model in panel]
    prices = live_prices(slugs)
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    full_table, full_cost, full_verbose = price_panel(panel, prices, n)
    sub_table, sub_cost, sub_verbose = price_panel(subset, prices, n)
    _, complete_cost, complete_verbose = price_panel(panel, prices, n_complete)
    _, complete_sub, complete_sub_verbose = price_panel(subset, prices, n_complete)
    tradition_rows = [
        "| Tradition | Questions | How counted |",
        "|---|---:|---|",
        *[f"| {name} | {count} | {how} |" for name, count, how in traditions],
        f"| **All six** | **{n_complete}** | |",
    ]
    scale = n / COMMITTED_QUESTIONS

    lines = [
        "# Estimated OpenRouter cost",
        "",
        f"Prices fetched {fetched} from {MODELS_URL}.",
        "",
        "The run is List A, all 16 models, search off. With all six traditions complete,",
        f"budget **{money(complete_verbose)}**. That is the higher figure: every model writes as",
        f"much as gpt-oss-20b did on the committed run. The floor for those same {n_complete}",
        f"questions is **{money(complete_cost)}**.",
        "",
        f"Questions on disk today are {n} (Christianity, Judaism, Islam). That smaller run is",
        f"**{money(full_cost)}** to **{money(full_verbose)}** on List A.",
        "",
        "`search` in the panel file is `false`. No model is sent `web_search`, so this",
        "estimate has no web-search fee. Set that key to `true` or `both` to change it.",
        "",
        f"The ~$70 and ~$14 figures were for the committed **{COMMITTED_QUESTIONS}-question** run.",
        f"The population run has **{n}** questions, so those amounts are the wrong scale.",
        "The dollars below keep that run's measured tokens per call and multiply by",
        f"{n} / {COMMITTED_QUESTIONS} ({scale:.3f}). Input is the mean of the three measured models",
        f"({IN_PER_QUESTION:.1f} tokens per question). Output for gpt-oss-20b is its own measured",
        f"rate ({VERBOSE_OUT_PER_QUESTION:.1f} tokens per question). Every other model uses the mean",
        f"of haiku and opus ({CLOSED_OUT_PER_QUESTION:.1f}). The last column prices every model at the",
        "gpt-oss-20b output rate, which is the verbose-reasoner headroom.",
        "",
        "These prompts are not the committed run's prompts. The scale assumes a call",
        "costs about the same per question. Christianity stays one English edition.",
        "Every other tradition is two editions once the data is in: native and English,",
        "240 questions each. Islam and Sikhism have only the native edition on disk.",
        "Hinduism and Buddhism have no passages yet.",
        "",
        "## All six traditions",
        "",
        *tradition_rows,
        "",
        f"List A, six traditions: floor **{money(complete_cost)}**, higher budget **{money(complete_verbose)}**.",
        f"List B, six traditions: floor **{money(complete_sub)}**, higher budget **{money(complete_sub_verbose)}**.",
        "That total is the population sample only. Familiarity lists are not in it.",
        "",
        f"## List A — {len(panel)} models",
        "",
        *full_table,
        "",
        f"List A, this file: floor **{money(full_cost)}**, higher budget **{money(full_verbose)}**.",
        "",
        f"## List B — {len(subset)} models",
        "",
        *sub_table,
        "",
        f"List B for this file: **{money(sub_cost)}**. Verbose-reasoner headroom: **{money(sub_verbose)}**.",
        "",
        "List A is `models/openrouter.yaml`. List B is `models/openrouter-subset.yaml`.",
        "Both are search off, temperature 0, one `OPENROUTER_API_KEY`.",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"questions {n}  list A {money(full_cost)}  headroom {money(full_verbose)}")
    print(f"list B {money(sub_cost)}  headroom {money(sub_verbose)}")


if __name__ == "__main__":
    main()
