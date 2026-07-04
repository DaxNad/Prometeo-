from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.context_source_reader_adapter import (
    ContextSourceReaderAdapter,
    ContextSourceReaderError,
)


def _write_runtime_index(repo_root: Path, source_text: str = "abcdef") -> Path:
    source = repo_root / "docs" / "tl_context_policy.md"
    source.parent.mkdir(parents=True)
    source.write_text(source_text, encoding="utf-8")

    index = repo_root / "memory" / "context_source_index.json"
    index.parent.mkdir(parents=True)
    index.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "tl_context_policy",
                        "path": "docs/tl_context_policy.md",
                        "source_type": "doc_fixture",
                        "access_mode": "read_only",
                        "runtime_enabled": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return index


def test_runtime_adapter_missing_index_keeps_existing_error_code(tmp_path):
    with pytest.raises(ContextSourceReaderError) as exc_info:
        ContextSourceReaderAdapter(
            index_path=tmp_path / "memory" / "missing.json",
            repo_root=tmp_path,
        )

    assert exc_info.value.code == "INDEX_NOT_FOUND"


def test_runtime_adapter_malformed_index_json_is_index_invalid(tmp_path):
    index = tmp_path / "memory" / "context_source_index.json"
    index.parent.mkdir(parents=True)
    index.write_text("{bad", encoding="utf-8")

    with pytest.raises(ContextSourceReaderError) as exc_info:
        ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)

    assert exc_info.value.code == "INDEX_INVALID"
    assert str(tmp_path) not in str(exc_info.value)
    assert "line" not in str(exc_info.value).lower()


def test_runtime_adapter_unreadable_index_is_index_not_found(monkeypatch, tmp_path):
    index = _write_runtime_index(tmp_path)
    original_open = Path.open

    def unreadable_open(self, *args, **kwargs):
        if self == index:
            raise PermissionError("permission denied detail")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", unreadable_open)

    with pytest.raises(ContextSourceReaderError) as exc_info:
        ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)

    assert exc_info.value.code == "INDEX_NOT_FOUND"
    assert "permission denied detail" not in str(exc_info.value)


def test_runtime_adapter_unreadable_source_excerpt_is_source_file_not_found(monkeypatch, tmp_path):
    index = _write_runtime_index(tmp_path)
    source = tmp_path / "docs" / "tl_context_policy.md"
    adapter = ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)
    original_read_text = Path.read_text

    def unreadable_read_text(self, *args, **kwargs):
        if self == source:
            raise PermissionError("source not readable")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable_read_text)

    with pytest.raises(ContextSourceReaderError) as exc_info:
        adapter.read_excerpt("tl_context_policy")

    assert exc_info.value.code == "SOURCE_FILE_NOT_FOUND"
    assert "source not readable" not in str(exc_info.value)


def test_runtime_adapter_unreadable_source_metadata_is_source_file_not_found(monkeypatch, tmp_path):
    index = _write_runtime_index(tmp_path)
    source = tmp_path / "docs" / "tl_context_policy.md"
    adapter = ContextSourceReaderAdapter(index_path=index, repo_root=tmp_path)
    original_exists = Path.exists

    def unreadable_exists(self):
        if self == source:
            raise OSError("metadata unavailable")
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", unreadable_exists)

    with pytest.raises(ContextSourceReaderError) as exc_info:
        adapter.read_metadata("tl_context_policy")

    assert exc_info.value.code == "SOURCE_FILE_NOT_FOUND"
    assert "metadata unavailable" not in str(exc_info.value)


def test_runtime_adapter_valid_excerpt_preserves_max_chars_and_metadata(tmp_path):
    index = _write_runtime_index(tmp_path, source_text="abcdef")
    adapter = ContextSourceReaderAdapter(
        index_path=index,
        repo_root=tmp_path,
        max_chars=3,
    )

    result = adapter.read_excerpt("tl_context_policy")

    assert result.status == "CONTENT_LIMIT_APPLIED"
    assert result.content == "abc"
    assert result.metadata["access_mode"] == "read_only"
    assert result.metadata["runtime_enabled"] is False
    assert result.metadata["relative_path"] == "docs/tl_context_policy.md"
