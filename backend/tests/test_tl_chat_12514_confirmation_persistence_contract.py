from pathlib import Path


CONTRACT_PATH = Path(__file__).resolve().parents[2] / "docs" / "TL_CHAT_12514_CONFIRMATION_PERSISTENCE_CONTRACT_001.md"


def _contract_text() -> str:
    assert CONTRACT_PATH.exists(), "missing persistence contract document"
    return CONTRACT_PATH.read_text(encoding="utf-8")


def test_12514_confirmation_persistence_contract_exists_and_is_contract_only():
    text = _contract_text()

    assert "TL_CHAT_12514_CONFIRMATION_PERSISTENCE_CONTRACT_001" in text
    assert "runtime evidence persistence contract" in text
    assert "persists a local governed evidence record" in text
    assert "still requires review before any operational promotion" in text


def test_12514_confirmation_persistence_contract_blocks_scope_creep():
    text = _contract_text()

    required_guards = [
        "promote 12514 to CERTO automatically",
        "write to PROMETEO_MASTER",
        "write to lifecycle registry",
        "write to SMF operational files",
        "enable planner eligibility",
        "create or modify production routes",
        "generalize to other articles",
        "accept arbitrary file paths",
        "accept uncontrolled schema fields",
        "overwrite existing confirmed records without review",
    ]

    for guard in required_guards:
        assert guard in text


def test_12514_confirmation_persistence_contract_requires_safe_semantic_state():
    text = _contract_text()

    required_state = [
        "confidence = DA_VERIFICARE",
        "planner_eligible = false",
        "promoted_to_certo = false",
        "requires_persistence_review = true",
    ]

    for item in required_state:
        assert item in text


def test_12514_confirmation_persistence_contract_limits_allowed_record_schema():
    text = _contract_text()

    required_fields = [
        "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
        "TL_CONFIRMED_PREVIEW",
        "confirmed_fields",
        "confirmed_by_role",
        "created_at",
    ]

    for field in required_fields:
        assert field in text
