"""Provider seam: one single-turn completion per (question, model).

Ported from multibench ``workflows/judging/judging/providers.py`` @ 14f6c9d4
(subject seam), trimmed to this pipeline's needs: single-turn prompts, no framing
prefix, no judge/schema seam yet (scoring is deterministic in Phase 1).

Kept from the original, deliberately:
- lazy SDK imports (tests mock at this seam without SDKs installed);
- missing credentials fail loud BEFORE any network call;
- bounded retries with linear backoff, then a loud ``ProviderError``;
- an explicit per-call HTTP timeout on EVERY live call (a hung socket must become
  a failed cell, never a wedged run);
- per-call usage extraction for cost accounting.

``provider: openai`` covers every OpenAI-chat-compatible host (OpenAI itself,
OpenRouter, …) via ``base_url`` + ``api_key_env``.
"""

from __future__ import annotations

import os
import time
from typing import Any

from sacredbench.config import ModelSpec

_BACKOFF_BASE_SECONDS = 2.0
REQUEST_TIMEOUT_SECONDS = 300.0

# Anthropic server-side web-search tool, pinned to one param version (the SDK exposes
# several; this is recorded in the committed run's README as part of what the run proves).
# max_uses bounds the per-call search cost.
WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 5}

# OpenAI Responses-API native web search — the search a ChatGPT user actually gets (#54).
# Pinned to the stable tool type; recorded in the run README as part of what the run proves.
OPENAI_WEB_SEARCH_TOOL = {"type": "web_search"}

# SINGLE SOURCE OF TRUTH (#54 review item 9): which model families an OpenRouter-class host
# forwards to the provider's OWN native server-side search, and the exact tool block to send
# for each. config.py derives its web_search allowlist from the KEYS of this map; this module
# picks the tool SHAPE from the VALUES. Add a family here and nowhere else — a new family must
# declare its block, so it can never silently inherit the normalised shape.
OPENROUTER_SEARCH_TOOL_BY_FAMILY = {
    "anthropic/": WEB_SEARCH_TOOL,       # Anthropic's native block, forwarded verbatim
    "openai/": OPENAI_WEB_SEARCH_TOOL,   # normalised {"type": "web_search"}
}

# Per-family expected provider-of-record (case-insensitive substring) and citation annotation
# style — the mechanical nativeness signals asserted on every search-on cell (#54 review item 4):
# the host's upstream must be the real vendor, and (when the answer cites) the annotation shape
# must be that vendor's own (Anthropic ships a `content` snippet; OpenAI ships char offsets).
_EXPECTED_PROVIDER_SUBSTR = {"anthropic/": ("claude", "anthropic"), "openai/": ("openai",)}
_EXPECTED_CITATION_STYLE = {"anthropic/": "anthropic_content", "openai/": "openai_offsets"}

# stop_reasons that mean the turn FINISHED and its text is the model's real answer. Any
# other value is an incomplete turn — max_tokens (truncated), pause_turn (a long-running
# server-tool turn that wants continuation), refusal, or model_context_window_exceeded —
# whose partial text must never be committed as the answer and must not be retried (each
# retry re-bills the web search). We make single-turn requests with no CLIENT-side tools,
# so tool_use is not a terminal-success reason for us either.
_TERMINAL_STOP = frozenset({"end_turn", "stop_sequence"})


class ProviderError(Exception):
    """A provider call failed (credentials / transport / empty response) — fail loud."""


def _require_env(*names: str) -> None:
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise ProviderError(f"missing credential env var(s): {', '.join(missing)}")


def sampling_kwargs(model: ModelSpec) -> dict:
    """Provider sampling args. Temperature is omitted when unset, so the host default stands."""
    if model.temperature is None:
        return {}
    return {"temperature": model.temperature}


def is_quota_error(exc: BaseException) -> bool:
    """True when the host refused the call for credit or quota, not a transient blip."""
    if getattr(exc, "status_code", None) == 402:
        return True
    text = str(exc).lower()
    return any(
        phrase in text
        for phrase in (
            "insufficient credit",
            "insufficient credits",
            "payment required",
            "out of credits",
            "exceeded your current quota",
        )
    )


