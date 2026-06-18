from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs" / "PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_CONTRACT_001.md"


def _contract_text() -> str:
    assert CONTRACT.exists(), "ContextSourceReaderAdapter contract is missing"
    return CONTRACT.read_text(encoding="utf-8")


def test_context_source_reader_adapter_contract_preserves_no_runtime_binding_policy():
    text = _contract_text()

    required_phrases = [
        "Non esiste ancora adapter operativo.",
        "Non esiste ancora binding runtime.",
        "Non esiste ancora accesso TL Chat.",
        "Non esiste ancora accesso ATLAS Engine.",
        "Non esiste ancora accesso planner.",
        "TL Chat non deve ancora usare questo adapter.",
        "ATLAS Engine non deve ancora usare questo adapter.",
        "Il planner non deve leggere questo adapter.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_context_source_reader_adapter_contract_preserves_readonly_metadata_boundaries():
    text = _contract_text()

    required_phrases = [
        "runtime_enabled=false",
        "access_mode=read_only",
        "Non leggere ancora il contenuto delle fonti indicizzate.",
        "Restituire solo metadati minimi.",
        "non modificare nulla",
        "nessuna scrittura file",
        "nessuna rete",
        "nessun accesso a `.env`",
        "nessun import di backend runtime",
        "nessun collegamento a FastAPI",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_context_source_reader_adapter_contract_preserves_forbidden_sources_and_actions():
    text = _contract_text()

    required_phrases = [
        "specs_finitura",
        "SMF reale",
        ".env",
        "backend/",
        "frontend/",
        "runtime/",
        "planner",
        "database",
        "contenuto integrale",
        "uso planner/runtime",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_context_source_reader_adapter_contract_declares_failure_on_scope_creep():
    text = _contract_text()

    required_phrases = [
        "Questo contratto fallisce se:",
        "introduce codice",
        "abilita runtime",
        "suggerisce lettura contenuti completa",
        "collega TL Chat, ATLAS Engine o planner",
        "trasforma l'LLM in fonte autorevole",
        "consente path arbitrari",
        "consente scrittura file",
    ]

    for phrase in required_phrases:
        assert phrase in text
