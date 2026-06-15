from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001.md"
THIS_FILE = Path(__file__).resolve()

REQUIRED_SECTIONS = (
    "## 1. Scopo",
    "## 2. Principio architetturale",
    "## 3. Input ammessi per futuro runtime",
    "## 4. Output ammesso",
    "## 5. Gate obbligatori futuri",
    "## 6. Divieti espliciti",
    "## 7. Stop condition",
    "## 8. Schema preview runtime futuro",
    "## 9. Criteri futuri per MEMORY_RETRIEVAL_RUNTIME_GUARD_001",
    "## 10. Non obiettivi",
    "## 11. Verdict del contratto",
)

REQUIRED_STRUCTURAL_TERMS = (
    "EvidenceItem",
    "ContextPack",
    "memory/*.md autorizzati",
    "runtime_request",
    "runtime_response",
    "dry_run",
    "ok",
    "blocked",
    "block_reason",
    "context_pack",
    "audit_reason",
)

REQUIRED_ALLOWED_INPUTS = (
    "query",
    "intent",
    "caller",
    "memory_root",
    "max_items",
    "max_chars_per_item",
    "context purpose",
    "caller dichiarato",
)

REQUIRED_ALLOWED_OUTPUTS = (
    "ContextPack",
    "selected_count",
    "total_candidates",
    "truncated",
    "build_reason",
    "source_id",
    "source_path",
    "authority",
    "confidence",
    "section",
    "text",
    "reason",
    "rank_reason",
)

REQUIRED_FUTURE_GATES = (
    "contract test sul runtime contract",
    "test su `ContextPack`",
    "test anti-sensitive",
    "test no-runtime-mutation",
    "test no-TL-Chat-side-effect",
    "test no-planner-side-effect",
    "test no-SMF/database-write",
    "audit log minimo o preview log read-only",
)

REQUIRED_STOP_CONDITIONS = (
    "`memory_root` non e autorizzato",
    "`ContextPack` contiene `sensitive=true`",
    "`source_path` non e sotto `memory/`",
    "`confidence` e mancante",
    "`authority` e mancante",
    "caller non e dichiarato",
    "query o intent e vuoto o non classificato",
    "viene richiesto apply o mutation",
    "viene richiesto accesso a fonti vietate",
)

REQUIRED_EXPLICIT_BANS = (
    "collegamento diretto a TL Chat in questa fase",
    "chiamata diretta da `governed_retrieval.py` senza capability dedicata",
    "uso LLM locale",
    "planner mutation",
    "backend mutation",
    "scrittura su `memory/`",
    "scrittura su SMF",
    "scrittura su database",
    "lettura di `specs_finitura/`",
    "lettura di `.env`",
    "lettura immagini/PDF/Excel reali",
    "accesso a dati produttivi reali grezzi",
    "apply operativo",
    "side effect runtime non dichiarati e non testati",
)

REQUIRED_SOURCE_HIERARCHY = (
    "`ContextPack` non decide",
    "`ContextPack` non promuove `confidence`",
    "AI, agenti e LLM non sono fonti autorevoli",
    "Planner suggerisce, non decide",
    "TL resta autorita operativa finale",
    "Specifica reale e conferma TL prevalgono sempre",
    "Nessuna informazione da `ContextPack` puo promuovere automaticamente una\n"
    "`INFERENZA` o un `DA_VERIFICARE` a `CERTO`",
)

FORBIDDEN_AUTHORIZATION_PATTERNS = (
    "autorizza tl chat binding diretto",
    "autorizza mutation/runtime apply",
    "autorizza llm locale",
    "autorizza planner mutation",
    "puo scrivere su memory/",
    "puo scrivere su smf",
    "puo scrivere su database",
    "promuove automaticamente a certo",
    "contextpack e fonte autorevole",
    "contextpack prevale su specifica reale",
    "contextpack prevale su conferma tl",
)

SAFE_SECTIONS = (
    "## 6. Divieti espliciti",
    "## 9. Criteri futuri per MEMORY_RETRIEVAL_RUNTIME_GUARD_001",
    "## 10. Non obiettivi",
)