def complete(model: ModelSpec, prompt: str, retries: int = 2) -> tuple[str, dict, int]:
    """Single-turn completion. Returns ``(text, usage, attempts)``; raises ``ProviderError``."""
    if model.provider == "anthropic":
        call = _anthropic
    elif model.provider == "openai":
        call = _openai
    elif model.provider == "gemini":
        call = _gemini
    else:
        raise ProviderError(
            f"unsupported provider {model.provider!r} (supported: anthropic, openai, gemini)"
        )
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            text, usage = call(model, prompt)
            if not text.strip():
                raise RuntimeError("empty response")
            return text.strip(), usage, attempt + 1
        except ProviderError:
            raise  # credentials / config: not transient, don't retry
        except Exception as e:  # noqa: BLE001 — transient API/transport; retry then fail
            if is_quota_error(e):
                raise ProviderError(
                    f"{model.id}: OpenRouter quota or credit stopped the call: {e}"
                ) from e
            last = e
            if attempt < retries:
                time.sleep(_BACKOFF_BASE_SECONDS * (attempt + 1))
    raise ProviderError(f"{model.id}: call failed after {retries + 1} attempts: {last}")


def _anthropic(model: ModelSpec, prompt: str) -> tuple[str, dict]:
    _require_env("ANTHROPIC_API_KEY")
    import anthropic

    client = anthropic.Anthropic(timeout=REQUEST_TIMEOUT_SECONDS)
    kwargs: dict[str, Any] = {
        "model": model.model,
        "max_tokens": model.max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        **sampling_kwargs(model),
    }
    if "web_search" in model.tools:
        kwargs["tools"] = [WEB_SEARCH_TOOL]
    resp = client.messages.create(**kwargs)
    # Only a FINISHED turn carries a real answer. An incomplete stop_reason (max_tokens
    # truncation, pause_turn mid-web-search, refusal, context-exceeded) would otherwise be
    # committed as a partial quote — indistinguishable from a genuinely wrong answer, which
    # corrupts the search-on/off contrast — or, when empty, retried, re-billing the web
    # search. Fail loud so the cell stays pending with a clear reason.
    stop = getattr(resp, "stop_reason", None)
    if stop not in _TERMINAL_STOP:
        raise ProviderError(
            f"{model.id}: incomplete turn (stop_reason={stop!r}) — not committing a partial "
            f"answer. For max_tokens, raise max_tokens ({model.max_tokens}); pause_turn means "
            "the server-tool turn wanted continuation. Retrying would re-bill the web search."
        )
    # text blocks only — a web-search response also carries server_tool_use /
    # web_search_tool_result blocks, which are not the answer.
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return text, _anthropic_usage(resp)


def _openai(model: ModelSpec, prompt: str) -> tuple[str, dict]:
    env = model.api_key_env or "OPENAI_API_KEY"
    _require_env(env)
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ[env], base_url=model.base_url, timeout=REQUEST_TIMEOUT_SECONDS
    )
    if "web_search" in model.tools:
        if model.base_url:
            # OpenRouter (or another OpenAI-compatible host): web_search runs through
            # chat.completions, and the host forwards it to the provider's NATIVE search.
            # config.py guarantees the model family is one that host forwards natively.
            return _openai_openrouter_search(client, model, prompt)
        # native OpenAI: web_search uses the Responses API, not chat.completions.
        return _openai_responses_search(client, model, prompt)
    # OpenAI proper only accepts `max_completion_tokens`; OpenAI-compatible hosts
    # (base_url set: OpenRouter etc.) still take legacy `max_tokens`.
    tok_kwarg = "max_tokens" if model.base_url else "max_completion_tokens"
    resp = client.chat.completions.create(
        model=model.model,
        messages=[{"role": "user", "content": prompt}],
        **{tok_kwarg: model.max_tokens},
        **sampling_kwargs(model),
    )
    text = resp.choices[0].message.content or ""
    usage = _openai_usage(resp)
    # OpenRouter reports the actual serving host; record it for provenance.
    provider = getattr(resp, "provider", None)
    if provider:
        usage["provider"] = provider
    return text, usage


