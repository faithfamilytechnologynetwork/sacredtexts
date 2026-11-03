"""Write the paired-claim report from finished score files.

    uv --project pipelines run python items/for-test/claim_tests.py --run-dir runs/rerun-2026-11-03

Reads <run-dir>/<model>/base/**/scores.jsonl and the population question files.
A file still being collected is included only for the cells it has already scored.
Stops when an answer row in the run dir has no population question, unless --allow-partial.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Annotated

import typer
from paper_join import REPO, check_coverage, model_files, partial_note, population_questions, resolve_run_dir, rows

from sacredbench.claims import fisher_p, mcnemar_p, negative_kind

OUT = REPO / "runs" / "paper" / "claim-tests.md"


def _meta(row: dict) -> dict:
    src = row["source"]
    trad = src["tradition"][0] if isinstance(src.get("tradition"), list) else src.get("tradition")
    return {
        "tradition": trad,
        "language": src.get("language"),
        "true_tradition": (row.get("expected") or {}).get("true_tradition"),
        "citation": src.get("citation"),
        "work": src.get("work"),
        "condition": src.get("condition"),
    }


def _fmt(p: float | None) -> str:
    if p is None:
        return "—"
    if p < 1e-3:
        return f"{p:.2e}"
    return f"{p:.3f}"


def main(
    run_dir: Annotated[str, typer.Option(help="run root holding <model>/base/**, such as runs/rerun-2026-11-03")],
    allow_partial: Annotated[
        bool, typer.Option(help="write the report even when some answer rows have no question")
    ] = False,
) -> None:
    runs = resolve_run_dir(run_dir)
    by_id = population_questions()
    matched, total = check_coverage(runs, by_id, allow_partial)
    questions = {qid: _meta(row) for qid, row in by_id.items()}
    quote_cite: dict[tuple, dict[str, str]] = defaultdict(dict)
    prompts: dict[tuple, dict[str, str]] = defaultdict(dict)
    verify: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])
    negatives: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    canon: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])
    n_cells = 0
    models: set[str] = set()

    for model, path in model_files(runs, "scores.jsonl"):
        for row in rows(path):
            meta = questions.get(row["question_id"])
            if not meta:
                continue
            n_cells += 1
            models.add(model)
            outcome = (row.get("metrics") or {}).get("outcome")
            task = row["task"]
            if task in {"retrieve_quote", "cite_passage"}:
                key = (model, meta["condition"], meta["tradition"], meta["work"], meta["citation"])
                quote_cite[key][task] = outcome
                if meta["condition"] in {"ask_english", "ask_native"} and outcome in {"correct", "incorrect"}:
                    prompts[(model, task, meta["tradition"], meta["work"], meta["citation"])][meta["condition"]] = outcome
            if task == "verify_source" and outcome in {"correct", "incorrect", "refused"} and (row.get("metrics") or {}).get("expected") == "no":
                kind = negative_kind(meta.get("language"), meta.get("tradition"), meta.get("true_tradition"))
                slot = negatives[kind]
                if outcome == "correct":
                    slot[0] += 1
                elif outcome == "incorrect":
                    slot[1] += 1
                else:
                    slot[2] += 1
            if task == "verify_source" and outcome in {"correct", "incorrect"}:
                expected = (row.get("metrics") or {}).get("expected")
                if expected in {"yes", "no"}:
                    slot = verify[(model, expected)]
                    slot[0 if outcome == "correct" else 1] += 1
            if outcome in {"correct", "incorrect"} and meta["tradition"] in {"Book of Mormon", "Encyclicals"}:
                slot = canon[(model, meta["tradition"])]
                slot[0 if outcome == "correct" else 1] += 1

    def discordant(pairs, a_name, b_name, group):
        tally: dict = defaultdict(lambda: [0, 0])
        for key, sides in pairs.items():
            a, b = sides.get(a_name), sides.get(b_name)
            if a not in {"correct", "incorrect"} or b not in {"correct", "incorrect"}:
                continue
            g = group(key)
            if a == "correct" and b == "incorrect":
                tally[g][0] += 1
            elif a == "incorrect" and b == "correct":
                tally[g][1] += 1
        return tally

    cite_vs_quote = discordant(
        quote_cite, "retrieve_quote", "cite_passage", lambda key: key[0]
    )
    prompt_cite = discordant(
        {k: v for k, v in prompts.items() if k[1] == "cite_passage"},
        "ask_english",
        "ask_native",
        lambda key: key[0],
    )

    lines = [
        "# Paired claims",
        "",
        f"From {n_cells} scored cells across {len(models)} models in `{runs.relative_to(REPO) if runs.is_relative_to(REPO) else runs}`."
        f"{partial_note(matched, total)} A file still being collected contributes only the cells it already has. Accuracy comparisons drop refusals. McNemar is the two-sided exact test on discordant pairs of the same citation. Fisher exact compares two independent answered sets.",
        "",
        "## Citation, English prompt against native prompt",
        "",
        "English-only means the English prompt was correct and the native prompt was not. Native-only is the reverse.",
        "",
        "| model | English only | native only | pairs | p |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, (en, nn) in sorted(prompt_cite.items(), key=lambda kv: mcnemar_p(*kv[1]) or 1):
        if en + nn < 20:
            continue
        lines.append(f"| {model} | {en} | {nn} | {en + nn} | {_fmt(mcnemar_p(en, nn))} |")

    lines += [
        "",
        "## Quote against cite",
        "",
        "Quote-only means the quotation was correct and the citation was not, on the same citation, both answered.",
        "",
        "| model | quote only | cite only | pairs | p |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, (q, c) in sorted(cite_vs_quote.items(), key=lambda kv: mcnemar_p(*kv[1]) or 1):
        if q + c < 20:
            continue
        lines.append(f"| {model} | {q} | {c} | {q + c} | {_fmt(mcnemar_p(q, c))} |")

    lines += [
        "",
        "## Verify, real passage against a fake",
        "",
        "| model | real yes | not this edition | p |",
        "|---|---:|---:|---:|",
    ]
    for model in sorted({m for m, _ in verify}):
        yc, yi = verify[(model, "yes")]
        nc, ni = verify[(model, "no")]
        if yc + yi < 20 or nc + ni < 20:
            continue
        lines.append(
            f"| {model} | {yc}/{yc + yi} | {nc}/{nc + ni} | {_fmt(fisher_p(yc, yi, nc, ni))} |"
        )

    lines += [
        "",
        "## What a correct no is actually testing",
        "",
        "Different script is an alphabet check (Gurmukhi, Pali, Sanskrit, Greek). The other rows are same-script judgments.",
        "",
        "| negative | correct | wrong | refused |",
        "|---|---:|---:|---:|",
    ]
    for name, (correct, incorrect, refused) in sorted(negatives.items(), key=lambda kv: (kv[1][0] / (kv[1][0] + kv[1][1] or 1))):
        answered = correct + incorrect
        if not answered:
            continue
        lines.append(f"| {name} | {correct}/{answered} | {incorrect} | {refused} |")

    lines += [
        "",
        "## Book of Mormon against encyclicals",
        "",
        "Answered cells only. A model that refuses most of both sets can show a large gap in coverage and a small, non-significant gap here.",
        "",
        "| model | Book of Mormon | Encyclicals | p |",
        "|---|---:|---:|---:|",
    ]
    for model in sorted({m for m, _ in canon}):
        bc, bi = canon[(model, "Book of Mormon")]
        ec, ei = canon[(model, "Encyclicals")]
        if bc + bi < 30 or ec + ei < 30:
            continue
        lines.append(
            f"| {model} | {bc}/{bc + bi} | {ec}/{ec + ei} | {_fmt(fisher_p(bc, bi, ec, ei))} |"
        )
    lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    typer.run(main)
