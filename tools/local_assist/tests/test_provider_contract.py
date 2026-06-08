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
    assert provider.SUPPORTED_PROVIDERS == {"ollama", "dummy"}
