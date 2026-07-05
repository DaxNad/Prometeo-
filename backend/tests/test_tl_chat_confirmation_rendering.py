from backend.app.services.tl_chat_confirmation_rendering import (
    FIELD_GROUP_BY_QUESTION_ID,
    FORBIDDEN_RUNTIME_EFFECTS,
    RUNTIME_EFFECTS_STATEMENT,
    TLChatConfirmationRenderingError,
    TLChatConfirmationRenderingInput,
    build_confirmation_rendering,
)


def test_build_confirmation_rendering_returns_non_persistent_candidate():
    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q1",
            tl_answer_state="YES",
            resulting_status="CANDIDATE_CONFIRMATION",
            candidate_data={
                "codice": "7056055000A0",
                "disegno": "A1675003603",
                "rev": "6",
                "rev_data": "25/09/2025",
            },
            missing_data=[],
            next_safe_action="mantenere come conferma candidata",
        )
    )

    assert result.article == "12514"
    assert result.question_id == "Q1"
    assert result.field_group == "article_identity"
    assert result.tl_answer_state == "YES"
    assert result.resulting_status == "CANDIDATE_CONFIRMATION"
    assert result.confidence == "DA_VERIFICARE"
    assert result.missing_data == []
    assert result.runtime_effects == RUNTIME_EFFECTS_STATEMENT
    assert result.forbidden_runtime_effects == FORBIDDEN_RUNTIME_EFFECTS
    assert result.next_safe_action == "mantenere come conferma candidata"

    assert "Articolo: 12514" in result.rendered_text
    assert "Domanda: Q1 - article_identity" in result.rendered_text
    assert "Risposta TL: YES" in result.rendered_text
    assert "Stato risultante: CANDIDATE_CONFIRMATION" in result.rendered_text
    assert "Confidenza: DA_VERIFICARE" in result.rendered_text
    assert RUNTIME_EFFECTS_STATEMENT in result.rendered_text
    assert "Prossima azione sicura: mantenere come conferma candidata" in result.rendered_text


def test_build_confirmation_rendering_preserves_candidate_data_copy():
    input_data = TLChatConfirmationRenderingInput(
        article="12514",
        question_id="Q2",
        tl_answer_state="CORRECTED_VALUE",
        resulting_status="CANDIDATE_CORRECTION",
        candidate_data={"imballo": "50563"},
        corrected_value={"quantita_imballo": 80},
        missing_data=["source confirmation"],
        next_safe_action="richiedere conferma fonte governata",
    )

    result = build_confirmation_rendering(input_data)

    assert result.field_group == "packaging_and_quantities"
    assert result.candidate_data == {"imballo": "50563"}
    assert result.corrected_value == {"quantita_imballo": 80}
    assert result.missing_data == ["source confirmation"]
    assert "Dati mancanti: source confirmation" in result.rendered_text


def test_build_confirmation_rendering_supports_all_q1_to_q7_field_groups():
    for question_id, field_group in FIELD_GROUP_BY_QUESTION_ID.items():
        state = "ABSENT" if question_id == "Q7" else "YES"

        result = build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id=question_id,
                tl_answer_state=state,
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={"sample": "value"},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )

        assert result.question_id == question_id
        assert result.field_group == field_group
        assert f"Domanda: {question_id} - {field_group}" in result.rendered_text


def test_build_confirmation_rendering_rejects_invalid_article_code():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="../12514",
                question_id="Q1",
                tl_answer_state="YES",
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "Invalid article code" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_rejects_unknown_question_id():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q8",
                tl_answer_state="YES",
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "Unsupported question_id" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_rejects_unknown_answer_state():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q1",
                tl_answer_state="MAYBE",
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "Unsupported tl_answer_state" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_rejects_unknown_resulting_status():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q1",
                tl_answer_state="YES",
                resulting_status="CERTO",
                candidate_data={},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "Unsupported resulting_status" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_requires_corrected_value_for_correction():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q2",
                tl_answer_state="CORRECTED_VALUE",
                resulting_status="CANDIDATE_CORRECTION",
                candidate_data={},
                corrected_value=None,
                missing_data=[],
                next_safe_action="richiedere conferma fonte governata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "CORRECTED_VALUE requires corrected_value" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_allows_absent_only_for_q7():
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

    assert result.question_id == "Q7"
    assert result.field_group == "pidmill_and_cp_visibility"
    assert result.tl_answer_state == "ABSENT"


def test_build_confirmation_rendering_rejects_absent_outside_q7():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q1",
                tl_answer_state="ABSENT",
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={},
                missing_data=[],
                next_safe_action="mantenere come conferma candidata",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "ABSENT is renderable only for Q7" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_build_confirmation_rendering_requires_next_safe_action():
    try:
        build_confirmation_rendering(
            TLChatConfirmationRenderingInput(
                article="12514",
                question_id="Q1",
                tl_answer_state="YES",
                resulting_status="CANDIDATE_CONFIRMATION",
                candidate_data={},
                missing_data=[],
                next_safe_action=" ",
            )
        )
    except TLChatConfirmationRenderingError as exc:
        assert "next_safe_action is required" in str(exc)
    else:
        raise AssertionError("Expected TLChatConfirmationRenderingError")


def test_forbidden_runtime_effects_are_all_false():
    assert FORBIDDEN_RUNTIME_EFFECTS == {
        "tl_answer_persistence": False,
        "preview_json_mutation": False,
        "certo_promotion": False,
        "planner_enablement": False,
        "atlas_invocation": False,
        "smf_write": False,
        "database_write": False,
        "api_contract_change": False,
        "production_readiness": False,
        "planning_readiness": False,
    }