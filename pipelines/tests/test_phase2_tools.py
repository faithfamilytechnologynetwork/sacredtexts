"""Web-search tool: config validation, collect fingerprint, provider seam, and the
tools-aware panel identity (Spec 8, Phase 2). No live API calls — the Anthropic SDK is
faked at its lazy import site."""

from __future__ import annotations

import json
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

from sacredbench import collect as collect_mod
from sacredbench import providers
from sacredbench.collect import CollectError, _panel_fingerprint, collect
from sacredbench.config import ConfigError, ModelSpec, RunConfig, load_config
from sacredbench.generate import Question
from sacredbench.providers import ProviderError, complete
from sacredbench.score import score_file

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = REPO_ROOT / "configs" / "models.example.yaml"


# --- config validation -------------------------------------------------------


def test_example_panel_loads_as_four_entries():
    cfg = load_config(EXAMPLE)
    assert [m.id for m in cfg.models] == ["opus-search", "opus", "haiku-search", "haiku"]
    by_id = {m.id: m for m in cfg.models}
    assert by_id["opus-search"].tools == ("web_search",) and by_id["opus"].tools == ()
    assert by_id["haiku-search"].tools == ("web_search",) and by_id["haiku"].tools == ()
    assert all(m.price_in is None and m.price_out is None for m in cfg.models)  # unpriced


def _write(tmp_path, models) -> Path:
    import yaml
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({"models": models}))
    return p


def test_web_search_on_undeclared_host_rejected(tmp_path):
    """web_search through an OpenAI-compatible host is pinned to hosts DECLARED to forward native
    search; an arbitrary host is not assumed to forward it — rejected even for a native family
    (#54 review item 1: no silent third-party-layer bypass)."""
    cfg = _write(tmp_path, [{"id": "a", "provider": "openai", "model": "anthropic/claude-sonnet-5.5",
                            "base_url": "https://evil-proxy.example/v1", "api_key_env": "K",
                            "tools": ["web_search"]}])
    with pytest.raises(ConfigError, match="not assumed to forward native search"):
        load_config(cfg)


def test_web_search_on_openrouter_native_family_accepted(tmp_path):
    """anthropic/* and openai/* on the DECLARED OpenRouter host carry the provider's NATIVE
    search (verified #54), so web_search is accepted there even with a base_url set."""
    for slug in ("anthropic/claude-sonnet-5.5", "openai/gpt-6.1-sol"):
        cfg = _write(tmp_path, [{"id": "a", "provider": "openai", "model": slug,
                                 "base_url": "https://openrouter.ai/api/v1",
                                 "api_key_env": "OPENROUTER_API_KEY", "tools": ["web_search"]}])
        loaded = load_config(cfg)
        assert loaded.models[0].tools == ("web_search",)


def test_web_search_gemini_family_on_openrouter_rejected(tmp_path):
    """google/* is intentionally NOT a forwarded family (grounding doesn't fire reliably through
    OpenRouter) — web_search on it even on the declared host is rejected; native key only."""
    cfg = _write(tmp_path, [{"id": "g", "provider": "openai", "model": "google/gemini-3.8-flash",
                             "base_url": "https://openrouter.ai/api/v1",
                             "api_key_env": "OPENROUTER_API_KEY", "tools": ["web_search"]}])
    with pytest.raises(ConfigError, match="natively only for families"):
        load_config(cfg)


def test_web_search_native_openai_accepted(tmp_path):
    """Native OpenAI (no base_url) + web_search is now valid — Responses-API search."""
    cfg = _write(tmp_path, [{"id": "a", "provider": "openai", "model": "gpt-x", "tools": ["web_search"]}])
    loaded = load_config(cfg)
    assert loaded.models[0].tools == ("web_search",) and loaded.models[0].base_url is None


def test_web_search_native_gemini_accepted(tmp_path):
    """Native Gemini + web_search is valid — Google-Search grounding."""
    cfg = _write(tmp_path, [{"id": "g", "provider": "gemini", "model": "gemini-x", "tools": ["web_search"]}])
    assert load_config(cfg).models[0].tools == ("web_search",)


