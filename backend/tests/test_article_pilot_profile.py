from __future__ import annotations

import json

import pandas as pd

from app.domain.article_pilot_profile import build_article_pilot_profile


def test_build_article_pilot_profile_from_bom_sources_detects_12056_discrepancy():
    specs = pd.DataFrame(
        [
            {
                "articolo": "12056",
                "codice_articolo": "7090883X00D0",
                "disegno": "A 214 501 3001",
                "rev": "10",
                "qta_lotto": 87,
                "qta_imballo": 8,
                "codice_imballo": "6429",
                "cluster_name": "DOPPIO_INNESTO_ZAW",
                "cp_required": "",
                "raw_json": json.dumps(
                    {
                        "pattern": "SINGOLO_INNESTO_ZAW",
                        "articolo": "12056",
                        "disegno": "A 214 501 3001",
                        "codice_sap": "7090883X00D0",
                        "sequenza": [
                            "LAVAGGIO",
                            "COLLAUDO_VISIVO_100%",
                            "INNESTO_RAPIDO_CRT015",
                            "CRIMP_RING_ZAW_CRM015",
                            "ASSEMBLAGGIO",
                            "IMBALLO",
                        ],
                        "innesto_rapido_1": {
                            "componenti": ["468791", "468948"],
                            "attrezzatura": "CRT015",
                        },
                        "zaw_1": {"crm": "CRM015"},
                        "packaging": {"sacchetto": "467660"},
                    }
                ),
            }
        ]
    )

    operations = pd.DataFrame(
        [
            {"articolo": "12056", "seq_no": 1, "fase": "LAVAGGIO"},
            {"articolo": "12056", "seq_no": 2, "fase": "COLLAUDO_VISIVO_100%"},
            {"articolo": "12056", "seq_no": 3, "fase": "INNESTO_RAPIDO_CRT015"},
            {"articolo": "12056", "seq_no": 4, "fase": "CRIMP_RING_ZAW_CRM015"},
            {"articolo": "12056", "seq_no": 5, "fase": "ASSEMBLAGGIO"},
            {"articolo": "12056", "seq_no": 6, "fase": "IMBALLO"},
        ]
    )

    controls = pd.DataFrame(
        [
            {
                "articolo": "12056",
                "extra": json.dumps({"visivo_100": True, "collaudo_pressione": False}),
            }
        ]
    )

    profile = build_article_pilot_profile(
        "12056",
        specs=specs,
        operations=operations,
        controls=controls,
    )

    assert profile["ok"] is True
    assert profile["article"] == "12056"
    assert profile["sap_code"] == "7090883X00D0"
    assert profile["drawing"] == "A 214 501 3001"
    assert profile["revision"] == "10"
    assert profile["route_raw"] == [
        "LAVAGGIO",
        "COLLAUDO_VISIVO_100%",
        "INNESTO_RAPIDO_CRT015",
        "CRIMP_RING_ZAW_CRM015",
        "ASSEMBLAGGIO",
        "IMBALLO",
    ]
    assert profile["components_from_specs"] == ["468791", "468948"]
    assert profile["tooling"] == ["CRT015", "CRM015"]
    assert profile["packaging"] == {"sacchetto": "467660"}
    assert profile["controls"] == {"visivo_100": True, "collaudo_pressione": False}
    assert profile["confidence"] == "INFERITO"
    assert "pattern_cluster_mismatch" in profile["discrepancies"]


def test_build_article_pilot_profile_missing_specs_is_da_verificare():
    profile = build_article_pilot_profile(
        "NOPE",
        specs=pd.DataFrame(columns=["articolo"]),
        operations=pd.DataFrame(columns=["articolo"]),
        controls=pd.DataFrame(columns=["articolo"]),
    )

    assert profile["ok"] is False
    assert profile["confidence"] == "DA_VERIFICARE"
    assert "missing_bom_specs" in profile["discrepancies"]

def test_build_article_pilot_profile_from_reader_is_read_only(tmp_path):
    import pandas as pd

    from app.domain.article_pilot_profile import build_article_pilot_profile_from_reader

    workbook = tmp_path / "smf.xlsx"

    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        pd.DataFrame(
            [
                {
                    "articolo": "12056",
                    "codice_articolo": "7090883X00D0",
                    "disegno": "A 214 501 3001",
                    "rev": "10",
                    "cluster_name": "DOPPIO_INNESTO_ZAW",
                    "raw_json": json.dumps(
                        {
                            "pattern": "SINGOLO_INNESTO_ZAW",
                            "innesto_rapido_1": {
                                "componenti": ["468791", "468948"],
                                "attrezzatura": "CRT015",
                            },
                            "zaw_1": {"crm": "CRM015"},
                            "packaging": {"sacchetto": "467660"},
                        }
                    ),
                }
            ]
        ).to_excel(writer, sheet_name="BOM_Specs", index=False)

        pd.DataFrame(
            [
                {"articolo": "12056", "seq_no": 1, "fase": "LAVAGGIO"},
                {"articolo": "12056", "seq_no": 2, "fase": "IMBALLO"},
            ]
        ).to_excel(writer, sheet_name="BOM_Operations", index=False)

        pd.DataFrame(
            [
                {
                    "articolo": "12056",
                    "extra": json.dumps({"visivo_100": True}),
                }
            ]
        ).to_excel(writer, sheet_name="BOM_Controls", index=False)

    class _Reader:
        path = workbook

    profile = build_article_pilot_profile_from_reader("12056", _Reader())

    assert profile["ok"] is True
    assert profile["article"] == "12056"
    assert profile["route_raw"] == ["LAVAGGIO", "IMBALLO"]
    assert profile["components_from_specs"] == ["468791", "468948"]
    assert profile["tooling"] == ["CRT015", "CRM015"]
    assert "pattern_cluster_mismatch" in profile["discrepancies"]

    missing_dir = tmp_path / "missing"
    missing_reader_path = missing_dir / "SuperMegaFile_Master.xlsx"

    class _MissingReader:
        path = missing_reader_path

    missing_profile = build_article_pilot_profile_from_reader("12056", _MissingReader())

    assert missing_profile["ok"] is False
    assert missing_profile["confidence"] == "DA_VERIFICARE"
    assert "missing_bom_specs" in missing_profile["discrepancies"]
    assert not missing_dir.exists()

