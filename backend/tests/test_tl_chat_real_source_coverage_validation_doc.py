from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "TL_CHAT_REAL_SOURCE_COVERAGE_VALIDATION_001.md"


def test_real_source_coverage_validation_document_exists() -> None:
    assert DOC_PATH.exists()


def test_real_source_coverage_validation_declares_required_classes() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    required_classes = [
        "ANSWERED",
        "PARTIAL",
        "MISSING",
        "BLOCKED",
    ]

    for required_class in required_classes:
        assert required_class in content


def test_real_source_coverage_validation_preserves_out_of_scope_boundaries() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    required_boundaries = [
        "planner",
        "ATLAS",
        "SMF/DB",
        "new sources",
        "API",
        "runtime",
        "coverage",
    ]

    for boundary in required_boundaries:
        assert boundary in content


def test_real_source_coverage_validation_contains_minimal_matrix() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "## Minimal validation matrix" in content
    assert "| ID | TL question | Expected source | Available source | Classification | Required behavior |" in content
    assert "Q001" in content
    assert "Q010" in content
