from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_boundary_document_exists():
    assert DOC_PATH.exists()


def test_boundary_document_names_capability_and_runtime_stub():
    text = _read_doc()

    assert "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001" in text
    assert "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_001" in text
    assert "backend/app/services/tl_chat_confirmation_rendering.py" in text
    assert "backend/tests/test_tl_chat_confirmation_rendering.py" in text


def test_boundary_document_preserves_service_only_scope():
    text = _read_doc()

    assert "## Service-only rule" in text
    assert "The service may be imported by tests." in text
    assert "FastAPI routes" in text
    assert "TL Chat endpoint handlers" in text
    assert "frontend components" in text
    assert "persistence adapters" in text
    assert "planner services" in text
    assert "ATLAS Engine" in text
    assert "SMF writers" in text
    assert "database sessions" in text
    assert "Any future binding requires a separate governed capability." in text


def test_boundary_document_lists_allowed_behavior():
    text = _read_doc()

    required_items = [
        "accept article 12514 confirmation rendering input",
        "validate question_id Q1-Q7",
        "validate TL answer state",
        "validate resulting status",
        "map Q1-Q7 to governed field groups",
        "preserve DA_VERIFICARE confidence",
        "construct candidate rendered text",
        "expose runtime effects as explicit no-op statements",
        "return forbidden runtime effects as false flags",
        "reject unsupported or unsafe input",
        "be tested through service-level tests only",
    ]

    for item in required_items:
        assert item in text


def test_boundary_document_lists_forbidden_behavior():
    text = _read_doc()

    required_items = [
        "save TL answers",
        "update source files",
        "mutate `data/local_reports/spec_intake_preview/12514_metadata_preview.json`",
        "promote candidate values to CERTO",
        "set `planner_eligible=true`",
        "set `route_status=CERTO`",
        "call planner code",
        "call ATLAS code",
        "write SMF files",
        "write database rows",
        "change `backend/app/api/tl_chat.py`",
        "change frontend code",
        "create production readiness claims",
        "create planning readiness claims",
        "treat TL answers as source of truth",
    ]

    for item in required_items:
        assert item in text


def test_boundary_document_preserves_article_12514_scope():
    text = _read_doc()

    assert "## Article scope" in text
    assert "`article = 12514`" in text
    assert "Any other article must be rejected." in text
    assert "generic confirmation engine" in text


def test_boundary_document_preserves_q1_to_q7_field_mapping():
    text = _read_doc()

    expected_rows = [
        "| Q1 | article_identity |",
        "| Q2 | packaging_and_quantities |",
        "| Q3 | normalized_route |",
        "| Q4 | zaw_station_resolution |",
        "| Q5 | components |",
        "| Q6 | tooling |",
        "| Q7 | pidmill_and_cp_visibility |",
    ]

    assert "## Question scope" in text
    for row in expected_rows:
        assert row in text


def test_boundary_document_preserves_answer_state_rules():
    text = _read_doc()

    expected_items = [
        "YES",
        "NO",
        "UNKNOWN",
        "CORRECTED_VALUE",
        "NOT_VISIBLE",
        "ABSENT",
        "CORRECTED_VALUE requires corrected_value.",
        "ABSENT is allowed only for Q7.",
        "UNKNOWN must preserve DA_VERIFICARE.",
        "YES must not promote data to CERTO.",
        "NO must not persist rejection.",
        "NOT_VISIBLE must not infer absence.",
    ]

    assert "## Answer state scope" in text
    for item in expected_items:
        assert item in text


def test_boundary_document_preserves_resulting_status_rules():
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

    assert "## Resulting status scope" in text
    for status in allowed_statuses:
        assert status in text
    for status in forbidden_statuses:
        assert status in text


def test_boundary_document_requires_runtime_effects_statement():
    text = _read_doc()

    assert "## Required runtime effects statement" in text
    assert "Effetti runtime: nessuna persistenza" in text
    assert "nessuna mutazione sorgente" in text
    assert "nessuna promozione a CERTO" in text
    assert "nessun planner" in text
    assert "nessun ATLAS" in text
    assert "nessuna scrittura SMF/DB" in text
    assert "This statement is not decorative." in text
    assert "boundary marker" in text


def test_boundary_document_requires_false_forbidden_runtime_effects_flags():
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

    assert "## Required forbidden runtime effects flags" in text
    assert "No flag may become true in this capability." in text

    for flag in required_flags:
        assert flag in text


def test_boundary_document_defines_candidate_only_output_nature():
    text = _read_doc()

    candidate_output_items = [
        "article",
        "question_id",
        "field_group",
        "tl_answer_state",
        "resulting_status",
        "candidate_data",
        "corrected_value",
        "confidence",
        "missing_data",
        "runtime_effects",
        "forbidden_runtime_effects",
        "next_safe_action",
        "rendered_text",
    ]

    forbidden_output_items = [
        "source of truth",
        "persisted confirmation",
        "operational authorization",
        "planning authorization",
        "production authorization",
    ]

    assert "## Required output nature" in text
    assert "The output is a renderable candidate only." in text

    for item in candidate_output_items:
        assert item in text
    for item in forbidden_output_items:
        assert item in text


def test_boundary_document_defines_stop_conditions():
    text = _read_doc()

    stop_conditions = [
        "bind the service to TL Chat API",
        "expose the service to frontend",
        "persist TL answers",
        "mutate preview JSON",
        "promote candidate data to CERTO",
        "enable planner",
        "invoke ATLAS",
        "write SMF or database",
        "claim article 12514 is ready for production",
        "claim article 12514 is ready for planning",
        "generalize the service beyond article 12514 without a new capability",
    ]

    assert "## Stop conditions" in text
    for condition in stop_conditions:
        assert condition in text


def test_boundary_document_defines_acceptance_criteria_and_next_capability():
    text = _read_doc()

    assert "## Acceptance criteria" in text
    assert "TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_TEST_001" in text
    assert "Guard this boundary document with a document-level test" in text
    assert "no API binding" in text
    assert "no frontend" in text
    assert "no persistence" in text
    assert "no preview JSON mutation" in text
    assert "no CERTO" in text
    assert "no planner" in text
    assert "no ATLAS" in text
    assert "no SMF/DB" in text
    assert "no production or planning readiness" in text


def test_boundary_document_preserves_non_goals_and_closure_verdict():
    text = _read_doc()

    assert "## Non-goals" in text
    assert "## Closure verdict" in text
    assert "STATUS: DOCUMENT_CREATED" in text
    assert "VERDICT: PENDING_TEST_AND_PR" in text
    assert "NEXT SAFE ACTION: add a document-level boundary test" in text