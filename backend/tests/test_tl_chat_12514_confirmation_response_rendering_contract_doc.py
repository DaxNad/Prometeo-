from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_001.md"


def _doc() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_rendering_contract_document_exists_and_declares_scope():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_001",
        "This is a rendering contract only",
        "It does not implement runtime behavior",
        "It does not persist TL answers",
        "It does not mutate preview JSON",
        "It does not promote any value to CERTO",
        "It does not enable planner eligibility",
        "It does not invoke ATLAS",
        "It does not write to SMF or database",
        "It does not change API behavior",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_source_references():
    text = _doc()

    required = [
        "docs/TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001.md",
        "docs/TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001.md",
        "docs/TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001.md",
        "backend/tests/test_tl_chat_12514_confirmation_prompt_contract_doc.py",
        "backend/tests/test_tl_chat_12514_confirmation_runtime_boundary_doc.py",
        "backend/tests/test_tl_chat_12514_confirmation_non_persistent_response_model_doc.py",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_rendering_principle():
    text = _doc()

    required = [
        "A TL Chat confirmation response may be displayed only as a non-persistent candidate",
        "the article is 12514",
        "the answered question id is Q1-Q7",
        "the response is not persisted",
        "the response is not source of truth",
        "the response does not promote data to CERTO",
        "the response does not enable planner eligibility",
        "the response does not make production readiness claims",
        "the response does not make planning readiness claims",
        "the next action remains governed confirmation or source review",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_required_rendered_sections():
    text = _doc()

    required = [
        "## Required rendered sections",
        "Article",
        "Question",
        "TL answer state",
        "Resulting status",
        "Candidate data",
        "Runtime effects",
        "Confidence",
        "Missing data",
        "Next safe action",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_allowed_and_forbidden_statuses():
    text = _doc()

    required = [
        "CANDIDATE_CONFIRMATION",
        "CANDIDATE_CORRECTION",
        "DA_VERIFICARE",
        "MISSING",
        "BLOCKED",
        "CERTO",
        "PRODUCTION_READY",
        "PLANNING_READY",
        "PLANNER_ELIGIBLE",
        "SOURCE_OF_TRUTH",
        "SAVED",
        "PERSISTED",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_runtime_effects_statement():
    text = _doc()

    required = [
        "Effetti runtime: nessuna persistenza",
        "nessuna mutazione sorgente",
        "nessuna promozione a CERTO",
        "nessun planner",
        "nessun ATLAS",
        "nessuna scrittura SMF/DB",
        "The wording may change in future UI implementation, but the meaning must remain present",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_required_rendering_shape():
    text = _doc()

    required = [
        "## Required rendering shape",
        "Articolo: 12514",
        "Domanda: Qx - <field_group>",
        "Risposta TL: <tl_answer_state>",
        "Stato risultante: <resulting_status>",
        "Dati candidati: <candidate data>",
        "Confidenza: DA_VERIFICARE / candidate only",
        "Dati mancanti: <missing data or none>",
        "Prossima azione sicura: <one governed next action>",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_q1_to_q7_rules():
    text = _doc()

    required = [
        "## Q1 rendering rule",
        "article_identity",
        "Q1 confirmation may be rendered as CANDIDATE_CONFIRMATION only",
        "It must not be rendered as CERTO",
        "## Q2 rendering rule",
        "packaging_and_quantities",
        "It must not be rendered as production-ready or planning-ready",
        "## Q3 rendering rule",
        "normalized_route",
        "It must not enable planner eligibility",
        "## Q4 rendering rule",
        "zaw_station_resolution",
        "Q4 confirmation must not infer ZAW2 from repeated ZAW operations",
        "## Q5 rendering rule",
        "components",
        "It must not promote component completeness to CERTO",
        "## Q6 rendering rule",
        "tooling",
        "It must not promote tooling completeness to CERTO",
        "## Q7 rendering rule",
        "pidmill_and_cp_visibility",
        "ABSENT is renderable only for Q7",
        "Absence must not be rendered as CERTO unless governed source confirmation exists later",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_examples():
    text = _doc()

    required = [
        "### YES example",
        "Risposta TL: YES",
        "Stato risultante: CANDIDATE_CONFIRMATION",
        "### CORRECTED_VALUE example",
        "Risposta TL: CORRECTED_VALUE",
        "Stato risultante: CANDIDATE_CORRECTION",
        "### UNKNOWN example",
        "Risposta TL: UNKNOWN",
        "Stato risultante: DA_VERIFICARE",
        "### BLOCKED example",
        "Stato risultante: BLOCKED",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_forbids_operational_claims():
    text = _doc()

    required = [
        "## Forbidden rendering behavior",
        "conferma salvata",
        "dato aggiornato",
        "dato certo",
        "articolo pronto per produzione",
        "articolo pronto per pianificazione",
        "planner abilitato",
        "ATLAS invocato",
        "SMF aggiornato",
        "database aggiornato",
        "sorgente modificata",
        "preview JSON modificato",
        "conferma usata come source of truth",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_one_next_safe_action_policy():
    text = _doc()

    required = [
        "## Safe next action policy",
        "Every rendered confirmation response must include exactly one next safe action",
        "mantenere come conferma candidata",
        "richiedere conferma fonte governata",
        "chiedere correzione mirata al TL",
        "consultare specifica reale",
        "mantenere DA_VERIFICARE",
        "bloccare la decisione operativa",
        "pianificare produzione",
        "autorizzare produzione",
        "promuovere a CERTO",
        "salvare risposta TL",
        "aggiornare preview JSON",
        "aggiornare SMF",
        "aggiornare database",
        "invocare planner",
        "invocare ATLAS",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_acceptance_criteria():
    text = _doc()

    required = [
        "## Acceptance criteria",
        "capability name",
        "rendering principle",
        "required rendered sections",
        "allowed rendered statuses",
        "forbidden rendered statuses",
        "required runtime effects statement",
        "required rendering shape",
        "Q1-Q7 rendering rules",
        "rendering examples",
        "forbidden rendering behavior",
        "one-next-safe-action policy",
        "explicit no persistence",
        "explicit no CERTO",
        "explicit no planner",
        "explicit no ATLAS",
        "explicit no SMF/DB",
        "explicit no API/runtime implementation",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_recommends_expected_next_capability():
    text = _doc()

    required = [
        "TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_TEST_001",
        "Guard this rendering contract with a document-level test before any runtime rendering",
        "required rendered sections",
        "allowed rendered statuses",
        "forbidden rendered statuses",
        "runtime effects statement",
        "Q1-Q7 rendering rules",
        "examples for YES, CORRECTED_VALUE, UNKNOWN, and BLOCKED",
        "forbidden persistence and operational claims",
        "exactly one safe next action policy",
        "no runtime implementation",
        "no planner",
        "no ATLAS",
        "no SMF/DB",
        "no API changes",
    ]

    for phrase in required:
        assert phrase in text


def test_rendering_contract_declares_non_goals_and_closure_verdict():
    text = _doc()

    required = [
        "## Non-goals",
        "runtime rendering",
        "frontend changes",
        "TL Chat API changes",
        "answer persistence",
        "confirmation persistence",
        "source mutation",
        "preview JSON mutation",
        "CERTO promotion",
        "planner enablement",
        "ATLAS invocation",
        "SMF write",
        "database write",
        "production readiness",
        "planning readiness",
        "## Closure verdict",
        "CAPABILITY: TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_001",
        "STATUS: DOCUMENT_CREATED",
        "VERDICT: PENDING_TEST_AND_PR",
        "NEXT SAFE ACTION: add a document-level test guard before runtime rendering",
    ]

    for phrase in required:
        assert phrase in text