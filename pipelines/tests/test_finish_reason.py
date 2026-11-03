"""#93: every chat-style provider path records the host's finish reason in ``usage``.

A ``length``-truncated completion on the plain OpenAI-compatible path (OpenRouter) used to be
committed with no trace that it was cut off. It is still committed and scored (a repetition loop
that exhausts the budget is the model failing the question), but now carries
``usage["finish_reason"]`` so analysis can flag it. SDKs are faked at their lazy import sites.
"""

from __future__ import annotations

import sys
import types

import pytest

from sacredbench.config import ModelSpec
from sacredbench.providers import complete


def _install_fake_openai(monkeypatch, resp):
    client = types.SimpleNamespace(
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **kw: resp))
    )
    fake = types.ModuleType("openai")
    fake.OpenAI = lambda **kw: client
    monkeypatch.setitem(sys.modules, "openai", fake)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")


def _chat_resp(content, finish):
    choice = types.SimpleNamespace(
        finish_reason=finish, message=types.SimpleNamespace(content=content)
    )
    return types.SimpleNamespace(
        choices=[choice],
        usage=types.SimpleNamespace(prompt_tokens=10, completion_tokens=4096),
        provider="DeepInfra",
    )


OPENROUTER_MODEL = ModelSpec(
    id="finish-reason-test", provider="openai", model="qwen/qwen3-32b", max_tokens=4096,
    temperature=0.0, base_url="https://openrouter.ai/api/v1", api_key_env="OPENROUTER_API_KEY",
)


@pytest.mark.parametrize("finish", ["length", "stop"])
def test_openrouter_chat_records_finish_reason_without_failing(monkeypatch, finish):
    loop = "ਸਚੁ " * 50
    _install_fake_openai(monkeypatch, _chat_resp(loop, finish))
    text, usage, attempts = complete(OPENROUTER_MODEL, "prompt")
    assert text == loop.strip() and attempts == 1  # committed and scored, not failed or retried
    assert usage["finish_reason"] == finish
    assert usage["provider"] == "DeepInfra" and usage["out"] == 4096


def test_openai_finish_reason_absent_is_not_invented(monkeypatch):
    choice = types.SimpleNamespace(message=types.SimpleNamespace(content="answer"))
    resp = types.SimpleNamespace(choices=[choice], usage=None)
    _install_fake_openai(monkeypatch, resp)
    _, usage, _ = complete(OPENROUTER_MODEL, "prompt")
    assert "finish_reason" not in usage


def test_anthropic_records_stop_reason(monkeypatch):
    resp = types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text="answer")],
        usage=types.SimpleNamespace(input_tokens=1, output_tokens=2),
        stop_reason="end_turn",
    )
    client = types.SimpleNamespace(messages=types.SimpleNamespace(create=lambda **kw: resp))
    fake = types.ModuleType("anthropic")
    fake.Anthropic = lambda **kw: client
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    m = ModelSpec(id="a", provider="anthropic", model="claude-x", max_tokens=256)
    _, usage, _ = complete(m, "prompt")
    assert usage["finish_reason"] == "end_turn"


def test_gemini_search_off_records_max_tokens_without_failing(monkeypatch):
    resp = types.SimpleNamespace(
        text="partial",
        candidates=[types.SimpleNamespace(finish_reason=types.SimpleNamespace(name="MAX_TOKENS"))],
        usage_metadata=types.SimpleNamespace(prompt_token_count=1, candidates_token_count=256),
    )
    client = types.SimpleNamespace(
        models=types.SimpleNamespace(generate_content=lambda **kw: resp)
    )
    fake_types = types.ModuleType("google.genai.types")
    fake_types.HttpOptions = lambda **kw: types.SimpleNamespace(**kw)
    fake_types.GenerateContentConfig = lambda **kw: types.SimpleNamespace(**kw)
    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = lambda **kw: client
    fake_genai.types = fake_types
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    m = ModelSpec(id="g", provider="gemini", model="gemini-x", max_tokens=256)
    text, usage, _ = complete(m, "prompt")
    assert text == "partial" and usage["finish_reason"] == "MAX_TOKENS"
