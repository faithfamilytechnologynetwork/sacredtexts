"""Optional per-model temperature (PR #30, part 1): config validation, panel-fingerprint
behaviour, and the provider sampling seam. No live API calls — the SDKs are faked at their
lazy import sites, mirroring test_phase2_tools.py."""

from __future__ import annotations

import sys
import types

import pytest
import yaml

from sacredbench.collect import _panel_fingerprint
from sacredbench.config import ConfigError, ModelSpec, load_config
from sacredbench.providers import complete, sampling_kwargs


def _write(tmp_path, models) -> "object":
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump({"models": models}))
    return p


# --- config validation -------------------------------------------------------


def test_temperature_unset_is_none(tmp_path):
    cfg = load_config(_write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m"}]))
    assert cfg.models[0].temperature is None


def test_temperature_set_is_float(tmp_path):
    cfg = load_config(_write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "temperature": 0}]))
    t = cfg.models[0].temperature
    assert t == 0.0 and isinstance(t, float)


def test_temperature_boundaries_accepted(tmp_path):
    for value in (0, 2, 1.5):
        cfg = load_config(_write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "temperature": value}]))
        assert cfg.models[0].temperature == float(value)


@pytest.mark.parametrize("value", [-0.1, 2.1, 3])
def test_temperature_out_of_range_rejected(tmp_path, value):
    with pytest.raises(ConfigError, match="between 0 and 2"):
        load_config(_write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "temperature": value}]))


@pytest.mark.parametrize("value", ["hot", True, [0]])
def test_temperature_non_number_rejected(tmp_path, value):
    with pytest.raises(ConfigError, match="must be a number"):
        load_config(_write(tmp_path, [{"id": "a", "provider": "anthropic", "model": "m", "temperature": value}]))


# --- panel fingerprint -------------------------------------------------------


def test_fingerprint_unchanged_when_temperature_unset():
    """An unset temperature must leave the fingerprint byte-identical to the pre-temperature
    shape, so already-committed runs' fingerprints are unchanged."""
    m = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5")
    assert _panel_fingerprint(m) == "anthropic|claude-haiku-5-5||"
    assert "t=" not in _panel_fingerprint(m)


def test_fingerprint_appends_temperature_when_set():
    base = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5")
    hot = ModelSpec(id="x", provider="anthropic", model="claude-haiku-5-5", temperature=0.7)
    assert _panel_fingerprint(hot) == _panel_fingerprint(base) + "|t=0.7"
    assert _panel_fingerprint(hot) != _panel_fingerprint(base)


def test_fingerprint_distinguishes_temperatures():
    a = ModelSpec(id="x", provider="anthropic", model="m", temperature=0.0)
    b = ModelSpec(id="x", provider="anthropic", model="m", temperature=1.0)
    assert _panel_fingerprint(a) != _panel_fingerprint(b)


# --- sampling_kwargs helper --------------------------------------------------


def test_sampling_kwargs_omitted_when_unset():
    assert sampling_kwargs(ModelSpec(id="x", provider="anthropic", model="m")) == {}


def test_sampling_kwargs_present_when_set():
    assert sampling_kwargs(ModelSpec(id="x", provider="anthropic", model="m", temperature=0.0)) == {"temperature": 0.0}


# --- provider seam (fake SDK at the lazy import site) ------------------------


class _Resp:
    def __init__(self, content, usage, stop_reason="end_turn"):
        self.content, self.usage, self.stop_reason = content, usage, stop_reason


def _install_fake_anthropic(monkeypatch):
    captured = {}
    resp = _Resp(
        [types.SimpleNamespace(type="text", text="ok")],
        types.SimpleNamespace(input_tokens=1, output_tokens=1, server_tool_use=None),
    )

    def create(**kwargs):
        captured.update(kwargs)
        return resp

    client_obj = types.SimpleNamespace(messages=types.SimpleNamespace(create=create))
    fake = types.ModuleType("anthropic")
    fake.Anthropic = lambda **kw: client_obj
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    return captured


def test_anthropic_passes_temperature_only_when_set(monkeypatch):
    captured = _install_fake_anthropic(monkeypatch)
    complete(ModelSpec(id="x", provider="anthropic", model="m", temperature=0.0), "p")
    assert captured["temperature"] == 0.0

    captured.clear()
    complete(ModelSpec(id="x", provider="anthropic", model="m"), "p")
    assert "temperature" not in captured  # host default stands


def _install_fake_openai(monkeypatch):
    captured = {}
    resp = types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))],
        usage=types.SimpleNamespace(prompt_tokens=1, completion_tokens=1),
    )

    def create(**kwargs):
        captured.update(kwargs)
        return resp

    client_obj = types.SimpleNamespace(
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create))
    )
    fake = types.ModuleType("openai")
    fake.OpenAI = lambda **kw: client_obj
    monkeypatch.setitem(sys.modules, "openai", fake)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    return captured


def test_openai_passes_temperature_only_when_set(monkeypatch):
    captured = _install_fake_openai(monkeypatch)
    spec = dict(id="x", provider="openai", model="m",
                base_url="https://openrouter.ai/api/v1", api_key_env="OPENROUTER_API_KEY")
    complete(ModelSpec(temperature=0.5, **spec), "p")
    assert captured["temperature"] == 0.5

    captured.clear()
    complete(ModelSpec(**spec), "p")
    assert "temperature" not in captured
