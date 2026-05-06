import importlib
import json

from fastapi.testclient import TestClient

import app.domain.article_process_matrix as apm
import app.domain.article_tl_summary as ats


def test_production_article_summary_endpoint_returns_12066_tl_summary(monkeypatch, tmp_path):
    env_base = tmp_path / "env_base"
    matrix_path = env_base / "finiture" / "article_route_matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)

    matrix_path.write_text(
        json.dumps(
            {
                "version": "0.1",
                "profiles": {
                    "12066": {
                        "article": "12066",
                        "confidence": "CERTO",
                        "route": [
                            "LAVAGGIO",
                            "CONTROLLO_VISIVO",
                            "INSERIMENTO_GUAINA",
                            "MARCATURA",
                            "HENN",
                            "INSERIMENTO_INNESTO_RAPIDO",
                            "ZAW1",
                            "PIDMILL",
                            "COLLAUDO_PRESSIONE",
                            "SACCHETTO",
                        ],
                        "signals": {
                            "has_henn": True,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "has_pidmill": True,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_component_risk": True,
                            "shared_components": ["468728", "468796"],
                        },
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "correct_value": "HENN_ZAW1_PIDMILL",
                                "status": "CONFIRMED_BY_TL",
                            }
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))
    importlib.reload(apm)
    importlib.reload(ats)

    from app.main import app

    client = TestClient(app)
    res = client.get("/production/article-summary/12066")
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["article"] == "12066"
    assert data["confidence"] == "CERTO"
    assert "ZAW1" in data["route"]
    assert data["signals"]["primary_zaw_station"] == "ZAW1"
    assert any("Usare ZAW1" in item for item in data["criticalities"])
    assert any("VERTICALE_DUE_PIANI" in item for item in data["criticalities"])
    assert "fonti discordanti" in data["tl_action"]


def test_production_article_summary_endpoint_missing_profile_is_safe(monkeypatch, tmp_path):
    env_base = tmp_path / "env_base"
    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))

    importlib.reload(apm)
    importlib.reload(ats)

    from app.main import app

    client = TestClient(app)
    res = client.get("/production/article-summary/NOPE")
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is False
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["route"] == []
    assert "non disponibile" in data["summary"]
