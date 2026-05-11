import json

from app.domain import article_profile_resolver as resolver


def test_local_specs_metadata_is_authoritative(monkeypatch, tmp_path):
    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12063"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12063",
        "confidence": "CERTO",
        "route_status": "CERTO",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_steps": [
            {"seq": 1, "station": "GUAINA"},
            {"seq": 2, "station": "MARCATURA"},
            {"seq": 3, "station": "ZAW1"},
            {"seq": 4, "station": "CP"},
        ],
        "constraints": {
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

    (article_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    monkeypatch.setattr(resolver, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(
        resolver,
        "get_derived_article_profile",
        lambda _article: {
            "article": "12063",
            "confidence": "DA_VERIFICARE",
            "route_status": "DA_VERIFICARE",
            "operational_class": "DA_VERIFICARE",
            "signals": {"primary_zaw_station": "ZAW2"},
        },
    )

    profile = resolver.resolve_article_profile("12063")

    assert profile is not None
    assert profile["source"] == "LOCAL_SPECS_METADATA"
    assert profile["authoritative"] is True
    assert profile["confidence"] == "CERTO"
    assert profile["route_status"] == "CERTO"
    assert profile["operational_class"] == "STANDARD"
    assert profile["planner_eligible"] is True
    assert profile["route"] == ["GUAINA", "MARCATURA", "ZAW1", "CP"]
    assert profile["signals"]["primary_zaw_station"] == "ZAW1"
    assert profile["signals"]["has_zaw2"] is False
    assert profile["signals"]["single_connector_both_ends"] is True


def test_derived_profile_is_used_only_when_local_metadata_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(resolver, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(
        resolver,
        "get_derived_article_profile",
        lambda _article: {
            "article": "99999",
            "confidence": "INFERITO",
            "signals": {"primary_zaw_station": "ZAW1"},
        },
    )

    profile = resolver.resolve_article_profile("99999")

    assert profile is not None
    assert profile["source"] == "ARTICLE_PROCESS_MATRIX_DERIVED"
    assert profile["authoritative"] is False
    assert profile["confidence"] == "INFERITO"
