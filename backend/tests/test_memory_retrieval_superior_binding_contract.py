from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "MEMORY_RETRIEVAL_SUPERIOR_BINDING_CONTRACT_001.md"
THIS_FILE = Path(__file__).resolve()

STATUS_MARKERS = (
    "# MEMORY_RETRIEVAL_SUPERIOR_BINDING_CONTRACT_001",
    "status: CONTRACT_ONLY",
    "runtime_impact: NONE",
    "no_runtime_binding: true",
)

LOWER_PIPELINE_MARKERS = (
    "collect_memory_evidence()",
    "build_context_pack()",
    "build_memory_retrieval_preview()",
    "MemoryRetrievalRuntimeRequest",
    "MemoryRetrievalRuntimeResponse",
    "ContextPack",
)

AUTHORIZED_CALLER_MARKERS = (
    "`runtime_preview`",
    "`tl" + "_chat_preview`: RESERVED_NOT_ENABLED",
    "`atlas_preview`: RESERVED_NOT_ENABLED",
)

AUTHORIZED_INTENTS = (
    "domain_memory_preview",
    "article_memory_preview",
    "rule_memory_preview",
)

FORBIDDEN_INTENTS = (
    "plan" + "ner_decision",
    "production_priority",
    "route_override",
    "metadata_update",
    "smf_update",
    "memory_write",
    "llm_answer_generation",
    "autonomous_decision",
)

REQUEST_SCHEMA_MARKERS = (
    "MemorySuperiorBindingRequest",
    "query: non-empty string",
    "intent: enum autorizzato",
    "caller: enum autorizzato",
    'memory_root: Path con nome "memory"',
    "dry_run: true obbligatorio",
    "max_items: integer, default 5",
    "max_chars_per_item: integer, default 500",
)

RESPONSE_SCHEMA_MARKERS = (
    "MemorySuperiorBindingResponse",
    "ok: bool",
    "blocked: bool",
    "block_reason: string | null",
    "query: string",
    "intent: string",
    "caller: string",
    "context_pack: ContextPack | null",
    "allowed_next_step: enum",
    "audit_reason: string",
)

ALLOWED_NEXT_STEPS = (
    "VIEW_ONLY",
    "ASK_HUMAN_CONFIRMATION",
    "NO_ACTION",
)

FORBIDDEN_NEXT_STEPS = (
    "PLAN_PRODUCTION",
    "CHANGE_ROUTE",
    "UPDATE_METADATA",
    "WRITE_MEMORY",
    "CALL_LLM",
    "CALL_PLANNER",
    "WRITE_SMF",
    "WRITE_DATABASE",
)

GATE_RULES = (
    "bloccare caller non autorizzato",
    "bloccare intent non autorizzato",
    "bloccare `dry_run` diverso da `true`",
    "bloccare query vuota",
    "bloccare `memory_root` non chiamata `memory`",
    "bloccare `ContextPack` con `source_path` fuori `memory/`",
    "bloccare `ContextPack` senza `authority`",
    "bloccare `ContextPack` senza `confidence`",
    "non promuovere `confidence`",
    "non cambiare `authority`",
    "non trasformare `ContextPack` in decisione operativa",
)

STOP_CONDITIONS = (
    "decisione produttiva",
    "mutazione dati",
    "generazione LLM operativa",
    "plan" + "ner",
    "route override",
    "update metadata",
    "SMF/database",
    "caller o intent sono ambigui",
    "source e sensibile o non autorizzata",
    "NO_ACTION",
)

EXPLICIT_NON_GOALS = (
    "no TL Chat binding",
    "no `governed" + "_retrieval.py` binding",
    "no plan" + "ner binding",
    "no LLM call",
    "no endpoint",
    "no DB write",
    "no SMF write",
    "no memory write",
    "no frontend",
    "no runtime mutation",
)

