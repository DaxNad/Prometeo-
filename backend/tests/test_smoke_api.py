import os
from fastapi.testclient import TestClient
import tempfile
from pathlib import Path


# Forza backend SQLite per evitare dipendenze da PostgreSQL in test
os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
os.environ.setdefault("DATABASE_URL", "")


from app.main import app  # noqa: E402  (import dopo set env)


def test_smoke_health_and_smf_endpoints():
    client = TestClient(app)

    r_health = client.get("/health")
    assert r_health.status_code == 200
    data = r_health.json()
    assert isinstance(data, dict)
    assert data.get("ok", data.get("status") == "ok") is not False

    r_status = client.get("/smf/status")
    assert r_status.status_code == 200
    status = r_status.json()
    assert "base_path" in status and "exists" in status

    r_structure = client.get("/smf/structure")
    assert r_structure.status_code == 200
    structure = r_structure.json()
    assert structure.get("exists") in {True, False}
    assert isinstance(structure.get("sheets"), list)

    r_preview = client.get("/smf/preview")
    assert r_preview.status_code == 200
    preview = r_preview.json()
    assert "exists" in preview and "available_sheets" in preview

    r_debug = client.get("/smf/debug-bootstrap")
    assert r_debug.status_code == 200
    dbg = r_debug.json()
    for key in [
        "base_path",
        "master_path",
        "base_exists",
        "base_is_dir",
        "master_exists",
        "writable_check",
        "bootstrap_attempted",
    ]:
        assert key in dbg

    payload = {
        "order_id": "SMOKE-0001",
        "cliente": "SmokeTest",
        "codice": "CODE-SMOKE",
        "qta": 1,
        "postazione": "TEST",
        "source_type": "test",
    }

    r_parse = client.post("/smf/parse-extracted-order", json=payload)
    assert r_parse.status_code == 200
    body = r_parse.json()
    assert body.get("ok") is True
    assert body.get("flow") == "parse_only"


def test_parse_extracted_order_validation_paths():
    client = TestClient(app)

    payload = {
        "order_id": "VAL-001",
        "cliente": "Cliente X",
        "codice": "CODE-X",
        "qta": "abc",  # invalida
        "due_date": "31-02-2026",  # invalida
        "source_type": "test",
    }

    r = client.post("/smf/parse-extracted-order", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert data.get("flow") == "parse_only"
    # Deve segnalare discrepanze (qta/due_date normalizzati)
    assert isinstance(data.get("discrepancies"), list)
    assert len(data.get("discrepancies")) >= 1


def test_smf_endpoints_with_corrupted_workbook():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        os.environ["SMF_BASE_PATH"] = str(base)
        # invalida il master con contenuto non-Excel
        master = base / "SuperMegaFile_Master.xlsx"
        base.mkdir(parents=True, exist_ok=True)
        master.write_text("NOT_AN_EXCEL_FILE", encoding="utf-8")
        # resetta l'adapter globale per forzare ri-creazione con nuovo base_path
        import app.api_smf as api_smf
        api_smf.adapter = None  # type: ignore

        client = TestClient(app)

        r_structure = client.get("/smf/structure")
        assert r_structure.status_code == 200
        data = r_structure.json()
        assert data.get("exists") in {True, False}

        r_preview = client.get("/smf/preview")
        assert r_preview.status_code == 200
        prev = r_preview.json()
        # su workbook corrotto non deve esplodere né esporre traceback
        assert isinstance(prev, dict)
        assert "rows_preview" in prev
        # opzionalmente può riportare un errore sintetico
        if "error" in prev:
            assert prev["error"] in {"workbook not readable", "sheet read error"}

        r_debug = client.get("/smf/debug-bootstrap")
        assert r_debug.status_code == 200
        dbg = r_debug.json()
        assert "schema_ok" in dbg
