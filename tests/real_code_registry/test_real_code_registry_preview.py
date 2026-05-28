import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/build_real_code_registry_preview.py"
OUT_JSON = ROOT / "data/local_reports/real_code_registry/real_code_registry_preview.json"

def run_preview():
    result = subprocess.run(
        ["python3", str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result

def load_registry():
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))

def test_technical_number_11434_is_excluded_from_records():
    run_preview()
    data = load_registry()

    record_codes = {r["code"] for r in data["records"]}
    excluded_values = {x["value"] for x in data["excluded_candidates"]}

    assert "11434" not in record_codes
    assert "11434" in excluded_values

def test_all_records_are_not_planner_safe_by_default():
    run_preview()
    data = load_registry()

    assert data["records"]
    assert all(r["planner_safe"] is False for r in data["records"])

def test_preview_does_not_write_to_runtime_targets():
    run_preview()
    data = load_registry()

    assert data["mode"] == "preview_only"
    assert data["rules"]["writes_to_planner"] is False
    assert data["rules"]["writes_to_smf"] is False
    assert data["rules"]["writes_to_db"] is False
    assert data["rules"]["promotes_to_certo"] is False
