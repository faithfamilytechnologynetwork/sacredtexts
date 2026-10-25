"""Agreement report: Jev judge verdicts vs the deterministic tiers (Spec 21, phase 4).

Joins a run's ``answers`` × ``scores`` × ``judgments`` on ``(question_id, model_id)`` for the judged
text-retrieval cells and quantifies how the paid judge's typed probabilities agree with the
deterministic headline the run already carries:

- **containment** — the judge's ``matches_requested_p`` (≥ ``THRESHOLD``) vs the deterministic
  ``contains_reference`` (0/1). The interesting cells are judge-says-contains where
  ``contains_reference == 0`` — the orthographic near-misses deterministic normalization can't fold.
- **refusal** — the judge's ``refusal_p`` (≥ ``THRESHOLD``) vs the deterministic ``refused`` outcome.
  This is a diagnostic cross-check only; refusal stays an outcome in ``outcomes.py``, never a grader.

Beside the thresholded agreement it reports the **raw per-deterministic-class probability
distribution** (so the judge's separation is visible, not just the 0.5 cut) and the **exhaustively
enumerated disagreement set** for manual review. It only READS a run (never re-scores, never mutates
committed ``scores.jsonl``/``answers.jsonl``/``summary.json``); its output is new sidecar evidence.

**Restricted-text reachability:** the report embeds full ``expected_text``/``answer`` for the manual
review, which the origin audit layer does not see (no ``source`` key). That is safe transitively, not
by the audit: ``jev.py``'s pre-send restricted guard means a restricted cell never gets a judgment
row, and this join is **judgment-driven**, so a restricted cell can never reach the report.
"""

from __future__ import annotations

import json
from pathlib import Path

from .jev import answer_digest as _answer_digest

THRESHOLD = 0.5
# the judged text-retrieval tasks (mirrors jev.JUDGED_TASKS; a judgment should only exist for these)
JUDGED_TASKS = ("retrieve_quote", "complete_unit")
_HIST_EDGES = (0.0, 0.25, 0.5, 0.75, 1.0)  # half-open bins [0,0.25), …, [0.75,1.0]


class AgreementError(Exception):
    pass


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AgreementError(f"{path}:{line_no}: not JSON ({exc})") from exc
    return rows


def _histogram(ps: list[float]) -> dict[str, int]:
    """Count probabilities into fixed half-open bins (the last bin includes 1.0)."""
    bins = {f"[{lo},{hi}{')' if hi < 1.0 else ']'}": 0
            for lo, hi in zip(_HIST_EDGES, _HIST_EDGES[1:])}
    labels = list(bins)
    for p in ps:
        idx = min(int(p / 0.25), 3)  # 1.0 → 3 (the last bin)
        bins[labels[idx]] += 1
    return bins


def _distribution(ps: list[float]) -> dict:
    """Summary of a probability list: n, mean (None when empty), and the fixed histogram."""
    return {
        "n": len(ps),
        "mean": round(sum(ps) / len(ps), 4) if ps else None,
        "histogram": _histogram(ps),
    }


