from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from backend.app.services.context_source_reader_adapter import (
    ContextSourceReaderAdapterError,
    read_context_source_index,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_INDEX = REPO_ROOT / "memory" / "context_source_index.json"


def _write_index(path: Path, **overrides) -> Path:
    data = {
        "schema": "PROMETEO_CONTEXT_SOURCE_INDEX_001",
        "status": "documental_index_only",
        "runtime_enabled": False,
        "sources": [
            {
                "id": "system_map",
                "path": "docs/PROMETEO_SYSTEM_MAP.md",
                "kind": "document",
                "tier": "B",
                "authority": "high",
                "role": "System orientation.",
                "access_mode": "read_only",
                "runtime_enabled": False,
                "allowed_for": ["architecture_context", "tl_chat_context_policy"],
                "exists": True,
                "bytes": 123,
            },
            {
                "id": "memory_policy",
                "path": "memory/retrieval/retrieval_policy.md",
                "kind": "memory_file",
                "tier": "B",
                "authority": "high",
                "role": "Retrieval policy.",
                "access_mode": "read_only",
                "runtime_enabled": False,
                "allowed_for": ["future_governed_retrieval"],
                "exists": True,
                "bytes": 456,
            },
        ],
    }
    data.update(overrides)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_reads_real_context_source_index_as_metadata_only():
    result = read_context_source_index(REAL_INDEX, max_sources=3)

    assert result["ok"] is True
    assert result["schema"] == "PROMETEO_CONTEXT_SOURCE_INDEX_001"
    assert result["status"] == "documental_index_only"
    assert result["runtime_enabled"] is False
    assert 0 < len(result["sources"]) <= 3
    assert all(source["access_mode"] == "read_only" for source in result["sources"])
    assert all(source["runtime_enabled"] is False for source in result["sources"])
    assert all("text" not in source for source in result["sources"])
    assert all("content" not in source for source in result["sources"])


def test_missing_index_is_blocked(tmp_path):
    result = read_context_source_index(tmp_path / "missing.json")

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "INDEX_MISSING"


def test_malformed_json_is_blocked(tmp_path):
    path = tmp_path / "index.json"
    path.write_text("{bad", encoding="utf-8")

    result = read_context_source_index(path)

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "JSON_MALFORMED"


def test_invalid_schema_is_blocked(tmp_path):
    path = _write_index(tmp_path / "index.json", schema="WRONG")

    result = read_context_source_index(path)

    assert result["ok"] is False
    assert any(error["code"] == "SCHEMA_INVALID" for error in result["errors"])


def test_invalid_status_is_blocked(tmp_path):
    path = _write_index(tmp_path / "index.json", status="runtime_ready")

    result = read_context_source_index(path)

    assert result["ok"] is False
    assert any(error["code"] == "STATUS_INVALID" for error in result["errors"])


def test_global_runtime_enabled_true_is_blocked(tmp_path):
    path = _write_index(tmp_path / "index.json", runtime_enabled=True)

    result = read_context_source_index(path)

    assert result["ok"] is False
    assert any(error["code"] == "GLOBAL_RUNTIME_ENABLED" for error in result["errors"])


def test_source_runtime_enabled_true_is_rejected(tmp_path):
    path = _write_index(
        tmp_path / "index.json",
        sources=[
            {
                "id": "bad",
                "path": "docs/BAD.md",
                "access_mode": "read_only",
                "runtime_enabled": True,
                "allowed_for": ["future_governed_retrieval"],
            }
        ],
    )

    result = read_context_source_index(path)

    assert result["ok"] is True
    assert result["sources"] == []
    assert result["rejected"][0]["reason"] == "SOURCE_RUNTIME_ENABLED"


def test_source_access_mode_not_read_only_is_rejected(tmp_path):
    path = _write_index(
        tmp_path / "index.json",
        sources=[
            {
                "id": "bad",
                "path": "docs/BAD.md",
                "access_mode": "write",
                "runtime_enabled": False,
                "allowed_for": ["future_governed_retrieval"],
            }
        ],
    )

    result = read_context_source_index(path)

    assert result["ok"] is True
    assert result["sources"] == []
    assert result["rejected"][0]["reason"] == "ACCESS_MODE_NOT_READ_ONLY"


def test_allowed_for_filter_selects_only_matching_sources(tmp_path):
    path = _write_index(tmp_path / "index.json")

    result = read_context_source_index(path, allowed_for="future_governed_retrieval")

    assert result["ok"] is True
    assert [source["id"] for source in result["sources"]] == ["memory_policy"]
    assert any(item["reason"] == "ALLOWED_FOR_FILTERED_OUT" for item in result["rejected"])


def test_source_ids_filter_selects_only_requested_sources(tmp_path):
    path = _write_index(tmp_path / "index.json")

    result = read_context_source_index(path, source_ids=["system_map"])

    assert result["ok"] is True
    assert [source["id"] for source in result["sources"]] == ["system_map"]


def test_unknown_source_id_is_reported(tmp_path):
    path = _write_index(tmp_path / "index.json")

    result = read_context_source_index(path, source_ids=["missing"])

    assert result["ok"] is True
    assert result["sources"] == []
    assert {"id": "missing", "reason": "SOURCE_ID_NOT_FOUND"} in result["rejected"]


@pytest.mark.parametrize(
    "blocked_path",
    [
        "../secret.md",
        "/tmp/secret.md",
        ".env",
        "backend/app/main.py",
        "frontend/src/App.tsx",
        "runtime/state.json",
        "planner/plan.json",
        "database/dump.sql",
        "data/local_smf/SMF.xlsx",
        "specs_finitura/12066/image.png",
    ],
)
def test_blocked_paths_are_rejected(tmp_path, blocked_path):
    path = _write_index(
        tmp_path / "index.json",
        sources=[
            {
                "id": "blocked",
                "path": blocked_path,
                "access_mode": "read_only",
                "runtime_enabled": False,
                "allowed_for": ["future_governed_retrieval"],
            }
        ],
    )

    result = read_context_source_index(path)

    assert result["ok"] is True
    assert result["sources"] == []
    assert result["rejected"][0]["reason"] == "SOURCE_PATH_BLOCKED"


def test_include_bytes_is_opt_in(tmp_path):
    path = _write_index(tmp_path / "index.json")

    without_bytes = read_context_source_index(path, source_ids=["system_map"])
    with_bytes = read_context_source_index(path, source_ids=["system_map"], include_bytes=True)

    assert "bytes" not in without_bytes["sources"][0]
    assert with_bytes["sources"][0]["bytes"] == 123


def test_max_sources_limits_selected_sources(tmp_path):
    path = _write_index(tmp_path / "index.json")

    result = read_context_source_index(path, max_sources=1)

    assert len(result["sources"]) == 1


def test_negative_max_sources_is_invalid(tmp_path):
    path = _write_index(tmp_path / "index.json")

    with pytest.raises(ContextSourceReaderAdapterError):
        read_context_source_index(path, max_sources=-1)


def test_adapter_does_not_import_runtime_modules(tmp_path):
    path = _write_index(tmp_path / "index.json")
    forbidden_modules = (
        "backend.app.api.tl_chat",
        "backend.app.atlas_engine.governed_retrieval",
        "backend.app.services.sequence_planner",
        "backend.app.services.planner_smf",
        "backend.app.main",
    )
    for module in forbidden_modules:
        sys.modules.pop(module, None)

    result = read_context_source_index(path)

    assert result["ok"] is True
    for module in forbidden_modules:
        assert module not in sys.modules
