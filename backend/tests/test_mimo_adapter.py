import json

import pytest

from app.ai_adapters.mimo_adapter import MiMoAdapter, MiMoAdapterError


def test_mimo_adapter_disabled_without_env(monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    monkeypatch.delenv("MIMO_BASE_URL", raising=False)

    adapter = MiMoAdapter()

    assert adapter.enabled is False


def test_mimo_adapter_enabled_with_env(monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://example.test")
    monkeypatch.setenv("MIMO_MODEL", "test-model")

    adapter = MiMoAdapter()

    assert adapter.enabled is True
    assert adapter.model == "test-model"


def test_mimo_adapter_raises_when_disabled(monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    monkeypatch.delenv("MIMO_BASE_URL", raising=False)

    adapter = MiMoAdapter()

    with pytest.raises(MiMoAdapterError) as exc:
        adapter.ask("test")

    assert "MiMo adapter non configurato" in str(exc.value)


def test_mimo_adapter_builds_openai_compatible_payload(monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://example.test")
    monkeypatch.setenv("MIMO_MODEL", "test-model")

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({
                "choices": [
                    {"message": {"content": "OK"}}
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            }).encode("utf-8")

    def fake_urlopen(req, timeout, context):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(req.header_items())
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    adapter = MiMoAdapter()
    result = adapter.ask("prompt TL", system="system TL")

    assert result["choices"][0]["message"]["content"] == "OK"
    assert captured["url"] == "https://example.test/chat/completions"
    assert captured["timeout"] == 60
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["headers"]["Content-type"] == "application/json"
    assert captured["body"]["model"] == "test-model"
    assert captured["body"]["temperature"] == 0.2
    assert captured["body"]["messages"] == [
        {"role": "system", "content": "system TL"},
        {"role": "user", "content": "prompt TL"},
    ]
