from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001.md"


def _doc() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_runtime_boundary_document_exists_and_declares_scope():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001",
        "governed local confirmation evidence persistence",
        "does not mutate preview JSON, promote any field to CERTO",
        "ask-only and summarize-only",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_allows_only_bounded_confirmation_surface():
    text = _doc()

    required = [
        "Q1 article identity confirmation",
        "Q2 packaging and quantities confirmation",
        "Q3 normalized route confirmation",
        "Q4 ZAW station resolution clarification",
        "Q5 components confirmation",
        "Q6 tooling confirmation",
        "Q7 PIDMILL and CP visibility clarification",
        "one bounded confirmation group at a time",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_declares_allowed_answer_states():
    text = _doc()

    required = [
        "YES",
        "NO",
        "UNKNOWN",
        "CORRECTED_VALUE",
        "NOT_VISIBLE",
        "ABSENT",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_declares_non_persisted_output_states():
    text = _doc()

    required = [
        "CANDIDATE_CONFIRMATION",
        "CANDIDATE_CORRECTION",
        "DA_VERIFICARE",
        "MISSING",
        "BLOCKED",
        "| CANDIDATE_CONFIRMATION | TL answer appears to confirm proposed value | No |",
        "| CANDIDATE_CORRECTION | TL provides corrected value | No |",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_forbids_persistence_and_source_mutation():
    text = _doc()

    forbidden_effects = [
        "treat persisted confirmation evidence as operational truth",
        "mutate data/local_reports/spec_intake_preview/12514_metadata_preview.json",
        "write confirmation state to SMF",
        "write confirmation state to database",
        "treating the answer as source of truth",
        "updating preview metadata",
    ]

    for phrase in forbidden_effects:
        assert phrase in text


def test_runtime_boundary_forbids_certo_planner_atlas_and_production_readiness():
    text = _doc()

    required = [
        "promote any field to CERTO",
        "set planner_eligible=true",
        "mark article 12514 ready for planning",
        "mark article 12514 ready for production",
        "invoke planner",
        "invoke ATLAS runtime",
        "no automatic promotion to CERTO",
        "no planner",
        "no ATLAS runtime",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_preserves_required_response_framing():
    text = _doc()

    required_framing = (
        "La tua risposta serve come input di conferma governata e puo essere salvata solo come evidenza locale. "
        "Non promuove automaticamente "
        "il dato a CERTO e non abilita planner o produzione."
    )

    assert required_framing in text


def test_runtime_boundary_declares_stop_conditions():
    text = _doc()

    required = [
        "confirm production readiness",
        "confirm planning readiness",
        "update source JSON",
        "write to SMF or database",
        "promote to CERTO",
        "infer route or ZAW station without explicit governed rule",
        "use ATLAS or planner for this confirmation",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_declares_future_implementation_preconditions():
    text = _doc()

    required = [
        "exact non-operational response model",
        "test cases for allowed Q1-Q7 prompts",
        "test cases for governed evidence persistence",
        "test cases for anti-CERTO behavior",
        "test cases for anti-planner and anti-ATLAS behavior",
        "explicit statement that preview JSON remains immutable",
    ]

    for phrase in required:
        assert phrase in text


def test_runtime_boundary_recommends_expected_next_capability():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_TEST_001",
        "guard this runtime boundary document with a document-level test",
        "require governed evidence persistence language",
        "require forbidden runtime effects",
        "require stop conditions",
        "require anti-CERTO, anti-planner, anti-ATLAS, and no JSON mutation boundaries",
    ]

    for phrase in required:
        assert phrase in text
