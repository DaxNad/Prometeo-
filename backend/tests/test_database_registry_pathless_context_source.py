from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.services.context_source_reader_adapter import read_context_source_index
from tools.context_source_reader_adapter import (
    ContextSourceReaderAdapter,
    ContextSourceReaderError,
)


def _write_index(root: Path, source: dict) -> Path:
    index = root / "memory" / "context_source_index.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        json.dumps(
            {
                "schema": "PROMETEO_CONTEXT_SOURCE_INDEX_001",
                "status": "documental_index_only",
                "runtime_enabled": False,
                "sources": [source],
            }
        ),
        encoding="utf-8",
    )
    return index


def _database_registry_source(**overrides) -> dict:
    source = {
        "id": "customer_demand_registry",
        "kind": "database_registry",
        "structural_origin": "customer_demand",
        "access_mode": "read_only",
        "runtime_enabled": False,
        "allowed_for": ["future_governed_retrieval"],
        "exists": True,
    }
    source.update(overrides)
    return source


def test_metadata_reader_accepts_database_registry_without_path(tmp_path):
    index = _write_index(tmp_path, _database_registry_source())

    result = read_context_source_index(index)

    assert result["ok"] is True
    assert result["rejected"] == []
    source = result["sources"][0]
    assert source["id"] == "customer_demand_registry"
    assert source["kind"] == "database_registry"
    assert source["locator_mode"] == "logical_registry"
    assert source["structural_origin"] == "customer_demand"
    assert source["path"].startswith("memory/logical_registry/")
    assert source["runtime_enabled"] is False


def test_metadata_reader_rejects_path_on_database_registry(tmp_path):
    index = _write_index(
        tmp_path,
        _database_registry_source(path="memory/not-a-real-registry-file.json"),
    )

    result = read_context_source_index(index)

    assert result["sources"] == []
    assert result["rejected"] == [
        {
            "id": "customer_demand_registry",
            "reason": "NON_FILE_SOURCE_PATH_FORBIDDEN",
        }
    ]


def test_runtime_adapter_returns_metadata_without_filesystem_access(tmp_path):
    index = _write_index(tmp_path, _database_registry_source())
    adapter = ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)

    result = adapter.read_metadata("customer_demand_registry")

    assert result.status == "METADATA_OK"
    assert result.content is None
    assert result.metadata == {
        "schema": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
        "source_type": "database_registry",
        "kind": "database_registry",
        "access_mode": "read_only",
        "runtime_enabled": False,
        "relative_path": None,
        "locator_mode": "logical_registry",
        "structural_origin": "customer_demand",
        "exists": True,
    }


def test_runtime_adapter_rejects_excerpt_for_database_registry(tmp_path):
    index = _write_index(tmp_path, _database_registry_source())
    adapter = ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)

    with pytest.raises(ContextSourceReaderError) as exc_info:
        adapter.read_excerpt("customer_demand_registry")

    assert exc_info.value.code == "SOURCE_EXCERPT_UNSUPPORTED"
    assert str(tmp_path) not in str(exc_info.value)


def test_runtime_adapter_rejects_runtime_enabled_database_registry(tmp_path):
    index = _write_index(
        tmp_path,
        _database_registry_source(runtime_enabled=True),
    )
    adapter = ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)

    with pytest.raises(ContextSourceReaderError) as exc_info:
        adapter.read_metadata("customer_demand_registry")

    assert exc_info.value.code == "RUNTIME_SOURCE_BLOCKED"


def test_file_backed_source_still_requires_governed_path(tmp_path):
    index = _write_index(
        tmp_path,
        {
            "id": "document_without_path",
            "kind": "document",
            "access_mode": "read_only",
            "runtime_enabled": False,
            "allowed_for": ["future_governed_retrieval"],
        },
    )

    result = read_context_source_index(index)

    assert result["sources"] == []
    assert result["rejected"] == [
        {"id": "document_without_path", "reason": "SOURCE_PATH_INVALID"}
    ]
