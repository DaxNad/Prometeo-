from pathlib import Path


def test_master_contains_tl_override_confirmation_contract():
    master = Path("docs/PROMETEO_MASTER.md")
    text = master.read_text(encoding="utf-8")
    normalized = text.lower()

    assert "tl override confirmation / conferma forte modifiche operative" in normalized
    assert "preview/diff" in normalized
    assert "confermo modifica 12097" in normalized
    assert "audit log" in normalized
    assert "rollback_id" in normalized
    assert "zaw/henn/pidmill/cp" in normalized
    assert "planner_eligible" in normalized
    assert "operational_class" in normalized
    assert '"ok", "sì", "vai"' in normalized or "\"ok\", \"sì\", \"vai\"" in text
    assert "specifica di finitura + tl" in normalized