def test_unknown_tool_rejected(tmp_path):
    cfg = _write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "tools": ["code_exec"]}])
    with pytest.raises(ConfigError, match="unknown tool"):
        load_config(cfg)


def test_items_for_test_panel_is_search_off():
    cfg = load_config(REPO_ROOT / "items" / "for-test" / "models" / "openrouter.yaml")
    assert len(cfg.models) == 16
    assert all(m.tools == () for m in cfg.models)
    assert all(m.temperature == 0 for m in cfg.models)
    assert {m.base_url for m in cfg.models} == {"https://openrouter.ai/api/v1"}


def test_panel_search_false_strips_tools(tmp_path):
    import yaml
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({
        "search": False,
        "models": [{"id": "a", "provider": "anthropic", "model": "m", "tools": ["web_search"]}],
    }))
    assert load_config(p).models[0].tools == ()


def test_panel_search_true_sets_tools(tmp_path):
    import yaml
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({
        "search": True,
        "models": [{"id": "a", "provider": "openai", "model": "openai/gpt-6.1-sol",
                    "base_url": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"}],
    }))
    assert load_config(p).models[0].tools == ("web_search",)


def test_panel_search_true_rejects_unforwarded_family(tmp_path):
    import yaml
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({
        "search": True,
        "models": [{"id": "g", "provider": "openai", "model": "google/gemini-4-argon",
                    "base_url": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"}],
    }))
    with pytest.raises(ConfigError, match="cannot take native web_search"):
        load_config(p)


def test_panel_search_both_splits_supported_models(tmp_path):
    import yaml
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({
        "search": "both",
        "models": [
            {"id": "sol", "provider": "openai", "model": "openai/gpt-6.1-sol",
             "base_url": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"},
            {"id": "argon", "provider": "openai", "model": "google/gemini-4-argon",
             "base_url": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"},
        ],
    }))
    loaded = load_config(p)
    assert [(m.id, m.tools) for m in loaded.models] == [
        ("sol", ()),
        ("sol-search", ("web_search",)),
        ("argon", ()),
    ]


def test_non_list_tools_rejected(tmp_path):
    cfg = _write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "tools": "web_search"}])
    with pytest.raises(ConfigError, match="'tools' must be a list"):
        load_config(cfg)


# --- collect panel fingerprint -----------------------------------------------


def test_fingerprint_distinguishes_tools():
    on = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",))
    off = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=())
    assert _panel_fingerprint(on) != _panel_fingerprint(off)
    assert _panel_fingerprint(on).endswith("|web_search") and _panel_fingerprint(off).endswith("|")


def _ar_q(qid: str = "retrieve_quote-aaaaaa") -> Question:
    return Question(id=qid, task="retrieve_quote", prompt="p",
                    expected={"text": "x"},
                    source={"tradition": ["T"], "work": "W", "version": "V", "language": "ar",
                            "document_type": "scripture", "citation": "W 1:1"})


def test_flipped_tools_resume_refused(tmp_path, monkeypatch):
    answers = tmp_path / "answers.jsonl"
    q = _ar_q()
    monkeypatch.setattr(collect_mod, "complete", lambda m, p, retries=2: ("a", {"in": 1, "out": 1}, 1))
    on = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",)),), concurrency=1)
    off = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="claude-haiku-5-5", tools=()),), concurrency=1)
    collect([q], on, answers)  # collected WITH web search
    with pytest.raises(CollectError, match="different panel identity"):
        collect([q], off, answers)  # resume WITHOUT -> refused


def test_resume_with_missing_fingerprint_refused(tmp_path, monkeypatch):
    """A legacy row (digest present, but NO panel_fingerprint — first-run's shape) must refuse
    resume: without the guard its missing fingerprint bypasses the identity check, so a
    tools-bearing config could silently mix web-search-on answers into a legacy id."""
    from sacredbench.generate import question_set_digest
    q = _ar_q()
    answers = tmp_path / "answers.jsonl"
    # digest matches the current set, so the digest guard passes — only the fingerprint is absent
    legacy = {"question_id": q.id, "model_id": "m", "question_set_digest": question_set_digest([q])}
    answers.write_text(json.dumps(legacy) + "\n")
    monkeypatch.setattr(collect_mod, "complete", lambda m, p, retries=2: ("a", {"in": 1, "out": 1}, 1))
    cfg = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",)),), concurrency=1)
    with pytest.raises(CollectError, match="no panel fingerprint"):
        collect([q], cfg, answers)


