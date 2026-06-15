from __future__ import annotations

import sys
from pathlib import Path

from backend.app.memory_retrieval import (
    MemoryRetrievalRuntimeRequest,
    MemoryRetrievalRuntimeResponse,
    build_memory_retrieval_preview,
)
from backend.app.memory_retrieval.binding import EvidenceItem
from backend.app.memory_retrieval.context_pack import ContextPack, ContextPackItem
from backend.app.memory_retrieval import runtime_preview


def _write_memory_file(root: Path, relative: str, front_matter: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter.strip()}\n---\n{body}", encoding="utf-8")
    return path


def _front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_RUNTIME_PREVIEW_TEST",
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


def _request(memory_root: Path, **overrides) -> MemoryRetrievalRuntimeRequest:
    fields = {
        "query": "ZAW2",
        "intent": "memory_preview",
        "caller": "test_runtime_preview",
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
        _front_matter(),
        "## FATTO\nZAW1 e ZAW2 non sono intercambiabili.",
    )
    return memory_root


def _blocked(response: MemoryRetrievalRuntimeResponse) -> bool:
    return response.blocked is True and response.ok is False and response.context_pack is None


def test_blocks_dry_run_false(tmp_path):
    response = build_memory_retrieval_preview(_request(tmp_path / "memory", dry_run=False))

    assert _blocked(response)
    assert response.block_reason == "dry_run must be true for preview-only runtime."


def test_blocks_empty_query(tmp_path):
    response = build_memory_retrieval_preview(_request(tmp_path / "memory", query="  "))

    assert _blocked(response)
    assert response.block_reason == "query is empty or not classified."


def test_blocks_empty_intent(tmp_path):
    response = build_memory_retrieval_preview(_request(tmp_path / "memory", intent="  "))

    assert _blocked(response)
    assert response.block_reason == "intent is empty or not classified."


def test_blocks_empty_caller(tmp_path):
    response = build_memory_retrieval_preview(_request(tmp_path / "memory", caller="  "))

    assert _blocked(response)
    assert response.block_reason == "caller is empty or not declared."


def test_blocks_missing_memory_root(tmp_path):
    response = build_memory_retrieval_preview(_request(tmp_path / "memory"))

    assert _blocked(response)
    assert response.block_reason == "memory_root does not exist."


def test_blocks_memory_root_that_is_not_directory(tmp_path):
    memory_file = tmp_path / "memory"
    memory_file.write_text("not a directory", encoding="utf-8")

    response = build_memory_retrieval_preview(_request(memory_file))

    assert _blocked(response)
    assert response.block_reason == "memory_root is not a directory."


def test_blocks_directory_not_named_memory(tmp_path):
    other_root = tmp_path / "not_memory"
    other_root.mkdir()

    response = build_memory_retrieval_preview(_request(other_root))

    assert _blocked(response)
    assert response.block_reason == "memory_root must point to an authorized memory directory."


def test_returns_ok_with_valid_memory_root_and_markdown(tmp_path):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root))

    assert response.ok is True
    assert response.blocked is False
    assert response.block_reason is None
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 1
    assert response.context_pack.items[0].source_id == "MEMORY_RUNTIME_PREVIEW_TEST"
    assert "caller='test_runtime_preview'" in response.audit_reason
    assert "intent='memory_preview'" in response.audit_reason
    assert "dry_run=True" in response.audit_reason
    assert "query='ZAW2'" in response.audit_reason
    assert "selected_count=1" in response.audit_reason


def test_query_filter_no_match_returns_empty_context_pack_ok(tmp_path):
    memory_root = _valid_memory_root(tmp_path)

    response = build_memory_retrieval_preview(_request(memory_root, query="NO_MATCH"))

    assert response.ok is True
    assert response.blocked is False
    assert response.context_pack is not None
    assert response.context_pack.selected_count == 0
    assert response.context_pack.total_candidates == 0


def test_respects_max_items(tmp_path):
    memory_root = tmp_path / "memory"
    for index in range(3):
        _write_memory_file(
            memory_root,
            f"domain/item_{index}.md",
            _front_matter(memory_id=f"MEMORY_RUNTIME_{index}"),
            "## FATTO\nZAW2 evidence.",
        )

    response = build_memory_retrieval_preview(_request(memory_root, max_items=2))

    assert response.context_pack is not None
    assert response.context_pack.selected_count == 2
    assert response.context_pack.truncated is True


