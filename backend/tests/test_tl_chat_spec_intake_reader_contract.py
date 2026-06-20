from __future__ import annotations


def _preview_contract_fixture() -> dict:
    return {
        "capability": "SPEC_INTAKE_12514_PREVIEW_001",
        "status": "PREVIEW_ONLY",
        "runtime_impact": "NONE",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "confidence": "DA_VERIFICARE",
        "article": {
            "articolo": "12514",
            "codice": "7056055000A0",
            "disegno": "A1675003603",
        },
        "classification": {
            "route_status": "DA_VERIFICARE",
            "zaw_station_resolution": "DA_VERIFICARE",
        },
        "forbidden_runtime_assumptions": [
            "Non trattare come profilo operativo CERTO.",
            "Non rendere planner_eligible senza conferma TL.",
            "Non inferire ZAW2 dai due passaggi ZAW.",
            "Non scrivere SMF, database o planner.",
            "Non versionare foto, screenshot o dati reali della specifica.",
        ],
        "tl_confirmation_required": [
            "Confermare se i due passaggi ZAW sono entrambi ZAW1 o coinvolgono altra postazione.",
            "Confermare sequenza route normalizzata PROMETEO.",
            "Confermare componenti 468728, 468865, 468796 e attrezzature CRT/CRM.",
            "Confermare se PIDMILL e CP sono assenti o solo non visibili nella specifica.",
        ],
    }


def test_spec_intake_preview_12514_contract_shape():
    data = _preview_contract_fixture()

    assert data["status"] == "PREVIEW_ONLY"
    assert data["runtime_impact"] == "NONE"
    assert data["planner_eligible"] is False
    assert data["requires_tl_confirmation"] is True
    assert data["confidence"] == "DA_VERIFICARE"

    article = data["article"]
    assert article["articolo"] == "12514"
    assert article["codice"] == "7056055000A0"
    assert article["disegno"] == "A1675003603"

    classification = data["classification"]
    assert classification["route_status"] == "DA_VERIFICARE"
    assert classification["zaw_station_resolution"] == "DA_VERIFICARE"


def test_spec_intake_preview_forbids_runtime_promotion():
    data = _preview_contract_fixture()

    forbidden = " ".join(data["forbidden_runtime_assumptions"])

    assert "Non trattare come profilo operativo CERTO." in forbidden
    assert "Non rendere planner_eligible senza conferma TL." in forbidden
    assert "Non inferire ZAW2 dai due passaggi ZAW." in forbidden
    assert "Non scrivere SMF, database o planner." in forbidden
    assert "Non versionare foto, screenshot o dati reali della specifica." in forbidden


def test_spec_intake_preview_requires_tl_confirmation_items():
    data = _preview_contract_fixture()

    confirmation = " ".join(data["tl_confirmation_required"])

    assert "Confermare se i due passaggi ZAW" in confirmation
    assert "Confermare sequenza route normalizzata PROMETEO." in confirmation
    assert "Confermare componenti 468728, 468865, 468796" in confirmation
    assert "Confermare se PIDMILL e CP sono assenti" in confirmation
