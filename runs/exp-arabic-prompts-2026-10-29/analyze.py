"""Score both conditions with the standard scorer and compare per cell.

The Arabic condition is scored on a normalized COPY of the answers (answers-ar-normalized.jsonl):
  - Arabic-Indic digits folded to ASCII (so a citation like ٢:٢٥٥ is not penalized)
  - for verify_source rows only, a leading «نعم»/«لا» token mapped to Yes/No
    (the scorer's leading-stance parse is English-only by contract)
Raw answers are untouched. The scorer itself (score_file) is the committed one.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/Users/mwk/Development/faithfamilytechnologynetwork/sacredtexts/pipelines")
from sacredbench.score import score_file  # noqa: E402

RUN = Path(sys.argv[1])

DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
YES_RE = re.compile(r'^[\s"«»“”\'‏‎]*نعم[\s,،.!:؛]*')
NO_RE = re.compile(r'^[\s"«»“”\'‏‎]*لا[\s,،.!:؛]+|^[\s"«»“”\'‏‎]*لا$')


def normalize_ar_answer(task: str, answer: str) -> str:
    out = answer.translate(DIGITS)
    if task == "verify_source":
        if YES_RE.match(out):
            out = YES_RE.sub("Yes. ", out, count=1)
        elif NO_RE.match(out):
            out = NO_RE.sub("No. ", out, count=1)
    return out


norm_path = RUN / "answers-ar-normalized.jsonl"
with (RUN / "answers-ar.jsonl").open(encoding="utf-8") as f, norm_path.open("w", encoding="utf-8") as g:
    n_mapped = 0
    for line in f:
        r = json.loads(line)
        if r.get("answer"):
            new = normalize_ar_answer(r["task"], r["answer"])
            if new != r["answer"]:
                n_mapped += 1
            r["answer"] = new
        g.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"normalized copy written ({n_mapped} answers transformed)")

score_file(RUN / "answers-en.jsonl", RUN / "scores-en.jsonl")
score_file(norm_path, RUN / "scores-ar.jsonl")


def load(p):
    return {
        (r["question_id"], r["model_id"]): r
        for r in (json.loads(l) for l in p.open(encoding="utf-8"))
    }


en, ar = load(RUN / "scores-en.jsonl"), load(RUN / "scores-ar.jsonl")
assert en.keys() == ar.keys() and len(en) == 56, (len(en), len(ar))

qmeta = {
    json.loads(l)["id"]: json.loads(l)["task"]
    for l in (RUN / "questions-en.jsonl").open(encoding="utf-8")
}


def outcome(r):
    o = r["metrics"]["outcome"]
    return o if o in ("refused", "correct", "incorrect") else ("correct" if r["metrics"]["correct"] else "incorrect")


print("\n=== per model x task: correct/refused/incorrect (n=7 each) ===")
models = sorted({m for _, m in en})
tasks = ["retrieve_quote", "complete_unit", "cite_passage", "verify_source"]
for m in models:
    for t in tasks:
        keys = [k for k in en if k[1] == m and qmeta[k[0]] == t]
        def tally(d):
            c = sum(1 for k in keys if outcome(d[k]) == "correct")
            rf = sum(1 for k in keys if outcome(d[k]) == "refused")
            return f"{c}✓ {rf}∅ {len(keys)-c-rf}✗"
        print(f"{m:8} {t:15} en: {tally(en):12}  ar: {tally(ar)}")

print("\n=== flips (outcome differs between conditions) ===")
n_flip = 0
for k in sorted(en):
    oe, oa = outcome(en[k]), outcome(ar[k])
    if oe != oa:
        n_flip += 1
        print(f"{k[1]:8} {qmeta[k[0]]:15} {k[0]}: en={oe} -> ar={oa}")
print(f"\n{n_flip} of 56 cells flipped")

print("\n=== headline ===")
for cond, d in (("en", en), ("ar", ar)):
    for m in models:
        keys = [k for k in d if k[1] == m]
        c = sum(1 for k in keys if outcome(d[k]) == "correct")
        rf = sum(1 for k in keys if outcome(d[k]) == "refused")
        inc = len(keys) - c - rf
        acc = c / (c + inc) if c + inc else float("nan")
        cov = (c + inc) / len(keys)
        print(f"{cond} {m:8} accuracy {acc:.1%} coverage {cov:.1%} ({c}✓ {rf}∅ {inc}✗ / {len(keys)})")
