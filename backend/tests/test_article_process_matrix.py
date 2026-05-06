import importlib
import json
from pathlib import Path

import app.domain.article_process_matrix as apm


def test_article_matrix_path_env_fallback_and_missing_file_are_safe(monkeypatch, tmp_path):
    env_base = tmp_path / "env_base"
    env_matrix = env_base / "finiture" / "article_route_matrix.json"
    env_matrix.parent.mkdir(parents=True, exist_ok=True)
    env_matrix.write_text(
        json.dumps(
            {
                "profiles": {
                    "ART-ENV": {
                        "route": ["CUT", "PAINT"],
                        "signals": {"priority_boost": 1},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))
    m = importlib.reload(apm)

    assert m.get_article_profile("ART-ENV") is not None
    assert m.get_article_route("ART-ENV") == ["CUT", "PAINT"]
    assert m.get_article_signals("ART-ENV") == {"priority_boost": 1}

    monkeypatch.delenv("SMF_BASE_PATH", raising=False)
    fallback_home = tmp_path / "fake_home"
    fallback_base = fallback_home / "Documents" / "local_smf"
    fallback_matrix = fallback_base / "finiture" / "article_route_matrix.json"
    fallback_matrix.parent.mkdir(parents=True, exist_ok=True)
    fallback_matrix.write_text(
        json.dumps(
            {
                "profiles": {
                    "ART-FALLBACK": {
                        "route": ["WELD"],
                        "signals": {"hazmat": False},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(Path, "home", staticmethod(lambda: fallback_home))
    m = importlib.reload(apm)

    assert m.get_article_route("ART-FALLBACK") == ["WELD"]
    assert m.get_article_signals("ART-FALLBACK") == {"hazmat": False}

    fallback_matrix.unlink()
    m = importlib.reload(apm)

    assert m.get_article_profile("ART-FALLBACK") is None
    assert m.get_article_route("ART-FALLBACK") == []
    assert m.get_article_signals("ART-FALLBACK") == {}

def test_article_matrix_reads_realistic_12066_profile_with_tl_confirmed_zaw1(monkeypatch, tmp_path):
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
    m = importlib.reload(apm)

    profile = m.get_article_profile("12066")
    route = m.get_article_route("12066")
    signals = m.get_article_signals("12066")

    assert profile is not None
    assert profile["confidence"] == "CERTO"
    assert route == [
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
    ]
    assert signals["primary_zaw_station"] == "ZAW1"
    assert signals["has_zaw1"] is True
    assert signals["has_zaw2"] is False
    assert signals["cp_required"] is True
    assert signals["cp_machine_mode"] == "VERTICALE_DUE_PIANI"
    assert profile["discrepancies"][0]["status"] == "CONFIRMED_BY_TL"