def test_score_config_drift_from_answers_refused(tmp_path, monkeypatch):
    """`score --config` must cross-check config fingerprints against the answers' fingerprints:
    flipping a model's tools between collect and score would mislabel the arm in the committed
    panel. Here the answers were collected WITH web search; scoring under a no-tools config for
    the same id is refused before any panel is emitted."""
    from typer.testing import CliRunner

    from sacredbench.cli import app
    from sacredbench.generate import write_questions
    from sacredbench.score import ScoreError

    q = _ar_q()
    answers = tmp_path / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", lambda m, p, retries=2: ("a", {"in": 1, "out": 1}, 1))
    on = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",)),), concurrency=1)
    collect([q], on, answers)  # answers carry fingerprint ...|web_search

    questions_path = tmp_path / "questions.jsonl"
    write_questions([q], questions_path)
    import yaml
    cfg_off = tmp_path / "cfg_off.yaml"  # same id, tools FLIPPED off
    cfg_off.write_text(yaml.safe_dump({"models": [{"id": "m", "provider": "anthropic", "model": "claude-haiku-5-5"}]}))

    r = CliRunner().invoke(app, ["score", str(answers),
                                 "--scores-out", str(tmp_path / "s.jsonl"),
                                 "--summary-out", str(tmp_path / "sum.json"),
                                 "--questions", str(questions_path), "--config", str(cfg_off)])
    assert r.exit_code != 0 and isinstance(r.exception, ScoreError)
    assert "mislabel the experimental arm" in str(r.exception)
    assert not (tmp_path / "sum.json").exists()  # refused before emitting the panel


# --- provider seam (fake SDK at the lazy import site) ------------------------


class _Block:
    def __init__(self, type_, text=""):
        self.type, self.text = type_, text


class _Usage:
    def __init__(self, in_=3, out=4, web=None):
        self.input_tokens, self.output_tokens = in_, out
        self.server_tool_use = types.SimpleNamespace(web_search_requests=web) if web is not None else None


class _Resp:
    def __init__(self, content, usage, stop_reason="end_turn"):
        self.content, self.usage, self.stop_reason = content, usage, stop_reason


def _install_fake_anthropic(monkeypatch, resp):
    """Fake the SDK the way `_anthropic` imports it: `import anthropic` inside the function
    (so patching sys.modules is required; there is no module-level import to setattr)."""
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return resp

    client_obj = types.SimpleNamespace(messages=types.SimpleNamespace(create=create))
    fake = types.ModuleType("anthropic")
    fake.Anthropic = lambda **kw: client_obj
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    return captured


def test_web_search_tool_passed_only_when_enabled(monkeypatch):
    resp = _Resp([_Block("text", "the answer")], _Usage(web=2))
    captured = _install_fake_anthropic(monkeypatch, resp)
    on = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",))
    text, usage, attempts = complete(on, "prompt")
    assert text == "the answer"
    assert captured["tools"] == [providers.WEB_SEARCH_TOOL]  # tool passed
    assert usage["web_search_requests"] == 2                  # request count recorded

    captured.clear()
    off = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=())
    complete(off, "prompt")
    assert "tools" not in captured                            # not passed when disabled


def test_extracts_text_alongside_tool_and_citation_blocks(monkeypatch):
    content = [
        _Block("server_tool_use"), _Block("web_search_tool_result"),
        _Block("text", "In the beginning "), _Block("text", "was the Word."),
    ]
    _install_fake_anthropic(monkeypatch, _Resp(content, _Usage()))
    on = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",))
    text, _, _ = complete(on, "prompt")
    assert text == "In the beginning was the Word."  # only the text blocks, joined