def join_cells(answers: list[dict], scores: list[dict], judgments: list[dict]) -> list[dict]:
    """Join the three JSONL streams on ``(question_id, model_id)`` into one cell per judgment.

    A judgment is the judge's output, so it drives the universe: every judgment must have a matching
    score (a judgment with no score is an incoherent pairing → fail fast). The answer supplies the
    text/expected for manual review; a missing answer leaves the review context blank. When both the
    answer and the judgment's ``answer_digest`` are present, they are **cross-checked** (the judgment's
    digest must equal ``jev.answer_digest`` of the joined answer) so the report is self-verifying —
    pointing it at the wrong answers file fails fast rather than producing a plausible-looking but
    mis-joined report. Non-text-retrieval judgments (there should be none) fail fast."""
    scores_by_key = {(r.get("question_id"), r.get("model_id")): r for r in scores}
    answers_by_key = {(r.get("question_id"), r.get("model_id")): r for r in answers}
    cells = []
    for j in judgments:
        key = (j.get("question_id"), j.get("model_id"))
        score = scores_by_key.get(key)
        if score is None:
            raise AgreementError(f"judgment {key} has no matching score row; cannot join")
        task = score.get("task")
        if task not in JUDGED_TASKS:
            raise AgreementError(f"judgment {key} is for non-judged task {task!r}")
        metrics = score.get("metrics") or {}
        answer = answers_by_key.get(key) or {}
        expected = (((answer.get("question") or {}).get("expected")) or {}).get("text")
        # self-verify the join: the judgment's answer_digest must match the joined answer's digest
        row_digest = j.get("answer_digest")
        if row_digest is not None and "answer" in answer:
            actual = _answer_digest(answer.get("answer") or "")
            if actual != row_digest:
                raise AgreementError(
                    f"judgment {key} answer_digest {row_digest!r} != the joined answer's {actual!r}; "
                    "the judgments were produced over different answers — point at the matching run"
                )
        cells.append({
            "question_id": key[0],
            "model_id": key[1],
            "task": task,
            "contains_reference": metrics.get("contains_reference"),
            "outcome": metrics.get("outcome"),
            "token_f1": metrics.get("token_f1"),
            "refusal_p": j.get("refusal_p"),
            "matches_requested_p": j.get("matches_requested_p"),
            "equivalence": j.get("equivalence"),
            "kind": j.get("kind"),
            "answer": answer.get("answer"),
            "expected_text": expected,
        })
    return cells


def load(answers_path: Path, scores_path: Path, judgments_path: Path) -> list[dict]:
    """Read + join a run's three streams. Does not read any sidecar manifest (identity is the
    judge pass's own concern); this is a read-only analysis over finished artifacts."""
    return join_cells(_read_jsonl(answers_path), _read_jsonl(scores_path), _read_jsonl(judgments_path))


def _confusion(cells: list[dict], judge_true, det_true) -> dict:
    """A 2×2 of judge-verdict × deterministic-verdict over the cells, plus agreement rate."""
    both = judge_only = det_only = neither = 0
    for c in cells:
        jt, dt = judge_true(c), det_true(c)
        if jt and dt:
            both += 1
        elif jt and not dt:
            judge_only += 1
        elif dt and not jt:
            det_only += 1
        else:
            neither += 1
    n = len(cells)
    agree = both + neither
    return {
        "n": n,
        "agree": agree,
        "disagree": judge_only + det_only,
        "agreement_rate": round(agree / n, 4) if n else None,
        "both": both, "judge_only": judge_only, "deterministic_only": det_only, "neither": neither,
    }


