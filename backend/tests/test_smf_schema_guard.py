import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.smf.smf_adapter import SMFAdapter, MASTER_NAME


def _temp_smf_dir(tmp_path: Path) -> Path:
    base = tmp_path / "local_smf"
    os.environ["SMF_BASE_PATH"] = str(base)
    return base


def test_debug_bootstrap_reports_schema(tmp_path):
    base = _temp_smf_dir(tmp_path)
    adapter = SMFAdapter(base_path=base)
    client = TestClient(app)

    # Force a scenario where workbook exists and schema should be OK after bootstrap
    r = client.get("/smf/debug-bootstrap")
    assert r.status_code == 200
    body = r.json()
    assert "schema_ok" in body
    assert "missing_counts" in body


def test_writer_blocks_missing_columns_validate(tmp_path):
    base = _temp_smf_dir(tmp_path)
    adapter = SMFAdapter(base_path=base)

    # Corrupt schema intentionally: drop a required column from Pianificazione
    import pandas as pd
    path = adapter.master_path()
    df = pd.read_excel(path, sheet_name="Pianificazione")
    if "Cliente" in df.columns:
        df = df.drop(columns=["Cliente"])  # remove one required column
    with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="Pianificazione", index=False)

    os.environ["SMF_SCHEMA_MODE"] = "validate"
    res = adapter.writer().append_row("Pianificazione", {"ID ordine": "T-1", "Cliente": "X"})
    assert res.get("ok") is False
    assert "missing columns" in res.get("error", "")


def test_writer_repairs_missing_columns_when_enabled(tmp_path):
    base = _temp_smf_dir(tmp_path)
    adapter = SMFAdapter(base_path=base)

    import pandas as pd
    path = adapter.master_path()
    df = pd.read_excel(path, sheet_name="Pianificazione")
    if "Cliente" in df.columns:
        df = df.drop(columns=["Cliente"])  # remove one required column
    with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="Pianificazione", index=False)

    os.environ["SMF_SCHEMA_MODE"] = "repair"
    res = adapter.writer().append_row("Pianificazione", {"ID ordine": "T-2", "Cliente": "Y"})
    assert res.get("ok") is True
    assert res.get("schema_mode") == "repair"

