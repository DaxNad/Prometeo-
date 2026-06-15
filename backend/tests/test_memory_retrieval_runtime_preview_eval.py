from __future__ import annotations

import sys
from pathlib import Path

import pytest

from backend.app.memory_retrieval import (
    MemoryRetrievalRuntimeRequest,
    build_memory_retrieval_preview,
)


FORBIDDEN_RUNTIME_MODULES = (
    "backend.app.api.tl_chat",
    "backend.app.atlas_engine.governed_retrieval",
    "backend.app.services.sequence_planner",
    "backend.app.services.planner_smf",
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
)


def _front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_RUNTIME_EVAL",
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


def _request(memory_root: Path, **overrides) -> MemoryRetrievalRuntimeRequest:
    fields = {
        "query": "ZAW2",
        "intent": "runtime_preview_eval",
        "caller": "test_eval",
        "memory_root": memory_root,
        "max_items": 5,
        "max_chars_per_item": 500,
        "dry_run": True,
    }
    fields.update(overrides)
    return MemoryRetrievalRuntimeRequest(**fields)


def _valid_memory_root(tmp_path: Path) -> Path:
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(memory_id="MEMORY_DOMAIN_INVARIANTS"),
        "## FATTO\nZAW1 e ZAW2 non sono intercambiabili.",
    )
    return memory_root


def test_preview_eval_happy_path_end_to_end(tmp_path):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.ok is True
    assert response.blocked is False
    assert response.block_reason is None
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1

    item = response.context_pack.items[0]
    assert item.source_id == "MEMORY_DOMAIN_INVARIANTS"
    assert item.source_path.startswith("memory/")
    assert item.authority == "governed_memory"
    assert item.confidence == "CERTO"
    assert item.section == "FATTO"
    assert "caller='test_eval'" in response.audit_reason
    assert "intent='runtime_preview_eval'" in response.audit_reason
    assert "dry_run=True" in response.audit_reason
    assert "selected_count=1" in response.audit_reason


def test_preview_eval_query_no_match_returns_empty_context_pack(tmp_path):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root, query="NO_MATCH"))

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.context_pack.total_candidates == 0


def test_preview_eval_ranks_confidence_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    for confidence in ("INFERITO", "DA_VERIFICARE", "CERTO"):
        _write_memory_file(
            memory_root,
            f"domain/{confidence.lower()}.md",
            _front_matter(memory_id=f"MEMORY_{confidence}", confidence=confidence),
            "## FATTO\nZAW2 common evidence.",
        )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.context_pack is not None
    assert [item.confidence for item in response.context_pack.items] == [
        "CERTO",
        "DA_VERIFICARE",
        "INFERITO",
    ]


def test_preview_eval_ranks_sections_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/sections.md",
        _front_matter(memory_id="MEMORY_SECTIONS", confidence="CERTO"),
        (
            "## DA_VERIFICARE\nZAW2 da verificare.\n"
            "## INFERENZA\nZAW2 inferenza.\n"
            "## FATTO\nZAW2 fatto."
        ),
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.context_pack is not None
    assert [item.section for item in response.context_pack.items] == [
        "FATTO",
        "INFERENZA",
        "DA_VERIFICARE",
    ]


def test_preview_eval_respects_max_items_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    for index in range(3):
        _write_memory_file(
            memory_root,
            f"domain/item_{index}.md",
            _front_matter(memory_id=f"MEMORY_ITEM_{index}"),
            "## FATTO\nZAW2 evidence.",
        )

    response = build_memory_retrieval_preview(_request(memory_root, max_items=2))

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 2
    assert response.context_pack.truncated is True
    assert response.context_pack.total_candidates == 3


def test_preview_eval_respects_max_chars_per_item_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/long.md",
        _front_matter(),
        "## FATTO\nZAW2 abcdefghijklmnop",
    )

    response = build_memory_retrieval_preview(_request(memory_root, max_chars_per_item=6))

    assert response.context_pack is not None
    assert response.context_pack.items[0].text == "ZAW2 a..."


def test_preview_eval_excludes_sensitive_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/sensitive.md",
        _front_matter(sensitive="true", allowed_for_retrieval="true"),
        "## FATTO\nZAW2 sensitive evidence.",
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.ok is True
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0


def test_preview_eval_excludes_not_allowed_end_to_end(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/not_allowed.md",
        _front_matter(allowed_for_retrieval="false", sensitive="false"),
        "## FATTO\nZAW2 not allowed evidence.",
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.ok is True
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0


def test_preview_eval_blocks_invalid_memory_root_name(tmp_path):
    not_memory = tmp_path / "not_memory"
    not_memory.mkdir()

    response = build_memory_retrieval_preview(_request(not_memory))

    assert response.blocked is True
    assert response.ok is False


def test_preview_eval_blocks_dry_run_false(tmp_path):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root, dry_run=False))

    assert response.blocked is True
    assert response.ok is False


@pytest.mark.parametrize(
    "field",
    ("caller", "intent", "query"),
)
def test_preview_eval_blocks_missing_caller_intent_or_query(tmp_path, field):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root, **{field: "  "}))

    assert response.blocked is True
    assert response.ok is False


def test_preview_eval_does_not_import_forbidden_runtime_modules(tmp_path):
    for module in FORBIDDEN_RUNTIME_MODULES:
        sys.modules.pop(module, None)

    build_memory_retrieval_preview(_request(_valid_memory_root(tmp_path)))

    for module in FORBIDDEN_RUNTIME_MODULES:
        assert module not in sys.modules


def test_preview_eval_file_itself_remains_safe():
    test_text = Path(__file__).read_text(encoding="utf-8")
    for parts in FORBIDDEN_SELF_MARKER_PARTS:
        marker = "".join(parts)
        assert marker not in test_text, f"eval file contains forbidden marker: {marker}"
