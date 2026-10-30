"""A/B analysis for the provider-native search experiment (#54), framed for H1/H2/H3.

Joins answers.jsonl + scores.jsonl in this run dir, and for each model's search-off vs
search-on arm reports: overall + per-text + per-task accuracy / coverage / outcome counts, the
failure-kind mix (via the committed `classify_failure`), and search provenance (cells that
fired native search, cited URLs). Prints a report; writes analysis.json.

    uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/analyze.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from sacredbench.failure_kind import classify_failure, expected_text

HERE = Path(__file__).resolve().parent
# model_id -> (base model label, arm) so we can pair off/on
ARMS = {
    "sonnet": ("sonnet", "off"), "sonnet-search": ("sonnet", "on"),
    "sol": ("sol", "off"), "sol-search": ("sol", "on"),
}
TEXTS = {"The Qur'an": "Qur'an", "Sahih al-Bukhari": "Bukhari"}


def load():
    answers = {}
    for line in (HERE / "answers.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            answers[(r["question_id"], r["model_id"])] = r
    rows = []
    for line in (HERE / "scores.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        s = json.loads(line)
        a = answers.get((s["question_id"], s["model_id"]))
        if a is None:
            continue
        m = s.get("metrics") or {}
        q = a.get("question") or {}
        src = q.get("source") or {}
        outcome = m.get("outcome") or ("correct" if m.get("correct") == 1 else "incorrect")
        kind = classify_failure(
            task=s["task"], correct=m.get("correct") == 1, refused=outcome == "refused",
            answer=a.get("answer") or "", expected=expected_text(q.get("expected") or {}),
            token_f1=m.get("token_f1"), normalized=m.get("normalized"),
            contains_reference=m.get("contains_reference"), n_candidates=m.get("n_candidates"),
        )
        rows.append({
            "model_id": s["model_id"], "task": s["task"], "text": src.get("work"),
            "outcome": outcome, "kind": kind, "usage": a.get("usage") or {},
            "question_id": s["question_id"],
        })
    return rows


def acc_cov(counter: Counter) -> tuple[float | None, float | None]:
    c, i, r = counter["correct"], counter["incorrect"], counter["refused"]
    acc = c / (c + i) if (c + i) else None
    cov = (c + i) / (c + i + r) if (c + i + r) else None
    return acc, cov


def fmt(x):
    return "  —  " if x is None else f"{x*100:5.1f}%"


def main() -> None:
    rows = load()
    # provenance per arm
    prov = defaultdict(lambda: {"searched": 0, "with_cites": 0, "n_cites": 0})
    for r in rows:
        u = r["usage"]
        if u.get("web_search_requests"):
            prov[r["model_id"]]["searched"] += 1
        cs = u.get("citations") or []
        if cs:
            prov[r["model_id"]]["with_cites"] += 1
            prov[r["model_id"]]["n_cites"] += len(cs)

    out = {"overall": {}, "by_text": {}, "by_task": {}, "kinds": {}, "provenance": dict(prov)}

    def counters(filt):
        d = defaultdict(Counter)
        for r in rows:
            if filt(r):
                d[r["model_id"]][r["outcome"]] += 1
        return d

    print("=" * 74)
    print("PROVENANCE (native search firing, per arm)")
    print("=" * 74)
    print(f"{'arm':<16}{'cells searched':<16}{'cells w/cites':<16}{'total cites'}")
    for mid in ARMS:
        p = prov[mid]
        print(f"{mid:<16}{p['searched']:<16}{p['with_cites']:<16}{p['n_cites']}")

    print("\n" + "=" * 74)
    print("OVERALL accuracy / coverage (off -> on), per model")
    print("=" * 74)
    ov = counters(lambda r: True)
    for base in ("sonnet", "sol"):
        off_id = base
        on_id = f"{base}-search"
        aoff, coff = acc_cov(ov[off_id]); aon, con = acc_cov(ov[on_id])
        out["overall"][base] = {"off": dict(ov[off_id]), "on": dict(ov[on_id])}
        print(f"  {base:<8} acc {fmt(aoff)} -> {fmt(aon)}   cov {fmt(coff)} -> {fmt(con)}   "
              f"(off {dict(ov[off_id])}  on {dict(ov[on_id])})")

    print("\n" + "=" * 74)
    print("BY TEXT accuracy / coverage (off -> on)")
    print("=" * 74)
    for work, label in TEXTS.items():
        bt = counters(lambda r, w=work: r["text"] == w)
        out["by_text"][label] = {}
        print(f"\n{label}:")
        for base in ("sonnet", "sol"):
            off_id, on_id = base, f"{base}-search"
            aoff, coff = acc_cov(bt[off_id]); aon, con = acc_cov(bt[on_id])
            out["by_text"][label][base] = {"off": dict(bt[off_id]), "on": dict(bt[on_id])}
            print(f"  {base:<8} acc {fmt(aoff)} -> {fmt(aon)}   cov {fmt(coff)} -> {fmt(con)}   "
                  f"(off {dict(bt[off_id])}  on {dict(bt[on_id])})")

    print("\n" + "=" * 74)
    print("BY TASK accuracy (off -> on)")
    print("=" * 74)
    for task in ("retrieve_quote", "complete_unit", "cite_passage", "verify_source"):
        bt = counters(lambda r, t=task: r["task"] == t)
        out["by_task"][task] = {}
        print(f"\n{task}:")
        for base in ("sonnet", "sol"):
            off_id, on_id = base, f"{base}-search"
            aoff, _ = acc_cov(bt[off_id]); aon, _ = acc_cov(bt[on_id])
            out["by_task"][task][base] = {"off": dict(bt[off_id]), "on": dict(bt[on_id])}
            print(f"  {base:<8} acc {fmt(aoff)} -> {fmt(aon)}   (off {dict(bt[off_id])}  on {dict(bt[on_id])})")

    print("\n" + "=" * 74)
    print("FAILURE-KIND MIX per arm (incorrect cells only)")
    print("=" * 74)
    for mid in ARMS:
        kinds = Counter(r["kind"] for r in rows if r["model_id"] == mid and r["kind"])
        out["kinds"][mid] = dict(kinds)
        print(f"  {mid:<16}{dict(kinds)}")

    # H3 focus: retrieve_quote failure kinds off vs on (edition/orthography signal)
    print("\n" + "=" * 74)
    print("H3 focus — retrieve_quote failure kinds (off -> on), per model")
    print("=" * 74)
    for base in ("sonnet", "sol"):
        for arm, mid in (("off", base), ("on", f"{base}-search")):
            kinds = Counter(r["kind"] for r in rows
                            if r["model_id"] == mid and r["task"] == "retrieve_quote" and r["kind"])
            print(f"  {base:<8} {arm:<4} {dict(kinds)}")

    (HERE / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\nwrote {HERE / 'analysis.json'}")


if __name__ == "__main__":
    main()