def _openai_responses_search(client: Any, model: ModelSpec, prompt: str) -> tuple[str, dict]:
    """Single-turn Responses-API call with OpenAI's native web_search tool."""
    resp = client.responses.create(
        model=model.model,
        input=prompt,
        tools=[OPENAI_WEB_SEARCH_TOOL],
        max_output_tokens=model.max_tokens,
        **sampling_kwargs(model),
    )
    # Only a COMPLETED turn carries a real answer. An incomplete turn (max_output_tokens
    # truncation mid-search, etc.) must never be committed as a partial quote — it corrupts
    # the search-on/off contrast — nor retried (each retry re-bills the web search). Fail loud
    # so the cell stays pending with a clear reason. Mirrors the Anthropic stop_reason guard.
    status = getattr(resp, "status", None)
    if status != "completed":
        reason = getattr(getattr(resp, "incomplete_details", None), "reason", None)
        raise ProviderError(
            f"{model.id}: incomplete Responses turn (status={status!r}, reason={reason!r}) — "
            f"not committing a partial answer. For max_output_tokens, raise max_tokens "
            f"({model.max_tokens}). Retrying would re-bill the web search."
        )
    text = getattr(resp, "output_text", None) or ""
    return text, _openai_responses_usage(resp)


def _family_of(model_slug: str) -> str | None:
    """The forwarded-family prefix this slug belongs to (``anthropic/`` / ``openai/``), or None."""
    for fam in OPENROUTER_SEARCH_TOOL_BY_FAMILY:
        if model_slug.startswith(fam):
            return fam
    return None


def _openrouter_search_tool(model_slug: str) -> dict:
    """The native-search tool block the host forwards for this model family, from the single
    source of truth. config.py has already confirmed the family is forwarded; defensive here."""
    fam = _family_of(model_slug)
    if fam is None:
        raise ProviderError(f"{model_slug}: no OpenRouter native-search tool shape for this family")
    return OPENROUTER_SEARCH_TOOL_BY_FAMILY[fam]


def _assert_native_arm(model_slug: str, usage: dict) -> None:
    """Fail loud unless this search-on cell mechanically proves the provider's OWN native
    search ran — not an OpenRouter-side generic/Exa layer (#54 review item 4). Every search-on
    cell must carry a provider-of-record matching the family; a cell that cited must carry the
    family's own annotation shape. This is the load-bearing discipline of the experiment, made
    mechanical so a drifted/non-native response stays pending instead of being committed."""
    fam = _family_of(model_slug)
    if fam is None:
        return
    prov = (usage.get("provider") or "").lower()
    if not prov:
        raise ProviderError(
            f"{model_slug}: search-on cell carries no provider-of-record — cannot prove native "
            "search (vs an OpenRouter/Exa layer); refusing to commit."
        )
    if not any(sub in prov for sub in _EXPECTED_PROVIDER_SUBSTR[fam]):
        raise ProviderError(
            f"{model_slug}: provider-of-record {usage.get('provider')!r} does not match the "
            f"native provider expected for family {fam!r} {_EXPECTED_PROVIDER_SUBSTR[fam]} — "
            "refusing (possible non-native / third-party search)."
        )
    style = usage.get("citation_style")
    if style and style != _EXPECTED_CITATION_STYLE[fam]:
        raise ProviderError(
            f"{model_slug}: cited with annotation style {style!r}, not the {fam!r} native shape "
            f"{_EXPECTED_CITATION_STYLE[fam]!r} — a uniform layer would not match the vendor's "
            "own shape; refusing (possible non-native search)."
        )