SECURITY_CONSTRAINTS = (
    "non leggere dati reali",
    "non leggere `specs" + "_finitura`",
    "non leggere SMF reale",
    "non leggere `" + "." + "env`",
    "non leggere immagini/PDF/Excel reali",
    "usare solo memory governata gia autorizzata",
    "usare fixture sintetiche per test futuri",
)

FUTURE_SEQUENCE = (
    "MEMORY_RETRIEVAL_SUPERIOR_BINDING_GUARD_001",
    "MEMORY_RETRIEVAL_SUPERIOR_BINDING_001 preview-only",
    "MEMORY_RETRIEVAL_SUPERIOR_BINDING_EVAL_001",
    "Solo dopo valutare TL Chat preview binding contract",
)

FINAL_VERDICT_MARKERS = (
    "controlled preview access to ContextPack",
    "does not authorize operational use",
    "automated decisions",
    "plan" + "ner integration",
    "TL Chat integration",
    "LLM generation",
    "data mutation",
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
    ("plan", "ner"),
    ("tl", "_chat"),
    ("governed", "_retrieval"),
)


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _assert_contains_all(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        assert marker in text, f"missing {label}: {marker}"


def test_superior_binding_contract_file_exists():
    assert CONTRACT.is_file()


def test_superior_binding_contract_status_is_contract_only():
    _assert_contains_all(_contract_text(), STATUS_MARKERS, "contract-only status marker")


def test_superior_binding_contract_preserves_lower_pipeline():
    _assert_contains_all(_contract_text(), LOWER_PIPELINE_MARKERS, "lower pipeline marker")


def test_superior_binding_contract_authorized_callers_are_strict():
    _assert_contains_all(_contract_text(), AUTHORIZED_CALLER_MARKERS, "authorized caller marker")


def test_superior_binding_contract_authorized_intents_are_strict():
    _assert_contains_all(_contract_text(), AUTHORIZED_INTENTS, "authorized intent")


def test_superior_binding_contract_forbidden_intents_are_present():
    _assert_contains_all(_contract_text(), FORBIDDEN_INTENTS, "forbidden intent")


def test_superior_binding_contract_request_schema_is_guarded():
    _assert_contains_all(_contract_text(), REQUEST_SCHEMA_MARKERS, "request schema marker")


def test_superior_binding_contract_response_schema_is_guarded():
    _assert_contains_all(_contract_text(), RESPONSE_SCHEMA_MARKERS, "response schema marker")


def test_superior_binding_contract_allowed_next_steps_are_non_operational():
    _assert_contains_all(_contract_text(), ALLOWED_NEXT_STEPS, "allowed next step")


def test_superior_binding_contract_forbidden_next_steps_are_operational():
    _assert_contains_all(_contract_text(), FORBIDDEN_NEXT_STEPS, "forbidden next step")


def test_superior_binding_contract_gate_rules_are_present():
    _assert_contains_all(_contract_text(), GATE_RULES, "gate rule")


def test_superior_binding_contract_stop_conditions_are_present():
    _assert_contains_all(_contract_text(), STOP_CONDITIONS, "stop condition")


def test_superior_binding_contract_explicit_non_goals_are_present():
    _assert_contains_all(_contract_text(), EXPLICIT_NON_GOALS, "explicit non-goal")


def test_superior_binding_contract_security_constraints_are_present():
    _assert_contains_all(_contract_text(), SECURITY_CONSTRAINTS, "security constraint")


def test_superior_binding_contract_future_sequence_is_present():
    _assert_contains_all(_contract_text(), FUTURE_SEQUENCE, "future sequence item")


def test_superior_binding_contract_final_verdict_blocks_operational_use():
    _assert_contains_all(_contract_text(), FINAL_VERDICT_MARKERS, "final verdict marker")


def test_superior_binding_guard_file_is_static_only():
    test_text = THIS_FILE.read_text(encoding="utf-8")
    for index, parts in enumerate(FORBIDDEN_SELF_MARKER_PARTS):
        marker = "".join(parts)
        assert marker not in test_text, f"guard contains forbidden self marker at index {index}"
