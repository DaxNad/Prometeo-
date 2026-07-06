from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import tl_chat as tl_chat_api


def _evidence_item(source_id: str, source_type: str = "existing") -> dict:
    return {
        "source_id": source_id,
        "source_type": source_type,
        "authority_rank": 10,
        "confidence": "PREVIEW_ONLY",
        "text": f"Evidence {source_id}",
        "reason": "test evidence",
    }


def test_tl_chat_runtime_evidence_merge_preserves_existing_when_not_full():
    pack = {
        "evidence": [
            _evidence_item("existing:1"),
            _evidence_item("existing:2"),
        ]
    }
    runtime = [_evidence_item("runtime:1", "ARTICLE_SUMMARY")]

    result = tl_chat_api._merge_runtime_evidence(pack, runtime, limit=5)

    assert [item["source_id"] for item in result["evidence"]] == [
        "existing:1",
        "existing:2",
        "runtime:1",
    ]
    assert len(result["evidence"]) <= 5


def test_tl_chat_runtime_evidence_merge_replaces_only_last_when_full():
    pack = {
        "evidence": [
            _evidence_item("existing:1"),
            _evidence_item("existing:2"),
            _evidence_item("existing:3"),
            _evidence_item("existing:4"),
            _evidence_item("existing:5"),
        ]
    }
    runtime = [_evidence_item("runtime:1", "ARTICLE_SUMMARY")]

    result = tl_chat_api._merge_runtime_evidence(pack, runtime, limit=5)

    assert [item["source_id"] for item in result["evidence"]] == [
        "existing:1",
        "existing:2",
        "existing:3",
        "existing:4",
        "runtime:1",
    ]
    assert len(result["evidence"]) == 5


def test_tl_chat_runtime_evidence_merge_deduplicates_by_source_id_and_type():
    duplicate = _evidence_item("same", "ARTICLE_SUMMARY")
    pack = {"evidence": [duplicate]}
    runtime = [_evidence_item("same", "ARTICLE_SUMMARY")]

    result = tl_chat_api._merge_runtime_evidence(pack, runtime, limit=5)

    assert result["evidence"] == [duplicate]


def test_tl_chat_runtime_evidence_merge_keeps_pack_identical_when_runtime_empty():
    evidence = [_evidence_item("existing:1")]
    pack = {"evidence": evidence}

    result = tl_chat_api._merge_runtime_evidence(pack, [], limit=5)

    assert result is pack
    assert result["evidence"] is evidence


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
    assert "NON DISPONIBILE NEL PROFILO ATTIVO" in data["answer"]
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

def test_tl_chat_contract_turn_question_without_article_does_not_generate_priority():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa faccio adesso?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "senza articolo" in data["answer"].lower()
    assert "non genero priorità automatica" in data["answer"].lower()
    assert "codice articolo" in data["recommended_action"].lower()
    assert "ordine" in data["recommended_action"].lower()
    assert "lotto" in data["recommended_action"].lower()


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



def test_tl_chat_contract_lists_local_intake_new_entry_candidates(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")

    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    intake.write_text(
        json.dumps(
            {
                "id": "TL_REAL_SPEC_INTAKE_001",
                "scope": "local_preview_only",
                "planner_auto_allowed": False,
                "items": [
                    {
                        "article": "12589",
                        "initial_classification": "NEW_ENTRY_CANDIDATE_ZAW",
                        "confidence": "DA_VERIFICARE",
                    },
                    {
                        "article": "12511",
                        "initial_classification": "NEW_ENTRY_CANDIDATE_COMPLESSO",
                        "confidence": "DA_VERIFICARE",
                    },
                    {
                        "article": "12066",
                        "initial_classification": "STANDARD",
                        "confidence": "CERTO",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)

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
    assert "12589" in data["answer"]
    assert "12511" in data["answer"]
    assert "12066" not in data["answer"]
    assert "intake locale" in data["answer"].lower()
    assert "nessuna pianificazione automatica" in data["risk"].lower()


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


def test_tl_chat_contract_lists_customer_request_only_with_fuori_produzione(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12402": {
                    "status": "CUSTOMER_REQUEST_ONLY",
                    "source": "tl",
                    "note": "Fuori produzione standard, producibile solo su richiesta cliente.",
                },
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
    assert "12402" in data["answer"]
    assert "12410" not in data["answer"]
    assert "richiesta cliente" in data["answer"].lower()
    assert "non devono essere promossi automaticamente" in data["risk"].lower()
    assert "conferma TL" in data["recommended_action"]

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
    import app.domain.article_profile_resolver as apr
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
    importlib.reload(apr)
    importlib.reload(ats)
    importlib.reload(tl_chat_api)
    monkeypatch.setattr(apr, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12066?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"

    answer = data["answer"]
    assert answer.startswith("12066 — CERTO.")
    assert "Route:" in answer
    assert "Vincoli:" in answer
    assert "Nota:" not in answer
    assert "Azione:" in answer
    assert answer.index("Route:") < answer.index("Vincoli:")
    assert answer.index("Vincoli:") < answer.index("Azione:")

    assert "Route: HENN → ZAW1 → PIDMILL → CP." in answer
    assert "HENN prima di ZAW" in answer
    assert "ZAW1 obbligatorio" in answer
    assert "ZAW2 non valida" in answer
    assert "CP finale" in answer
    assert "BOM discordante" in answer
    assert "468728" in answer
    assert "468796" in answer
    assert "ordine attivo" in answer

    assert "\n" not in answer
    assert len(answer) <= 260
    assert "VERTICALE_DUE_PIANI" not in answer
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

    import app.domain.article_profile_resolver as resolver

    monkeypatch.setattr(resolver, "SPECS_ROOT", tmp_path / "missing_specs_finitura")
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "missing_specs_finitura")
    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))
    importlib.reload(apm)
    importlib.reload(ats)
    importlib.reload(tl_chat_api)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "missing_specs_finitura")

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

    import app.domain.article_profile_resolver as resolver

    monkeypatch.setattr(resolver, "SPECS_ROOT", tmp_path / "missing_specs_finitura")
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "missing_specs_finitura")
    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))
    importlib.reload(apm)
    importlib.reload(ats)
    importlib.reload(tl_chat_api)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "missing_specs_finitura")

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
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

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