def _openai_openrouter_search(client: Any, model: ModelSpec, prompt: str) -> tuple[str, dict]:
    """Single-turn chat.completions call that carries a provider's NATIVE web search through an
    OpenAI-compatible host (OpenRouter). Records provider-of-record, the server-tool search
    count, cost, and cited URLs into usage, and asserts the arm is mechanically native before
    returning — the per-cell nativeness evidence #54 requires."""
    resp = client.chat.completions.create(
        model=model.model,
        messages=[{"role": "user", "content": prompt}],
        tools=[_openrouter_search_tool(model.model)],
        max_tokens=model.max_tokens,
        extra_body={"usage": {"include": True}},  # ask the host to return cost + server_tool_use
        **sampling_kwargs(model),
    )
    choice = resp.choices[0]
    # Only a finished turn carries a real answer. A truncated turn (finish_reason 'length') or
    # an upstream error ('error') must never be committed as a partial quote nor retried
    # in-call (re-billing the search) — fail loud so the cell stays pending for a clean re-run.
    if choice.finish_reason != "stop":
        raise ProviderError(
            f"{model.id}: non-terminal finish_reason={choice.finish_reason!r} via "
            f"{getattr(resp, 'provider', None)!r} — not committing a partial answer. "
            f"For 'length', raise max_tokens ({model.max_tokens}); 'error' is an upstream "
            "failure (re-run retries the pending cell)."
        )
    text = choice.message.content or ""
    usage = _openrouter_usage(resp, choice)
    _assert_native_arm(model.model, usage)  # mechanical nativeness gate — fail loud if not native
    return text, usage


def _gemini(model: ModelSpec, prompt: str) -> tuple[str, dict]:
    _require_env("GEMINI_API_KEY")
    from google import genai
    from google.genai import types

    client = genai.Client(
        http_options=types.HttpOptions(timeout=int(REQUEST_TIMEOUT_SECONDS * 1000))
    )
    search_on = "web_search" in model.tools
    cfg_kwargs: dict[str, Any] = {"max_output_tokens": model.max_tokens, **sampling_kwargs(model)}
    if search_on:
        # Google-Search grounding — the search a Gemini user actually gets (#54).
        cfg_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    resp = client.models.generate_content(
        model=model.model,
        contents=prompt,
        config=types.GenerateContentConfig(**cfg_kwargs),
    )
    if search_on:
        # Only a STOP finish carries a real answer. A truncated/blocked grounded turn
        # (MAX_TOKENS, SAFETY, RECITATION, …) must not be committed as a partial quote; fail
        # loud so the cell stays pending. Scoped to the search arm so the search-off path is
        # byte-identical to prior behaviour (no committed run uses the native non-search path).
        cands = getattr(resp, "candidates", None) or []
        fr = getattr(cands[0], "finish_reason", None) if cands else None
        fr_name = getattr(fr, "name", str(fr))
        if fr_name != "STOP":
            raise ProviderError(
                f"{model.id}: incomplete grounded turn (finish_reason={fr_name}) — not "
                f"committing a partial answer. For MAX_TOKENS, raise max_tokens "
                f"({model.max_tokens})."
            )
    text = getattr(resp, "text", None) or ""
    usage = _gemini_usage(resp)
    if search_on:
        usage.update(_gemini_search_provenance(resp))
    return text, usage


# --- Usage extraction (best-effort; defensive) --------------------------------


def _anthropic_usage(resp: Any) -> dict:
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    usage = {
        "in": getattr(u, "input_tokens", 0) or 0,
        "out": getattr(u, "output_tokens", 0) or 0,
    }
    # server-side web-search is billed per request (not in in/out tokens); record the
    # count as provenance when present (the committed run stays unpriced, so this never
    # feeds a cost figure — it just documents that search ran and how much).
    stu = getattr(u, "server_tool_use", None)
    if stu is not None:
        wsr = getattr(stu, "web_search_requests", None)
        if wsr:
            usage["web_search_requests"] = wsr
    return usage


def _openai_usage(resp: Any) -> dict:
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    return {
        "in": getattr(u, "prompt_tokens", 0) or 0,
        "out": getattr(u, "completion_tokens", 0) or 0,
    }


def _dedupe(urls: list[str]) -> list[str]:
    """First-seen-order unique — provenance should list each cited URL once."""
    seen: dict[str, None] = {}
    for u in urls:
        seen.setdefault(u, None)
    return list(seen)


