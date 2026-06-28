from pathlib import Path

from backend.app.services.tl_chat_confirmation_rendering import (
    FIELD_GROUP_BY_QUESTION_ID,
    FORBIDDEN_RUNTIME_EFFECTS,
    RUNTIME_EFFECTS_STATEMENT,
    TLChatConfirmationRenderingInput,
    build_confirmation_rendering,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_DOC_PATH = (
    REPO_ROOT
    / "docs/TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001.md"
)


def _read_boundary_doc() -> str:
    return BOUNDARY_DOC_PATH.read_text(encoding="utf-8")


def test_service_and_boundary_preserve_article_12514_only_scope():
    boundary_text = _read_boundary_doc()

    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q1",
            tl_answer_state="YES",
            resulting_status="CANDIDATE_CONFIRMATION",
            candidate_data={"codice": "7056055000A0"},
            missing_data=[],
            next_safe_action="mantenere come conferma candidata",
        )
    )

    assert result.article == "12514"
    assert "`article = 12514`" in boundary_text
    assert "Any other article must be rejected." in boundary_text


def test_service_and_boundary_preserve_q1_to_q7_field_group_mapping():
    boundary_text = _read_boundary_doc()

    for question_id, field_group in FIELD_GROUP_BY_QUESTION_ID.items():
        answer_state = "ABSENT" if question_id == "Q7" else "YES"

        result = build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id=question_id,
                tl_answer_state=answer_state,
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={"sample": "value"},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )

        assert result.field_group == field_group
        assert f"| {question_id} | {field_group} |" in boundary_text


def test_service_and_boundary_preserve_da_verificare_confidence():
    boundary_text = _read_boundary_doc()

    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q3",
            tl_answer_state="UNKNOWN",
            resulting_status="DA_VERIFICARE",
            candidate_data={"route": "preview"},
            missing_data=["source confirmation"],
            next_safe_action="mantenere DA_VERIFICARE",
        )
    )

    assert result.confidence == "DA_VERIFICARE"
    assert "preserve DA_VERIFICARE confidence" in boundary_text
    assert "UNKNOWN must preserve DA_VERIFICARE." in boundary_text


def test_service_and_boundary_preserve_runtime_effects_statement():
    boundary_text = _read_boundary_doc()

    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q4",
            tl_answer_state="YES",
            resulting_status="CANDIDATE_CONFIRMATION",
            candidate_data={"station": "ZAW"},
            missing_data=[],
            next_safe_action="mantenere come conferma candidata",
        )
    )

    assert result.runtime_effects == RUNTIME_EFFECTS_STATEMENT
    assert RUNTIME_EFFECTS_STATEMENT in result.rendered_text
    assert "Effetti runtime: nessuna persistenza" in boundary_text
    assert "nessuna mutazione sorgente" in boundary_text
    assert "nessuna promozione a CERTO" in boundary_text
    assert "nessun planner" in boundary_text
    assert "nessun ATLAS" in boundary_text
    assert "nessuna scrittura SMF/DB" in boundary_text


def test_service_and_boundary_preserve_false_forbidden_runtime_effects():
    boundary_text = _read_boundary_doc()

    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q5",
            tl_answer_state="YES",
            resulting_status="CANDIDATE_CONFIRMATION",
            candidate_data={"component": "468922"},
            missing_data=[],
            next_safe_action="mantenere come conferma candidata",
        )
    )

    assert result.forbidden_runtime_effects == FORBIDDEN_RUNTIME_EFFECTS
    assert all(value is False for value in result.forbidden_runtime_effects.values())
    assert "No flag may become true in this capability." in boundary_text

    for flag in FORBIDDEN_RUNTIME_EFFECTS:
        assert flag in boundary_text


def test_service_output_is_candidate_only_according_to_boundary():
    boundary_text = _read_boundary_doc()

    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q6",
            tl_answer_state="CORRECTED_VALUE",
            resulting_status="CANDIDATE_CORRECTION",
            candidate_data={"tool": "candidate"},
            corrected_value={"tool": "corrected"},
            missing_data=["governed source confirmation"],
            next_safe_action="richiedere conferma fonte governata",
        )
    )

    assert result.resulting_status == "CANDIDATE_CORRECTION"
    assert result.corrected_value == {"tool": "corrected"}
    assert result.confidence == "DA_VERIFICARE"
    assert "The output is a renderable candidate only." in boundary_text
    assert "source of truth" in boundary_text
    assert "persisted confirmation" in boundary_text
    assert "operational authorization" in boundary_text
    assert "planning authorization" in boundary_text
    assert "production authorization" in boundary_text


def test_boundary_blocks_service_binding_and_side_effects():
    boundary_text = _read_boundary_doc()

    forbidden_binding_markers = [
        "TL Chat API binding | Forbidden",
        "Frontend rendering | Forbidden",
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

    for marker in forbidden_binding_markers:
        assert marker in boundary_text


def test_service_rendered_text_does_not_claim_operational_readiness():
    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q7",
            tl_answer_state="ABSENT",
            resulting_status="CANDIDATE_CONFIRMATION",
            candidate_data={"PIDMILL": "absent", "CP": "absent"},
            missing_data=[],
            next_safe_action="mantenere come conferma candidata",
        )
    )

    forbidden_claims = [
        "PRODUCTION_READY",
        "PLANNING_READY",
        "PLANNER_ELIGIBLE",
        "SOURCE_OF_TRUTH",
        "SAVED",
        "PERSISTED",
    ]

    for claim in forbidden_claims:
        assert claim not in result.rendered_text

    assert "Confidenza: DA_VERIFICARE" in result.rendered_text
    assert "Effetti runtime:" in result.rendered_text