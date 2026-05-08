import json

from app.domain.article_operational_registry import (
    get_operational_registry_entry,
    reset_article_operational_registry_cache,
)
from app.domain.article_tl_summary import build_article_tl_summary


def test_operational_registry_entry_lookup(tmp_path, monkeypatch):
    path = tmp_path / "article_operational_registry.json"
    path.write_text(
        json.dumps(
            {
                "version": "test",
                "articles": {
                    "12191A": {
                        "drawing": "A1675017304",
                        "description": "P. 12191A DIS. A 167 501 7304",
                        "operational_class": "REFERENCE_ONLY",
                        "planner_eligible": False,
                        "tl_confirmation_required": True,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(path))
    reset_article_operational_registry_cache()

    entry = get_operational_registry_entry("12191a")

    assert entry is not None
    assert entry["article"] == "12191A"
    assert entry["drawing"] == "A1675017304"
    assert entry["operational_class"] == "REFERENCE_ONLY"


def test_tl_summary_uses_operational_registry_for_reference_only_code(tmp_path, monkeypatch):
    path = tmp_path / "article_operational_registry.json"
    path.write_text(
        json.dumps(
            {
                "version": "test",
                "articles": {
                    "12191A": {
                        "drawing": "A1675017304",
                        "description": "P. 12191A DIS. A 167 501 7304",
                        "operational_class": "REFERENCE_ONLY",
                        "planner_eligible": False,
                        "tl_confirmation_required": True,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(path))
    reset_article_operational_registry_cache()

    summary = build_article_tl_summary("12191A")

    assert summary["ok"] is True
    assert summary["confidence"] == "CERTO"
    assert summary["operational_class"] == "REFERENCE_ONLY"
    assert summary["planner_eligible"] is False
    assert summary["tl_confirmation_required"] is True
    assert summary["route"] == []
    assert "registro operativo" in summary["summary"]
    assert "non pianificare automaticamente" in summary["tl_action"]
