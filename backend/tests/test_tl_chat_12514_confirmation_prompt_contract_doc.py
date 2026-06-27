from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001.md"


def _read_contract() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_12514_confirmation_prompt_contract_document_exists() -> None:
    assert DOC_PATH.exists()


def test_12514_confirmation_prompt_contract_requires_q1_to_q7() -> None:
    content = _read_contract()

    required_questions = [
        "### Q1 - Article identity",
        "### Q2 - Packaging and quantities",
        "### Q3 - Normalized route",
        "### Q4 - ZAW station resolution",
        "### Q5 - Components",
        "### Q6 - Tooling",
        "### Q7 - PIDMILL and CP visibility",
    ]

    for required_question in required_questions:
        assert required_question in content


def test_12514_confirmation_prompt_contract_declares_allowed_answer_states() -> None:
    content = _read_contract()

    required_states = [
        "YES",
        "NO",
        "UNKNOWN",
        "CORRECTED_VALUE",
        "NOT_VISIBLE",
        "ABSENT",
    ]

    for required_state in required_states:
        assert required_state in content


def test_12514_confirmation_prompt_contract_preserves_anti_certo_language() -> None:
    content = _read_contract()

    required_phrases = [
        "does not promote any field to CERTO",
        "must not automatically promote preview data to CERTO",
        "confirmation does not mean CERTO",
        "Non promuove automaticamente il dato a CERTO",
        "no automatic promotion to CERTO",
    ]

    for required_phrase in required_phrases:
        assert required_phrase in content


def test_12514_confirmation_prompt_contract_preserves_blocked_runtime_boundaries() -> None:
    content = _read_contract()

    required_boundaries = [
        "no runtime confirmation",
        "no preview JSON mutation",
        "no planner",
        "no ATLAS runtime",
        "no SMF/DB write",
        "no new source ingestion",
        "no TL Chat API change",
        "no production decision automation",
    ]

    for boundary in required_boundaries:
        assert boundary in content


def test_12514_confirmation_prompt_contract_declares_forbidden_prompt_behavior() -> None:
    content = _read_contract()

    required_forbidden_behavior = [
        "article 12514 is ready for planning",
        "article 12514 is ready for production",
        "planner_eligible can become true in this capability",
        "route can become CERTO automatically",
        "ZAW2 can be inferred from repeated ZAW operations",
        "SMF/DB can be written",
        "ATLAS runtime can be invoked",
    ]

    for forbidden_behavior in required_forbidden_behavior:
        assert forbidden_behavior in content


def test_12514_confirmation_prompt_contract_declares_output_schema() -> None:
    content = _read_contract()

    required_schema_fields = [
        "article: 12514",
        "question_id",
        "field_group",
        "proposed_value",
        "tl_answer_state",
        "corrected_value, if any",
        "resulting_status: CANDIDATE_CONFIRMATION, DA_VERIFICARE, MISSING, or BLOCKED",
        "forbidden_runtime_effects_preserved: true",
    ]

    for schema_field in required_schema_fields:
        assert schema_field in content


def test_12514_confirmation_prompt_contract_points_to_next_test_capability() -> None:
    content = _read_contract()

    assert "TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_TEST_001" in content
