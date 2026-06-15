from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.memory_retrieval import (
    MemorySuperiorBindingRequest,
    build_memory_superior_binding_preview,
)
from backend.app.memory_retrieval.superior_binding import FORBIDDEN_INTENTS


OPERATIONAL_NEXT_STEPS = frozenset(
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

ALLOWED_NEXT_STEPS = frozenset(
    {
        "VIEW_ONLY",
        "ASK_HUMAN_CONFIRMATION",
        "NO_ACTION",
    }
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
    ("plan", "ner"),
    ("sequence", "_plan", "ner"),
    ("plan", "ner_smf"),
    ("sql", "alchemy"),
    ("psy", "copg"),
)


def _front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_SUPERIOR_EVAL",
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


def _memory_root(
    tmp_path: Path,
    *,
    confidence: str = "CERTO",
    allowed_for_retrieval: str = "true",
    sensitive: str = "false",
    memory_id: str = "MEMORY_SUPERIOR_EVAL",
) -> Path:
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(
            memory_id=memory_id,
            confidence=confidence,
            allowed_for_retrieval=allowed_for_retrieval,
            sensitive=sensitive,
        ),
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


def test_eval_superior_binding_end_to_end_domain_view_only(tmp_path):
    response = build_memory_superior_binding_preview(_request(_memory_root(tmp_path)))

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.allowed_next_step == "VIEW_ONLY"

    item = response.context_pack.items[0]
    assert item.confidence == "CERTO"
    assert item.authority == "governed_memory"
    assert item.section == "FATTO"
    assert "caller='runtime_preview'" in response.audit_reason
    assert "intent='domain_memory_preview'" in response.audit_reason
    assert "dry_run=True" in response.audit_reason
    assert "allowed_next_step=VIEW_ONLY" in response.audit_reason
    assert "selected_count=1" in response.audit_reason


def test_eval_superior_binding_end_to_end_no_match_no_action(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), query="NO_MATCH")
    )

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.allowed_next_step == "NO_ACTION"


def test_eval_article_da_verificare_requires_human_confirmation(tmp_path):
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


def test_eval_article_inferito_requires_human_confirmation(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(
            _memory_root(tmp_path, confidence="INFERITO"),
            intent="article_memory_preview",
        )
    )

    assert response.context_pack is not None
    assert response.context_pack.items[0].confidence == "INFERITO"
    assert response.allowed_next_step == "ASK_HUMAN_CONFIRMATION"


def test_eval_article_certo_remains_view_only(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path, confidence="CERTO"), intent="article_memory_preview")
    )

    assert response.context_pack is not None
    assert response.context_pack.items[0].confidence == "CERTO"
    assert response.allowed_next_step == "VIEW_ONLY"


def test_eval_rule_preview_certo_remains_view_only(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path, confidence="CERTO"), intent="rule_memory_preview")
    )

    assert response.context_pack is not None
    assert response.context_pack.items[0].confidence == "CERTO"
    assert response.allowed_next_step == "VIEW_ONLY"


def test_eval_sensitive_memory_is_excluded_and_no_action(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path, sensitive="true", allowed_for_retrieval="true"))
    )

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.allowed_next_step == "NO_ACTION"


def test_eval_not_allowed_memory_is_excluded_and_no_action(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path, allowed_for_retrieval="false", sensitive="false"))
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.allowed_next_step == "NO_ACTION"


def test_eval_ranking_confidence_survives_superior_binding(tmp_path):
    memory_root = tmp_path / "memory"
    for confidence in ("INFERITO", "DA_VERIFICARE", "CERTO"):
        _write_memory_file(
            memory_root,
            f"domain/{confidence.lower()}.md",
            _front_matter(memory_id=f"MEMORY_{confidence}", confidence=confidence),
            "## FATTO\nZAW2 common evidence.",
        )

    response = build_memory_superior_binding_preview(_request(memory_root))

    assert response.context_pack is not None
    assert [item.confidence for item in response.context_pack.items] == [
        "CERTO",
        "DA_VERIFICARE",
        "INFERITO",
    ]
    assert response.allowed_next_step == "VIEW_ONLY"


