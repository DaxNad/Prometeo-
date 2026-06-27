from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001.md"


def _doc() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_non_persistent_response_model_document_exists_and_declares_scope():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001",
        "document-only model",
        "does not implement runtime confirmation",
        "persist TL answers",
        "mutate preview JSON",
        "promote any field to CERTO",
        "enable planner",
        "invoke ATLAS",
        "write to SMF/database",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_required_fields():
    text = _doc()

    required = [
        "article",
        "question_id",
        "field_group",
        "proposed_value",
        "tl_answer_state",
        "corrected_value",
        "resulting_status",
        "forbidden_runtime_effects_preserved",
        "Must be true",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_allowed_question_ids():
    text = _doc()

    required = [
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5",
        "Q6",
        "Q7",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_allowed_answer_states():
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


def test_non_persistent_response_model_declares_allowed_resulting_statuses():
    text = _doc()

    required = [
        "CANDIDATE_CONFIRMATION",
        "CANDIDATE_CORRECTION",
        "DA_VERIFICARE",
        "MISSING",
        "BLOCKED",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_field_group_mapping():
    text = _doc()

    required = [
        "article_identity",
        "packaging_and_quantities",
        "normalized_route",
        "zaw_station_resolution",
        "components",
        "tooling",
        "pidmill_and_cp_visibility",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_state_transition_rules():
    text = _doc()

    required = [
        "YES may produce",
        "YES must not produce",
        "NO may produce",
        "NO must not persist rejection",
        "UNKNOWN must produce",
        "UNKNOWN must not infer missing values",
        "CORRECTED_VALUE may produce",
        "CORRECTED_VALUE requires corrected_value to be present",
        "CORRECTED_VALUE must not mutate source data or become CERTO",
        "NOT_VISIBLE may produce",
        "NOT_VISIBLE must not infer absence",
        "ABSENT is allowed only for Q7",
        "ABSENT must not promote absence to CERTO",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_preserves_required_invariant():
    text = _doc()

    required = [
        "Every response object must include forbidden_runtime_effects_preserved=true",
        '"forbidden_runtime_effects_preserved": true',
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_forbids_runtime_effects():
    text = _doc()

    required = [
        "no TL answer persistence",
        "no preview JSON mutation",
        "no automatic promotion to CERTO",
        "no planner enablement",
        "no ATLAS invocation",
        "no SMF write",
        "no database write",
        "no TL Chat API contract change",
        "no production or planning readiness decision",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_forbids_persisted_or_operational_fields():
    text = _doc()

    required = [
        "persisted",
        "saved",
        "source_of_truth",
        "certo",
        "planner_eligible",
        "route_status",
        "production_ready",
        "planning_ready",
        "atlas_invoked",
        "smf_written",
        "database_written",
        "preview_json_mutated",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_stop_conditions():
    text = _doc()

    required = [
        "save the confirmation",
        "update source JSON",
        "promote any value to CERTO",
        "set planner_eligible=true",
        "confirm article 12514 ready for planning",
        "confirm article 12514 ready for production",
        "infer ZAW2 from repeated ZAW operations",
        "write to SMF or database",
        "invoke ATLAS or planner",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_declares_future_test_preconditions():
    text = _doc()

    required = [
        "all required fields are present",
        "only allowed question_id values are accepted",
        "only allowed tl_answer_state values are accepted",
        "CORRECTED_VALUE requires corrected_value",
        "ABSENT is allowed only for Q7",
        "forbidden runtime effects remain preserved",
        "no persistence or source mutation occurs",
        "no CERTO, planner, ATLAS, SMF, DB, or API effects occur",
    ]

    for phrase in required:
        assert phrase in text


def test_non_persistent_response_model_recommends_expected_next_capability():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_TEST_001",
        "guard this non-persistent response model with a document-level test",
        "require required fields",
        "require allowed values",
        "require forbidden field names",
        "require anti-persistence, anti-CERTO, anti-planner, anti-ATLAS, anti-SMF/DB behavior",
    ]

    for phrase in required:
        assert phrase in text
