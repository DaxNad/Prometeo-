from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


TECHNICAL_NOISE = (
    "traceback",
    "pytest",
    "sqlalchemy",
    "stacktrace",
    "uvicorn",
)


@pytest.fixture
def isolated_tl_sources(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    return {
        "registry": registry,
        "staging": staging,
        "intake": intake,
        "preview": preview,
    }


def _ask(question: str, context: dict[str, str] | None = None) -> dict:
    client = TestClient(app)
    payload: dict[str, object] = {"question": question}
    if context is not None:
        payload["context"] = context

    response = client.post("/tl/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["technical_details_hidden"] is True
    return data


def _combined(data: dict) -> str:
    return " ".join(str(data.get(key) or "") for key in ("answer", "risk", "recommended_action"))


def _assert_operational_shape(data: dict) -> None:
    combined = _combined(data)
    assert data["answer"]
    assert data.get("risk")
    assert data.get("recommended_action")
    assert not any(token in combined.lower() for token in TECHNICAL_NOISE)


def _assert_runtime_evidence(
    data: dict,
    *,
    expected_source_type: str,
    allowed_confidences: set[str],
) -> dict:
    evidence_pack = data["evidence_pack"]
    assert evidence_pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert "read-only" in evidence_pack["constraints"]
    assert "no DB writes" in evidence_pack["constraints"]
    assert "no SMF writes" in evidence_pack["constraints"]
    assert "no planner mutation" in evidence_pack["constraints"]

    evidence = evidence_pack["evidence"]
    assert evidence
    item = next(
        item for item in evidence
        if item["source_type"] == expected_source_type
    )

    required = {"source_id", "source_type", "authority_rank", "confidence", "text", "reason"}
    assert required <= set(item)
    assert item["source_id"]
    assert item["confidence"] in allowed_confidences
    assert item["text"]
    assert item["reason"]

    for value in item.values():
        if isinstance(value, str):
            assert not value.startswith("/")
            assert f"/{'Users'}/" not in value

    return item


def test_practical_q1_certain_article_12066(monkeypatch, isolated_tl_sources):
    def summary(article: str) -> dict:
        assert article == "12066"
        return {
            "ok": True,
            "article": "12066",
            "confidence": "CERTO",
            "route": ["HENN", "ZAW1", "PIDMILL", "CP"],
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
            "criticalities": [
                "Discrepanza confermata da TL: ZAW1 obbligatoria, ZAW2 non automatica."
            ],
            "tl_action": "Seguire route confermata e usare criticita come checklist operativa.",
        }

    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", summary)

    data = _ask("12066?")
    _assert_operational_shape(data)

    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "12066" in data["answer"]
    assert "Route:" in data["answer"]
    assert "HENN" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "ZAW2" in data["answer"]
    assert "PIDMILL" in data["answer"]
    assert "CP finale obbligatorio" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "Vincoli:" in data["answer"]
    assert "Azione:" in data["answer"]


@pytest.mark.parametrize(
    ("scenario", "expected_source_type", "allowed_confidences"),
    [
        ("local_specs_metadata", "ARTICLE_METADATA", {"CERTO"}),
        ("article_summary", "ARTICLE_SUMMARY", {"CERTO"}),
        ("route_preview", "PREVIEW_PROFILE", {"PREVIEW_ONLY"}),
        ("staging_preview", "PREVIEW_PROFILE", {"PREVIEW_ONLY"}),
        ("lifecycle_registry", "LIFECYCLE_REGISTRY", {"CERTO"}),
        ("intake_new_entry", "ARTICLE_METADATA", {"PREVIEW_ONLY"}),
    ],
)
def test_practical_runtime_provenance_completeness(
    monkeypatch,
    isolated_tl_sources,
    scenario,
    expected_source_type,
    allowed_confidences,
):
    if scenario == "local_specs_metadata":
        article_dir = tl_chat_api.SPECS_ROOT / "12056"
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                    "article": "12056",
                    "confidence": "CERTO",
                    "route_status": "CERTO",
                    "operational_class": "STANDARD",
                    "planner_eligible": True,
                    "route_steps": [
                        {"seq": 1, "station": "ZAW1", "status": "CERTO"},
                        {"seq": 2, "station": "CP", "status": "CERTO"},
                    ],
                    "constraints": {"cp_required": True},
                }
            ),
            encoding="utf-8",
        )
        data = _ask("12056?")
        assert data["confidence"] == "CERTO"
        assert data["requires_confirmation"] is False
        assert "12056" in data["answer"]

    elif scenario == "article_summary":
        def summary(article: str) -> dict:
            assert article == "12066"
            return {
                "ok": True,
                "article": "12066",
                "confidence": "CERTO",
                "route": ["HENN", "ZAW1", "PIDMILL", "CP"],
                "signals": {
                    "has_henn": True,
                    "has_zaw1": True,
                    "has_zaw2": False,
                    "primary_zaw_station": "ZAW1",
                    "has_pidmill": True,
                    "cp_required": True,
                },
                "criticalities": [],
                "tl_action": "Seguire route confermata e usare criticita come checklist operativa.",
            }

        monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", summary)
        data = _ask("12066?")
        assert data["confidence"] == "CERTO"
        assert data["requires_confirmation"] is False
        assert "12066" in data["answer"]

    elif scenario == "route_preview":
        isolated_tl_sources["preview"].write_text(
            json.dumps(
                {
                    "profiles": {
                        "12070": {
                            "article": "12070",
                            "confidence": "INFERITO",
                            "signals": {
                                "has_henn": False,
                                "has_zaw1": True,
                                "has_zaw2": False,
                                "primary_zaw_station": "ZAW1",
                                "cp_required": True,
                            },
                            "review_reasons": [],
                            "discrepancies": [],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        data = _ask("12070?")
        assert data["confidence"] == "INFERITO"
        assert data["requires_confirmation"] is True
        assert "Profilo inferito" in data["answer"]

    elif scenario == "staging_preview":
        isolated_tl_sources["staging"].write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "codice": "12056",
                            "tl_decision": "PENDING",
                            "staging_status": "PREVIEW_ONLY",
                            "next_action": "REVIEW_BEFORE_STAGING",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        data = _ask("Quali codici posso densificare?")
        assert data["confidence"] == "CERTO"
        assert data["requires_confirmation"] is True
        assert "12056" in data["answer"]
        assert "staging preview" in data["risk"]

    elif scenario == "lifecycle_registry":
        isolated_tl_sources["registry"].write_text(
            json.dumps(
                {
                    "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
                    "12410": {"status": "NEW_ENTRY", "source": "tl"},
                }
            ),
            encoding="utf-8",
        )
        data = _ask("Quali codici sono fuori produzione?")
        assert data["confidence"] == "CERTO"
        assert data["requires_confirmation"] is True
        assert "12053" in data["answer"]
        assert "12410" not in data["answer"]

    else:
        isolated_tl_sources["intake"].write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "article": "12589",
                            "initial_classification": "NEW_ENTRY_CANDIDATE_ZAW",
                            "confidence": "DA_VERIFICARE",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        data = _ask("Quali codici sono new entry?")
        assert data["confidence"] == "CERTO"
        assert data["requires_confirmation"] is True
        assert "12589" in data["answer"]
        assert "intake locale" in data["answer"].lower()

    _assert_operational_shape(data)
    _assert_runtime_evidence(
        data,
        expected_source_type=expected_source_type,
        allowed_confidences=allowed_confidences,
    )


def test_practical_runtime_provenance_exceptions_keep_empty_evidence(isolated_tl_sources):
    missing_article = _ask("Dimmi lo stato del codice.", {"article": "99999"})
    assert missing_article["confidence"] == "DA_VERIFICARE"
    assert missing_article["evidence_pack"]["evidence"] == []

    missing_staging = _ask("Quali codici posso densificare?")
    assert "Non risultano codici pronti" in missing_staging["answer"]
    assert missing_staging["evidence_pack"]["evidence"] == []

    guardrail = _ask("Cosa faccio partire adesso?")
    assert "Domanda turno" in guardrail["answer"]
    assert guardrail["evidence_pack"]["evidence"] == []


@pytest.mark.parametrize(
    "question",
    [
        "Quali codici sono pronti per la densificazione?",
        "Quali codici sono pronti per revisione del responsabile di produzione prima della densificazione?",
    ],
)
def test_practical_global_intent_recognizes_densification_phrasings(
    isolated_tl_sources,
    question,
):
    isolated_tl_sources["staging"].write_text(
        json.dumps(
            {
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
                ]
            }
        ),
        encoding="utf-8",
    )

    data = _ask(question)

    assert "richiede almeno un articolo" not in data["answer"]
    assert "Codici pronti per revisione del responsabile di produzione prima della densificazione" in data["answer"]
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "12056" in data["answer"]
    assert "12410" in data["answer"]
    _assert_runtime_evidence(
        data,
        expected_source_type="PREVIEW_PROFILE",
        allowed_confidences={"PREVIEW_ONLY"},
    )


@pytest.mark.parametrize(
    "question",
    [
        "Quali sono i nuovi inserimenti?",
        "Quali codici sono new entry?",
    ],
)
def test_practical_global_intent_recognizes_new_entry_phrasings(
    isolated_tl_sources,
    question,
):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
                "12402": {"status": "DA_VERIFICARE", "source": "tl"},
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask(question)

    assert "richiede almeno un articolo" not in data["answer"]
    assert "Codici NEW_ENTRY nel lifecycle registry reparto" in data["answer"]
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "12410" in data["answer"]
    assert "12402" not in data["answer"]
    assert "12053" not in data["answer"]
    _assert_runtime_evidence(
        data,
        expected_source_type="LIFECYCLE_REGISTRY",
        allowed_confidences={"CERTO"},
    )


def test_practical_q_article_summary_da_verificare_requires_confirmation(monkeypatch, isolated_tl_sources):
    def summary(article: str) -> dict:
        assert article == "12067"
        return {
            "ok": True,
            "article": "12067",
            "confidence": "DA_VERIFICARE",
            "route": ["HENN", "ZAW1"],
            "signals": {
                "has_henn": True,
                "has_zaw1": True,
                "has_zaw2": False,
                "primary_zaw_station": "ZAW1",
            },
            "criticalities": ["Profilo articolo da verificare."],
            "tl_action": "Confermare con TL prima di usare la route.",
        }

    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", summary)

    data = _ask("12067?")

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "12067" in data["answer"]


def test_practical_q2_inferred_article_12070_requires_confirmation(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps({"12070": {"status": "NEW_ENTRY", "source": "tl"}}),
        encoding="utf-8",
    )

    data = _ask("12070?")
    _assert_operational_shape(data)

    assert data["confidence"] != "CERTO"
    assert data["requires_confirmation"] is True
    assert "12070" in data["answer"]
    assert "NEW_ENTRY" in data["answer"]
    assert "confermat" in _combined(data).lower()


def test_practical_q3_lists_codes_to_verify(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12402": {"status": "DA_VERIFICARE", "source": "tl"},
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono da verificare?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12402" in data["answer"]
    assert "DA_VERIFICARE" in data["answer"]
    assert "12053" not in data["answer"]
    assert "12410" not in data["answer"]
    assert "Verifica del responsabile di produzione richiesta" in data["recommended_action"]


def test_practical_q4_lists_densification_candidates_without_planner_promotion(isolated_tl_sources):
    isolated_tl_sources["staging"].write_text(
        json.dumps(
            {
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
                ]
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici posso densificare?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12056" in data["answer"]
    assert "12410" in data["answer"]
    assert "12402" not in data["answer"]
    assert "staging preview" in data["risk"]
    assert "conferma del responsabile di produzione" in data["risk"]


def test_practical_q5_lists_fuori_produzione_as_consultive_only(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
                "12402": {
                    "status": "CUSTOMER_REQUEST_ONLY",
                    "source": "tl",
                    "note": "Fuori produzione standard, solo su richiesta cliente.",
                },
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono fuori produzione?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12053" in data["answer"]
    assert "12402" in data["answer"]
    assert "12410" not in data["answer"]
    assert "FUORI_PRODUZIONE" in data["answer"]
    assert "richiesta cliente" in _combined(data).lower()
    assert "non devono essere promossi automaticamente" in data["risk"]


def test_practical_q6_lists_new_entry_as_consultable_not_auto_plannable(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
                "12402": {"status": "DA_VERIFICARE", "source": "tl"},
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono new entry?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12410" in data["answer"]
    assert "NEW_ENTRY" in data["answer"]
    assert "12402" not in data["answer"]
    assert "12053" not in data["answer"]
    assert "conferma del responsabile di produzione" in data["risk"]


def test_practical_q7_12402_verification_respects_customer_request_only(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12402": {
                    "status": "CUSTOMER_REQUEST_ONLY",
                    "source": "tl",
                    "note": "Fuori produzione standard, solo su richiesta cliente.",
                }
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Il 12402 e da verificare?")
    _assert_operational_shape(data)

    assert data["confidence"] != "CERTO"
    assert data["requires_confirmation"] is True
    assert "12402" in data["answer"]
    assert "fuori produzione standard" in data["answer"]
    assert "richiesta cliente" in _combined(data).lower()
    assert "non pianificare automaticamente" in data["risk"]


def test_practical_q_why_zaw2_excluded_uses_metadata_reason(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "12100"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "12100",
                "confidence": "CERTO",
                "route_status": "CERTO",
                "operational_class": "STANDARD",
                "planner_eligible": True,
                "constraints": {
                    "primary_zaw_station": "ZAW1",
                    "has_zaw2": False,
                    "zaw_passes": 1,
                },
                "route_steps": [
                    {"station": "GUAINA"},
                    {"station": "MARCATURA"},
                    {"station": "HENN"},
                    {"station": "ZAW1"},
                    {"station": "PIDMILL"},
                    {"station": "CP"},
                ],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("perché ZAW2 è esclusa per 12100?")
    _assert_operational_shape(data)

    combined = _combined(data).lower()
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "12100" in data["answer"]
    assert "perché" in data["answer"]
    assert "primary_zaw_station=zaw1" in combined
    assert "has_zaw2=false" in combined
    assert "non va usata come alternativa automatica" in combined
    assert "route:" not in data["answer"].lower()


def test_practical_q_why_planner_false_explains_admission_not_profile_dump(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "12097"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "12097",
                "confidence": "CERTO",
                "route_status": "CERTO",
                "operational_class": "STANDARD",
                "planner_eligible": False,
                "planner_admission_status": "BLOCKED",
                "constraints": {
                    "primary_zaw_station": "ZAW1",
                    "has_zaw2": False,
                    "has_pidmill": True,
                    "cp_required": True,
                },
                "route_steps": [
                    {"station": "LAVAGGIO"},
                    {"station": "CONTROLLO_VISIVO"},
                    {"station": "GUAINA"},
                    {"station": "MARCATURA"},
                    {"station": "HENN"},
                    {"station": "ZAW1"},
                    {"station": "PIDMILL"},
                    {"station": "CP"},
                ],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("perché planner_eligible=false per 12097?")
    _assert_operational_shape(data)

    combined = _combined(data).lower()
    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is True
    assert "12097" in data["answer"]
    assert "planner_eligible=false" in combined
    assert "route confermata e ammissione planner sono due cose diverse" in combined
    assert "route:" not in data["answer"].lower()


def test_practical_q_planner_eligible_true_da_verificare_requires_confirmation(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "12098"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "12098",
                "confidence": "DA_VERIFICARE",
                "route_status": "DA_VERIFICARE",
                "operational_class": "STANDARD",
                "planner_eligible": True,
            }
        ),
        encoding="utf-8",
    )

    data = _ask("perché planner_eligible=true per 12098?")

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "planner_eligible=true" in data["answer"]


def test_practical_q_wintec_article_does_not_emit_zaw_noise(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50042"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50042",
                "confidence": "DA_VERIFICARE",
                "route_status": "DA_VERIFICARE",
                "operational_class": "DA_VERIFICARE",
                "planner_eligible": False,
                "famiglia_tecnica": "WINTEC_FORNO_PLASTICA_AMG_MARCATURA",
                "components": ["468772", "917377"],
                "packaging": {
                    "imballo": "50563",
                    "sacchetto": "917377",
                    "quantita_per_imballo": 120
                },
                "constraints": {
                    "has_wintec": True,
                    "has_forno_plastica_amg": True,
                    "has_henn": False,
                    "has_pidmill": False,
                    "has_zaw1": False,
                    "has_zaw2": False,
                    "do_not_infer_zaw": True,
                    "cp_required": False
                },
                "route_steps": [
                    {"seq": 1, "station": "CONTROLLO_VISIVO", "status": "CERTO_DA_SPECIFICA"},
                    {"seq": 2, "station": "FORNO", "status": "CERTO_DA_SPECIFICA"},
                    {"seq": 3, "station": "WINTEC", "status": "CERTO_DA_SPECIFICA"},
                    {"seq": 4, "station": "MARCATURA", "status": "CERTO_DA_SPECIFICA"},
                    {"seq": 5, "station": "ASSEMBLAGGIO", "status": "CERTO_DA_SPECIFICA"},
                    {"seq": 6, "station": "SACCHETTO", "status": "CERTO_DA_SPECIFICA"}
                ]
            }
        ),
        encoding="utf-8",
    )

    data = _ask("50042?")
    _assert_operational_shape(data)

    assert "50042" in data["answer"]
    assert "WINTEC" in data["answer"]
    assert "ZAW2 esclusa" not in data["answer"]
    assert "ZAW2" not in data["answer"]


def test_practical_q_zaw_article_still_emits_zaw2_excluded_when_relevant(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "12100"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "12100",
                "confidence": "CERTO",
                "route_status": "CERTO",
                "operational_class": "STANDARD",
                "planner_eligible": True,
                "constraints": {
                    "has_henn": True,
                    "has_pidmill": True,
                    "has_zaw": True,
                    "has_zaw1": True,
                    "has_zaw2": False,
                    "primary_zaw_station": "ZAW1",
                    "do_not_infer_zaw2": True,
                    "cp_required": True
                },
                "route_steps": [
                    {"seq": 1, "station": "GUAINA", "status": "CERTO"},
                    {"seq": 2, "station": "MARCATURA", "status": "CERTO"},
                    {"seq": 3, "station": "HENN", "status": "CERTO"},
                    {"seq": 4, "station": "ZAW1", "status": "CERTO"},
                    {"seq": 5, "station": "PIDMILL", "status": "CERTO"},
                    {"seq": 6, "station": "CP", "status": "CERTO"}
                ]
            }
        ),
        encoding="utf-8",
    )

    data = _ask("12100?")
    _assert_operational_shape(data)

    assert "12100" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "ZAW2 esclusa" in data["answer"]

def test_practical_q_component_intent_manicotto_50036_resolves_tube_code(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50036"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50036",
                "confidence": "CERTO",
                "components": ["468783", "468772", "12201"],
                "linked_bom": [
                    {
                        "component": "12201",
                        "description": "Manicotto associato da conoscenza operativa TL",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("quale manicotto monta nel 50036?")
    _assert_operational_shape(data)

    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "50036" in data["answer"]
    assert "manicotto: 12201" in data["answer"].lower()
    assert "468772" not in data["answer"].lower()


def test_practical_q_component_intent_unclassified_component_is_not_manicotto(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50037"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50037",
                "confidence": "CERTO",
                "components": ["468772"],
                "linked_bom": [
                    {
                        "component": "468772",
                        "description": "Componente WINTEC",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("quale manicotto monta nel 50037?")

    assert "manicotto:" not in data["answer"].lower()
    assert "componenti: 468772" in data["answer"].lower()


def test_practical_q_component_intent_without_classification_source_uses_components_fallback(
    isolated_tl_sources,
):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50038"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50038",
                "confidence": "CERTO",
                "components": ["12201"],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("quale manicotto monta nel 50038?")

    assert "manicotto:" not in data["answer"].lower()
    assert "componenti: 12201" in data["answer"].lower()


def test_practical_q_component_intent_explicit_manicotto_keeps_uncertain_confidence(
    isolated_tl_sources,
):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50040"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50040",
                "confidence": "DA_VERIFICARE",
                "components": ["12201"],
                "linked_bom": [
                    {
                        "component": "12201",
                        "description": "Manicotto associato da conoscenza operativa TL",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("quale manicotto monta nel 50040?")

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "manicotto: 12201" in data["answer"].lower()


def test_practical_q_component_general_response_is_unchanged(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50039"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50039",
                "confidence": "CERTO",
                "components": ["468783", "468772"],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("componenti 50039?")

    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "50039" in data["answer"]
    assert "componenti: 468783, 468772" in data["answer"].lower()


def test_practical_q_components_missing_requires_confirmation(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50041"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50041",
                "confidence": "CERTO",
            }
        ),
        encoding="utf-8",
    )

    data = _ask("componenti 50041?")

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "componenti non disponibili" in data["answer"].lower()


def test_practical_q_components_unreadable_requires_confirmation(isolated_tl_sources):
    specs_root = tl_chat_api.SPECS_ROOT
    article_dir = specs_root / "50042"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "PROMETEO_REAL_DATA_PILOT_V1",
                "article": "50042",
                "confidence": "CERTO",
                "components": ["CRT001", "SUPPORTO"],
            }
        ),
        encoding="utf-8",
    )

    data = _ask("componenti 50042?")

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "componenti presenti ma non leggibili" in data["answer"].lower()
