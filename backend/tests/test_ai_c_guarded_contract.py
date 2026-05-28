from app.ai_router.policy_gate import evaluate_ai_router_policy


def _allowed_boundary():
    return {"allowed_external": True, "risk_level": "LOW"}


def test_c_guarded_external_ai_requires_verifier():
    decision = evaluate_ai_router_policy(
        target_adapter="claude",
        scope="C_GUARDED",
        sanitized_prompt="sanitized prompt",
        data_boundary_check=_allowed_boundary(),
        sanitized=True,
        verifier_present=False,
    )

    assert decision["blocked"] is True
    assert "verifier_required" in decision["reason"]


def test_c_guarded_external_ai_allows_verified_invocation():
    decision = evaluate_ai_router_policy(
        target_adapter="claude",
        scope="C_GUARDED",
        sanitized_prompt="sanitized prompt",
        data_boundary_check=_allowed_boundary(),
        sanitized=True,
        verifier_present=True,
    )

    assert decision["allowed"] is True
    assert decision["blocked"] is False
    assert decision["reason"] is None
