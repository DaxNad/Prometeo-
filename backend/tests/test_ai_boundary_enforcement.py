from __future__ import annotations

import json

import pytest

from app.ai_adapters.mimo_adapter import MiMoAdapter, MiMoAdapterError
from app.services.anthropic_provider import claude_chat


def test_mimo_adapter_blocks_unsanitized_operational_prompt_before_cloud_call(monkeypatch, tmp_path):
    monkeypatch.setenv("MIMO_API_KEY", "test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://example.test")
    monkeypatch.setattr(
        "app.ai_router.policy_gate.AI_INVOCATION_AUDIT_LOG",
        tmp_path / "ai_invocation_audit.jsonl",
    )

    called = {"urlopen": False}

    def fake_urlopen(*_args, **_kwargs):
        called["urlopen"] = True
        raise AssertionError("external MiMo call must be blocked before urlopen")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    adapter = MiMoAdapter()
    raw_prompt = (
        "Analizza BOM route ZAW1 per articolo 12066 da "
        "[PRIVATE_SPEC_PATH_REDACTED]"
    )

    with pytest.raises(MiMoAdapterError) as exc:
        adapter.ask(raw_prompt)

    assert "policy blocked" in str(exc.value)
    assert called["urlopen"] is False

    audit_log = tmp_path / "ai_invocation_audit.jsonl"
    record = json.loads(audit_log.read_text(encoding="utf-8").strip())
    assert record["adapter"] == "mimo_cloud"
    assert record["blocked"] is True
    assert record["raw_prompt_stored"] is False
    assert "data_boundary_not_allowed" in record["reason"]


def test_mimo_adapter_allows_scoped_sanitized_prompt_and_audits(monkeypatch, tmp_path):
    monkeypatch.setenv("MIMO_API_KEY", "test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://example.test")
    monkeypatch.setenv("MIMO_MODEL", "test-model")
    monkeypatch.setattr(
        "app.ai_router.policy_gate.AI_INVOCATION_AUDIT_LOG",
        tmp_path / "ai_invocation_audit.jsonl",
    )

    captured: dict = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "OK"}}]}).encode("utf-8")

    def fake_urlopen(req, timeout, context):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = MiMoAdapter().ask("Refactor mocked code path.")

    assert result["choices"][0]["message"]["content"] == "OK"
    assert captured["body"]["messages"][-1]["content"] == "Refactor mocked code path."

    audit_log = tmp_path / "ai_invocation_audit.jsonl"
    record = json.loads(audit_log.read_text(encoding="utf-8").strip())
    assert record["adapter"] == "mimo_cloud"
    assert record["blocked"] is False
    assert record["raw_prompt_stored"] is False
    assert record["sanitized"] is True


def test_claude_chat_blocks_operational_prompt_before_provider_call(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.ai_router.policy_gate.AI_INVOCATION_AUDIT_LOG",
        tmp_path / "ai_invocation_audit.jsonl",
    )

    called = {"post": False}

    def fake_post(*_args, **_kwargs):
        called["post"] = True
        raise AssertionError("external Claude call must be blocked before requests.post")

    monkeypatch.setattr("requests.post", fake_post)

    raw_prompt = "Valuta route ZAW1 per articolo 12066 e componente 468796."

    with pytest.raises(RuntimeError) as exc:
        claude_chat(raw_prompt)

    assert "Claude policy blocked" in str(exc.value)
    assert called["post"] is False

    audit_log = tmp_path / "ai_invocation_audit.jsonl"
    record = json.loads(audit_log.read_text(encoding="utf-8").strip())
    assert record["adapter"] == "claude"
    assert record["blocked"] is True
    assert record["raw_prompt_stored"] is False
