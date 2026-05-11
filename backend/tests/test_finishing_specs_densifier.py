from app.domain.finishing_specs_densifier import (
    ALREADY_AUTHORITATIVE,
    ASK_TL,
    AUTO_NORMALIZABLE,
    BLOCKED,
    build_densification_preview,
)


def test_densifier_marks_already_authoritative_without_patch():
    def loader(_record):
        return {}

    preview = build_densification_preview(
        metadata_loader=loader,
        specs_root=None,
    )

    # Questo test usa il repo reale solo se esiste; il contratto centrale è coperto dai test sotto.
    assert preview["schema"] == "PROMETEO_FINISHING_SPECS_DENSIFICATION_PREVIEW_V1"
    assert preview["mode"] == "preview_only"


def test_densifier_auto_normalizes_structured_synthetic_metadata(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12999",
                "authoritative": False,
                "confidence": "CERTO",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    metadata = {
        "stations_expected": [
            "LAVAGGIO",
            "CONTROLLO_VISIVO",
            "INSERIMENTO_GUAINA",
            "MARCATURA",
            "HENN",
            "ZAW1",
            "COLLAUDO_PRESSIONE",
            "COLLAUDO_VERTICALE",
            "SACCHETTO",
        ],
        "linked_bom": [
            {"component": "468922"},
            {"component": "469122"},
            {"component": "468763"},
        ],
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == AUTO_NORMALIZABLE
    patch = result["proposed_patch"]
    assert patch["schema"] == "PROMETEO_REAL_DATA_PILOT_V1"
    assert patch["route_status"] == "CERTO"
    assert [step["station"] for step in patch["route_steps"]] == [
        "LAVAGGIO",
        "CONTROLLO_VISIVO",
        "GUAINA",
        "MARCATURA",
        "HENN",
        "ZAW1",
        "CP",
    ]
    assert patch["constraints"]["has_henn"] is True
    assert patch["constraints"]["has_guaina"] is True
    assert patch["constraints"]["cp_required"] is True
    assert patch["constraints"]["cp_machine_mode"] == "VERTICALE_DUE_PIANI"


def test_densifier_asks_tl_for_real_zaw2(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12888",
                "authoritative": False,
                "confidence": "CERTO",
                "issues": [],
            }
        ]
    }
    metadata = {"stations_expected": ["LAVAGGIO", "ZAW2", "COLLAUDO_PRESSIONE"]}

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == ASK_TL
    assert "zaw2_real_station_requires_tl_confirmation" in result["reasons"]
    assert result["proposed_patch"] == {}


def test_densifier_blocks_poor_metadata(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12777",
                "authoritative": False,
                "confidence": "DA_VERIFICARE",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: {})
    result = preview["results"][0]

    assert result["classification"] == BLOCKED
    assert "missing_stations_expected" in result["reasons"]
    assert result["proposed_patch"] == {}


def test_densifier_keeps_authoritative_records_untouched(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12066",
                "authoritative": True,
                "confidence": "CERTO",
                "issues": [],
            }
        ]
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: {})
    result = preview["results"][0]

    assert result["classification"] == ALREADY_AUTHORITATIVE
    assert result["proposed_patch"] == {}
