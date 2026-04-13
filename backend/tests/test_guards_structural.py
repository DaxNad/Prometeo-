"""
Test TASK A: verifica strutturale dei guard token in ProductionDashboard.tsx.
Riproduce la logica di frontend/scripts/guard_tl_board.sh come test Python
in modo da rilevare regressioni prima del workflow CI.
"""
from pathlib import Path

DASHBOARD_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "src" / "pages" / "ProductionDashboard.tsx"
)

REQUIRED_TOKENS = [
    "TL Board",
    "attenzione immediata",
    "carico postazioni",
    "sequenza consigliata",
    "<th>codice</th>",
    "<th>postazione</th>",
    "<th>qta totale</th>",
    "<th>righe</th>",
    "<th>prio</th>",
]


def test_dashboard_guard_tokens_present():
    """Tutti i guard token richiesti da guard_tl_board.sh sono presenti nel file."""
    assert DASHBOARD_PATH.exists(), f"File non trovato: {DASHBOARD_PATH}"
    content = DASHBOARD_PATH.read_text(encoding="utf-8")
    missing = [t for t in REQUIRED_TOKENS if t not in content]
    assert not missing, f"Guard token mancanti in ProductionDashboard.tsx: {missing}"


def test_dashboard_no_conflict_markers():
    """Il file non deve contenere marker di merge conflict."""
    assert DASHBOARD_PATH.exists()
    content = DASHBOARD_PATH.read_text(encoding="utf-8")
    for marker in ["<<<<<<< ", ">>>>>>> ", "======="]:
        assert marker not in content, (
            f"Marker di merge conflict trovato in ProductionDashboard.tsx: '{marker}'"
        )
