from app.domain import article_tl_summary as summary_module


def test_article_tl_summary_uses_authoritative_resolver(monkeypatch):
    def fake_resolve_article_profile(article_code: str):
        assert article_code == "12063"
        return {
            "article": "12063",
            "source": "LOCAL_SPECS_METADATA",
            "authoritative": True,
            "confidence": "CERTO",
            "route_status": "CERTO",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route": ["GUAINA", "MARCATURA", "ZAW1", "CP"],
            "signals": {
                "source": "LOCAL_SPECS_METADATA",
                "authoritative": True,
                "has_henn": False,
                "has_guaina": True,
                "has_pidmill": False,
                "primary_zaw_station": "ZAW1",
                "has_zaw1": True,
                "has_zaw2": False,
                "do_not_infer_zaw2": True,
                "single_connector_both_ends": True,
                "cp_required": True,
                "shared_components": ["468728", "468796"],
            },
        }

    monkeypatch.setattr(summary_module, "resolve_article_profile", fake_resolve_article_profile)

    summary = summary_module.build_article_tl_summary("12063")

    assert summary["ok"] is True
    assert summary["article"] == "12063"
    assert summary["confidence"] == "CERTO"
    assert summary["operational_class"] == "STANDARD"
    assert summary["planner_eligible"] is True
    assert summary["route"] == ["GUAINA", "MARCATURA", "ZAW1", "CP"]
    assert summary["signals"]["source"] == "LOCAL_SPECS_METADATA"
    assert summary["signals"]["authoritative"] is True
    assert summary["signals"]["has_zaw2"] is False
    assert summary["signals"]["single_connector_both_ends"] is True