def test_respects_max_chars_per_item(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(),
        "## FATTO\nZAW2 abcdef",
    )

    response = build_memory_retrieval_preview(_request(memory_root, max_chars_per_item=4))

    assert response.context_pack is not None
    assert response.context_pack.items[0].text == "ZAW2..."


def test_blocks_context_pack_source_path_outside_memory(tmp_path, monkeypatch):
    memory_root = _valid_memory_root(tmp_path)
    item = ContextPackItem(
        source_id="BAD",
        source_path="outside/invariants.md",
        source_type="domain_invariant",
        authority="governed_memory",
        confidence="CERTO",
        section="FATTO",
        text="ZAW2",
        reason="test",
        rank_reason="test",
    )
    monkeypatch.setattr(runtime_preview, "collect_memory_evidence", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        runtime_preview,
        "build_context_pack",
        lambda *_args, **_kwargs: ContextPack(
            query="ZAW2",
            items=[item],
            total_candidates=1,
            selected_count=1,
            truncated=False,
            build_reason="test",
        ),
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert _blocked(response)
    assert response.block_reason == "context_pack contains source_path outside memory/."


def test_blocks_context_pack_item_missing_authority(tmp_path, monkeypatch):
    memory_root = _valid_memory_root(tmp_path)
    item = ContextPackItem(
        source_id="NO_AUTHORITY",
        source_path="memory/domain/invariants.md",
        source_type="domain_invariant",
        authority=" ",
        confidence="CERTO",
        section="FATTO",
        text="ZAW2",
        reason="test",
        rank_reason="test",
    )
    monkeypatch.setattr(runtime_preview, "collect_memory_evidence", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        runtime_preview,
        "build_context_pack",
        lambda *_args, **_kwargs: ContextPack(
            query="ZAW2",
            items=[item],
            total_candidates=1,
            selected_count=1,
            truncated=False,
            build_reason="test",
        ),
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert _blocked(response)
    assert response.block_reason == "context_pack contains item with missing authority."


def test_blocks_context_pack_item_missing_confidence(tmp_path, monkeypatch):
    memory_root = _valid_memory_root(tmp_path)
    item = ContextPackItem(
        source_id="NO_CONFIDENCE",
        source_path="memory/domain/invariants.md",
        source_type="domain_invariant",
        authority="governed_memory",
        confidence=" ",
        section="FATTO",
        text="ZAW2",
        reason="test",
        rank_reason="test",
    )
    monkeypatch.setattr(runtime_preview, "collect_memory_evidence", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        runtime_preview,
        "build_context_pack",
        lambda *_args, **_kwargs: ContextPack(
            query="ZAW2",
            items=[item],
            total_candidates=1,
            selected_count=1,
            truncated=False,
            build_reason="test",
        ),
    )

    response = build_memory_retrieval_preview(_request(memory_root))

    assert _blocked(response)
    assert response.block_reason == "context_pack contains item with missing confidence."


def test_does_not_import_forbidden_runtime_modules(tmp_path):
    forbidden_modules = (
        "backend.app.api.tl_chat",
        "backend.app.atlas_engine.governed_retrieval",
        "backend.app.services.sequence_planner",
        "backend.app.services.planner_smf",
    )
    for module in forbidden_modules:
        sys.modules.pop(module, None)

    build_memory_retrieval_preview(_request(_valid_memory_root(tmp_path)))

    for module in forbidden_modules:
        assert module not in sys.modules


def test_no_side_effects_outside_tmp_path(tmp_path):
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    build_memory_retrieval_preview(_request(_valid_memory_root(tmp_path)))

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert after == sorted(
        before
        + [
            "memory",
            "memory/domain",
            "memory/domain/invariants.md",
        ]
    )


def test_exports_runtime_preview_api():
    from backend.app.memory_retrieval import (  # noqa: PLC0415
        MemoryRetrievalRuntimeRequest as ExportedRequest,
        MemoryRetrievalRuntimeResponse as ExportedResponse,
        build_memory_retrieval_preview as exported_builder,
    )

    assert ExportedRequest is MemoryRetrievalRuntimeRequest
    assert ExportedResponse is MemoryRetrievalRuntimeResponse
    assert exported_builder is build_memory_retrieval_preview
