import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/query_registry_evidence_pack.py"


def run_query(code: str):
    return subprocess.run(
        ["python3", str(SCRIPT), code],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_query_existing_code_returns_compact_evidence_pack():
    result = run_query("12511")

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["found"] is True
    assert data["mode"] == "preview_only"
    assert data["record"]["code"] == "12511"
    assert data["record"]["planner_safe"] is False
    assert data["record"]["planner_allowed"] is False
    assert data["record"]["safe_answer_mode"] == "OBSERVATIONAL_ONLY"
    assert "sources" in data["record"]
    assert "evidence_refs" in data["record"]
    assert "process_signals" in data["record"]
    assert "contradictions" in data["record"]


def test_query_missing_code_is_safe_preview_only_miss():
    result = run_query("99998")

    assert result.returncode == 1
    data = json.loads(result.stdout)

    assert data["found"] is False
    assert data["code"] == "99998"
    assert data["mode"] == "preview_only"
    assert data["planner_allowed"] is False
    assert data["safe_answer_mode"] == "OBSERVATIONAL_ONLY"


def test_query_rejects_invalid_code():
    result = run_query("ABC")

    assert result.returncode == 2
    assert "5-digit" in result.stderr


def test_query_script_does_not_require_backend_runtime():
    result = run_query("12511")

    assert result.returncode == 0
    assert "uvicorn" not in result.stderr.lower()
    assert "fastapi" not in result.stderr.lower()