@pytest.mark.parametrize("stop_reason", ["max_tokens", "pause_turn", "refusal", "model_context_window_exceeded"])
def test_incomplete_turn_fails_loud_not_committed(monkeypatch, stop_reason):
    # an incomplete turn (truncation, or a paused server-tool turn) must NOT commit its
    # partial text and must NOT retry (re-billing the web search) — it fails loud.
    _install_fake_anthropic(monkeypatch, _Resp([_Block("text", "partial")], _Usage(), stop_reason=stop_reason))
    on = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",))
    with pytest.raises(ProviderError, match="incomplete turn"):
        complete(on, "prompt")


def test_terminal_stop_reasons_succeed(monkeypatch):
    for sr in ("end_turn", "stop_sequence"):
        _install_fake_anthropic(monkeypatch, _Resp([_Block("text", "ok")], _Usage(), stop_reason=sr))
        off = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", tools=())
        text, _, _ = complete(off, "prompt")
        assert text == "ok"


# --- OpenAI native search (Responses API) ------------------------------------


def _install_fake_openai(monkeypatch, responses_resp=None, chat_resp=None):
    """Fake the SDK as `_openai` imports it (`from openai import OpenAI` inside the function).
    The fake client exposes BOTH endpoints so a test can assert which one the code chose."""
    captured: dict = {}

    def rcreate(**kwargs):
        captured.update(kwargs)
        captured["_endpoint"] = "responses"
        return responses_resp

    def ccreate(**kwargs):
        captured.update(kwargs)
        captured["_endpoint"] = "chat"
        return chat_resp

    client_obj = types.SimpleNamespace(
        responses=types.SimpleNamespace(create=rcreate),
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=ccreate)),
    )
    fake = types.ModuleType("openai")
    fake.OpenAI = lambda **kw: client_obj
    monkeypatch.setitem(sys.modules, "openai", fake)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    return captured


def _responses_resp(text="the answer", status="completed", searches=1, citations=("https://a",), reason=None):
    output = [types.SimpleNamespace(type="web_search_call") for _ in range(searches)]
    anns = [types.SimpleNamespace(type="url_citation", url=u) for u in citations]
    block = types.SimpleNamespace(type="output_text", annotations=anns)
    output.append(types.SimpleNamespace(type="message", content=[block]))
    usage = types.SimpleNamespace(input_tokens=3, output_tokens=4)
    incomplete = types.SimpleNamespace(reason=reason) if reason else None
    return types.SimpleNamespace(
        status=status, output_text=text, output=output, usage=usage, incomplete_details=incomplete
    )


def test_openai_native_web_search_uses_responses_with_provenance(monkeypatch):
    resp = _responses_resp(searches=2, citations=("https://a", "https://a", "https://b"))
    captured = _install_fake_openai(monkeypatch, responses_resp=resp)
    m = ModelSpec(id="o", provider="openai", model="gpt-x", max_tokens=256, tools=("web_search",))
    text, usage, _ = complete(m, "prompt")
    assert text == "the answer"
    assert captured["_endpoint"] == "responses"              # Responses API, not chat
    assert captured["tools"] == [providers.OPENAI_WEB_SEARCH_TOOL]
    assert captured["input"] == "prompt" and captured["max_output_tokens"] == 256
    assert usage["in"] == 3 and usage["out"] == 4
    assert usage["web_search_requests"] == 2                 # two web_search_call items
    assert usage["citations"] == ["https://a", "https://b"]  # deduped, first-seen order


def test_openai_responses_incomplete_turn_fails_loud(monkeypatch):
    _install_fake_openai(monkeypatch, responses_resp=_responses_resp(status="incomplete", reason="max_output_tokens"))
    m = ModelSpec(id="o", provider="openai", model="gpt-x", tools=("web_search",))
    with pytest.raises(ProviderError, match="incomplete Responses turn"):
        complete(m, "prompt")


