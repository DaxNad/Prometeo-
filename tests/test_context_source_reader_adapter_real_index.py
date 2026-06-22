from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.context_source_reader_adapter import (  # noqa: E402
    ContextSourceReaderAdapter,
    ContextSourceReaderError,
)


def test_real_index_reads_metadata_for_context_access_binding():
    adapter = ContextSourceReaderAdapter()

    result = adapter.read_metadata("context_access_binding")

    assert result.status == "METADATA_OK"
    assert result.source_id == "context_access_binding"
    assert result.content is None
    assert result.metadata["schema"] == "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001"
    assert result.metadata["access_mode"] == "read_only"
    assert result.metadata["runtime_enabled"] is False
    assert result.metadata["relative_path"] == "docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md"
    assert result.metadata["exists"] is True

    serialized = str(result.metadata)
    assert "/Users/" not in serialized
    assert "/PROMETEO/" not in serialized


def test_real_index_reads_limited_excerpt_for_context_access_binding():
    adapter = ContextSourceReaderAdapter(max_chars=500)

    result = adapter.read_excerpt("context_access_binding")

    assert result.status in {"READ_OK", "CONTENT_LIMIT_APPLIED"}
    assert result.source_id == "context_access_binding"
    assert result.content is not None
    assert len(result.content) <= 500
    assert "PROMETEO" in result.content

    serialized = str(result.metadata)
    assert "/Users/" not in serialized
    assert "/PROMETEO/" not in serialized


def test_real_index_rejects_direct_path_input():
    adapter = ContextSourceReaderAdapter()

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md")

    assert exc.value.code == "SOURCE_ID_INVALID"


def test_real_index_rejects_unknown_source():
    adapter = ContextSourceReaderAdapter()

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("unknown_source_for_test")

    assert exc.value.code == "SOURCE_NOT_FOUND"
