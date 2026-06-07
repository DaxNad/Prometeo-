import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/build_context_isolation_preview.py"


def run_context(code: str):
    return subprocess.run(
        ["python3", str(SCRIPT), code],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_context_isolation_existing_code_outputs_four_contexts():
    result = run_context("12511")

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["found"] is True
    assert data["mode"] == "preview_only"
    assert data["code"] == "12511"

    assert "article_context" in data
    assert "spec_context" in data
    assert "turn_context" in data
    assert "deploy_context" in data


def test_context_isolation_never_allows_planner_or_writes():
    result = run_context("12511")

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["article_context"]["planner_safe"] is False
    assert data["guard"]["planner_allowed"] is False
    assert data["deploy_context"]["writes_to_planner"] is False
    assert data["deploy_context"]["writes_to_smf"] is False
    assert data["deploy_context"]["writes_to_db"] is False


def test_context_isolation_preserves_observational_safe_answer_mode():
    result = run_context("12511")

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["turn_context"]["safe_answer_mode"] == "OBSERVATIONAL_ONLY"
    assert data["guard"]["response_allowed"] is True


def test_context_isolation_missing_code_is_safe_preview_only_miss():
    result = run_context("99998")

    assert result.returncode == 1
    data = json.loads(result.stdout)

    assert data["found"] is False
    assert data["mode"] == "preview_only"
    assert data["article_context"]["known"] is False
    assert data["guard"]["planner_allowed"] is False
    assert data["turn_context"]["tl_required"] is True


def test_context_isolation_rejects_invalid_code():
    result = run_context("ABC")

    assert result.returncode == 2
    assert "5-digit" in result.stderr


def test_context_isolation_does_not_require_backend_or_ai_runtime():
    result = run_context("12511")

    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["deploy_context"]["uses_backend_runtime"] is False
    assert data["deploy_context"]["uses_ai_runtime"] is False
    assert "uvicorn" not in result.stderr.lower()
    assert "fastapi" not in result.stderr.lower()
