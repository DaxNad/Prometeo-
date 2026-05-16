from __future__ import annotations

import json

from app.ai_router.policy_gate import append_ai_invocation_audit, evaluate_ai_router_policy
from app.security.data_boundary_classifier import classify_data_boundary
from app.security.prompt_sanitizer import sanitize_prompt


def test_classifier_allows_scoped_public_code():
    result = classify_data_boundary(
        "Refactor a pure function with mocked inputs.",
        scope_declared=True,
    )

    assert result["allowed_external"] is True
    assert result["risk_level"] == "LOW"
    assert result["detected_classes"] == ["PUBLIC_CODE"]
    assert result["reasons"] == []


def test_classifier_blocks_sensitive_path_and_operational_references():
    local_path = "/" + "Users" + "/local/project/specs_finitura/12066/image.png"
    result = classify_data_boundary(
        f"Route ZAW1 with BOM reference at {local_path}",
        scope_declared=True,
    )

    assert result["allowed_external"] is False
    assert result["risk_level"] == "HIGH"
    assert "INDUSTRIAL_SENSITIVE" in result["detected_classes"]
    assert "OPERATIONAL_REAL" in result["detected_classes"]
    assert "PERSONAL" in result["detected_classes"]
    assert "local_path_detected" in result["reasons"]
    assert "industrial_reference_detected" in result["reasons"]


def test_classifier_blocks_secret_and_email_without_literal_private_data():
    address = "team" + "@" + "example.invalid"
    secret_key = "tok" + "en"
    secret_value = "abc" + "defghijklmnopqrstuvwxyz"
    result = classify_data_boundary(
        f"{secret_key}='{secret_value}' contact {address}",
        scope_declared=True,
    )

    assert result["allowed_external"] is False
    assert result["risk_level"] == "CRITICAL"
    assert "SECRET" in result["detected_classes"]
    assert "PERSONAL" in result["detected_classes"]
    assert "secret_detected" in result["reasons"]
    assert "email_detected" in result["reasons"]


def test_prompt_sanitizer_redacts_paths_email_secrets_and_codes():
    local_path = "/" + "Users" + "/local/project/specs_finitura/12066/sheet.pdf"
    address = "planner" + "@" + "example.invalid"
    secret_key = "api" + "_" + "key"
    secret_value = "abc" + "defghijklmnopqrstuvwxyz"
    raw_prompt = (
        f"Check {local_path} for article 12066 and component 468796. "
        f"Contact {address}. {secret_key}='{secret_value}'"
    )

    result = sanitize_prompt(raw_prompt, scope_declared=True)
    sanitized = result["sanitized_prompt"]

    assert result["sanitized"] is True
    assert "[LOCAL_PATH_REDACTED]" in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "[SECRET_REDACTED]" in sanitized
    assert "ARTICLE_A" in sanitized
    assert "COMPONENT_A" in sanitized
    assert result["redaction_report"]["local_paths"] == 1
    assert result["redaction_report"]["emails"] == 1
    assert result["redaction_report"]["secrets"] == 1


def test_ai_router_blocks_external_adapter_when_boundary_fails():
    boundary = classify_data_boundary("BOM with route ZAW1 for 12066", scope_declared=True)
    decision = evaluate_ai_router_policy(
        target_adapter="codex",
        scope="code_patch_only",
        sanitized_prompt="BOM with route ZAW1 for ARTICLE_A",
        data_boundary_check=boundary,
        sanitized=True,
    )

    assert decision["allowed"] is False
    assert decision["blocked"] is True
    assert "data_boundary_not_allowed" in decision["reason"]
    assert decision["raw_prompt_stored"] is False


def test_ai_router_allows_external_adapter_only_with_sanitized_scoped_prompt():
    boundary = classify_data_boundary("Refactor mocked code path.", scope_declared=True)
    decision = evaluate_ai_router_policy(
        target_adapter="codex",
        scope="code_patch_only",
        sanitized_prompt="Refactor mocked code path.",
        data_boundary_check=boundary,
        sanitized=True,
    )

    assert decision["allowed"] is True
    assert decision["blocked"] is False
    assert decision["reason"] is None
    assert decision["raw_prompt_stored"] is False


def test_ai_invocation_audit_never_stores_raw_prompt(tmp_path):
    boundary = classify_data_boundary("Refactor mocked code path.", scope_declared=True)
    decision = evaluate_ai_router_policy(
        target_adapter="codex",
        scope="code_patch_only",
        sanitized_prompt="Refactor mocked code path.",
        data_boundary_check=boundary,
        sanitized=True,
    )
    log_path = tmp_path / "ai_invocation_audit.jsonl"

    record = append_ai_invocation_audit(decision, log_path=log_path)
    stored = json.loads(log_path.read_text(encoding="utf-8").strip())

    assert record["raw_prompt_stored"] is False
    assert stored["raw_prompt_stored"] is False
    assert "prompt" not in stored
    assert stored["adapter"] == "codex"