FORBIDDEN_TEST_IMPORT_PARTS = (
    ("backend", "app", "api", "tl_chat"),
    ("backend", "app", "atlas_engine", "governed_retrieval"),
    ("backend", "app", "services", "sequence_planner"),
    ("backend", "app", "services", "planner_smf"),
)

FORBIDDEN_TEST_SIDE_EFFECT_PARTS = (
    ("tmp", "_path"),
    ("Temporary", "Directory"),
    ("Named", "Temporary", "File"),
    ("sub", "process"),
    ("re", "quests"),
    ("url", "lib"),
    ("sock", "et"),
    ("os", ".", "system"),
    ("git", " "),
)


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _section_bounds(text: str) -> list[tuple[str, int, int]]:
    headings: list[tuple[str, int]] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            headings.append((line.strip(), offset))
        offset += len(line)

    bounds: list[tuple[str, int, int]] = []
    for index, (heading, start) in enumerate(headings):
        end = headings[index + 1][1] if index + 1 < len(headings) else len(text)
        bounds.append((heading, start, end))
    return bounds


def _remove_safe_sections(text: str) -> str:
    stripped = text
    for heading, start, end in reversed(_section_bounds(text)):
        if heading in SAFE_SECTIONS:
            stripped = stripped[:start] + stripped[end:]
    return stripped


def _assert_contains_all(text: str, required: tuple[str, ...], label: str) -> None:
    for item in required:
        assert item in text, f"missing {label}: {item}"


def test_memory_retrieval_runtime_contract_exists():
    assert CONTRACT.is_file()


def test_memory_retrieval_runtime_contract_has_required_sections():
    _assert_contains_all(_contract_text(), REQUIRED_SECTIONS, "required section")


def test_memory_retrieval_runtime_contract_has_structural_terms():
    _assert_contains_all(_contract_text(), REQUIRED_STRUCTURAL_TERMS, "structural term")


def test_memory_retrieval_runtime_contract_lists_allowed_inputs():
    _assert_contains_all(_contract_text(), REQUIRED_ALLOWED_INPUTS, "allowed input")


def test_memory_retrieval_runtime_contract_lists_allowed_outputs():
    _assert_contains_all(_contract_text(), REQUIRED_ALLOWED_OUTPUTS, "allowed output")


def test_memory_retrieval_runtime_contract_lists_future_gates():
    _assert_contains_all(_contract_text(), REQUIRED_FUTURE_GATES, "future gate")


def test_memory_retrieval_runtime_contract_lists_stop_conditions():
    _assert_contains_all(_contract_text(), REQUIRED_STOP_CONDITIONS, "stop condition")


def test_memory_retrieval_runtime_contract_lists_explicit_bans():
    _assert_contains_all(_contract_text(), REQUIRED_EXPLICIT_BANS, "explicit ban")


def test_memory_retrieval_runtime_contract_preserves_source_hierarchy():
    _assert_contains_all(_contract_text(), REQUIRED_SOURCE_HIERARCHY, "source hierarchy rule")


def test_memory_retrieval_runtime_contract_does_not_authorize_forbidden_runtime_behavior():
    unsafe_text = _remove_safe_sections(_contract_text()).lower()
    for pattern in FORBIDDEN_AUTHORIZATION_PATTERNS:
        assert pattern not in unsafe_text, f"contract authorizes forbidden behavior: {pattern}"


def test_runtime_contract_guard_does_not_import_runtime_modules():
    test_text = THIS_FILE.read_text(encoding="utf-8")
    for parts in FORBIDDEN_TEST_IMPORT_PARTS:
        module = ".".join(parts)
        assert f"import {module}" not in test_text
        assert f"from {module}" not in test_text


def test_runtime_contract_guard_is_document_only():
    test_text = THIS_FILE.read_text(encoding="utf-8")
    for parts in FORBIDDEN_TEST_SIDE_EFFECT_PARTS:
        marker = "".join(parts)
        assert marker not in test_text, f"test contains forbidden side-effect marker: {marker}"
