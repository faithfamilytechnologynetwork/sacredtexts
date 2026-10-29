"""Run configuration (YAML): the model panel and run parameters.

    concurrency: 8
    models:
      - id: haiku            # short id used in results files
        provider: anthropic  # anthropic | openai | gemini
        model: claude-haiku-5-5
        max_tokens: 1024
      - id: gemma-4
        provider: openai     # any OpenAI-chat-compatible host
        base_url: https://openrouter.ai/api/v1
        api_key_env: OPENROUTER_API_KEY
        model: google/gemma-4-27b-it
        max_tokens: 1024

Fail-fast: unknown providers, duplicate ids, and missing required keys raise
``ConfigError`` at load time, before any provider call.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

PROVIDERS = ("anthropic", "openai", "gemini")
# Tool-use settings a panel entry may request. Today only web search. It is each provider's
# NATIVE server-side search — Anthropic `web_search`, OpenAI Responses-API `web_search`,
# Google-Search grounding — i.e. the search a user actually gets from that product.
TOOLS = ("web_search",)
# Providers that expose a native server-side search tool. All three current providers do, so
# `web_search` is valid on each — but see the base_url guard below: on `openai` it is rejected
# when a third-party `base_url` is set, because that routes search through a third-party
# OpenAI-compatible host (OpenRouter `:online` / Exa), a uniform third-party layer rather than
# the real product experience (#54 explicitly rejects those). `anthropic`/`gemini` always use
# the vendor's own client in the provider seam (base_url is not a search path), so only the
# `openai` host needs guarding.
_NATIVE_SEARCH_PROVIDERS = frozenset({"anthropic", "openai", "gemini"})


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: str
    model: str
    max_tokens: int = 1024
    temperature: float | None = None  # unset → host default; recorded, never invented
    base_url: str | None = None
    api_key_env: str | None = None
    # optional USD price per 1M tokens; both must be given to compute a cost
    price_in: float | None = None
    price_out: float | None = None
    # tool-use settings (e.g. ("web_search",)); part of the model's panel identity
    tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunConfig:
    models: tuple[ModelSpec, ...]
    concurrency: int = 8


def _parse_tools(raw, provider: str, base_url: str | None, i: int, path: Path) -> tuple[str, ...]:
    """Validate a model entry's optional ``tools`` list, fail-fast. ``None`` → no tools.
    A non-list or an unrecognised value is a ``ConfigError``. ``web_search`` is a native
    server-side tool: valid on any provider that exposes one, but rejected on ``openai`` when
    a third-party ``base_url`` is set (that would route search through a third-party layer,
    which #54 forbids) — never silently ignored (the YAML key is otherwise unchecked today)."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ConfigError(f"{path}: models[{i}] 'tools' must be a list, got {type(raw).__name__}")
    tools: list[str] = []
    for t in raw:
        if t not in TOOLS:
            raise ConfigError(
                f"{path}: models[{i}] unknown tool {t!r} (supported: {TOOLS})"
            )
        if t == "web_search":
            if provider not in _NATIVE_SEARCH_PROVIDERS:
                raise ConfigError(
                    f"{path}: models[{i}] tool 'web_search' needs a provider with a native "
                    f"search tool ({sorted(_NATIVE_SEARCH_PROVIDERS)}), not {provider!r}"
                )
            if provider == "openai" and base_url:
                raise ConfigError(
                    f"{path}: models[{i}] tool 'web_search' is OpenAI's native Responses-API "
                    f"search and runs only on OpenAI's own endpoint; it must not route through "
                    f"a third-party OpenAI-compatible host (base_url={base_url!r}) — third-party "
                    "search layers (OpenRouter ':online' / Exa) are out of scope (#54)"
                )
        tools.append(t)
    # order-independent identity: a model's tools are a set, serialised sorted
    return tuple(sorted(set(tools)))


def load_config(path: Path) -> RunConfig:
    if not Path(path).exists():
        raise ConfigError(
            f"{path}: run config not found — copy configs/models.example.yaml to "
            "configs/models.yaml and set your panel (keys come from the environment)"
        )
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or not isinstance(data.get("models"), list) or not data["models"]:
        raise ConfigError(f"{path}: config must have a non-empty 'models' list")
    specs: list[ModelSpec] = []
    for i, m in enumerate(data["models"]):
        if not isinstance(m, dict):
            raise ConfigError(f"{path}: models[{i}] is not a mapping")
        for key in ("id", "provider", "model"):
            if not m.get(key):
                raise ConfigError(f"{path}: models[{i}] missing required key '{key}'")
        if m["provider"] not in PROVIDERS:
            raise ConfigError(
                f"{path}: models[{i}] unknown provider {m['provider']!r} (supported: {PROVIDERS})"
            )
        temperature = m.get("temperature")
        if temperature is not None:
            if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
                raise ConfigError(f"{path}: models[{i}] temperature must be a number")
            if not 0 <= float(temperature) <= 2:
                raise ConfigError(f"{path}: models[{i}] temperature must be between 0 and 2")
            temperature = float(temperature)
        price_in, price_out = m.get("price_in"), m.get("price_out")
        if (price_in is None) != (price_out is None):
            raise ConfigError(
                f"{path}: models[{i}] must set both price_in and price_out (USD per 1M tokens) or neither"
            )
        for pk, pv in (("price_in", price_in), ("price_out", price_out)):
            if pv is not None and (not isinstance(pv, (int, float)) or pv < 0):
                raise ConfigError(f"{path}: models[{i}] {pk} must be a non-negative number")
        tools = _parse_tools(m.get("tools"), m["provider"], m.get("base_url"), i, path)
        specs.append(
            ModelSpec(
                id=str(m["id"]),
                provider=m["provider"],
                model=str(m["model"]),
                max_tokens=int(m.get("max_tokens", 1024)),
                temperature=temperature,
                base_url=m.get("base_url"),
                api_key_env=m.get("api_key_env"),
                price_in=float(price_in) if price_in is not None else None,
                price_out=float(price_out) if price_out is not None else None,
                tools=tools,
            )
        )
    ids = [s.id for s in specs]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"{path}: duplicate model ids in config")
    concurrency = int(data.get("concurrency", 8))
    if concurrency < 1:
        raise ConfigError(f"{path}: concurrency must be >= 1")
    return RunConfig(models=tuple(specs), concurrency=concurrency)