def test_openai_search_off_uses_chat_completions(monkeypatch):
    """The refactor must not leak the Responses path onto the search-off arm: off still uses
    chat.completions and passes no search tool."""
    chat = types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="off answer"))],
        usage=types.SimpleNamespace(prompt_tokens=1, completion_tokens=2),
    )
    captured = _install_fake_openai(monkeypatch, chat_resp=chat)
    m = ModelSpec(id="o", provider="openai", model="gpt-x", max_tokens=256, tools=())
    text, usage, _ = complete(m, "prompt")
    assert text == "off answer" and captured["_endpoint"] == "chat"
    assert "tools" not in captured
    assert usage == {"in": 1, "out": 2}


# --- OpenRouter-transported native search (chat.completions) -----------------


class _Dump:
    """A stand-in for a pydantic object: exposes model_dump() returning a fixed dict."""
    def __init__(self, d):
        self._d = d

    def model_dump(self):
        return self._d


def _url_citation(url, style):
    """Build a url_citation annotation in a vendor-native shape: 'anthropic_content' carries a
    content snippet; 'openai_offsets' carries char offsets; 'other' is a bare url (an Exa-like
    uniform shape that the nativeness gate must reject)."""
    uc = {"url": url}
    if style == "anthropic_content":
        uc["content"] = "…snippet…"
    elif style == "openai_offsets":
        uc["start_index"], uc["end_index"] = 10, 40
    return _Dump({"type": "url_citation", "url_citation": uc})


def _openrouter_chat_resp(text="the answer", finish="stop", searches=2, citations=("https://a",),
                          provider="OpenAI", style="openai_offsets", cost=0.0123):
    usage = _Dump({"prompt_tokens": 3, "completion_tokens": 4, "cost": cost,
                   "server_tool_use_details": {"web_search_requests": searches}})
    anns = [_url_citation(u, style) for u in citations]
    msg = types.SimpleNamespace(content=text, annotations=anns)
    choice = types.SimpleNamespace(finish_reason=finish, message=msg)
    return types.SimpleNamespace(choices=[choice], usage=usage, provider=provider)


def _or_model(model_id, slug):
    return ModelSpec(id=model_id, provider="openai", model=slug,
                     base_url="https://openrouter.ai/api/v1", api_key_env="OPENROUTER_API_KEY",
                     max_tokens=4096, temperature=0, tools=("web_search",))


def test_openrouter_native_search_anthropic_family_forwards_anthropic_block(monkeypatch):
    resp = _openrouter_chat_resp(searches=1, citations=("https://a", "https://a", "https://b"),
                                 provider="Claude Platform on AWS", style="anthropic_content")
    captured = _install_fake_openai(monkeypatch, chat_resp=resp)
    text, usage, _ = complete(_or_model("sonnet-search", "anthropic/claude-sonnet-5.5"), "p")
    assert text == "the answer" and captured["_endpoint"] == "chat"
    assert captured["tools"] == [providers.WEB_SEARCH_TOOL]       # Anthropic native block
    assert captured["max_tokens"] == 4096
    assert usage["web_search_requests"] == 1
    assert usage["citations"] == ["https://a", "https://b"]       # deduped
    assert usage["provider"] == "Claude Platform on AWS"          # provider-of-record recorded
    assert usage["citation_style"] == "anthropic_content"         # vendor-native annotation shape
    assert usage["cost"] == 0.0123                                # per-cell cost captured (item 3)
    assert usage["in"] == 3 and usage["out"] == 4


def test_openrouter_native_search_openai_family_forwards_normalised_shape(monkeypatch):
    captured = _install_fake_openai(monkeypatch, chat_resp=_openrouter_chat_resp(provider="OpenAI"))
    _, usage, _ = complete(_or_model("sol-search", "openai/gpt-6.1-sol"), "p")
    assert captured["tools"] == [providers.OPENAI_WEB_SEARCH_TOOL]  # {"type": "web_search"}
    assert usage["provider"] == "OpenAI" and usage["web_search_requests"] == 2
    assert usage["citation_style"] == "openai_offsets"


@pytest.mark.parametrize("finish", ["length", "error"])
def test_openrouter_search_non_stop_finish_fails_loud(monkeypatch, finish):
    _install_fake_openai(monkeypatch, chat_resp=_openrouter_chat_resp(finish=finish))
    with pytest.raises(ProviderError, match="non-terminal finish_reason"):
        complete(_or_model("x", "anthropic/claude-sonnet-5.5"), "p")


