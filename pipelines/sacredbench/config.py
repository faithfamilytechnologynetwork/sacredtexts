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

from dataclasses import dataclass, replace
from pathlib import Path
from urllib.parse import urlparse

import yaml

PROVIDERS = ("anthropic", "openai", "gemini")
# Tool-use settings a panel entry may request. Today only web search. It is each provider's
# NATIVE server-side search — Anthropic `web_search`, OpenAI Responses-API `web_search`,
# Google-Search grounding — i.e. the search a user actually gets from that product.
TOOLS = ("web_search",)
# Providers that expose a native server-side search tool on their OWN endpoint. All three do.
_NATIVE_SEARCH_PROVIDERS = frozenset({"anthropic", "openai", "gemini"})
# `web_search` may also run through an OpenAI-compatible host (`provider: openai` + `base_url`)
# — but ONLY on a host DECLARED to forward the provider's NATIVE search, and only for a family
# that host forwards (verified per-arm, #54: provider-of-record is the real vendor, usage
# carries that vendor's `server_tool_use_details`, citations use the vendor's own annotation
# shape — NOT a uniform OpenRouter/Exa web layer). The host is pinned by netloc: an ARBITRARY
# OpenAI-compatible base_url is NOT assumed to forward native search (it could be any proxy or a
# generic web layer), so web_search on an unlisted host is rejected (#54 review item 1). The
# forwarded families are the KEYS of providers.OPENROUTER_SEARCH_TOOL_BY_FAMILY (single source of
# truth — imported where used to avoid an import cycle). gemini is intentionally absent: its
# grounding does not reliably fire through OpenRouter (routing-variance across Google AI Studio /
# Vertex), so it runs only on a native GEMINI_API_KEY (provider: gemini).
_SEARCH_FORWARDING_HOST_NETLOCS = frozenset({"openrouter.ai"})


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


def _parse_tools(
    raw, provider: str, base_url: str | None, model: str, i: int, path: Path
) -> tuple[str, ...]:
    """Validate a model entry's optional ``tools`` list, fail-fast. ``None`` → no tools.
    A non-list or an unrecognised value is a ``ConfigError``. ``web_search`` is native
    server-side search: valid on a provider's own endpoint, and also through an OpenAI-
    compatible host (``provider: openai`` + ``base_url``) but ONLY for a model family whose
    request OpenRouter forwards to the provider's native search (``_OPENROUTER_NATIVE_SEARCH_
    FAMILIES``) — any other family on a third-party host is a third-party web layer, which #54
    forbids. Never silently ignored (the YAML key is otherwise unchecked today)."""
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
                # import here (not at module top) to avoid a config<->providers import cycle
                from sacredbench.providers import OPENROUTER_SEARCH_TOOL_BY_FAMILY
                netloc = urlparse(base_url).netloc
                if netloc not in _SEARCH_FORWARDING_HOST_NETLOCS:
                    raise ConfigError(
                        f"{path}: models[{i}] tool 'web_search' on an OpenAI-compatible host is "
                        f"pinned to hosts declared to forward the provider's native search "
                        f"({sorted(_SEARCH_FORWARDING_HOST_NETLOCS)}); base_url={base_url!r} "
                        f"(host {netloc!r}) is not one — an arbitrary host is not assumed to "
                        "forward native search and could be a third-party web layer (#54)"
                    )
                families = tuple(OPENROUTER_SEARCH_TOOL_BY_FAMILY)
                if not any(model.startswith(fam) for fam in families):
                    raise ConfigError(
                        f"{path}: models[{i}] tool 'web_search' on host {netloc!r} is forwarded "
                        f"natively only for families {list(families)}; model {model!r} is not "
                        "one, so this would be a third-party web layer (':online' / Exa), out "
                        "of scope (#54)"
                    )
        tools.append(t)
    # order-independent identity: a model's tools are a set, serialised sorted
    return tuple(sorted(set(tools)))


def _search_supported(spec: ModelSpec, path: Path) -> bool:
    """True when this model can take native web_search under the existing host rules."""
    try:
        _parse_tools(["web_search"], spec.provider, spec.base_url, spec.model, 0, path)
    except ConfigError:
        return False
    return True


def _apply_search(raw, specs: list[ModelSpec], path: Path) -> list[ModelSpec]:
    """Panel-level search switch. Absent leaves each model's own ``tools`` list.

    ``false`` forces every model to no tools, so a later ``tools: [web_search]``
    cannot turn search on by accident. ``true`` adds ``web_search`` to every
    model and fails if any model cannot take it. ``both`` runs each model once
    with search off (its own id) and, when the host can forward native search,
    once more as ``<id>-search``.
    """
    if raw is None:
        return specs
    if raw is True:
        mode = "true"
    elif raw is False:
        mode = "false"
    elif isinstance(raw, str) and raw.strip().lower() in {"true", "false", "both"}:
        mode = raw.strip().lower()
    else:
        raise ConfigError(f"{path}: search must be false, true, or both, got {raw!r}")
    if mode == "false":
        return [replace(spec, tools=()) for spec in specs]
    if mode == "true":
        blocked = [spec.id for spec in specs if not _search_supported(spec, path)]
        if blocked:
            raise ConfigError(
                f"{path}: search is true, but these models cannot take native web_search "
                f"on this host: {blocked}. Set search to false, or to both."
            )
        return [replace(spec, tools=("web_search",)) for spec in specs]
    expanded: list[ModelSpec] = []
    for spec in specs:
        expanded.append(replace(spec, tools=()))
        if _search_supported(spec, path):
            expanded.append(replace(spec, id=f"{spec.id}-search", tools=("web_search",)))
    return expanded


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
        tools = _parse_tools(
            m.get("tools"), m["provider"], m.get("base_url"), str(m["model"]), i, path
        )
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
    specs = _apply_search(data.get("search", None), specs, path)
    ids = [s.id for s in specs]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"{path}: duplicate model ids in config")
    concurrency = int(data.get("concurrency", 8))
    if concurrency < 1:
        raise ConfigError(f"{path}: concurrency must be >= 1")
    return RunConfig(models=tuple(specs), concurrency=concurrency)
