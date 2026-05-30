import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/build_real_code_registry_preview.py"
OUT_JSON = ROOT / "data/local_reports/real_code_registry/real_code_registry_preview.json"


def test_real_code_registry_fixture_mode_restores_ci_preview_inputs(tmp_path):
    env = os.environ.copy()
    env["PROMETEO_REAL_CODE_REGISTRY_FIXTURE_ONLY"] = "1"
    env["PROMETEO_REAL_CODE_REGISTRY_OUT_DIR"] = str(tmp_path)

    subprocess.run(
        ["python3", str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )

    data = json.loads((tmp_path / OUT_JSON.name).read_text(encoding="utf-8"))
    records = {record["code"]: record for record in data["records"]}
    excluded_values = {item["value"] for item in data["excluded_candidates"]}

    assert "12056" in records
    assert "12058" in records
    assert "12511" in records
    assert "SMF_BOM_SPECS" in records["12056"]["sources"]
    assert "TL_REAL_SPEC_INTAKE" in records["12511"]["sources"]
    assert records["12056"]["planner_safe"] is False
    assert records["12511"]["planner_safe"] is False
    assert "11434" in excluded_values
