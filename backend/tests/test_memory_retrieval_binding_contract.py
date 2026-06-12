from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md"

REQUIRED_SECTIONS = (
    "## 1. Scopo",
    "## 2. Principio architetturale",
    "## 3. File ammessi in futuro",
    "## 4. Sezioni leggibili",
    "## 5. Output evidence pack",
    "## 6. Fonti vietate",
    "## 7. Divieti espliciti",
    "## 8. Criteri futuri per guard",
)

REQUIRED_MEMORY_FRONT_MATTER_FIELDS = (
    "memory_id",
    "type",
    "status",
    "authority",
    "confidence",
    "allowed_for_retrieval",
    "sensitive",
    "last_review",
)

REQUIRED_EVIDENCE_FIELDS = (
    "source_id",
    "source_path",
    "source_type",
    "authority",
    "confidence",
    "section",
    "text",
    "reason",
    "retrieval_allowed",
    "sensitive",
)

REQUIRED_FORBIDDEN_SOURCES = (
    ".env",
    "specs_finitura/",
    "data/local_smf",
    "immagini",
    "PDF",
    "Excel",
    "dump database",
    "cache non governate",
    "log privati",
    "embeddings non governati",
    "file fuori `memory/`",
)

REQUIRED_EXPLICIT_BANS = (
    "TL Chat",
    "governed_retrieval.py",
    "runtime",
    "LLM locale",
    "planner",
    "mutation backend",
    "scrittura su `memory/`",
    "SMF",
    "database",
    "promozione automatica di `INFERENZA` o `DA_VERIFICARE` a `CERTO`",
)

FORBIDDEN_AUTHORIZATION_PHRASES = (
    "collega a tl chat",
    "integra con tl chat",
    "chiama governed_retrieval",
    "usa llm locale",
    "scrive su memory",
    "scrive su database",
    "modifica smf",
    "promuove automaticamente",
)


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _remove_explicit_ban_sections(text: str) -> str:
    """Ignore sections whose purpose is to list forbidden behavior."""
    lowered = text.lower()
    for start_marker, end_marker in (
        ("## 7. divieti espliciti", "## 8. criteri futuri per guard"),
        ("## 8. criteri futuri per guard", "## 9. non obiettivi"),
        ("## 9. non obiettivi", "## 10. verdict del contratto"),
    ):
        start = lowered.find(start_marker)
        end = lowered.find(end_marker)
        if start != -1 and end != -1 and end > start:
            text = text[:start] + text[end:]
            lowered = text.lower()
    return text


def test_memory_retrieval_binding_contract_exists():
    assert CONTRACT.is_file()


def test_memory_retrieval_binding_contract_has_required_sections():
    text = _contract_text()
    for section in REQUIRED_SECTIONS:
        assert section in text, f"missing contract section: {section}"


def test_memory_retrieval_binding_contract_lists_required_memory_front_matter_fields():
    text = _contract_text()
    for field in REQUIRED_MEMORY_FRONT_MATTER_FIELDS:
        assert field in text, f"missing future memory front matter field: {field}"


def test_memory_retrieval_binding_contract_defines_evidence_schema():
    text = _contract_text()
    for field in REQUIRED_EVIDENCE_FIELDS:
        assert field in text, f"missing evidence schema field: {field}"


def test_memory_retrieval_binding_contract_lists_forbidden_sources():
    text = _contract_text()
    for source in REQUIRED_FORBIDDEN_SOURCES:
        assert source in text, f"missing forbidden source: {source}"


def test_memory_retrieval_binding_contract_has_explicit_bans():
    text = _contract_text()
    for banned in REQUIRED_EXPLICIT_BANS:
        assert banned in text, f"missing explicit ban: {banned}"


def test_memory_retrieval_binding_contract_does_not_authorize_runtime_binding():
    normalized = _remove_explicit_ban_sections(_contract_text()).lower()
    for phrase in FORBIDDEN_AUTHORIZATION_PHRASES:
        assert phrase not in normalized, f"contract authorizes forbidden behavior: {phrase}"
