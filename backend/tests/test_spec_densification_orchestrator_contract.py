from pathlib import Path


def test_master_contains_spec_densification_orchestrator_contract():
    repo_root = Path(__file__).resolve().parents[2]
    master = repo_root / "docs" / "PROMETEO_MASTER.md"
    text = master.read_text(encoding="utf-8")

    assert "Spec Densification Orchestrator" in text
    assert "Capo Guardia Specifiche" in text
    assert "preview-only" in text
    assert "SPECIFICA DI FINITURA + TL" in text
    assert "nessuna scrittura diretta su SMF, database, planner o metadata reali" in text
    assert "domande TL mirate" in text
    assert "nessuna promozione automatica a `CERTO` da fonti derivate/cache/preview" in text
