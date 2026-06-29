from pathlib import Path


DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "TL_CHAT_CONFIRMATION_EVIDENCE_READBACK_GENERALIZATION_CONTRACT_001.md"


def _doc_text() -> str:
    assert DOC_PATH.exists(), "missing generalization contract document"
    return DOC_PATH.read_text(encoding="utf-8")


def test_confirmation_evidence_readback_generalization_contract_exists_and_is_contract_only():
    text = _doc_text()

    assert "TL_CHAT_CONFIRMATION_EVIDENCE_READBACK_GENERALIZATION_CONTRACT_001" in text
    assert "Contract-only document" in text
    assert "does not implement runtime behavior" in text
    assert "does not expand runtime support to other articles" in text


def test_confirmation_evidence_readback_generalization_contract_preserves_non_operational_invariants():
    text = _doc_text()

    required = [
        "confidence = DA_VERIFICARE",
        "requires_confirmation = true",
        "planner_eligible = false",
        "promoted_to_certo = false",
        "requires_persistence_review = true",
        "confirmation evidence is not operational truth",
    ]

    for item in required:
        assert item in text


def test_confirmation_evidence_readback_generalization_contract_blocks_scope_creep():
    text = _doc_text()

    forbidden_markers = [
        "treat persisted confirmation evidence as CERTO",
        "enable planner eligibility from confirmation evidence alone",
        "mark an article ready for production",
        "mark an article ready for planning",
        "write to PROMETEO_MASTER",
        "write to lifecycle registry",
        "write to SMF operational files",
        "accept arbitrary article/path pairs",
        "generalize from 12514 without dedicated tests",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_confirmation_evidence_readback_generalization_contract_declares_future_tests():
    text = _doc_text()

    required_tests = [
        "invalid schema is ignored",
        "wrong article is ignored",
        "planner_eligible=true is rejected",
        "promoted_to_certo=true is rejected",
        "missing evidence keeps candidate-only fallback",
        "readback answer keeps DA_VERIFICARE",
        "path traversal is impossible",
    ]

    for marker in required_tests:
        assert marker in text