# --- mechanical nativeness gate (#54 review item 4) --------------------------


def test_openrouter_search_missing_provider_of_record_fails_loud(monkeypatch):
    resp = _openrouter_chat_resp(provider=None)  # no provider-of-record
    _install_fake_openai(monkeypatch, chat_resp=resp)
    with pytest.raises(ProviderError, match="no provider-of-record"):
        complete(_or_model("sol-search", "openai/gpt-6.1-sol"), "p")


def test_openrouter_search_wrong_provider_of_record_fails_loud(monkeypatch):
    # provider-of-record doesn't match the family → possible non-native routing → refuse
    resp = _openrouter_chat_resp(provider="SomeProxy")
    _install_fake_openai(monkeypatch, chat_resp=resp)
    with pytest.raises(ProviderError, match="does not match the native provider"):
        complete(_or_model("sol-search", "openai/gpt-6.1-sol"), "p")


def test_openrouter_search_uniform_annotation_shape_fails_loud(monkeypatch):
    # citations in a bare/uniform shape (not the vendor's own) → Exa-layer smell → refuse
    resp = _openrouter_chat_resp(provider="OpenAI", style="other")
    _install_fake_openai(monkeypatch, chat_resp=resp)
    with pytest.raises(ProviderError, match="not the 'openai/' native shape"):
        complete(_or_model("sol-search", "openai/gpt-6.1-sol"), "p")


# --- Gemini native search (Google-Search grounding) --------------------------


def _install_fake_gemini(monkeypatch, resp):
    """Fake `google.genai` as `_gemini` imports it (`from google import genai` +
    `from google.genai import types`). The fake `types` makes HttpOptions / Tool /
    GoogleSearch / GenerateContentConfig constructible so the real call code runs."""
    captured: dict = {}

    def generate_content(**kwargs):
        captured.update(kwargs)
        return resp

    client_obj = types.SimpleNamespace(models=types.SimpleNamespace(generate_content=generate_content))
    fake_types = types.ModuleType("google.genai.types")
    fake_types.HttpOptions = lambda **kw: types.SimpleNamespace(**kw)
    fake_types.GenerateContentConfig = lambda **kw: types.SimpleNamespace(**kw)
    fake_types.GoogleSearch = lambda **kw: types.SimpleNamespace(**kw)
    fake_types.Tool = lambda **kw: types.SimpleNamespace(**kw)
    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = lambda **kw: client_obj
    fake_genai.types = fake_types
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    return captured


def _gemini_resp(text="the answer", finish="STOP", queries=("q1",), uris=("https://a",)):
    gm = types.SimpleNamespace(
        web_search_queries=list(queries),
        grounding_chunks=[types.SimpleNamespace(web=types.SimpleNamespace(uri=u)) for u in uris],
    )
    cand = types.SimpleNamespace(finish_reason=types.SimpleNamespace(name=finish), grounding_metadata=gm)
    usage = types.SimpleNamespace(prompt_token_count=3, candidates_token_count=4, thoughts_token_count=0)
    return types.SimpleNamespace(text=text, candidates=[cand], usage_metadata=usage)


def test_gemini_native_grounding_passes_tool_with_provenance(monkeypatch):
    resp = _gemini_resp(queries=("q1", "q2"), uris=("https://a", "https://a", "https://b"))
    captured = _install_fake_gemini(monkeypatch, resp)
    m = ModelSpec(id="g", provider="gemini", model="gemini-x", max_tokens=256, tools=("web_search",))
    text, usage, _ = complete(m, "prompt")
    assert text == "the answer"
    cfg = captured["config"]
    assert cfg.tools and cfg.tools[0].google_search is not None   # grounding tool passed
    assert usage["in"] == 3 and usage["out"] == 4
    assert usage["web_search_requests"] == 2                       # two search queries
    assert usage["citations"] == ["https://a", "https://b"]        # deduped grounded URIs


