#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "provider.py"
spec = importlib.util.spec_from_file_location("provider", MODULE_PATH)
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)


def test_dummy_provider_returns_valid_contract_json():
    raw = provider.run_provider("dummy", "unused", "prompt")
    data = json.loads(raw)
    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "MEDIUM"
    assert data["requires_human_confirmation"] is True


def test_unknown_provider_is_rejected():
    try:
        provider.run_provider("unknown", "unused", "prompt")
    except ValueError as exc:
        assert "Provider non supportato" in str(exc)
    else:
        raise AssertionError("unknown provider should fail")


def test_supported_providers_are_explicit():
    assert provider.SUPPORTED_PROVIDERS == {"ollama", "dummy", "openai-local"}


def test_openai_local_provider_parses_compatible_response(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"choices":[{"message":{"content":"{\\"verdict\\":\\"PASS\\",\\"risk\\":\\"LOW\\",\\"summary\\":\\"ok\\",\\"suggested_next_command\\":null,\\"requires_human_confirmation\\":true}"}}]}'

    def fake_urlopen(request, timeout):
        return FakeResponse()

    monkeypatch.setattr(provider.urllib.request, "urlopen", fake_urlopen)

    raw = provider.run_provider("openai-local", "local-model", "prompt")
    data = json.loads(raw)
    assert data["verdict"] == "PASS"
    assert data["risk"] == "LOW"


def test_openai_local_provider_rejects_invalid_response_shape(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"unexpected": true}'

    def fake_urlopen(request, timeout):
        return FakeResponse()

    monkeypatch.setattr(provider.urllib.request, "urlopen", fake_urlopen)

    try:
        provider.run_provider("openai-local", "local-model", "prompt")
    except RuntimeError as exc:
        assert "openai-local invalid response shape" in str(exc)
    else:
        raise AssertionError("invalid response shape should fail")