def test_eval_article_mixed_confidence_requires_human_confirmation(tmp_path):
    memory_root = tmp_path / "memory"
    for confidence in ("CERTO", "DA_VERIFICARE"):
        _write_memory_file(
            memory_root,
            f"articles/{confidence.lower()}.md",
            _front_matter(memory_id=f"MEMORY_ARTICLE_{confidence}", confidence=confidence),
            "## FATTO\nZAW2 article evidence.",
        )

    response = build_memory_superior_binding_preview(
        _request(memory_root, intent="article_memory_preview")
    )

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 2
    assert response.allowed_next_step == "ASK_HUMAN_CONFIRMATION"
    assert [item.confidence for item in response.context_pack.items] == [
        "CERTO",
        "DA_VERIFICARE",
    ]


def test_eval_max_items_truncates_before_superior_response(tmp_path):
    memory_root = tmp_path / "memory"
    for index in range(3):
        _write_memory_file(
            memory_root,
            f"domain/item_{index}.md",
            _front_matter(memory_id=f"MEMORY_ITEM_{index}"),
            "## FATTO\nZAW2 evidence.",
        )

    response = build_memory_superior_binding_preview(_request(memory_root, max_items=2))

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 2
    assert response.context_pack.total_candidates == 3
    assert response.context_pack.truncated is True
    assert response.allowed_next_step == "VIEW_ONLY"


@pytest.mark.parametrize("caller", ("tl" + "_chat_preview", "atlas_preview"))
def test_eval_reserved_callers_stay_blocked_end_to_end(tmp_path, caller):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), caller=caller)
    )

    assert response.ok is False
    assert response.blocked is True
    assert response.block_reason == "reserved_caller_not_enabled"
    assert response.allowed_next_step == "NO_ACTION"
    assert response.context_pack is None


@pytest.mark.parametrize("intent", sorted(FORBIDDEN_INTENTS))
def test_eval_forbidden_intents_stay_blocked_end_to_end(tmp_path, intent):
    response = build_memory_superior_binding_preview(
        _request(_memory_root(tmp_path), intent=intent)
    )

    assert response.ok is False
    assert response.blocked is True
    assert response.block_reason == "forbidden_intent"
    assert response.allowed_next_step == "NO_ACTION"


def test_eval_runtime_preview_block_propagates_to_superior(tmp_path):
    response = build_memory_superior_binding_preview(
        _request(tmp_path / "missing" / "memory")
    )

    assert response.ok is False
    assert response.blocked is True
    assert response.block_reason is not None
    assert response.block_reason.startswith("runtime_preview_blocked:")
    assert response.allowed_next_step == "NO_ACTION"


def test_eval_never_emits_operational_next_steps(tmp_path):
    responses = (
        build_memory_superior_binding_preview(_request(_memory_root(tmp_path))),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path), query="NO_MATCH")
        ),
        build_memory_superior_binding_preview(
            _request(
                _memory_root(tmp_path, confidence="DA_VERIFICARE"),
                intent="article_memory_preview",
            )
        ),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path), caller="tl" + "_chat_preview")
        ),
        build_memory_superior_binding_preview(
            _request(_memory_root(tmp_path), intent=next(iter(FORBIDDEN_INTENTS)))
        ),
    )

    for response in responses:
        assert response.allowed_next_step not in OPERATIONAL_NEXT_STEPS
        assert response.allowed_next_step in ALLOWED_NEXT_STEPS


def test_eval_file_itself_remains_static_safe():
    test_text = Path(__file__).read_text(encoding="utf-8")
    for index, parts in enumerate(FORBIDDEN_SELF_MARKER_PARTS):
        marker = "".join(parts)
        assert marker not in test_text, f"eval file contains forbidden marker at index {index}"
