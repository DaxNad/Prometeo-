from pathlib import Path


def test_master_contains_spec_densification_orchestrator_contract():
    master = Path("docs/PROMETEO_MASTER.md")
    text = master.read_text(encoding="utf-8")
    normalized = text.lower()

    assert "spec densification orchestrator / capo guardia specifiche" in normalized
    assert "preview-only" in normalized
    assert "specifica di finitura + tl" in normalized
    assert "nessuna scrittura diretta su smf, database, planner o metadata reali" in normalized
    assert "domande tl mirate" in normalized
    assert "nessuna promozione automatica a `certo` da fonti derivate/cache/preview" in normalized
