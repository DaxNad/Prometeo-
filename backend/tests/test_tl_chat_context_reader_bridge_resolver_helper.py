from __future__ import annotations

import json

from tools.context_source_reader_adapter import ContextSourceReaderAdapter
from tools.tl_chat_context_reader_bridge import (
    resolve_context_reader_source_for_tl_chat,
)


def _write_context_index(repo_root):
    source = repo_root / "docs" / "tl_context_policy.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "TL Chat retrieval source fixture. Confidence remains DA_VERIFICARE.",
        encoding="utf-8",
    )

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


def test_context_reader_bridge_resolves_authorized_source_through_resolver(tmp_path):
    index = _write_context_index(tmp_path)
    adapter = ContextSourceReaderAdapter(
        index_path=index,
        repo_root=tmp_path,
        max_chars=80,
    )

    result = resolve_context_reader_source_for_tl_chat(
        source_id="tl_context_policy",
        article="12514",
        adapter=adapter,
    )

    assert result["article"] == "12514"
    assert result["source"] == "tl_context_policy"
    assert result["source_status"] == "SOURCE_FOUND"
    assert result["reader_status"] == "READ_OK"
    assert result["confidence"] == "DA_VERIFICARE"
    assert result["missing_data"] == "nessun dato certo promosso; conferma TL richiesta"
    assert "non applicare decisioni operative" in result["next_safe_action"]
    assert result["requires_tl_confirmation"] is True
    assert result["planner_eligible"] is False
    assert result["can_promote"] is False
    assert result["relative_path"] == "docs/tl_context_policy.md"
    assert "TL Chat retrieval source fixture" in result["excerpt"]


def test_context_reader_bridge_blocks_non_logical_source_id(tmp_path):
    index = _write_context_index(tmp_path)
    adapter = ContextSourceReaderAdapter(
        index_path=index,
        repo_root=tmp_path,
        max_chars=80,
    )

    result = resolve_context_reader_source_for_tl_chat(
        source_id="../secrets",
        article="12514",
        adapter=adapter,
    )

    assert result["article"] == "12514"
    assert result["source_status"] == "SOURCE_FORBIDDEN"
    assert result["confidence"] == "DA_VERIFICARE"
    assert result["missing_data"] == "fonte non disponibile, vietata o non risolta"
    assert result["next_safe_action"] == (
        "verificare source_id o fonte ammessa prima di usare il contesto"
    )
    assert result["planner_eligible"] is False
    assert result["can_promote"] is False
    assert result["relative_path"] == ""
    assert result["excerpt"] == ""