def agreement(cells: list[dict]) -> dict:
    """The agreement report over joined cells: containment + refusal confusion at ``THRESHOLD``, the
    raw per-deterministic-class probability distributions, and the exhaustive disagreement set.

    Fail fast on a cell missing a probability or the deterministic field it is compared against — a
    silently-skipped cell would make the denominators lie."""
    for c in cells:
        for field in ("matches_requested_p", "refusal_p"):
            p = c.get(field)
            if not isinstance(p, (int, float)) or isinstance(p, bool) or not (0.0 <= float(p) <= 1.0):
                raise AgreementError(f"cell {(c['question_id'], c['model_id'])} {field} not a probability: {p!r}")
        if c.get("contains_reference") not in (0, 1):
            raise AgreementError(f"cell {(c['question_id'], c['model_id'])} contains_reference not 0/1: {c.get('contains_reference')!r}")
        if c.get("outcome") not in ("correct", "incorrect", "refused"):
            raise AgreementError(f"cell {(c['question_id'], c['model_id'])} outcome unexpected: {c.get('outcome')!r}")

    judge_contains = lambda c: c["matches_requested_p"] >= THRESHOLD
    det_contains = lambda c: c["contains_reference"] == 1
    judge_refusal = lambda c: c["refusal_p"] >= THRESHOLD
    det_refused = lambda c: c["outcome"] == "refused"

    # raw per-class distributions: the judge's probability split by the DETERMINISTIC class, so the
    # separation (not just the 0.5 cut) is visible.
    cont_by_class = {
        "contains_reference=1": _distribution([c["matches_requested_p"] for c in cells if det_contains(c)]),
        "contains_reference=0": _distribution([c["matches_requested_p"] for c in cells if not det_contains(c)]),
    }
    ref_by_class = {
        "refused": _distribution([c["refusal_p"] for c in cells if det_refused(c)]),
        "not_refused": _distribution([c["refusal_p"] for c in cells if not det_refused(c)]),
    }

    disagreements = []
    for c in cells:
        axes = []
        if judge_contains(c) != det_contains(c):
            axes.append("containment")
        if judge_refusal(c) != det_refused(c):
            axes.append("refusal")
        if axes:
            disagreements.append({
                "question_id": c["question_id"], "model_id": c["model_id"],
                "disagree_on": axes,
                "contains_reference": c["contains_reference"], "matches_requested_p": c["matches_requested_p"],
                "outcome": c["outcome"], "refusal_p": c["refusal_p"], "token_f1": c["token_f1"],
                "expected_text": c["expected_text"], "answer": c["answer"],
            })

    return {
        "n_cells": len(cells),
        "threshold": THRESHOLD,
        "containment": {"confusion": _confusion(cells, judge_contains, det_contains),
                        "judge_prob_by_deterministic_class": cont_by_class},
        "refusal": {"confusion": _confusion(cells, judge_refusal, det_refused),
                    "judge_prob_by_deterministic_class": ref_by_class},
        "n_disagreements": len(disagreements),
        "disagreements": disagreements,
    }


def _excerpt(text, limit: int = 160) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit] + "…"


def render_markdown(report: dict) -> str:
    """A compact human-readable agreement report (the sibling of the JSON artifact)."""
    lines = [
        "# Jev agreement report",
        "",
        f"Judged cells: **{report['n_cells']}** · threshold p ≥ {report['threshold']}",
        "",
        "## Containment — judge `matches_requested_p` vs deterministic `contains_reference`",
    ]
    cc = report["containment"]["confusion"]
    lines += [
        f"- agreement: **{cc['agreement_rate']}** ({cc['agree']}/{cc['n']}); "
        f"both {cc['both']}, judge-only {cc['judge_only']}, deterministic-only {cc['deterministic_only']}, "
        f"neither {cc['neither']}",
        "- judge `matches_requested_p` by deterministic class:",
    ]
    for cls, d in report["containment"]["judge_prob_by_deterministic_class"].items():
        lines.append(f"    - {cls}: n={d['n']} mean={d['mean']} {d['histogram']}")
    lines += ["", "## Refusal — judge `refusal_p` vs deterministic `refused` outcome"]
    rc = report["refusal"]["confusion"]
    lines += [
        f"- agreement: **{rc['agreement_rate']}** ({rc['agree']}/{rc['n']}); "
        f"both {rc['both']}, judge-only {rc['judge_only']}, deterministic-only {rc['deterministic_only']}, "
        f"neither {rc['neither']}",
        "- judge `refusal_p` by deterministic class:",
    ]
    for cls, d in report["refusal"]["judge_prob_by_deterministic_class"].items():
        lines.append(f"    - {cls}: n={d['n']} mean={d['mean']} {d['histogram']}")
    lines += ["", f"## Disagreements ({report['n_disagreements']})", ""]
    if not report["disagreements"]:
        lines.append("_None._")
    else:
        for d in report["disagreements"]:
            lines += [
                f"### {d['question_id']} × {d['model_id']} — {', '.join(d['disagree_on'])}",
                f"- contains_reference={d['contains_reference']} matches_requested_p={d['matches_requested_p']} "
                f"token_f1={d['token_f1']} · outcome={d['outcome']} refusal_p={d['refusal_p']}",
                f"- expected: `{_excerpt(d['expected_text'])}`",
                f"- answer: `{_excerpt(d['answer'])}`",
                "",
            ]
    return "\n".join(lines) + "\n"
