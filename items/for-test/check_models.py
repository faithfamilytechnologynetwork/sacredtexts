"""Confirm each panel model answers on OpenRouter, and record its catalogue fields.

Reads OPENROUTER_API_KEY from the environment, or from .env in the repo root.
Does not print the key. Writes runs/<id>/model.json: list price, context length,
and the token counts and cost from a one-word probe.

    python items/for-test/check_models.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PANEL = ROOT / "models" / "openrouter.yaml"
RUNS = REPO / "runs"
MODELS_URL = "https://openrouter.ai/api/v1/models"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    env = REPO / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    raise SystemExit("OPENROUTER_API_KEY is not set in the environment or .env")


def get_json(url: str, key: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="GET" if body is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode())


def catalogue_row(row: dict) -> dict:
    pricing = row.get("pricing") or {}
    top = row.get("top_provider") or {}
    arch = row.get("architecture") or {}
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "context_length": row.get("context_length"),
        "max_completion_tokens": top.get("max_completion_tokens"),
        "modality": arch.get("modality"),
        "tokenizer": arch.get("tokenizer"),
        "pricing_usd_per_token": {
            "prompt": pricing.get("prompt"),
            "completion": pricing.get("completion"),
            "request": pricing.get("request"),
        },
        "pricing_usd_per_million": {
            "input": _per_million(pricing.get("prompt")),
            "output": _per_million(pricing.get("completion")),
        },
        "supported_parameters": row.get("supported_parameters") or [],
    }


def _per_million(per_token) -> float | None:
    if per_token is None:
        return None
    return round(float(per_token) * 1_000_000, 6)


def probe(slug: str, key: str) -> dict:
    body = {
        "model": slug,
        "messages": [{"role": "user", "content": "Reply with the single word ok."}],
        "max_tokens": 16,
        "temperature": 0,
        "usage": {"include": True},
    }
    try:
        data = get_json(CHAT_URL, key, body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        return {"ok": False, "status": e.code, "error": detail}
    except Exception as e:  # noqa: BLE001 — record the failure and keep going
        return {"ok": False, "error": str(e)}
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    usage = data.get("usage") or {}
    return {
        "ok": True,
        "finish_reason": choice.get("finish_reason"),
        "text": (message.get("content") or "").strip(),
        "provider": data.get("provider"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "cost_usd": usage.get("cost"),
    }


def main() -> None:
    key = load_key()
    panel = yaml.safe_load(PANEL.read_text(encoding="utf-8"))["models"]
    catalog = {row["id"]: row for row in get_json(MODELS_URL, key)["data"]}
    failed = []
    for model in panel:
        slug = model["model"]
        row = catalog.get(slug)
        card = {
            "panel_id": model["id"],
            "openrouter_id": slug,
            "temperature": 0,
            "search": False,
        }
        if row is None:
            card["catalogue"] = None
            card["probe"] = {"ok": False, "error": "not in the OpenRouter model list"}
            failed.append(model["id"])
        else:
            card["catalogue"] = catalogue_row(row)
            card["probe"] = probe(slug, key)
            if not card["probe"].get("ok"):
                failed.append(model["id"])
        dest = RUNS / model["id"] / "model.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            previous = json.loads(dest.read_text(encoding="utf-8"))
            if "collected" in previous:
                card["collected"] = previous["collected"]
        dest.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
        status = "ok" if card["probe"].get("ok") else "FAIL"
        cost = card["probe"].get("cost_usd")
        print(f"{status:4} {model['id']:16} {slug} cost={cost}")
    if failed:
        raise SystemExit(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
