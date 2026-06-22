from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.context_source_reader_adapter import (  # noqa: E402
    ContextSourceReaderAdapter,
    ContextSourceReaderError,
)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "PROMETEO"
    (repo / "memory").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    (repo / "docs" / "allowed.md").write_text(
        "PROMETEO allowed source content.",
        encoding="utf-8",
    )

    (repo / "blocked" / "forbidden.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "blocked" / "forbidden.md").write_text("blocked test content", encoding="utf-8")

    index = {
        "schema": "PROMETEO_CONTEXT_SOURCE_INDEX_001",
        "runtime_enabled": False,
        "sources": [
            {
                "source_id": "PROMETEO_ALLOWED_SOURCE",
                "path": "docs/allowed.md",
                "access_mode": "read_only",
                "runtime_enabled": False,
                "source_type": "governance_doc",
            },
            {
                "source_id": "PROMETEO_FORBIDDEN_ENV",
                "path": "blocked/forbidden.md",
                "access_mode": "read_only",
                "runtime_enabled": False,
                "source_type": "forbidden",
            },
            {
                "source_id": "PROMETEO_TRAVERSAL",
                "path": "../outside.md",
                "access_mode": "read_only",
                "runtime_enabled": False,
                "source_type": "invalid",
            },
            {
                "source_id": "PROMETEO_RUNTIME_SOURCE",
                "path": "docs/allowed.md",
                "access_mode": "read_only",
                "runtime_enabled": True,
                "source_type": "runtime",
            },
        ],
    }

    (repo / "memory" / "context_source_index.json").write_text(
        json.dumps(index, indent=2),
        encoding="utf-8",
    )

    return repo


def test_read_metadata_allowed_source(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    result = adapter.read_metadata("PROMETEO_ALLOWED_SOURCE")

    assert result.status == "METADATA_OK"
    assert result.source_id == "PROMETEO_ALLOWED_SOURCE"
    assert result.content is None
    assert result.metadata["relative_path"] == "docs/allowed.md"
    assert result.metadata["access_mode"] == "read_only"
    assert result.metadata["runtime_enabled"] is False


def test_read_excerpt_allowed_source(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    result = adapter.read_excerpt("PROMETEO_ALLOWED_SOURCE")

    assert result.status == "READ_OK"
    assert result.content == "PROMETEO allowed source content."
    assert str(repo) not in str(result.metadata)
    assert str(repo) not in str(result.metadata)


def test_content_limit_applied(tmp_path: Path):
    repo = make_repo(tmp_path)
    (repo / "docs" / "allowed.md").write_text("A" * 100, encoding="utf-8")

    adapter = ContextSourceReaderAdapter(repo_root=repo, max_chars=10)
    result = adapter.read_excerpt("PROMETEO_ALLOWED_SOURCE")

    assert result.status == "CONTENT_LIMIT_APPLIED"
    assert result.content == "A" * 10


def test_rejects_unknown_source_id(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("UNKNOWN_SOURCE")

    assert exc.value.code == "SOURCE_NOT_FOUND"


def test_rejects_path_like_source_id(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("docs/allowed.md")

    assert exc.value.code == "SOURCE_ID_INVALID"


def test_blocks_forbidden_path(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("PROMETEO_FORBIDDEN_ENV")

    assert exc.value.code == "FORBIDDEN_PATH_BLOCKED"


def test_blocks_path_traversal_from_index(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("PROMETEO_TRAVERSAL")

    assert exc.value.code == "PATH_TRAVERSAL_BLOCKED"


def test_blocks_runtime_enabled_source(tmp_path: Path):
    repo = make_repo(tmp_path)
    adapter = ContextSourceReaderAdapter(repo_root=repo)

    with pytest.raises(ContextSourceReaderError) as exc:
        adapter.read_metadata("PROMETEO_RUNTIME_SOURCE")

    assert exc.value.code == "RUNTIME_SOURCE_BLOCKED"
