from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "docs" / "PROMETEO_CONTEXT_SOURCE_INDEX_LIFECYCLE_RETENTION_POLICY_001.md"


def _read_policy() -> str:
    assert POLICY_PATH.exists()
    return POLICY_PATH.read_text(encoding="utf-8")


def test_lifecycle_policy_contract_markers_are_preserved() -> None:
    text = _read_policy()
    required_markers = [
        "CAPABILITY: CONTEXT_SOURCE_INDEX_LIFECYCLE_RETENTION_POLICY_001",
        "TYPE: DOCUMENTAL_TEST_ONLY",
        "RUNTIME_BINDING: FORBIDDEN",
        "FULL_CONTENT_READING: FORBIDDEN",
        "INDEX_MUTATION_RUNTIME: FORBIDDEN",
        "TL_CHAT_BINDING: FORBIDDEN",
        "ATLAS_ENGINE_BINDING: FORBIDDEN",
        "PLANNER_BINDING: FORBIDDEN",
        "DELETE_AUTOMATICALLY: FALSE",
        "PREFER_SUPERSEDE_OVER_DELETE: TRUE",
        "PREFER_ARCHIVE_OVER_DELETE: TRUE",
        "VERDETTO: POLICY_DEFINED_DOCUMENTAL_ONLY",
        "NEXT_ALLOWED_MOVE: ADD_DOCUMENTAL_POLICY_TEST",
        "RUNTIME_BINDING_ALLOWED: FALSE",
        "FULL_CONTENT_READING_ALLOWED: FALSE",
    ]
    for marker in required_markers:
        assert marker in text


def test_lifecycle_policy_preserves_allowed_source_states() -> None:
    text = _read_policy()
    for state in ["ACTIVE", "SUPERSEDED", "DEPRECATED", "REJECTED", "ARCHIVED", "DRAFT"]:
        assert state in text


def test_lifecycle_policy_preserves_runtime_binding_prohibitions() -> None:
    text = _read_policy()
    forbidden_phrases = [
        "runtime binding",
        "endpoint FastAPI",
        "retrieval runtime",
        "lettura contenuto integrale",
        "collegamento TL Chat",
        "collegamento ATLAS Engine",
        "collegamento planner",
        "agenti liberi",
        "path locali assoluti",
    ]
    for phrase in forbidden_phrases:
        assert phrase in text


def test_lifecycle_policy_preserves_anti_scope_creep_boundaries() -> None:
    text = _read_policy()
    required_fragments = [
        "Regola anti-scope-creep",
        "Questa capability",
        "policy",
        "Non pu",
        "modificare il comportamento del sistema",
        "Context Source Index",
        "fonte runtime",
        "metadata-only",
        "content-reading",
    ]
    for fragment in required_fragments:
        assert fragment in text


def test_lifecycle_policy_does_not_embed_local_paths_or_secrets() -> None:
    text = _read_policy()
    local_path = "/Users/" + "davidepiangiolino"
    assert local_path not in text
    assert "DATABASE_URL" not in text
    assert "sk-" not in text
    assert "BEGIN PRIVATE KEY" not in text

