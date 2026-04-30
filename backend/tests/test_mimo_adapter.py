from app.ai_adapters.mimo_adapter import MiMoAdapter


def test_mimo_adapter_disabled_without_env(monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    monkeypatch.delenv("MIMO_BASE_URL", raising=False)

    adapter = MiMoAdapter()

    assert adapter.enabled is False
