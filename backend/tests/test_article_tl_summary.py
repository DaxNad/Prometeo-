import importlib
import json
from pathlib import Path

import app.domain.article_process_matrix as apm
import app.domain.article_tl_summary as ats


def test_article_tl_summary_builds_readable_12066_profile(monkeypatch, tmp_path):
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
                            "long_sheath_risk": True,
                        },
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "wrong_source": "BOM_Specs.csv famiglia_processo=HENN_ZAW2_PIDMILL",
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
    m = importlib.reload(ats)

    summary = m.build_article_tl_summary("12066")

    assert summary["ok"] is True
    assert summary["article"] == "12066"
    assert summary["confidence"] == "CERTO"
    assert "ZAW1" in summary["route"]
    assert summary["signals"]["primary_zaw_station"] == "ZAW1"
    assert any("Usare ZAW1" in item for item in summary["criticalities"])
    assert any("HENN" in item for item in summary["criticalities"])
    assert any("PIDMILL" in item for item in summary["criticalities"])
    assert any("VERTICALE_DUE_PIANI" in item for item in summary["criticalities"])
    assert any("468728" in item for item in summary["criticalities"])
    assert any("HENN_ZAW1_PIDMILL" in item for item in summary["criticalities"])
    assert "fonti discordanti" in summary["tl_action"]


def test_article_tl_summary_missing_profile_is_safe(monkeypatch, tmp_path):
    env_base = tmp_path / "env_base"
    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))

    importlib.reload(apm)
    m = importlib.reload(ats)

    summary = m.build_article_tl_summary("NOPE")

    assert summary["ok"] is False
    assert summary["confidence"] == "DA_VERIFICARE"
    assert summary["route"] == []
    assert "non disponibile" in summary["summary"]
