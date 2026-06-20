from __future__ import annotations

import json

from app.atlas_engine.spec_intake_preview_reader import read_spec_intake_preview


def _write_preview(root, article: str = "12514") -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{article}_metadata_preview.json").write_text(
        json.dumps(
            {
                "status": "PREVIEW_ONLY",
                "runtime_impact": "NONE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "confidence": "DA_VERIFICARE",
                "article": {
                    "articolo": article,
                    "codice": "7056055000A0",
                    "disegno": "A1675003603",
                },
            }
        ),
        encoding="utf-8",
    )


def test_spec_intake_reader_returns_source_found_for_preview(tmp_path):
    _write_preview(tmp_path)

    result = read_spec_intake_preview(article="12514", root=tmp_path)

    assert result["source_id"] == "spec_intake_preview"
    assert result["source_status"] == "SOURCE_FOUND"
    assert result["article"] == "12514"
    assert result["confidence"] == "DA_VERIFICARE"
    assert result["requires_tl_confirmation"] is True
    assert result["planner_eligible"] is False
    assert "12514 trovato" in result["excerpt"]
    assert "preview-only" in result["limitation"]


def test_spec_intake_reader_returns_source_missing_for_absent_article(tmp_path):
    result = read_spec_intake_preview(article="99999", root=tmp_path)

    assert result["source_status"] == "SOURCE_MISSING"
    assert result["article"] == "99999"
    assert result["excerpt"] == ""
    assert result["planner_eligible"] is False
    assert result["requires_tl_confirmation"] is True


def test_spec_intake_reader_blocks_path_traversal(tmp_path):
    result = read_spec_intake_preview(article="../12514", root=tmp_path)

    assert result["source_status"] == "PATH_TRAVERSAL_BLOCKED"
    assert result["planner_eligible"] is False
    assert result["requires_tl_confirmation"] is True
    assert "safe article policy" in result["limitation"]


def test_spec_intake_reader_forbids_unknown_source_id(tmp_path):
    result = read_spec_intake_preview(
        article="12514",
        source_id="unauthorized_source",
        root=tmp_path,
    )

    assert result["source_status"] == "SOURCE_FORBIDDEN"
    assert result["source_id"] == "unauthorized_source"
    assert result["planner_eligible"] is False
    assert result["requires_tl_confirmation"] is True
