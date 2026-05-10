from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import tl_chat as tl_chat_api


def test_tl_chat_contract_reads_12402_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "99997": {
                    "status": "DA_VERIFICARE",
                    "source": "riunione_aziendale_memoria_tl",
                    "note": "Codice citato tra quelli da rivalutare.",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 99997 è da verificare?",
            "context": {"article": "99997"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "99997" in data["answer"]
    assert "riunione_aziendale_memoria_tl" in data["answer"]
    assert "Verifica TL richiesta" in data["recommended_action"]


def test_tl_chat_contract_handles_new_entry_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps({"12410": {"status": "NEW_ENTRY", "source": "tl"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 12410 è nuovo?",
            "context": {"article": "12410"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "INFERITO"
    assert data["requires_confirmation"] is True
    assert "NEW_ENTRY" in data["answer"]
    assert "priorità alta" in data["recommended_action"].lower()


def test_tl_chat_contract_handles_fuori_produzione_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps({"12053": {"status": "FUORI_PRODUZIONE", "source": "tl"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 12053 è ancora attivo?",
            "context": {"article": "12053"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "INFERITO"
    assert data["requires_confirmation"] is True
    assert "FUORI_PRODUZIONE" in data["answer"]
    assert "Non portare in staging" in data["recommended_action"]


def test_tl_chat_contract_unknown_article_stays_da_verificare(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Dimmi lo stato del codice.",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "non è presente nel lifecycle registry" in data["answer"]
    assert "git" not in data["answer"].lower()
    assert "pytest" not in data["answer"].lower()
    assert "guard" not in data["answer"].lower()


def test_tl_chat_contract_missing_registry_is_safe(monkeypatch, tmp_path):
    missing_dir = tmp_path / "missing"
    missing_registry = missing_dir / "article_lifecycle_registry.json"
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", missing_registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 99997 è da verificare?",
            "context": {"article": "99997"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert not missing_dir.exists()


def test_tl_chat_contract_requires_context_for_specific_answer():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa devo verificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "codice articolo" in data["recommended_action"].lower()

def test_tl_chat_contract_lists_codes_da_verificare(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "99997": {
                    "status": "DA_VERIFICARE",
                    "source": "riunione_aziendale_memoria_tl",
                },
                "12053": {
                    "status": "FUORI_PRODUZIONE",
                    "source": "tl",
                },
                "12410": {
                    "status": "NEW_ENTRY",
                    "source": "tl",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici sono da verificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "99997" in data["answer"]
    assert "12053" not in data["answer"]
    assert "12410" not in data["answer"]
    assert "Verifica TL richiesta" in data["recommended_action"]


def test_tl_chat_contract_lists_no_codes_da_verificare(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12053": {"status": "FUORI_PRODUZIONE"},
                "12410": {"status": "NEW_ENTRY"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici sono da verificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "Non risultano codici DA_VERIFICARE" in data["answer"]

def test_tl_chat_contract_lists_new_entry_codes(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12402": {"status": "DA_VERIFICARE"},
                "12410": {"status": "NEW_ENTRY"},
                "12053": {"status": "FUORI_PRODUZIONE"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici sono new entry?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "12410" in data["answer"]
    assert "12402" not in data["answer"]
    assert "12053" not in data["answer"]
    assert "NEW_ENTRY" in data["answer"]


def test_tl_chat_contract_lists_fuori_produzione_codes(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12402": {"status": "DA_VERIFICARE"},
                "12410": {"status": "NEW_ENTRY"},
                "12053": {"status": "FUORI_PRODUZIONE"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici sono fuori produzione?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "12053" in data["answer"]
    assert "12402" not in data["answer"]
    assert "12410" not in data["answer"]
    assert "FUORI_PRODUZIONE" in data["answer"]

def test_tl_chat_contract_lists_densification_candidates(monkeypatch, tmp_path):
    staging = tmp_path / "codici_staging_preview.json"
    staging.write_text(
        json.dumps(
            {
                "ok": True,
                "mode": "CODICI_STAGING_PREVIEW_V1",
                "items": [
                    {
                        "codice": "12056",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "REVIEW_BEFORE_STAGING",
                    },
                    {
                        "codice": "12410",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "REVIEW_HIGH_PRIORITY",
                    },
                    {
                        "codice": "12402",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "TL_REVIEW_REQUIRED",
                    },
                ],
                "excluded": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici posso densificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "12056" in data["answer"]
    assert "12410" in data["answer"]
    assert "12402" not in data["answer"]
    assert "conferma TL" in data["risk"]


def test_tl_chat_contract_handles_missing_staging_preview(monkeypatch, tmp_path):
    missing = tmp_path / "missing" / "codici_staging_preview.json"
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", missing)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Quali codici posso densificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "Non risultano codici pronti" in data["answer"]
    assert not missing.parent.exists()


def test_tl_chat_answers_12066_from_article_summary_before_lifecycle(monkeypatch, tmp_path):
    import importlib
    import json

    import app.domain.article_process_matrix as apm
    import app.domain.article_tl_summary as ats
    from app.api import tl_chat as tl_chat_api

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
                        "route": ["HENN", "ZAW1", "PIDMILL", "COLLAUDO_PRESSIONE"],
                        "signals": {
                            "has_henn": True,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "has_pidmill": True,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
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
    importlib.reload(tl_chat_api)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12066?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert "12066" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "ZAW2" in data["answer"]
    assert "HENN" in data["answer"]
    assert "PIDMILL" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "468728" in data["answer"]
    assert data["technical_details_hidden"] is True

def test_tl_chat_answers_12055_from_article_summary(monkeypatch, tmp_path):
    import importlib
    import json

    import app.domain.article_process_matrix as apm
    import app.domain.article_tl_summary as ats
    from app.api import tl_chat as tl_chat_api

    env_base = tmp_path / "env_base"
    matrix_path = env_base / "finiture" / "article_route_matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)

    matrix_path.write_text(
        json.dumps(
            {
                "version": "0.1",
                "profiles": {
                    "12055": {
                        "article": "12055",
                        "confidence": "CERTO",
                        "route": ["HENN", "ZAW1", "COLLAUDO_PRESSIONE"],
                        "signals": {
                            "has_henn": True,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "has_pidmill": False,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_components": ["468763", "468796"],
                        },
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "correct_value": "HENN_ZAW1",
                                "status": "CONFIRMED_BY_SPEC",
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
    importlib.reload(tl_chat_api)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12055?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert "12055" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "ZAW2" in data["answer"]
    assert "HENN" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "468763" in data["answer"]
    assert "HENN_ZAW1" in data["answer"]
    assert data["technical_details_hidden"] is True

def test_tl_chat_answers_12102_double_zaw_pass_without_henn(monkeypatch, tmp_path):
    import importlib
    import json

    import app.domain.article_process_matrix as apm
    import app.domain.article_tl_summary as ats
    from app.api import tl_chat as tl_chat_api

    env_base = tmp_path / "env_base"
    matrix_path = env_base / "finiture" / "article_route_matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)

    matrix_path.write_text(
        json.dumps(
            {
                "version": "0.1",
                "profiles": {
                    "12102": {
                        "article": "12102",
                        "confidence": "CERTO",
                        "route": [
                            "INSERIMENTO_INNESTO_RAPIDO",
                            "ZAW1",
                            "INSERIMENTO_INNESTO_RAPIDO_2",
                            "ZAW1_2",
                            "COLLAUDO_PRESSIONE",
                        ],
                        "signals": {
                            "has_henn": False,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "zaw_passes": 2,
                            "has_pidmill": False,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_components": ["468728", "468796", "468830", "468841"],
                        },
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "correct_value": "ZAW1_DOPPIO_PASSAGGIO_GUAINA_DOPPIA",
                                "status": "CONFIRMED_BY_SPEC",
                            },
                            {
                                "code": "cp_vertical_mode_not_route_phase",
                                "correct_value": "COLLAUDO_PRESSIONE con machine_mode=VERTICALE_DUE_PIANI",
                                "status": "NORMALIZED_BY_DOMAIN_RULE",
                            },
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
    importlib.reload(tl_chat_api)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12102?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert "12102" in data["answer"]
    assert "ZAW1 con 2 passaggi" in data["answer"]
    assert "ZAW1_2 non è ZAW2" in data["answer"]
    assert "HENN assente/non indicato" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "468830" in data["answer"]
    assert "ZAW1_DOPPIO_PASSAGGIO_GUAINA_DOPPIA" in data["answer"]
    assert data["technical_details_hidden"] is True

def test_tl_chat_uses_preview_for_inferred_article_when_active_summary_missing(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    preview = tmp_path / "article_route_matrix.preview.json"
    preview.write_text(
        json.dumps(
            {
                "profiles": {
                    "12056": {
                        "article": "12056",
                        "confidence": "INFERITO",
                        "signals": {
                            "has_henn": False,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "zaw_passes": 1,
                            "has_pidmill": False,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_components": [],
                        },
                        "review_reasons": [],
                        "discrepancies": [],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12056?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "INFERITO"
    assert "Profilo inferito" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True


def test_tl_chat_uses_local_specs_metadata_when_present(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12056"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12056",
        "drawing": "A2145013001",
        "rev": "10",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_status": "CERTO",
        "confidence": "CERTO",
        "route_steps": [
            {"seq": 1, "station": "ZAW1", "status": "CERTO"},
            {"seq": 2, "station": "ZAW2", "status": "CERTO"},
            {"seq": 3, "station": "PIDMILL", "status": "CERTO"},
            {"seq": 4, "station": "CP", "status": "CERTO"},
        ],
        "constraints": {
            "has_henn": False,
            "cp_required": True,
        },
        "components": ["468791", "468948", "SAGOMA"],
        "packaging": {
            "sacchetto": "467660",
            "imballo": "6429",
            "quantita_per_imballo": 8,
        },
    }
    (article_dir / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12056?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "Route: ZAW1 → ZAW2 → PIDMILL → CP" in data["answer"]
    assert "classe STANDARD, planner_eligible=true" in data["answer"]
    assert "componenti noti" in data["answer"]
    assert "packaging" in data["answer"]
    assert "HENN assente sul singolo" in data["answer"]
    assert "CP finale obbligatorio" in data["answer"]


def test_tl_chat_local_specs_metadata_shows_henn_present(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12057"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12057",
        "drawing": "A2145013001",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_status": "CERTO",
        "confidence": "CERTO",
        "route_steps": [
            {"seq": 1, "station": "MARCATURA", "status": "CERTO"},
            {"seq": 2, "station": "HENN", "status": "CERTO"},
            {"seq": 3, "station": "CP", "status": "CERTO"},
        ],
        "constraints": {
            "has_henn": True,
            "cp_required": True,
        },
    }
    (article_dir / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12057?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "Route: MARCATURA → HENN → CP" in data["answer"]
    assert "HENN presente" in data["answer"]
    assert "CP finale obbligatorio" in data["answer"]


def test_tl_chat_local_specs_metadata_shows_guaina_and_zaw_specificity(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12058"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12058",
        "drawing": "A2145013001",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_status": "CERTO",
        "confidence": "CERTO",
        "route_steps": [
            {"seq": 1, "station": "GUAINA", "status": "CERTO"},
            {"seq": 2, "station": "MARCATURA", "status": "CERTO"},
            {"seq": 3, "station": "ZAW", "status": "CERTO"},
            {"seq": 4, "station": "CP", "status": "CERTO"},
        ],
        "constraints": {
            "has_henn": False,
            "has_guaina": True,
            "zaw_station_specificity": "DA_VERIFICARE",
            "cp_required": True,
        },
    }
    (article_dir / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12058?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "Route: GUAINA → MARCATURA → ZAW → CP" in data["answer"]
    assert "HENN assente sul singolo" in data["answer"]
    assert "GUAINA presente" in data["answer"]
    assert "specificità ZAW da verificare" in data["answer"]
    assert "CP finale obbligatorio" in data["answer"]


def test_tl_chat_uses_preview_for_da_verificare_article(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    preview = tmp_path / "article_route_matrix.preview.json"
    preview.write_text(
        json.dumps(
            {
                "profiles": {
                    "99998": {
                        "article": "99998",
                        "confidence": "DA_VERIFICARE",
                        "signals": {
                            "has_henn": False,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "zaw_passes": 2,
                            "has_pidmill": True,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_components": ["468796"],
                        },
                        "review_reasons": ["discrepancies_to_verify"],
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "wrong_source": "BOM_Specs.csv famiglia_processo=PIDMILL_ZAW2",
                                "status": "DA_VERIFICARE",
                            }
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "99998?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert "Profilo non operativo" in data["answer"]
    assert "discrepancies_to_verify" in data["answer"]
    assert "PIDMILL_ZAW2" in data["answer"]
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

def test_tl_chat_answers_12402_confirmed_double_zaw_pidmill_profile(monkeypatch, tmp_path):
    import importlib
    import json

    import app.domain.article_process_matrix as apm
    import app.domain.article_tl_summary as ats
    from app.api import tl_chat as tl_chat_api

    env_base = tmp_path / "env_base"
    matrix_path = env_base / "finiture" / "article_route_matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)

    matrix_path.write_text(
        json.dumps(
            {
                "version": "0.1",
                "profiles": {
                    "12402": {
                        "article": "12402",
                        "confidence": "CERTO",
                        "route": [
                            "MARCATURA",
                            "INNESTO_RAPIDO_1",
                            "CRIMP_RING_ZAW_1",
                            "INNESTO_RAPIDO_2",
                            "CRIMP_RING_ZAW_2",
                            "PIDMILL_MOLLETTA",
                            "PIDMILL_GOMMOTTO",
                            "COLLAUDO_PRESSIONE",
                        ],
                        "signals": {
                            "has_henn": False,
                            "has_zaw1": True,
                            "has_zaw2": False,
                            "primary_zaw_station": "ZAW1",
                            "zaw_passes": 2,
                            "has_pidmill": True,
                            "cp_required": True,
                            "cp_machine_mode": "VERTICALE_DUE_PIANI",
                            "shared_components": ["468796"],
                        },
                        "discrepancies": [
                            {
                                "code": "bom_family_process_mismatch",
                                "correct_value": "ZAW1_DOPPIO_PASSAGGIO_PIDMILL",
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
    importlib.reload(tl_chat_api)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12402?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert "12402" in data["answer"]
    assert "ZAW1 con 2 passaggi" in data["answer"]
    assert "ZAW1_2 non è ZAW2" in data["answer"]
    assert "HENN assente/non indicato" in data["answer"]
    assert "PIDMILL presente" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "468796" in data["answer"]
    assert "ZAW1_DOPPIO_PASSAGGIO_PIDMILL" in data["answer"]
    assert data["requires_confirmation"] is False
    assert data["technical_details_hidden"] is True
