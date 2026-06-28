from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = (
    REPO_ROOT
    / "docs/TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001.md"
)


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_api_binding_contract_document_exists_and_declares_capability():
    text = _read_doc()

    assert (
        "# TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001"
        in text
    )
    assert (
        "`TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001`"
        in text
    )
    assert "This is a documentation-only capability." in text
    assert "It does not implement API binding." in text


def test_api_binding_contract_preserves_existing_governed_dependencies():
    text = _read_doc()

    required_dependencies = [
        "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_001",
        "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001",
        "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_TEST_001",
        "TL_CHAT_12514_CONFIRMATION_RENDERING_SERVICE_REGRESSION_TEST_001",
    ]

    for dependency in required_dependencies:
        assert dependency in text


def test_api_binding_contract_forbids_runtime_api_frontend_and_persistence_scope():
    text = _read_doc()

    forbidden_scope_rows = [
        "Runtime change | Forbidden",
        "`backend/app/api/tl_chat.py` change | Forbidden",
        "Frontend change | Forbidden",
        "TL answer persistence | Forbidden",
        "Preview JSON mutation | Forbidden",
        "CERTO promotion | Forbidden",
        "Planner eligibility | Forbidden",
        "ATLAS invocation | Forbidden",
        "SMF write | Forbidden",
        "Database write | Forbidden",
        "Production readiness | Forbidden",
        "Planning readiness | Forbidden",
    ]

    for row in forbidden_scope_rows:
        assert row in text


def test_api_binding_contract_defines_future_allowed_binding_behavior():
    text = _read_doc()

    allowed_future_behavior = [
        "call the rendering service",
        "return a candidate confirmation rendering object",
        "preserve article 12514-only scope",
        "preserve Q1-Q7 scope",
        "preserve DA_VERIFICARE confidence",
        "preserve runtime effects statement",
        "preserve forbidden runtime effects false flags",
        "expose missing data explicitly",
        "expose next safe action explicitly",
    ]

    for item in allowed_future_behavior:
        assert item in text


def test_api_binding_contract_forbids_future_side_effects():
    text = _read_doc()

    forbidden_future_behavior = [
        "save TL answers",
        "persist candidate confirmations",
        "update `data/local_reports/spec_intake_preview/12514_metadata_preview.json`",
        "promote candidate data to CERTO",
        "mark article 12514 as production ready",
        "mark article 12514 as planning ready",
        "enable planner eligibility",
        "invoke ATLAS",
        "write SMF",
        "write database rows",
        "change frontend behavior in the same capability",
    ]

    for item in forbidden_future_behavior:
        assert item in text


def test_api_binding_contract_defines_allowed_api_output_fields():
    text = _read_doc()

    allowed_fields = [
        "`article`",
        "`question_id`",
        "`field_group`",
        "`tl_answer_state`",
        "`resulting_status`",
        "`candidate_data`",
        "`corrected_value`",
        "`confidence`",
        "`missing_data`",
        "`runtime_effects`",
        "`forbidden_runtime_effects`",
        "`next_safe_action`",
        "`rendered_text`",
    ]

    for field in allowed_fields:
        assert field in text


def test_api_binding_contract_defines_forbidden_api_output_fields():
    text = _read_doc()

    forbidden_fields = [
        "`source_of_truth=true`",
        "`persisted=true`",
        "`saved=true`",
        "`planner_eligible=true`",
        "`route_status=CERTO`",
        "`production_ready=true`",
        "`planning_ready=true`",
        "`atlas_invoked=true`",
        "`smf_written=true`",
        "`database_written=true`",
        "`preview_json_mutated=true`",
        "Equivalent semantic claims are also forbidden.",
    ]

    for field in forbidden_fields:
        assert field in text


def test_api_binding_contract_preserves_article_12514_only_scope():
    text = _read_doc()

    assert "`article = 12514`" in text
    assert "Any request for a different article must be rejected" in text
    assert "must not silently generalize" in text
    assert "beyond article 12514" in text


def test_api_binding_contract_preserves_q1_to_q7_scope_and_mapping():
    text = _read_doc()

    expected_mapping = {
        "Q1": "article_identity",
        "Q2": "packaging_and_quantities",
        "Q3": "normalized_route",
        "Q4": "zaw_station_resolution",
        "Q5": "components",
        "Q6": "tooling",
        "Q7": "pidmill_and_cp_visibility",
    }

    for question_id, field_group in expected_mapping.items():
        assert f"| {question_id} | {field_group} |" in text

    assert "The future API binding must reject unknown question ids." in text


def test_api_binding_contract_preserves_answer_state_rules():
    text = _read_doc()

    allowed_states = [
        "YES",
        "NO",
        "UNKNOWN",
        "CORRECTED_VALUE",
        "NOT_VISIBLE",
        "ABSENT",
    ]

    required_rules = [
        "CORRECTED_VALUE requires corrected_value.",
        "ABSENT is allowed only for Q7.",
        "UNKNOWN must preserve DA_VERIFICARE.",
        "YES must not promote data to CERTO.",
        "NO must not persist rejection.",
        "NOT_VISIBLE must not infer absence.",
    ]

    for state in allowed_states:
        assert f"- {state}" in text

    for rule in required_rules:
        assert rule in text


