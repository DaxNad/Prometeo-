from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.memory_retrieval import (
    MemorySuperiorBindingRequest,
    MemorySuperiorBindingResponse,
    build_memory_superior_binding_preview,
)
from backend.app.memory_retrieval.superior_binding import FORBIDDEN_INTENTS


ROOT = Path(__file__).resolve().parents[2]
SUPERIOR_BINDING = ROOT / "backend" / "app" / "memory_retrieval" / "superior_binding.py"

FORBIDDEN_OPERATIONAL_NEXT_STEPS = frozenset(
    {
        "PLAN_PRODUCTION",
        "CHANGE_ROUTE",
        "UPDATE_METADATA",
        "WRITE_MEMORY",
        "CALL_LLM",
        "CALL_PLANNER",
        "WRITE_SMF",
        "WRITE_DATABASE",
    }
)

FORBIDDEN_SOURCE_MARKER_PARTS = (
    ("Fast", "API"),
    ("API", "Router"),
    ("tl", "_chat"),
    ("governed", "_retrieval"),
    ("plan", "ner"),
    ("sequence", "_planner"),
    ("planner", "_smf"),
    ("sql", "alchemy"),
    ("psy", "copg"),
    ("re", "quests"),
    ("url", "lib"),
    ("sock", "et"),
    ("sub", "process"),
    ("open", "ai"),
    ("anth", "ropic"),
    ("ol", "lama"),
    ("lite", "llm"),
    ("smf", "_update"),
    ("database", " write"),
)


def _front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_SUPERIOR_BINDING_TEST",
        "type": "domain_invariant",
        "status": "active",
        "authority": "governed_memory",
        "confidence": "CERTO",
        "allowed_for_retrieval": "true",
        "sensitive": "false",
        "last_review": "2026-06-15",
    }
    fields.update(overrides)
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def _write_memory_file(root: Path, relative: str, front_matter: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter.strip()}\n---\n{body}", encoding="utf-8")
    return path


def _memory_root(tmp_path: Path, *, confidence: str = "CERTO") -> Path:
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(confidence=confidence),
        "## FATTO\nZAW1 e ZAW2 non sono intercambiabili.",
    )
    return memory_root


def _request(memory_root: Path, **overrides) -> MemorySuperiorBindingRequest:
    fields = {
        "query": "ZAW2",
        "intent": "domain_memory_preview",
        "caller": "runtime_preview",
        "memory_root": memory_root,
        "dry_run": True,
        "max_items": 5,
        "max_chars_per_item": 500,
    }
    fields.update(overrides)
    return MemorySuperiorBindingRequest(**fields)


def _blocked(response: MemorySuperiorBindingResponse, reason: str) -> None:
    assert response.ok is False
    assert response.blocked is True
    assert response.block_reason == reason
    assert response.allowed_next_step == "NO_ACTION"


def test_happy_path_domain_preview(tmp_path):
    response = build_memory_superior_binding_preview(_request(_memory_root(tmp_path)))

    assert response.ok is True
    assert response.blocked is False
    assert response.block_reason is None
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.allowed_next_step == "VIEW_ONLY"


def test_no_match_returns_no_action(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), query="NO_MATCH")
    )

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.allowed_next_step == "NO_ACTION"


def test_article_preview_with_da_verificare_requires_human_confirmation(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(
            _memory_root(tmp_path, confidence="DA_VERIFICARE"),
            intent="article_memory_preview",
        )
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.context_pack.items[0].confidence == "DA_VERIFICARE"
    assert response.allowed_next_step == "ASK_HUMAN_CONFIRMATION"


def test_article_preview_with_inferito_requires_human_confirmation(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(
            _memory_root(tmp_path, confidence="INFERITO"),
            intent="article_memory_preview",
        )
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.context_pack.items[0].confidence == "INFERITO"
    assert response.allowed_next_step == "ASK_HUMAN_CONFIRMATION"


def test_article_preview_with_certo_stays_view_only(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path, confidence="CERTO"), intent="article_memory_preview")
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.context_pack.items[0].confidence == "CERTO"
    assert response.allowed_next_step == "VIEW_ONLY"


def test_rule_preview_with_certo_stays_view_only(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), intent="rule_memory_preview")
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.allowed_next_step == "VIEW_ONLY"


