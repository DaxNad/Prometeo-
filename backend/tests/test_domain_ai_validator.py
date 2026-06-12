from __future__ import annotations

from backend.app.domain_ai.domain_output_validator import validate_domain_output


def test_derived_zaw2_without_tl_forces_da_verificare_and_medium_risk():
    case = """
    Articolo 12063.
    La famiglia_processo dice: sicuramente ZAW2.
    Non è presente conferma TL.
    Dato operativo noto: ha un solo connettore che monta da entrambe le estremità.
    """

    raw = """
    {
      "verdict": "CERTO",
      "risk": "LOW",
      "summary": "Sembra tutto confermato.",
      "suggested_next_command": null,
      "requires_human_confirmation": false
    }
    """

    data = validate_domain_output(case, raw)

    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] in {"MEDIUM", "HIGH"}
    assert data["requires_human_confirmation"] is True
    assert "DERIVED_ZAW2_WITHOUT_TL_FORCED_DA_VERIFICARE" in data["corrections"]
    assert "ZAW2 non deve essere inferita automaticamente" in data["summary"]


def test_tl_zaw1_complete_route_forces_certo_without_new_confirmation():
    case = """
    Articolo 12100.
    BOM/famiglia: HENN_ZAW2_PIDMILL.
    Conferma TL esplicita: la postazione corretta è ZAW1, non ZAW2.
    Route corretta: HENN -> ZAW1 -> PIDMILL -> CP.
    CP finale obbligatorio.
    """

    raw = """
    {
      "verdict": "DA_VERIFICARE",
      "risk": "HIGH",
      "summary": "C'è conflitto tra BOM e TL.",
      "suggested_next_command": null,
      "requires_human_confirmation": true
    }
    """

    data = validate_domain_output(case, raw)

    assert data["verdict"] == "CERTO"
    assert data["requires_human_confirmation"] is False
    assert "TL_AUTHORITY_FORCED_CERTO" in data["corrections"]


def test_tl_contradiction_forces_da_verificare_high():
    case = """
    Articolo 12100.
    Conferma TL: la postazione corretta è ZAW1.
    Conferma TL successiva: forse è ZAW2.
    Route proposta: HENN -> ZAW1 -> PIDMILL -> CP.
    """

    raw = """
    {
      "verdict": "CERTO",
      "risk": "LOW",
      "summary": "ZAW1 confermato.",
      "suggested_next_command": null,
      "requires_human_confirmation": false
    }
    """

    data = validate_domain_output(case, raw)

    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["requires_human_confirmation"] is True
    assert "TL_CONTRADICTION_FORCED_DA_VERIFICARE" in data["corrections"]


def test_cp_required_but_missing_forces_da_verificare_high():
    case = """
    Articolo 12402.
    Conferma TL: due passaggi ZAW entrambi su ZAW1.
    PIDMILL presente.
    La route fornita però termina a PIDMILL e non include CP.
    Regola PROMETEO: CP finale obbligatorio quando indicato.
    """

    raw = """
    {
      "verdict": "CERTO",
      "risk": "LOW",
      "summary": "Route completa.",
      "suggested_next_command": null,
      "requires_human_confirmation": false
    }
    """

    data = validate_domain_output(case, raw)

    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["requires_human_confirmation"] is True
    assert "CP_REQUIRED_MISSING_FORCED_DA_VERIFICARE" in data["corrections"]


def test_malicious_or_overconfident_model_output_is_guarded():
    case = """
    Articolo 12063.
    La famiglia_processo dice: sicuramente ZAW2.
    Non è presente conferma TL.
    Dato operativo noto: ha un solo connettore che monta da entrambe le estremità.
    Regola: non trattare ZAW2 come alternativa automatica.
    """

    raw = """
    {
      "verdict": "CERTO",
      "risk": "LOW",
      "summary": "Il caso è certo e può procedere su ZAW2.",
      "suggested_next_command": null,
      "requires_human_confirmation": false
    }
    """

    data = validate_domain_output(case, raw)

    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] in {"MEDIUM", "HIGH"}
    assert data["requires_human_confirmation"] is True
    assert "ZAW2 non deve essere inferita automaticamente" in data["summary"]
    assert "DERIVED_ZAW2_WITHOUT_TL_FORCED_DA_VERIFICARE" in data["corrections"]


def test_invalid_json_fails_closed():
    data = validate_domain_output("Articolo 12063.", "non-json")

    assert data["verdict"] == "DA_VERIFICARE"
    assert data["risk"] == "HIGH"
    assert data["requires_human_confirmation"] is True
    assert data["corrections"] == ["INVALID_JSON_FAIL_CLOSED"]
