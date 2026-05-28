from app.ai_router.policy_gate import prepare_external_ai_invocation


def test_prepare_external_ai_invocation_blocks_c_guarded_without_verifier():
    result = prepare_external_ai_invocation(
        target_adapter="claude",
        scope="C_GUARDED",
        raw_prompt="safe mocked prompt",
        verifier_present=False,
    )

    assert result["blocked"] is True
    assert "verifier_required" in result["decision"]["reason"]


def test_prepare_external_ai_invocation_allows_c_guarded_with_verifier():
    result = prepare_external_ai_invocation(
        target_adapter="claude",
        scope="C_GUARDED",
        raw_prompt="safe mocked prompt",
        verifier_present=True,
    )

    assert result["allowed"] is True
    assert result["blocked"] is False
