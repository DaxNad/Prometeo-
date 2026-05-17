from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOAL_MAP = ROOT / "docs" / "PROMETEO_GOAL_MAP.md"


def test_goal_closure_policy_exists():
    text = GOAL_MAP.read_text(encoding="utf-8")

    assert "## PROMETEO_GOAL_CLOSURE" in text
    assert "GOAL_CLOSURE" in text


def test_goal_closure_blocks_scope_expansion():
    text = GOAL_MAP.read_text(encoding="utf-8").lower()

    required = [
        "non si aggiungono nuovi layer architetturali",
        "capability gia esistente",
        "nessun nuovo world model autonomo",
        "nessun nuovo adapter ai",
        "nessuna nuova ui o dashboard",
        "nessun nuovo runtime",
        "dati reali non sanificati",
    ]

    for item in required:
        assert item in text


def test_goal_closure_defines_goal_criterion():
    text = GOAL_MAP.read_text(encoding="utf-8").lower()

    assert "criterio goal" in text
    assert "piu chiusa" in text
    assert "piu verificabile" in text
    assert "piu sicura" in text
    assert "senza introdurre dipendenze laterali" in text