def test_gemini_grounding_incomplete_finish_fails_loud(monkeypatch):
    _install_fake_gemini(monkeypatch, _gemini_resp(finish="MAX_TOKENS"))
    m = ModelSpec(id="g", provider="gemini", model="gemini-x", tools=("web_search",))
    with pytest.raises(ProviderError, match="incomplete grounded turn"):
        complete(m, "prompt")


def test_gemini_search_off_passes_no_tool_and_ignores_finish(monkeypatch):
    """The search-off Gemini path is byte-identical to prior behaviour: no grounding tool, no
    finish-reason gate (a non-STOP finish off-arm is not this experiment's concern), no
    provenance keys."""
    captured = _install_fake_gemini(monkeypatch, _gemini_resp(finish="MAX_TOKENS"))
    m = ModelSpec(id="g", provider="gemini", model="gemini-x", tools=())
    text, usage, _ = complete(m, "prompt")
    assert text == "the answer"                        # not failed loud despite MAX_TOKENS
    assert getattr(captured["config"], "tools", None) is None
    assert "web_search_requests" not in usage and "citations" not in usage


# --- tools-aware panel identity in summary.json ------------------------------


def _answer(qid, model_id, api_model, digest="d"):
    return {
        "question_id": qid, "model_id": model_id, "task": "retrieve_quote",
        "model": api_model, "question_set_digest": digest,
        "answer": "x", "usage": {"in": 1, "out": 1},
        "question": {"expected": {"text": "x"}, "source": {"tradition": ["T"]}},
    }


def test_panel_tools_field_distinguishes_arms_and_dedupes_bare_model(tmp_path):
    """Approach B (Issue #11): `tools` is a real panel field and `model` is raw. The two arms
    still get distinct standings keys (tools is part of the key), but the no-tools arm now keys
    IDENTICALLY to first-run's bare committed row — its stale row becomes supersedable. This is
    the score.py written-snapshot half; it replaces Spec 8's marker + api_model shape."""
    answers = tmp_path / "answers.jsonl"
    rows = [_answer("retrieve_quote-0", "haiku-search", "claude-haiku-5-5"),
            _answer("retrieve_quote-1", "haiku", "claude-haiku-5-5")]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    # panel as cli.py builds it under Approach B: raw model + a real tools list
    panel = {
        "haiku-search": {"provider": "anthropic", "model": "claude-haiku-5-5",
                         "tools": ["web_search"], "endpoint": "api.anthropic.com"},
        "haiku": {"provider": "anthropic", "model": "claude-haiku-5-5",
                  "tools": [], "endpoint": "api.anthropic.com"},
    }
    summary = score_file(answers, tmp_path / "scores.jsonl", panel=panel)
    p = summary["panel"]

    def key(mid):
        return (p[mid]["provider"], p[mid]["model"], tuple(p[mid]["tools"]))

    # the two arms still get distinct standings keys (tools is part of the key)...
    assert key("haiku-search") != key("haiku")
    # ...and the no-tools arm now keys identically to first-run's bare committed row
    # (provider, model, no tools), so that stale row becomes supersedable — the #11 fix.
    first_run_key = ("anthropic", "claude-haiku-5-5", ())
    assert key("haiku") == first_run_key
    assert key("haiku-search") != first_run_key
    # raw model (no marker), real tools list, api_model dropped as pure redundancy
    assert p["haiku-search"]["model"] == p["haiku"]["model"] == "claude-haiku-5-5"
    assert p["haiku-search"]["tools"] == ["web_search"] and p["haiku"]["tools"] == []
    # panel carries only non-secret identity fields — tools replaces api_model
    assert set(p["haiku"]) == {"provider", "model", "tools", "endpoint", "max_tokens", "temperature", "served_by"}
    # generated_at present and ISO-parseable (Issue #7 half)
    assert datetime.fromisoformat(summary["generated_at"])

    # the markdown panel table renders a tools column: web_search on the search arm, '—' off.
    # Scope to the panel-composition section — the token-usage table shares the first cell.
    from sacredbench.score import summary_markdown
    md = summary_markdown(summary)
    panel_md = md[md.index("### Panel composition"):md.index("### Token usage")]
    assert "| tools |" in panel_md  # header carries the column
    search_row = next(ln for ln in panel_md.splitlines() if ln.startswith("| haiku-search |"))
    notools_row = next(ln for ln in panel_md.splitlines() if ln.startswith("| haiku |"))
    # tools is the 4th cell: model_id | provider | model | tools | endpoint | served_by —
    # assert that exact cell (not a loose substring: served_by is also '—')
    assert search_row.split("|")[4].strip() == "web_search"
    assert notools_row.split("|")[4].strip() == "—"


