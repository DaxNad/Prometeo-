import json

import pandas as pd
from fastapi.testclient import TestClient

import app.api_smf as api_smf
from app.main import app


def test_family_summary_by_drawing_enriches_tl_ready_fields(monkeypatch):
    sheets = {
        "BOM_Specs": pd.DataFrame(
            [
                {
                    "articolo": "ART-001",
                    "disegno": "DWG-100",
                    "famiglia_processo": "PIDMILL_DIRETTO",
                    "raw_json": json.dumps(
                        {
                            "componenti": [{"codice": "468922"}],
                            "complessivo_articolo": "ASSIEME-1",
                            "parziale_articolo": "ART-001",
                        }
                    ),
                },
                {
                    "articolo": "ART-002",
                    "disegno": "DWG-100",
                    "famiglia_processo": "HENN_BASE",
                    "raw_json": json.dumps(
                        {
                            "componenti": [{"codice": "468728"}],
                            "complessivo_articolo": "ASSIEME-1",
                            "parziale_articolo": "ART-002",
                        }
                    ),
                },
                {
                    "articolo": "ART-003",
                    "disegno": "DWG-100",
                    "famiglia_processo": "BASE",
                    "raw_json": json.dumps(
                        {
                            "componenti": [{"codice": "468976"}],
                            "complessivo_articolo": "ASSIEME-1",
                            "parziale_articolo": "ART-003",
                        }
                    ),
                },
            ]
        ),
        "BOM_Components": pd.DataFrame(
            [
                {
                    "articolo": "ART-001",
                    "codice_componente": "468922",
                    "extra": json.dumps({"componenti_annidati": ["CRT004", "CRM004"]}),
                },
                {
                    "articolo": "ART-002",
                    "codice_componente": "",
                    "extra": json.dumps({"componenti_annidati": ["468728", "BAT010"]}),
                },
            ]
        ),
        "BOM_Operations": pd.DataFrame(
            [
                {
                    "articolo": "ART-001",
                    "fase": "taglio PIDMILL",
                    "extra": json.dumps({"materiale_riferimento": ["BAT010"]}),
                },
                {
                    "articolo": "ART-002",
                    "fase": "finitura HENN",
                    "extra": json.dumps({"materiale_riferimento": ["469122"]}),
                },
                {
                    "articolo": "ART-003",
                    "fase": "assemblaggio",
                    "extra": json.dumps({}),
                },
            ]
        ),
        "BOM_Markings": pd.DataFrame(
            [
                {"articolo": "ART-001", "tipo": "LASER"},
                {"articolo": "ART-002", "tipo": "INK"},
            ]
        ),
        "BOM_Variants": pd.DataFrame(
            [
                {
                    "articolo": "ART-001",
                    "nome_variante": "parziale complessivo",
                    "raw_json": json.dumps({"stato_processo": "parziale complessivo"}),
                }
            ]
        ),
    }

    monkeypatch.setattr(api_smf, "_read_smf_sheet", lambda sheet_name: sheets[sheet_name].copy())

    client = TestClient(app)
    response = client.get("/smf/bom/family-summary/by-drawing", params={"disegno": " DWG -100 "})

    assert response.status_code == 200
    body = response.json()

    assert body["ok"] is True
    assert body["drawing"] == " DWG -100 "
    assert body["normalized_drawing"] == "DWG-100"
    assert body["count_articoli"] == 3
    assert body["tipo_famiglia"] == "famiglia_complessivo"
    assert body["tassativo"] is True
    assert body["rotazione"] == "da_verificare"
    assert body["peso_turno"]["livello"] == "alto"
    assert body["peso_turno"]["per_postazione"] == {"HENN": 2, "PIDMILL": 2}
    assert body["classificazione_per_articolo"] == {
        "ART-001": "parziale_di_complessivo",
        "ART-002": "parziale_di_complessivo",
        "ART-003": "parziale_di_complessivo",
    }
    assert body["dipendenza_parziale"] == {
        "ART-001": True,
        "ART-002": True,
        "ART-003": True,
    }
    assert body["quota_per_complessivo"] == {
        "ART-001": 3,
        "ART-002": 3,
        "ART-003": 3,
    }
    assert set(body["componenti_coinvolti"]) == {
        "468922",
        "468728",
        "468976",
        "469122",
        "CRT004",
        "CRM004",
        "BAT010",
    }