@pytest.mark.parametrize("caller", ("tl" + "_chat_preview", "atlas_preview"))
def test_reserved_callers_are_blocked(tmp_path, caller):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), caller=caller)
    )

    _blocked(response, "reserved_caller_not_enabled")


def test_unauthorized_caller_blocked(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), caller="unknown_preview")
    )

    _blocked(response, "unauthorized_caller")


@pytest.mark.parametrize("intent", sorted(FORBIDDEN_INTENTS))
def test_forbidden_intents_blocked(tmp_path, intent):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), intent=intent)
    )

    _blocked(response, "forbidden_intent")


def test_unauthorized_intent_blocked(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), intent="not_enabled_preview")
    )

    _blocked(response, "unauthorized_intent")


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("caller", "missing_caller"),
        ("intent", "missing_intent"),
        ("query", "missing_query"),
    ),
)
def test_missing_caller_intent_or_query_blocked(tmp_path, field, reason):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), **{field: "  "})
    )

    _blocked(response, reason)


def test_dry_run_false_blocked(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), dry_run=False)
    )

    _blocked(response, "dry_run_required")


def test_invalid_memory_root_name_blocked(tmp_path):
    not_memory = tmp_path / "not_memory"
    not_memory.mkdir()

    response = build_memory_superior_binding_preview(_request(not_memory))

    _blocked(response, "invalid_memory_root")


def test_runtime_preview_blocked_propagates(tmp_path):
    missing_memory_root = tmp_path / "missing" / "memory"

    response = build_memory_superior_binding_preview(_request(missing_memory_root))

    assert response.ok is False
    assert response.blocked is True
    assert response.block_reason is not None
    assert response.block_reason.startswith("runtime_preview_blocked:")
    assert response.allowed_next_step == "NO_ACTION"


def test_audit_reason_includes_control_fields(tmp_path):
    response = build_memory_superior_binding_preview(_request(_memory_root(tmp_path)))

    assert "caller='runtime_preview'" in response.audit_reason
    assert "intent='domain_memory_preview'" in response.audit_reason
    assert "dry_run=True" in response.audit_reason
    assert "allowed_next_step=VIEW_ONLY" in response.audit_reason
    assert "selected_count=1" in response.audit_reason


def test_response_never_emits_operational_next_steps(tmp_path):
    responses = (
        build_memory_superior_binding_preview(_request(_memory_root(tmp_path))),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path), query="NO_MATCH")
        ),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path, confidence="INFERITO"), intent="article_memory_preview")
        ),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path), caller="unknown_preview")
        ),
    )

    for response in responses:
        assert response.allowed_next_step not in FORBIDDEN_OPERATIONAL_NEXT_STEPS
        assert response.allowed_next_step in {
            "VIEW_ONLY",
            "ASK_HUMAN_CONFIRMATION",
            "NO_ACTION",
        }


def test_module_does_not_import_forbidden_runtime_integrations():
    source = SUPERIOR_BINDING.read_text(encoding="utf-8")
    for index, parts in enumerate(FORBIDDEN_SOURCE_MARKER_PARTS):
        marker = "".join(parts)
        assert marker not in source, f"forbidden source marker at index {index}"


def test_exports_superior_binding_api():
    from backend.app.memory_retrieval import (  # noqa: PLC0415
        MemorySuperiorBindingRequest as ExportedRequest,
        MemorySuperiorBindingResponse as ExportedResponse,
        build_memory_superior_binding_preview as exported_builder,
    )

    assert ExportedRequest is MemorySuperiorBindingRequest
    assert ExportedResponse is MemorySuperiorBindingResponse
    assert exported_builder is build_memory_superior_binding_preview