def test_api_binding_contract_preserves_resulting_status_scope():
    text = _read_doc()

    allowed_statuses = [
        "CANDIDATE_CONFIRMATION",
        "CANDIDATE_CORRECTION",
        "DA_VERIFICARE",
        "MISSING",
        "BLOCKED",
    ]

    forbidden_statuses = [
        "CERTO",
        "PRODUCTION_READY",
        "PLANNING_READY",
        "PLANNER_ELIGIBLE",
        "SOURCE_OF_TRUTH",
        "SAVED",
        "PERSISTED",
    ]

    for status in allowed_statuses:
        assert f"- {status}" in text

    for status in forbidden_statuses:
        assert f"- {status}" in text


def test_api_binding_contract_preserves_runtime_effects_statement():
    text = _read_doc()

    assert "Effetti runtime: nessuna persistenza" in text
    assert "nessuna mutazione sorgente" in text
    assert "nessuna promozione a CERTO" in text
    assert "nessun planner" in text
    assert "nessun ATLAS" in text
    assert "nessuna scrittura SMF/DB" in text
    assert "must remain visible or machine-readable" in text


def test_api_binding_contract_preserves_forbidden_runtime_effects_false_flags():
    text = _read_doc()

    required_flags = [
        "tl_answer_persistence",
        "preview_json_mutation",
        "certo_promotion",
        "planner_enablement",
        "atlas_invocation",
        "smf_write",
        "database_write",
        "api_contract_change",
        "production_readiness",
        "planning_readiness",
    ]

    for flag in required_flags:
        assert flag in text

    assert "No flag may become true in the future API binding capability." in text


def test_api_binding_contract_preserves_source_planner_atlas_persistence_policies():
    text = _read_doc()

    required_policy_markers = [
        "The future API binding may not claim real source confirmation",
        "The API must not collapse these states into CERTO.",
        "The future API binding must not enable planner behavior.",
        "The API must not call planner services.",
        "The future API binding must not invoke ATLAS.",
        "The future API binding must not persist:",
        "Any persistence requires a separate governed capability",
    ]

    for marker in required_policy_markers:
        assert marker in text


def test_api_binding_contract_preserves_frontend_and_error_handling_policies():
    text = _read_doc()

    required_markers = [
        "This contract does not authorize frontend changes.",
        "requires a separate governed frontend capability",
        "must be testable without frontend changes",
        "non-12514 article",
        "unknown question_id",
        "unsupported answer state",
        "unsupported resulting status",
        "CORRECTED_VALUE without corrected_value",
        "ABSENT outside Q7",
        "empty next safe action",
        "Error handling must not mutate state.",
        "Error handling must not persist anything.",
    ]

    for marker in required_markers:
        assert marker in text


def test_api_binding_contract_defines_required_tests_and_stop_conditions():
    text = _read_doc()

    required_test_markers = [
        "Before API binding is implemented, a separate test contract must verify:",
        "this API binding contract exists",
        "`backend/app/api/tl_chat.py` is not changed in this capability",
        "allowed API output fields",
        "forbidden API output fields",
        "article 12514-only scope",
        "Q1-Q7 scope",
        "answer state scope",
        "resulting status scope",
        "runtime effects statement",
        "forbidden runtime effects false flags",
        "no persistence",
        "no preview JSON mutation",
        "no CERTO promotion",
        "no planner",
        "no ATLAS",
        "no SMF/DB",
        "no production or planning readiness",
    ]

    stop_conditions = [
        "persist TL answer",
        "mutate preview JSON",
        "promote to CERTO",
        "enable planner",
        "invoke ATLAS",
        "write SMF or database",
        "change frontend in the same capability",
        "generalize beyond article 12514",
        "claim operational readiness",
        "claim planning readiness",
        "treat candidate response as source of truth",
    ]

    for marker in required_test_markers:
        assert marker in text

    for condition in stop_conditions:
        assert condition in text


def test_api_binding_contract_preserves_non_goals_and_closure_verdict():
    text = _read_doc()

    non_goals = [
        "API binding",
        "TL Chat endpoint change",
        "frontend rendering",
        "persistence",
        "preview JSON mutation",
        "source-of-truth promotion",
        "CERTO promotion",
        "planner enablement",
        "ATLAS invocation",
        "SMF write",
        "database write",
        "production readiness",
        "planning readiness",
        "multi-article generalization",
    ]

    for non_goal in non_goals:
        assert non_goal in text

    assert (
        "CAPABILITY: TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001"
        in text
    )
    assert "STATUS: DOCUMENT_CREATED" in text
    assert "VERDICT: PENDING_TEST_AND_PR" in text
    assert "NEXT SAFE ACTION: add API binding contract document-level test" in text