def test_synthesised_panel_entry_defaults_tools_empty(tmp_path):
    """A model present in usage (an answer row) but absent from the panel gets a SYNTHESISED
    panel entry (score.py's `set(usage) | set(panel)` path). Its tools must default to [] so
    every emitted entry has the field and keys like a no-tools run."""
    answers = tmp_path / "answers.jsonl"
    rows = [_answer("retrieve_quote-0", "opus", "claude-opus-5"),
            _answer("retrieve_quote-1", "ghost", "claude-haiku-5-5")]  # "ghost" not in panel
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    panel = {"opus": {"provider": "anthropic", "model": "claude-opus-5",
                      "tools": ["web_search"], "endpoint": "api.anthropic.com"}}
    summary = score_file(answers, tmp_path / "scores.jsonl", panel=panel)
    g = summary["panel"]["ghost"]
    assert g["tools"] == []  # synthesised default, not missing/None
    assert g["model"] == "claude-haiku-5-5"  # recovered from usage
    assert set(g) == {"provider", "model", "tools", "endpoint", "max_tokens", "temperature", "served_by"}


def test_cli_score_panel_emits_tools_field_and_raw_model(tmp_path, monkeypatch):
    """cli.py builds the panel inline, behind the fingerprint cross-check — a hand-built panel
    dict can't reach it. Exercise it end-to-end: collect fingerprinted answers for a
    search-on + search-off pair, then `score --config`, and inspect the written summary.json.
    Without this, cli.py's Approach-B emission would ship untested until the Phase-2 migration."""
    from typer.testing import CliRunner

    from sacredbench.cli import app
    from sacredbench.generate import write_questions

    q = _ar_q()
    answers = tmp_path / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", lambda m, p, retries=2: ("x", {"in": 1, "out": 1}, 1))
    cfg = RunConfig(models=(
        ModelSpec(id="haiku-search", provider="anthropic", model="claude-haiku-5-5", tools=("web_search",)),
        ModelSpec(id="haiku", provider="anthropic", model="claude-haiku-5-5", tools=()),
    ), concurrency=1)
    collect([q], cfg, answers)  # each answer row carries its arm's panel fingerprint

    questions_path = tmp_path / "questions.jsonl"
    write_questions([q], questions_path)
    import yaml
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump({"models": [
        {"id": "haiku-search", "provider": "anthropic", "model": "claude-haiku-5-5", "tools": ["web_search"]},
        {"id": "haiku", "provider": "anthropic", "model": "claude-haiku-5-5"},
    ]}))
    summary_out = tmp_path / "sum.json"
    r = CliRunner().invoke(app, ["score", str(answers),
                                 "--scores-out", str(tmp_path / "s.jsonl"),
                                 "--summary-out", str(summary_out),
                                 "--questions", str(questions_path), "--config", str(cfg_path)])
    assert r.exit_code == 0, r.output
    panel = json.loads(summary_out.read_text())["panel"]
    # raw model, a real tools list, api_model gone — the Approach-B shape from cli.py
    assert panel["haiku-search"]["model"] == "claude-haiku-5-5"
    assert panel["haiku-search"]["tools"] == ["web_search"] and panel["haiku"]["tools"] == []
    # exact written key-set (==, not subset): proves cli.py's in-memory price_in/price_out are
    # stripped by score.py and api_model is gone — asserted here because this is the only path
    # that actually carries price fields into the build.
    for mid in ("haiku-search", "haiku"):
        assert set(panel[mid]) == {"provider", "model", "tools", "endpoint", "max_tokens", "temperature", "served_by"}
    blob = json.dumps(panel)
    assert "[no-tools]" not in blob and "[web_search]" not in blob  # no leftover marker