def _openai_responses_usage(resp: Any) -> dict:
    """Tokens plus search provenance: how many web_search calls fired and which URLs the
    answer cited (``usage['web_search_requests']`` / ``usage['citations']``, present only when
    non-empty — same shape as the Anthropic path records). Best-effort and defensive."""
    out: dict = {}
    u = getattr(resp, "usage", None)
    if u is not None:
        out = {
            "in": getattr(u, "input_tokens", 0) or 0,
            "out": getattr(u, "output_tokens", 0) or 0,
        }
    searches = 0
    citations: list[str] = []
    for item in getattr(resp, "output", None) or []:
        itype = getattr(item, "type", None)
        if itype == "web_search_call":
            searches += 1
        elif itype == "message":
            for block in getattr(item, "content", None) or []:
                if getattr(block, "type", None) != "output_text":
                    continue
                for ann in getattr(block, "annotations", None) or []:
                    if getattr(ann, "type", None) == "url_citation":
                        url = getattr(ann, "url", None)
                        if url:
                            citations.append(url)
    if searches:
        out["web_search_requests"] = searches
    if citations:
        out["citations"] = _dedupe(citations)
    return out


def _openrouter_usage(resp: Any, choice: Any) -> dict:
    """Tokens + nativeness provenance from an OpenAI-compatible host (OpenRouter): the
    provider-of-record, the server-tool web-search count (``server_tool_use_details``), and the
    cited URLs (message ``annotations``). ``web_search_requests`` / ``citations`` keep the same
    shape the native paths record. Best-effort and defensive."""
    out: dict = {}
    u = getattr(resp, "usage", None)
    udump = u.model_dump() if (u is not None and hasattr(u, "model_dump")) else {}
    out["in"] = udump.get("prompt_tokens", 0) or 0
    out["out"] = udump.get("completion_tokens", 0) or 0
    stu = udump.get("server_tool_use_details")
    if isinstance(stu, dict) and stu.get("web_search_requests"):
        out["web_search_requests"] = stu["web_search_requests"]
    # per-cell cost (the host reports it with usage.include; UNPRICED scoring ignores it, but
    # recording it makes cost provenance TRUE for future collects — #54 review item 3).
    cost = udump.get("cost")
    if cost is not None:
        out["cost"] = cost
    # provider-of-record (OpenRouter's upstream): part of the per-cell nativeness evidence
    provider = getattr(resp, "provider", None)
    if provider:
        out["provider"] = provider
    citations: list[str] = []
    style: str | None = None
    for ann in getattr(choice.message, "annotations", None) or []:
        ad = ann.model_dump() if hasattr(ann, "model_dump") else (ann if isinstance(ann, dict) else {})
        if ad.get("type") == "url_citation":
            uc = ad.get("url_citation") or {}
            url = uc.get("url")
            if url:
                citations.append(url)
            style = style or _citation_style(uc)
    if citations:
        out["citations"] = _dedupe(citations)
    if style:
        out["citation_style"] = style
    return out


def _citation_style(url_citation: dict) -> str | None:
    """Classify a url_citation annotation by its vendor-native shape: Anthropic ships a
    ``content`` snippet; OpenAI ships character offsets. The per-provider difference is the
    decisive proof the search is native, not a uniform OpenRouter/Exa layer (#54)."""
    if url_citation.get("content"):
        return "anthropic_content"
    if url_citation.get("start_index") is not None or url_citation.get("end_index") is not None:
        return "openai_offsets"
    return "other"


def _gemini_search_provenance(resp: Any) -> dict:
    """Grounding provenance from the first candidate's grounding_metadata: the count of
    Google-Search queries issued (``web_search_requests``) and the grounded source URLs
    (``citations``). Best-effort and defensive; empty fields are omitted."""
    cands = getattr(resp, "candidates", None) or []
    if not cands:
        return {}
    gm = getattr(cands[0], "grounding_metadata", None)
    if gm is None:
        return {}
    out: dict = {}
    queries = getattr(gm, "web_search_queries", None) or []
    if queries:
        out["web_search_requests"] = len(queries)
    citations: list[str] = []
    for chunk in getattr(gm, "grounding_chunks", None) or []:
        web = getattr(chunk, "web", None)
        uri = getattr(web, "uri", None) if web is not None else None
        if uri:
            citations.append(uri)
    if citations:
        out["citations"] = _dedupe(citations)
    return out


def _gemini_usage(resp: Any) -> dict:
    u = getattr(resp, "usage_metadata", None)
    if u is None:
        return {}
    return {
        "in": getattr(u, "prompt_token_count", 0) or 0,
        "out": (getattr(u, "candidates_token_count", 0) or 0)
        + (getattr(u, "thoughts_token_count", 0) or 0),
    }
