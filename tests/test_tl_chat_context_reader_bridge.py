from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.tl_chat_context_reader_bridge import build_context_reader_candidate
from backend.app.services.tl_chat_context_resolver import resolve_tl_chat_context


def test_context_reader_bridge_builds_candidate_from_real_index():
    candidate = build_context_reader_candidate(
        source_id="context_access_binding",
        article="12514",
        include_excerpt=True,
        max_chars=300,
    )

    assert candidate.source_name == "context_source_reader_adapter"
    assert candidate.source_status == "SOURCE_FOUND"
    assert candidate.confidence == "DA_VERIFICARE"
    assert candidate.planner_eligible is False
    assert candidate.requires_tl_confirmation is True

    assert candidate.payload["article"] == "12514"
    assert candidate.payload["source_id"] == "context_access_binding"
    assert candidate.payload["reader_status"] in {"READ_OK", "CONTENT_LIMIT_APPLIED"}
    assert "metadata" in candidate.payload
    assert "excerpt" in candidate.payload
    assert len(candidate.payload["excerpt"]) <= 300


def test_context_reader_bridge_candidate_resolves_without_promotion():
    candidate = build_context_reader_candidate(
        source_id="context_access_binding",
        article="12514",
        include_excerpt=True,
        max_chars=300,
    )

    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[candidate],
    )

    assert resolved.article == "12514"
    assert resolved.selected_source == "context_source_reader_adapter"
    assert resolved.source_status == "SOURCE_FOUND"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.can_promote is False
    assert resolved.planner_eligible is False
    assert resolved.requires_tl_confirmation is True
    assert resolved.payload["source_id"] == "context_access_binding"


def test_context_reader_bridge_handles_unknown_source_as_missing():
    candidate = build_context_reader_candidate(
        source_id="unknown_source_for_bridge_test",
        article="12514",
    )

    assert candidate.source_status == "SOURCE_MISSING"
    assert candidate.confidence == "DA_VERIFICARE"
    assert candidate.planner_eligible is False
    assert candidate.requires_tl_confirmation is True
    assert candidate.payload["error_code"] == "SOURCE_NOT_FOUND"


def test_context_reader_bridge_rejects_path_like_source_id():
    candidate = build_context_reader_candidate(
        source_id="docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md",
        article="12514",
    )

    assert candidate.source_status == "SOURCE_FORBIDDEN"
    assert candidate.payload["error_code"] == "SOURCE_ID_INVALID"


def test_context_reader_bridge_does_not_expose_absolute_repo_path():
    candidate = build_context_reader_candidate(
        source_id="context_access_binding",
        article="12514",
        include_excerpt=False,
    )

    serialized = str(candidate.payload)
    assert Path.cwd().as_posix() not in serialized
    assert candidate.payload["metadata"]["relative_path"].startswith("docs/")
