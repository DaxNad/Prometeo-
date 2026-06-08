#!/usr/bin/env python3
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "local_assist.py"
spec = importlib.util.spec_from_file_location("local_assist", MODULE_PATH)
local_assist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_assist)


def test_validate_valid_output():
    raw = """{
      "verdict": "PASS",
      "risk": "LOW",
      "summary": "checks ok",
      "suggested_next_command": null,
      "requires_human_confirmation": false
    }"""
    data = local_assist.validate_output(raw)
    assert data["verdict"] == "PASS"
    assert data["risk"] == "LOW"
    assert data["requires_human_confirmation"] is True


def test_validate_invalid_json_fails_closed():
    data = local_assist.validate_output("not-json")
    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["suggested_next_command"] is None
    assert data["requires_human_confirmation"] is True


def test_validate_missing_fields_fails_closed():
    data = local_assist.validate_output('{"verdict":"PASS"}')
    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["suggested_next_command"] is None
    assert data["requires_human_confirmation"] is True


def test_validate_bad_enum_fails_closed():
    raw = """{
      "verdict": "MERGE",
      "risk": "SAFE",
      "summary": "bad enums",
      "suggested_next_command": "git push origin main",
      "requires_human_confirmation": false
    }"""
    data = local_assist.validate_output(raw)
    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["requires_human_confirmation"] is True


def test_validate_forbidden_command_fails_closed_even_with_valid_enums():
    raw = """{
      "verdict": "PASS",
      "risk": "LOW",
      "summary": "looks safe but is not",
      "suggested_next_command": "git push origin main",
      "requires_human_confirmation": false
    }"""
    data = local_assist.validate_output(raw)
    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["suggested_next_command"] is None
    assert data["requires_human_confirmation"] is True


def test_validate_extracts_json_from_noisy_output():
    raw = """Ecco il risultato:
    {
      "verdict": "FAIL",
      "risk": "HIGH",
      "summary": "Data Leak Guard failed",
      "suggested_next_command": "gh run view 123 --log-failed",
      "requires_human_confirmation": false
    }
    Fine."""
    data = local_assist.validate_output(raw)
    assert data["verdict"] == "FAIL"
    assert data["risk"] == "HIGH"
    assert data["summary"] == "Data Leak Guard failed"
    assert data["requires_human_confirmation"] is True


def test_deterministic_fallback_data_leak_guard_failure():
    data = local_assist.deterministic_fallback(
        "classifica check",
        "Some checks were not successful\nX Data Leak Guard\n2 failing"
    )
    assert data is not None
    assert data["verdict"] == "FAIL"
    assert data["risk"] == "HIGH"
    assert "Data Leak Guard" in data["summary"]
    assert data["requires_human_confirmation"] is True


def test_deterministic_fallback_all_checks_successful():
    data = local_assist.deterministic_fallback(
        "classifica check",
        "All checks were successful\n0 failing\n11 successful"
    )
    assert data is not None
    assert data["verdict"] == "PASS"
    assert data["risk"] == "LOW"
    assert data["requires_human_confirmation"] is True


def test_command_forbidden_rejects_non_string_command():
    assert local_assist.command_is_forbidden(["git", "push"]) is True
