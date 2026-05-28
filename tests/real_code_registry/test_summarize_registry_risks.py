import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/summarize_registry_risks.py"


def run_summary():
    return subprocess.run(
        ["python3", str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_summary_outputs_preview_only_registry_risk_counts():
    result = run_summary()

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["mode"] == "preview_only"
    assert data["planner_allowed"] is False
    assert data["safe_answer_mode"] == "OBSERVATIONAL_ONLY"
    assert data["records_total"] > 0
    assert data["contradicted_records"] >= 0
    assert data["tl_required_records"] >= 0
    assert data["not_strict_input_ready"] >= 0


def test_summary_exposes_codes_requiring_tl_as_list():
    result = run_summary()

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert isinstance(data["codes_requiring_tl"], list)
    assert all(isinstance(code, str) for code in data["codes_requiring_tl"])


def test_summary_exposes_top_contradictions_as_counted_items():
    result = run_summary()

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert isinstance(data["top_contradictions"], list)
    for item in data["top_contradictions"]:
        assert set(item) == {"kind", "count"}
        assert isinstance(item["kind"], str)
        assert isinstance(item["count"], int)


def test_summary_does_not_require_backend_runtime():
    result = run_summary()

    assert result.returncode == 0
    assert "uvicorn" not in result.stderr.lower()
    assert "fastapi" not in result.stderr.lower()
