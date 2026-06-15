from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "ANTI_ENTROPY_GATE_CONTRACT_001.md"
THIS_FILE = Path(__file__).resolve()

STATUS_MARKERS = (
    "status: CONTRACT_ONLY",
    "runtime_impact: NONE",
    "no_new_runtime: true",
    "created_for: PROMETEO capability closure governance",
)

REQUIRED_SECTIONS = (
    "# ANTI_ENTROPY_GATE_CONTRACT_001",
    "## Status",
    "## Purpose",
    "## Scope",
    "## Non-goals",
    "## Core principle",
    "## Conceptual input schema",
    "## Conceptual output schema",
    "## DONE definition contract",
    "## Entropy budget",
    "## Allowed verdicts",
    "### CLOSE",
    "### CONTINUE",
    "### BLOCK",
    "## Blocking rules",
    "## Close rule",
    "## Stop rule",
    "## Forbidden actions",
    "## Relation with AGENT MOD GUARD",
    "## Relation with future Codex prompts",
    "## Relation with TL Chat, planner and ATLAS Engine",
    "## Recommended future guard",
    "## Final verdict",
)

ALLOWED_VERDICTS = (
    "CLOSE",
    "CONTINUE",
    "BLOCK",
)

FORBIDDEN_UPPERCASE_VERDICTS = (
    "PLAN",
    "EXECUTE",
    "BUILD",
    "DEPLOY",
    "MUTATE",
    "DECIDE_PRODUCTION",
    "UPDATE_ROUTE",
    "WRITE_MEMORY",
    "CALL_LLM",
    "CALL_PLANNER",
    "WRITE_SMF",
    "WRITE_DATABASE",
)

CORE_PRINCIPLE_MARKERS = (
    "riduce direttamente la distanza",
    "stato\nattuale",
    "DONE verificabile",
    "capability corrente",
)

INPUT_SCHEMA_MARKERS = (
    "capability_target",
    "done_definition",
    "current_state",
    "residual_gap",
    "proposed_action",
    "allowed_files",
    "forbidden_files",
    "entropy_budget",
    "minimal_tests",
    "known_blockers",
)

OUTPUT_SCHEMA_MARKERS = (
    "verdict",
    "reason",
    "missing_items",
    "rejected_actions",
    "allowed_next_action",
)

ENTROPY_BUDGET_MARKERS = (
    "max_files",
    "max_tests",
    "max_docs",
    "max_runtime_changes",
    "max_dependencies",
    "allowed_directories",
    "forbidden_directories",
    "capability_lateral_ban",
    "refactor_ban",
    "data_mutation_ban",
)

BLOCKING_RULE_MARKERS = (
    "non esiste DONE verificabile",
    "mancano test minimi o verifiche minime",
    "proposta fuori scope",
    "file fuori budget",
    "nuova architettura non richiesta",
    "refactor laterale",
    "nuova dipendenza",
    "capability laterale",
    "runtime non autorizzato",
    "modifica dati reali",
    "modifica " + "." + "env/segreti",
    "modifica SMF reale",
    "modifica specs" + "_finitura",
    "azione migliora genericamente il sistema ma non chiude la capability",
)

FORBIDDEN_ACTION_MARKERS = (
    "runtime implementation",
    "autonomous agent behavior",
    "planner behavior",
    "architecture generation",
    "TL Chat binding",
    "planner binding",
    "endpoint creation",
    "LLM generation",
    "DB write",
    "SMF write",
    "metadata update",
    "route override",
    "production priority",
    "memory write automation",
    "frontend integration",
)

CLOSE_AND_STOP_MARKERS = (
    "Se DONE definition e soddisfatta",
    "verifiche minime passano",
    "verdict deve\nessere CLOSE",
    "non proporre ulteriori miglioramenti",
    "non proporre ulteriori miglioramenti o prossimi step\ntecnici",
)

GOVERNANCE_RELATION_MARKERS = (
    "AGENT MOD GUARD definisce il perimetro operativo",
    "ANTI_ENTROPY_GATE valuta se una proposta riduce la distanza dal DONE",
    "Il gate non sostituisce il report iniziale obbligatorio",
    "file ammessi",
    "file\nvietati",
    "test minimi",
)

FINAL_VERDICT_MARKERS = (
    "authorizes no runtime behavior",
    "no autonomous agent",
    "no planner integration",
    "no TL Chat integration",
    "no LLM generation",
    "no endpoint exposure",
    "no data\nmutation",
)

FORBIDDEN_SELF_MARKER_PARTS = (
    ("sub", "process"),
    ("re", "quests"),
    ("url", "lib"),
    ("sock", "et"),
    ("os", ".", "system"),
    ("git", " "),
    (".", "env"),
    ("specs", "_finitura"),
    ("data", "/", "local_smf"),
    ("open", "ai"),
    ("anth", "ropic"),
    ("ol", "lama"),
    ("lite", "llm"),
    ("Fast", "API"),
    ("API", "Router"),
    ("governed", "_retrieval"),
    ("tl", "_chat"),
    ("planner", "_smf"),
    ("sql", "alchemy"),
    ("psy", "copg"),
)


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _assert_contains_all(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        assert marker in text, f"missing {label}: {marker}"


def test_anti_entropy_contract_exists():
    assert CONTRACT.is_file()


def test_anti_entropy_contract_status_is_contract_only():
    _assert_contains_all(_contract_text(), STATUS_MARKERS, "status marker")


def test_anti_entropy_contract_required_sections():
    _assert_contains_all(_contract_text(), REQUIRED_SECTIONS, "required section")


def test_anti_entropy_contract_verdicts_are_limited():
    text = _contract_text()
    _assert_contains_all(text, ALLOWED_VERDICTS, "allowed verdict")
    for marker in FORBIDDEN_UPPERCASE_VERDICTS:
        assert marker not in text, f"contract contains unauthorized verdict marker: {marker}"


def test_anti_entropy_contract_core_principle():
    _assert_contains_all(_contract_text(), CORE_PRINCIPLE_MARKERS, "core principle")


def test_anti_entropy_contract_input_schema():
    _assert_contains_all(_contract_text(), INPUT_SCHEMA_MARKERS, "input schema marker")


def test_anti_entropy_contract_output_schema():
    _assert_contains_all(_contract_text(), OUTPUT_SCHEMA_MARKERS, "output schema marker")


def test_anti_entropy_contract_entropy_budget():
    _assert_contains_all(_contract_text(), ENTROPY_BUDGET_MARKERS, "entropy budget marker")


def test_anti_entropy_contract_blocking_rules():
    _assert_contains_all(_contract_text(), BLOCKING_RULE_MARKERS, "blocking rule")


def test_anti_entropy_contract_forbidden_actions():
    _assert_contains_all(_contract_text(), FORBIDDEN_ACTION_MARKERS, "forbidden action")


def test_anti_entropy_contract_close_and_stop_rules():
    _assert_contains_all(_contract_text(), CLOSE_AND_STOP_MARKERS, "close or stop rule")


def test_anti_entropy_contract_relation_with_governance():
    _assert_contains_all(_contract_text(), GOVERNANCE_RELATION_MARKERS, "governance relation")


def test_anti_entropy_contract_no_runtime_authorization():
    _assert_contains_all(_contract_text(), FINAL_VERDICT_MARKERS, "final verdict marker")


def test_anti_entropy_guard_test_is_static_safe():
    test_text = THIS_FILE.read_text(encoding="utf-8")
    for index, parts in enumerate(FORBIDDEN_SELF_MARKER_PARTS):
        marker = "".join(parts)
        assert marker not in test_text, f"guard contains forbidden marker at index {index}"
