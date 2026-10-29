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
# Reached only via provider=openai with NO base_url (config.py forbids web_search on a
# third-party OpenAI-compatible host), so this always runs on OpenAI's own endpoint.
OPENAI_WEB_SEARCH_TOOL = {"type": "web_search"}

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
        # native search uses the Responses API, not chat.completions; config.py guarantees
        # base_url is unset here (no third-party host), so this hits OpenAI's own endpoint.
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