def test_tl_chat_local_specs_confidence_uses_semantic_registry_fallback(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12991"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12991",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_status": "DA_VERIFICARE",
        "confidence": "TL_DA_DOCUMENTARE",
        "route_steps": [{"seq": 1, "station": "ZAW1", "status": "DA_VERIFICARE"}],
        "constraints": {},
    }
    (article_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "12991?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["answer"].startswith("12991 — DA_VERIFICARE.")
    assert data["requires_confirmation"] is True


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


def test_tl_chat_operational_v2_contract_for_local_metadata(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12999"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12999",
        "drawing": "MOCKDRAWING",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "route_status": "CERTO",
        "confidence": "CERTO",
        "route_steps": [
            {"seq": 1, "station": "HENN", "status": "CERTO"},
            {"seq": 2, "station": "ZAW1", "status": "CERTO"},
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
    res = client.post("/tl/chat", json={"question": "12999?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False

    answer = data["answer"]
    assert answer.startswith("12999 — CERTO.")
    assert "Route:" in answer
    assert "Vincoli:" in answer
    assert "Nota:" not in answer
    assert "Azione:" in answer
    assert "Route: HENN → ZAW1 → CP." in answer
    assert "disegno MOCKDRAWING" in answer
    assert "classe STANDARD, planner_eligible=true" in answer
    assert "Azione: usare route confermata." in answer


def test_tl_chat_operational_answer_formatter_shape_is_brief_and_actionable():
    from app.api.tl_chat import _format_operational_answer

    answer = _format_operational_answer(
        article="ITEM_SHAPE",
        confidence="CERTO",
        route="HENN → ZAW1 → CP",
        constraints=["CP finale obbligatorio", "ZAW2 non inferita"],
        note="profilo operativo confermato",
        action="usare route confermata",
    )

    assert answer.startswith("ITEM_SHAPE — CERTO.")
    assert "Route:" in answer
    assert "Vincoli:" in answer
    assert "Nota:" not in answer
    assert "Azione:" in answer

    assert answer.index("Route:") < answer.index("Vincoli:")
    assert answer.index("Vincoli:") < answer.index("Azione:")

    assert "Route: HENN → ZAW1 → CP." in answer
    assert "Vincoli: CP finale obbligatorio; ZAW2 non inferita; profilo operativo confermato." in answer
    assert "Azione: usare route confermata." in answer

    assert "\n" not in answer
    assert len(answer) <= 260
    assert "git" not in answer.lower()
    assert "pytest" not in answer.lower()
    assert "runtime" not in answer.lower()
    assert "frontend" not in answer.lower()


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
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

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


def test_tl_chat_preview_confidence_uses_semantic_registry_fallback(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    preview = tmp_path / "article_route_matrix.preview.json"
    preview.write_text(
        json.dumps(
            {
                "profiles": {
                    "99997": {
                        "article": "99997",
                        "confidence": "NON_CANONICO",
                        "signals": {},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

    client = TestClient(app)
    res = client.post("/tl/chat", json={"question": "99997?"})
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert "Profilo non operativo" in data["answer"]
    assert data["requires_confirmation"] is True


def test_tl_chat_reference_only_confirmed_route_still_requires_tl_confirmation(monkeypatch, tmp_path):
    specs_root = tmp_path / "specs_finitura"
    article_dir = specs_root / "12402"
    article_dir.mkdir(parents=True)

    metadata = {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": "12402",
        "confidence": "CERTO",
        "route_status": "CERTO",
        "operational_class": "REFERENCE_ONLY",
        "planner_eligible": False,
        "route_steps": [
            {"station": "LAVAGGIO"},
            {"station": "ZAW1"},
            {"station": "ZAW1"},
            {"station": "PIDMILL"},
            {"station": "CP"},
        ],
        "constraints": {
            "has_henn": False,
            "has_pidmill": True,
            "primary_zaw_station": "ZAW1",
            "zaw_passes": 2,
            "has_zaw2": False,
            "cp_required": True,
            "cp_mode": "VERTICALE",
            "cp_pieces_per_plane": 2,
        },
    }

    (article_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)

    client = TestClient(app)
    response = client.post("/tl/chat", json={"question": "Il 12402 è da verificare?"})

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "route CERTO" in data["answer"]
    assert "REFERENCE_ONLY" in data["answer"]
    assert "planner_eligible=false" in data["answer"]
    assert "Non va pianificato automaticamente" in data["answer"]
    assert "richiesta cliente esplicita" in data["recommended_action"].lower()
    assert "conferma TL" in data["recommended_action"]


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


def test_tl_chat_answers_zaw_interchangeability_without_article():
    client = TestClient(app)

    res = client.post(
        "/tl/chat",
        json={"question": "ZAW1 e ZAW2 sono intercambiabili?"},
    )
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "non sono intercambiabili" in data["answer"]
    assert "ZAW1_2" in data["answer"]
    assert "non ZAW2" in data["answer"]


def test_tl_chat_answers_turn_question_without_article_with_safe_checklist():
    client = TestClient(app)

    res = client.post(
        "/tl/chat",
        json={"question": "Cosa conviene controllare adesso sul turno?"},
    )
    data = res.json()

    assert res.status_code == 200
    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "Domanda turno senza articolo" in data["answer"]
    assert "non genero priorità automatica" in data["answer"].lower()
    assert "codice articolo" in data["answer"].lower()
    assert "evento aperto" in data["answer"].lower()
    assert "ordine" in data["answer"].lower()
    assert "lotto" in data["answer"].lower()
    assert "12066" not in data["answer"]
    assert "12100" not in data["answer"]
    assert "Nota:" not in data["answer"]


def test_tl_chat_contract_turn_question_requires_operational_context():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa faccio partire adesso?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True

    text = (
        data["answer"] + " " +
        str(data.get("recommended_action") or "")
    ).lower()

    assert "non genero priorità automatica" in text
    assert "codice articolo" in text
    assert "ordine" in text
    assert "lotto" in text


def test_tl_chat_contract_zaw1_load_does_not_allow_auto_move_to_zaw2():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Ho ZAW1 piena, posso spostare su ZAW2?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True

    text = (
        data["answer"] + " " +
        str(data.get("recommended_action") or "")
    ).lower()

    assert "zaw1" in text
    assert "zaw2" in text
    assert (
        "non intercambiabili" in text
        or "non usare zaw2 come alternativa automatica" in text
        or "non spostare" in text
    )


def test_tl_chat_contract_zaw2_ambiguous_question_stays_safe():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Questo va su ZAW2?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"

    text = (
        data["answer"] + " " +
        str(data.get("recommended_action") or "")
    ).lower()

    assert (
        "codice articolo" in text
        or "contesto" in text
        or "ripetere la domanda" in text
    )


def test_tl_chat_contract_article_summary_preserves_core_domain_constraints(monkeypatch):
    def fake_summary(article: str):
        assert article == "12100"
        return {
            "ok": True,
            "confidence": "CERTO",
            "route": ["HENN", "ZAW1", "PIDMILL", "COLLAUDO_PRESSIONE"],
            "planner_eligible": True,
            "signals": {
                "has_henn": True,
                "primary_zaw_station": "ZAW1",
                "zaw_passes": 1,
                "has_zaw2": False,
                "has_pidmill": True,
                "cp_required": True,
            },
            "criticalities": [],
            "tl_action": "Seguire route confermata.",
        }

    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", fake_summary)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "12100?",
            "context": {"article": "12100"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True

    text = data["answer"].lower()

    assert "henn" in text
    assert "zaw1" in text
    assert "pidmill" in text
    assert "cp" in text or "collaudo" in text
    assert "zaw2 obbligatorio" not in text


def test_tl_chat_rendering_article_summary_uses_shift_trust_sections(monkeypatch):
    def fake_summary(article: str):
        assert article == "12100"
        return {
            "ok": True,
            "confidence": "CERTO",
            "route": ["HENN", "ZAW1", "PIDMILL", "COLLAUDO_PRESSIONE"],
            "planner_eligible": True,
            "signals": {
                "has_henn": True,
                "primary_zaw_station": "ZAW1",
                "zaw_passes": 1,
                "has_zaw2": False,
                "has_pidmill": True,
                "cp_required": True,
            },
            "criticalities": [],
            "tl_action": "Seguire route confermata.",
        }

    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", fake_summary)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "12100?",
            "context": {"article": "12100"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    answer = data["answer"]

    assert "Azione:" in answer
    assert "Vincoli:" in answer
    assert "HENN" in answer
    assert "ZAW1" in answer
    assert "PIDMILL" in answer
    assert "CP" in answer or "collaudo" in answer.lower()


def test_tl_chat_rendering_turn_fallback_uses_non_decido_sections():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa faccio partire adesso?"},
    )

    assert response.status_code == 200
    data = response.json()

    answer = data["answer"]

    assert "NON DECIDO" in answer
    assert "DATO MANCANTE:" in answer
    assert "DOMANDA TL:" in answer
    assert "codice articolo" in answer.lower()
    assert "ordine" in answer.lower()
    assert "lotto" in answer.lower()


def test_tl_chat_attaches_governed_evidence_pack_preview_only():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Spiegami confidence CERTO INFERITO DA_VERIFICARE"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["technical_details_hidden"] is True

    evidence_pack = data["evidence_pack"]
    assert evidence_pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert evidence_pack["question"] == "Spiegami confidence CERTO INFERITO DA_VERIFICARE"
    assert evidence_pack["article"] is None
    assert "no LLM calls" in evidence_pack["constraints"]
    assert "no DB writes" in evidence_pack["constraints"]
    assert "no SMF writes" in evidence_pack["constraints"]

    semantic_items = [
        item for item in evidence_pack["evidence"]
        if item["source_type"] == "semantic_registry_confidence"
    ]
    assert semantic_items
    assert all(item["confidence"] == "PREVIEW_ONLY" for item in semantic_items)


def test_tl_chat_contract_answers_article_from_spec_intake_preview(monkeypatch, tmp_path):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True, exist_ok=True)

    preview_file = preview_root / "12514_metadata_preview.json"
    preview_file.write_text(
        json.dumps(
            {
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
                    "rev": "6",
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "12514"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

    assert data["source"] == "spec_intake_preview"
    assert data["source_status"] == "PREVIEW_ONLY"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["missing_data"] == []

    assert "Articolo 12514" in data["answer"]
    assert "Dati disponibili:" in data["answer"]
    assert "Fonte:" in data["answer"]
    assert "Stato:" in data["answer"]
    assert "Affidabilità:" in data["answer"]
    assert "Dati mancanti:" in data["answer"]
    assert "Prossima azione sicura:" in data["answer"]
    assert "7056055000A0" in data["answer"]
    assert "A1675003603" in data["answer"]
    assert "planner_eligible=false" not in data["answer"]
    assert "requires_tl_confirmation=true" not in data["answer"]
    assert "can_promote=false" not in data["answer"]

    assert "pianificazione" in data["risk"].lower()
    assert "team leader" in data["recommended_action"].lower()

def test_tl_chat_uses_governed_retrieval_when_no_article_context():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Spiegami confidence CERTO INFERITO DA_VERIFICARE"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "Fonte governata read-only" in data["answer"]
    assert "semantic_registry_confidence" in data["answer"]
    assert "Limite:" in data["answer"]
    assert data["evidence_pack"]["mode"] == "GOVERNED_RETRIEVAL_001"
    assert data["evidence_pack"]["article"] is None
    assert "no LLM calls" in data["evidence_pack"]["constraints"]
    assert "no DB writes" in data["evidence_pack"]["constraints"]
    assert "no SMF writes" in data["evidence_pack"]["constraints"]

def test_tl_chat_contract_uses_context_reader_bridge_for_governed_source_question(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Mostrami la fonte governata retrieval per 99999",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

    assert "Answer:" in data["answer"]
    assert "Source:" in data["answer"]
    assert "Confidence:" in data["answer"]
    assert "Missing data:" in data["answer"]
    assert "Next safe action:" in data["answer"]

    assert "fonte governata read-only disponibile" in data["answer"]
    assert "contenuto tecnico sintetizzato" in data["answer"]
    assert "Source: context_access_binding" in data["answer"]
    assert "can_promote=false" in data["answer"]
    assert "planner_eligible=false" in data["answer"]
    assert "nessuna promozione a CERTO" in data["answer"]
    assert "nessuna decisione automatica" in data["answer"]
    assert "NON DISPONIBILE NEL PROFILO ATTIVO" not in data["answer"]


def test_tl_chat_real_question_validation_contract_001(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    route_preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    preview_root.mkdir(parents=True, exist_ok=True)
    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(
            {
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
                    "rev": "6",
                },
            }
        ),
        encoding="utf-8",
    )

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    route_preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", route_preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    client = TestClient(app)

    scenarios = [
        {
            "name": "unknown article status",
            "payload": {
                "question": "Il codice 99999 è attivo?",
                "context": {"article": "99999"},
            },
            "required": ["DA_VERIFICARE"],
            "forbidden": ["priorità automatica", "planner_eligible=true"],
        },
        {
            "name": "generic turn decision without article",
            "payload": {"question": "Cosa faccio partire adesso?"},
            "required": ["NON DECIDO", "DATO MANCANTE:", "codice articolo", "ordine", "lotto"],
            "forbidden": ["12066", "12100"],
        },
        {
            "name": "governed source request",
            "payload": {
                "question": "Mostrami la fonte governata retrieval per 99999",
                "context": {"article": "99999"},
            },
            "required": ["Answer:", "Source:", "Confidence:", "Missing data:", "Next safe action:"],
            "forbidden": ["can_promote=true", "planner_eligible=true"],
        },
        {
            "name": "confidence semantics",
            "payload": {"question": "Spiegami confidence CERTO INFERITO DA_VERIFICARE"},
            "required": ["Fonte governata read-only", "semantic_registry_confidence", "Limite:"],
            "forbidden": ["scrittura abilitata", "decisione automatica operativa"],
        },
        {
            "name": "article-specific preview question",
            "payload": {"question": "Cosa sai del 12514?"},
            "required": [
                "Articolo 12514",
                "7056055000A0",
                "A1675003603",
                "Prossima azione sicura",
            ],
            "forbidden": [
                "planner_eligible=true",
                "planner_eligible=false",
                "requires_tl_confirmation=true",
                "can_promote=true",
                "can_promote=false",
            ],
        },
    ]

    for scenario in scenarios:
        response = client.post("/tl/chat", json=scenario["payload"])
        assert response.status_code == 200, scenario["name"]

        data = response.json()
        assert data["ok"] is True, scenario["name"]
        assert data["mode"] == "TL_CHAT_CONTRACT_V1", scenario["name"]
        assert data["confidence"] == "DA_VERIFICARE", scenario["name"]
        assert data["requires_confirmation"] is True, scenario["name"]
        assert data["technical_details_hidden"] is True, scenario["name"]

        surface = " ".join(
            [
                str(data.get("answer") or ""),
                str(data.get("risk") or ""),
                str(data.get("recommended_action") or ""),
                str(data.get("confidence") or ""),
                json.dumps(data.get("evidence_pack") or {}, sort_keys=True),
            ]
        )

        for expected in scenario["required"]:
            assert expected in surface, scenario["name"]

        lowered_surface = surface.lower()
        for forbidden in scenario["forbidden"]:
            assert forbidden.lower() not in lowered_surface, scenario["name"]




def test_tl_chat_mixed_system_map_and_confidence_evidence_keeps_primary_source_traceability():
    response = tl_chat_api._response_from_governed_evidence_pack(
        evidence_pack={
            "mode": "GOVERNED_RETRIEVAL_001",
            "question": "Spiegami planner confidence",
            "article": None,
            "constraints": ["no LLM calls", "no DB writes", "no SMF writes"],
            "evidence": [
                {
                    "source_id": "docs/prometeo_system_map.md",
                    "source_type": "system_map",
                    "confidence": "PREVIEW_ONLY",
                    "text": "Planner e confidence sono concetti governati nel system map.",
                },
                {
                    "source_id": "semantic_registry_confidence:CERTO",
                    "source_type": "semantic_registry_confidence",
                    "confidence": "PREVIEW_ONLY",
                    "text": "CERTO: dato confermato da fonte reale.",
                },
                {
                    "source_id": "semantic_registry_confidence:INFERITO",
                    "source_type": "semantic_registry_confidence",
                    "confidence": "PREVIEW_ONLY",
                    "text": "INFERITO: dato dedotto da contesto governato.",
                },
                {
                    "source_id": "semantic_registry_confidence:DA_VERIFICARE",
                    "source_type": "semantic_registry_confidence",
                    "confidence": "PREVIEW_ONLY",
                    "text": "DA_VERIFICARE: dato non confermato.",
                },
            ],
        }
    )

    assert response is not None
    assert response.ok is True
    assert response.confidence == "DA_VERIFICARE"
    assert response.requires_confirmation is True
    assert response.technical_details_hidden is True

    assert "Fonte governata read-only: docs/prometeo_system_map.md" in response.answer
    assert "Tipo fonte: system_map" in response.answer
    assert "Confidence fonte: PREVIEW_ONLY" in response.answer
    assert "Planner e confidence sono concetti governati nel system map." in response.answer

    assert "CERTO:" not in response.answer
    assert "INFERITO:" not in response.answer
    assert "DA_VERIFICARE:" not in response.answer
    assert "semantic_registry_confidence" not in response.answer

    assert "nessuna promozione a CERTO" in response.answer
    assert "nessuna scrittura" in response.answer
    assert "nessuna decisione automatica" in response.answer


def test_tl_chat_real_question_keeps_primary_source_traceability():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Spiegami planner confidence"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True

    evidence_pack = data["evidence_pack"]
    evidence = evidence_pack["evidence"]
    assert evidence[0]["source_id"] == "docs/prometeo_system_map.md"
    assert evidence[0]["source_type"] == "system_map"

    answer = data["answer"]
    assert "Fonte governata read-only: docs/prometeo_system_map.md" in answer
    assert "Tipo fonte: system_map" in answer
    assert evidence[0]["text"] in answer

    assert "semantic_registry_confidence" not in answer
    assert "CERTO:" not in answer
    assert "INFERITO:" not in answer
    assert "DA_VERIFICARE:" not in answer


def test_tl_chat_real_question_rendering_improvement_001(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    route_preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    route_preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", route_preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    client = TestClient(app)

    unknown_response = client.post(
        "/tl/chat",
        json={
            "question": "Il codice 99999 è attivo?",
            "context": {"article": "99999"},
        },
    )
    assert unknown_response.status_code == 200
    unknown_data = unknown_response.json()

    assert unknown_data["ok"] is True
    assert unknown_data["confidence"] == "DA_VERIFICARE"
    assert unknown_data["requires_confirmation"] is True
    assert "NON DISPONIBILE NEL PROFILO ATTIVO" in unknown_data["answer"]
    assert unknown_data["recommended_action"]
    assert "fonte autorizzata" in unknown_data["recommended_action"]
    assert "non trattare come attivo" in unknown_data["recommended_action"]

    source_response = client.post(
        "/tl/chat",
        json={
            "question": "Mostrami la fonte governata retrieval per 99999",
            "context": {"article": "99999"},
        },
    )
    assert source_response.status_code == 200
    source_data = source_response.json()

    assert source_data["ok"] is True
    assert source_data["confidence"] == "DA_VERIFICARE"
    assert source_data["requires_confirmation"] is True
    assert "Answer:" in source_data["answer"]
    assert "Source:" in source_data["answer"]
    assert "Confidence:" in source_data["answer"]
    assert "Missing data:" in source_data["answer"]
    assert "Next safe action:" in source_data["answer"]
    assert "contenuto tecnico sintetizzato" in source_data["answer"]
    assert "can_promote=false" in source_data["answer"]
    assert "planner_eligible=false" in source_data["answer"]
    assert "nessuna promozione a CERTO" in source_data["answer"]
    assert "nessuna decisione automatica" in source_data["answer"]
    assert "TL_CHAT_CONTEXT_RETRIEVAL" not in source_data["answer"]
    assert "BEGIN" not in source_data["answer"]
    assert "END" not in source_data["answer"]

    confidence_response = client.post(
        "/tl/chat",
        json={"question": "Spiegami confidence CERTO INFERITO DA_VERIFICARE"},
    )
    assert confidence_response.status_code == 200
    confidence_data = confidence_response.json()

    assert confidence_data["ok"] is True
    assert confidence_data["confidence"] == "DA_VERIFICARE"
    assert confidence_data["requires_confirmation"] is True
    assert "CERTO:" in confidence_data["answer"]
    assert "INFERITO:" in confidence_data["answer"]
    assert "DA_VERIFICARE:" in confidence_data["answer"]
    assert "nessuna promozione a CERTO" in confidence_data["answer"]
    assert "nessuna scrittura" in confidence_data["answer"]
    assert "nessuna decisione automatica" in confidence_data["answer"]

def test_tl_chat_12514_confirmation_rendering_api_binding_returns_candidate_only(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    preview_payload = {
        "status": "PREVIEW_ONLY",
        "confidence": "DA_VERIFICARE",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "article": {
            "articolo": "12514",
            "codice": "7056055000A0",
            "disegno": "A1675003603",
            "rev": "6",
        },
    }
    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(preview_payload),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(
        tl_chat_api,
        "CONFIRMATION_12514_PATH",
        tmp_path / "spec_intake_confirmation" / "missing_12514_confirmation.json",
    )
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Render conferma TL per articolo 12514",
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "Articolo: 12514" in data["answer"]
    assert "Domanda: Q1 - article_identity" in data["answer"]
    assert "Risposta TL: UNKNOWN" in data["answer"]
    assert "Stato risultante: DA_VERIFICARE" in data["answer"]
    assert "codice 7056055000A0" in data["answer"]
    assert "disegno A1675003603" in data["answer"]
    assert "rev 6" in data["answer"]
    assert "Confidenza: DA_VERIFICARE" in data["answer"]
    assert "Effetti runtime: nessuna persistenza" in data["answer"]
    assert "nessuna mutazione sorgente" in data["answer"]
    assert "nessuna promozione a CERTO" in data["answer"]
    assert "nessun planner" in data["answer"]
    assert "nessun ATLAS" in data["answer"]
    assert "nessuna scrittura SMF/DB" in data["answer"]
    assert "non persistente" in data["risk"]
    assert "non autorizza pianificazione" in data["risk"]
    assert "non produce effetti operativi" in data["risk"]
    assert "non persistere" in data["recommended_action"]
    assert "promuovere a CERTO" in data["recommended_action"]


def test_tl_chat_12514_confirmation_rendering_api_binding_keeps_preview_fallback(monkeypatch, tmp_path):
    import json

    from app.api import tl_chat as tl_chat_api

    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    preview_payload = {
        "status": "PREVIEW_ONLY",
        "confidence": "DA_VERIFICARE",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "article": {
            "articolo": "12514",
            "codice": "7056055000A0",
            "disegno": "A1675003603",
            "rev": "6",
        },
    }
    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(preview_payload),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Cosa sai del 12514?",
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["source"] == "spec_intake_preview"
    assert data["source_status"] == "PREVIEW_ONLY"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["missing_data"] == []
    assert "Dati disponibili:" in data["answer"]
    assert "Fonte:" in data["answer"]
    assert "- spec_intake_preview" in data["answer"]
    assert "planner_eligible=" not in data["answer"]
    assert "requires_tl_confirmation=" not in data["answer"]
    assert "can_promote=" not in data["answer"]
    assert "Codice cliente: 7056055000A0" in data["answer"]
    assert "Disegno: A1675003603, revisione 6" in data["answer"]
    assert "Articolo: 12514" not in data["answer"]
    assert "Effetti runtime:" not in data["answer"]

def test_tl_chat_12514_confirmation_rendering_reads_persisted_evidence_without_promotion(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    preview_payload = {
        "status": "PREVIEW_ONLY",
        "confidence": "DA_VERIFICARE",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "article": {
            "articolo": "12514",
            "codice": "7056055000A0",
            "disegno": "A1675003603",
            "rev": "6",
        },
    }
    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(preview_payload),
        encoding="utf-8",
    )

    confirmation_path = tmp_path / "spec_intake_confirmation" / "12514_confirmation.json"
    confirmation_path.parent.mkdir(parents=True)
    confirmation_path.write_text(
        json.dumps(
            {
                "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
                "article": "12514",
                "source_capability": "TL_CHAT_12514_CONFIRMATION_STRUCTURED_INPUT_001",
                "confirmation_status": "TL_CONFIRMED_PREVIEW",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "promoted_to_certo": False,
                "requires_persistence_review": True,
                "confirmed_fields": ["codice", "disegno", "rev"],
                "confirmed_by_role": "TL",
                "notes": "Conferma TL persistita come evidenza locale",
                "created_at": "2026-06-29T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "CONFIRMATION_12514_PATH", confirmation_path)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Render conferma TL per articolo 12514",
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

    assert "Articolo: 12514" in data["answer"]
    assert "Evidenza TL persistita: presente" in data["answer"]
    assert "TL_CONFIRMED_PREVIEW" in data["answer"]
    assert "confirmed_fields: codice, disegno, rev" in data["answer"]
    assert "requires_persistence_review=true" in data["answer"]
    assert "planner_eligible=false" in data["answer"]
    assert "promoted_to_certo=false" in data["answer"]

    assert "DA_VERIFICARE" in data["risk"]
    assert "non autorizza pianificazione" in data["risk"]
    assert "non produce effetti operativi" in data["risk"]

def test_tl_chat_contract_context_reader_unavailable_stays_verifiable(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    def unavailable_candidate(*, source_id, article, adapter=None, include_excerpt=True, max_chars=500):
        return tl_chat_api.TLChatContextCandidate(
            source_name="context_source_reader_adapter",
            source_status="SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
            confidence="DA_VERIFICARE",
            payload={
                "article": article,
                "source_id": source_id,
                "error_code": "INDEX_NOT_FOUND",
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    monkeypatch.setattr(tl_chat_api, "build_context_reader_candidate", unavailable_candidate)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Mostrami la fonte governata retrieval per 99999",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "SOURCE_AUTHORIZED_BUT_UNAVAILABLE" in data["answer"]
    assert "planner_eligible=true" not in data["answer"]
    assert "can_promote=true" not in data["answer"]
    assert "CERTO" not in data["confidence"]


def test_tl_chat_context_reader_preserves_error_code_internally_without_public_field(monkeypatch):
    def fake_adapter(*args, **kwargs):
        return object()

    def unavailable_candidate(*, source_id, article, adapter=None, include_excerpt=True, max_chars=500):
        return tl_chat_api.TLChatContextCandidate(
            source_name="context_source_reader_adapter",
            source_status="SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
            confidence="DA_VERIFICARE",
            payload={
                "article": article,
                "source_id": source_id,
                "error_code": "INDEX_NOT_FOUND",
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    monkeypatch.setattr(tl_chat_api, "ContextSourceReaderAdapter", fake_adapter)
    monkeypatch.setattr(tl_chat_api, "build_context_reader_candidate", unavailable_candidate)

    response = tl_chat_api._response_from_context_reader_bridge("99999")

    assert response is not None
    assert response.confidence == "DA_VERIFICARE"
    assert response.requires_confirmation is True
    assert response._error_code == "INDEX_NOT_FOUND"
    assert "error_code" not in response.model_dump()
    assert "INDEX_NOT_FOUND" not in response.model_dump_json()


def test_tl_chat_contract_context_reader_forbidden_does_not_expose_content(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    def forbidden_candidate(*, source_id, article, adapter=None, include_excerpt=True, max_chars=500):
        return tl_chat_api.TLChatContextCandidate(
            source_name="context_source_reader_adapter",
            source_status="SOURCE_FORBIDDEN",
            confidence="DA_VERIFICARE",
            payload={
                "article": article,
                "source_id": source_id,
                "error_code": "SOURCE_NOT_ALLOWED",
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    monkeypatch.setattr(tl_chat_api, "build_context_reader_candidate", forbidden_candidate)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Mostrami la fonte governata retrieval per 99999",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "SOURCE_FORBIDDEN" in data["answer"]
    assert "contenuto tecnico sintetizzato" not in data["answer"]
    assert "../" not in data["answer"]
    assert ("/" + "Users/") not in data["answer"]
    assert "planner_eligible=true" not in data["answer"]
    assert "can_promote=true" not in data["answer"]


def test_tl_chat_contract_preview_source_is_not_bypassed_by_context_reader(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"
    specs_root = tmp_path / "specs"
    preview_root = tmp_path / "spec_intake_preview"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")
    preview_root.mkdir(parents=True)
    (preview_root / "99999_metadata_preview.json").write_text(
        json.dumps(
            {
                "status": "PREVIEW_ONLY",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "article": {
                    "articolo": "99999",
                    "codice": "TEST99999",
                    "disegno": "DRAW99999",
                },
                "operations_preview": ["LAVAGGIO", "COLLAUDO VISIVO 100%"],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", specs_root)
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    def should_not_be_called(*args, **kwargs):
        raise AssertionError("context reader bridge must not bypass spec intake preview")

    monkeypatch.setattr(tl_chat_api, "build_context_reader_candidate", should_not_be_called)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Cosa sai del 99999?",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["source"] == "spec_intake_preview"
    assert data["source_status"] == "PREVIEW_ONLY"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["missing_data"] == ["Revisione disegno"]
    assert "Dati disponibili:" in data["answer"]
    assert "Fonte:" in data["answer"]
    assert "- spec_intake_preview" in data["answer"]
    assert "context_access_binding" not in data["answer"]
    assert "planner_eligible=" not in data["answer"]
    assert "requires_tl_confirmation=" not in data["answer"]
    assert "can_promote=" not in data["answer"]


def test_spec_intake_preview_asks_tl_only_for_missing_operational_data(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    (preview_root / "54321_metadata_preview.json").write_text(
        json.dumps(
            {
                "capability": "SPEC_INTAKE_54321_PREVIEW_001",
                "status": "PREVIEW_ONLY",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "article": {
                    "articolo": "54321",
                    "codice": "TEST-CODE",
                    "disegno": "",
                    "rev": "",
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_PREVIEW_ROOT",
        preview_root,
    )

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa sai dell'articolo 54321?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "Codice cliente: TEST-CODE" in data["answer"]
    assert "Disegno" in data["answer"]
    assert "Revisione disegno" in data["answer"]

    assert "Puoi fornire o confermare" in data["answer"]

    assert data["missing_data"] == [
        "Disegno",
        "Revisione disegno",
    ]

    assert "Abilitazione all'uso per pianificazione" not in data["answer"]
    assert "Autorizzazione alla promozione a CERTO" not in data["answer"]

    assert "non è utilizzabile per pianificazione" in data["answer"]
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True


def test_spec_intake_preview_reports_missing_assembly_data_for_real_question(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(
            {
                "capability": "SPEC_INTAKE_12514_PREVIEW_001",
                "status": "PREVIEW_ONLY",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "article": {
                    "articolo": "12514",
                    "codice": "7056055000A0",
                    "disegno": "A1675003603",
                    "rev": "6",
                },
                "operations_preview": [
                    "ASSEMBLAGGIO",
                    "MARCATURA",
                    "COLLAUDO A PRESSIONE",
                ],
                "components_and_tools_preview": [
                    {
                        "code": "468922",
                        "type": "component",
                        "note": "guaina",
                    },
                    {
                        "code": "CRT004",
                        "type": "tooling",
                        "note": "attrezzatura tacca numero 004",
                    },
                ],
                "tl_confirmation_required": [
                    (
                        "Confermare se i due passaggi ZAW sono entrambi ZAW1 "
                        "o coinvolgono altra postazione."
                    ),
                    "Confermare sequenza route normalizzata PROMETEO.",
                    (
                        "Confermare componenti 468728, 468865, 468796 "
                        "e attrezzature CRT/CRM."
                    ),
                    (
                        "Confermare se PIDMILL e CP sono assenti "
                        "o solo non visibili nella specifica."
                    ),
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_PREVIEW_ROOT",
        preview_root,
    )

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": (
                "Quali dati operativi mancano per completare le indicazioni "
                "di assemblaggio dell'articolo 12514?"
            )
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["source"] == "spec_intake_preview"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["missing_data"] == [
        (
            "Confermare se i due passaggi ZAW sono entrambi ZAW1 "
            "o coinvolgono altra postazione."
        ),
        "Confermare sequenza route normalizzata PROMETEO.",
        (
            "Confermare componenti 468728, 468865, 468796 "
            "e attrezzature CRT/CRM."
        ),
        (
            "Confermare se PIDMILL e CP sono assenti "
            "o solo non visibili nella specifica."
        ),
    ]

    assert "Dati mancanti:" in data["answer"]
    assert "Richiesta al TL:" in data["answer"]
    assert (
        "Puoi fornire o confermare: Confermare se i due passaggi ZAW "
        "sono entrambi ZAW1 o coinvolgono altra postazione."
        in data["answer"]
    )
    assert "Dati mancanti:\n- Nessuno" not in data["answer"]
