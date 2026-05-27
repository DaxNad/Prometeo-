import subprocess
import sys
from pathlib import Path

from evals.run_tl_semantic_eval import load_matrix, run_eval


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "evals" / "run_tl_semantic_eval.py"
RAG_MATRIX_PATH = REPO_ROOT / "evals" / "fixtures" / "rag_eval_preview_001.json"


def test_rag_eval_preview_fixture_is_preview_only():
    matrix = load_matrix(RAG_MATRIX_PATH)

    assert matrix["state"] == "RAG_EVAL_PREVIEW_READY"
    assert matrix["eval_matrix_id"] == "RAG_EVAL_PREVIEW_001"
    assert matrix["preview_only"] is True
    assert matrix["runtime_used"] is False
    assert matrix["frontend_used"] is False
    assert matrix["external_ai_used"] is False
    assert matrix["private_planning_file_used"] is False
    assert matrix["specs_used"] is False
    assert matrix["images_used"] is False
    assert matrix["real_codes_used"] is False


def test_rag_eval_preview_matrix_passes_with_context_answer():
    matrix = load_matrix(RAG_MATRIX_PATH)
    passed, lines = run_eval(matrix)

    assert passed is True
    assert "PROMETEO TL SEMANTIC EVAL" in lines
    assert "matrix=RAG_EVAL_PREVIEW_001" in lines
    assert "PASS CASE_001_ZAW_CONTEXT_BENEFIT" in lines
    assert "RESULT=PASS" in lines


def test_rag_eval_preview_cli_accepts_custom_matrix():
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), "--matrix", str(RAG_MATRIX_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "matrix=RAG_EVAL_PREVIEW_001" in completed.stdout
    assert "PASS CASE_001_ZAW_CONTEXT_BENEFIT" in completed.stdout
    assert "RESULT=PASS" in completed.stdout
    assert completed.stderr == ""
