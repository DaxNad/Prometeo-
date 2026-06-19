from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs/TL_CHAT_CONTEXT_RESOLVER_CONTRACT_001.md"


def _contract_text() -> str:
    assert CONTRACT_PATH.exists(), "Missing TL chat context resolver contract"
    return CONTRACT_PATH.read_text(encoding="utf-8")


def test_tl_chat_context_resolver_contract_preserves_no_runtime_scope() -> None:
    text = _contract_text()

    required_markers = [
        "status: CONTRACT_ONLY",
        "runtime_impact: NONE",
        "no_runtime_binding: true",
        "no_frontend_change: true",
        "no_planner_binding: true",
        "no_atlas_binding: true",
        "no_specs_finitura_real_read: true",
        "no_smf_real_read: true",
        "no_data_mutation: true",
    ]

    for marker in required_markers:
        assert marker in text


def test_tl_chat_context_resolver_contract_defines_resolution_contract() -> None:
    text = _contract_text()

    required_sections = [
        "## Scopo",
        "## Non-scopo",
        "## Input",
        "## Output",
        "## Intent class minime",
        "## Entity detection minima",
        "## Candidate source type",
        "## Confidence",
        "## Stop condition",
        "## Forbidden actions",
        "## Esempi obbligatori",
        "## Test minimi futuri",
        "## Criteri di chiusura",
    ]

    for section in required_sections:
        assert section in text


def test_tl_chat_context_resolver_contract_preserves_intent_classes() -> None:
    text = _contract_text()

    required_intents = [
        "SYSTEM_CAPABILITY",
        "ARTICLE_OPERATIONAL",
        "EXPLICIT_CANDIDATE_LIST",
        "TURN_WITHOUT_CONTEXT",
        "FAMILY_OR_COMPONENT",
        "UNKNOWN_OR_UNSUPPORTED",
    ]

    for intent in required_intents:
        assert intent in text


def test_tl_chat_context_resolver_contract_blocks_forbidden_runtime_paths() -> None:
    text = _contract_text()

    forbidden_runtime_markers = [
        "TL Chat binding",
        "frontend change",
        "planner binding",
        "ATLAS Engine binding",
        "endpoint creation",
        "LLM generation",
        "specs_finitura real read",
        "SMF real read",
        "promotion to CERTO",
    ]

    for marker in forbidden_runtime_markers:
        assert marker in text
