import subprocess
import sys
from pathlib import Path

from evals.run_tl_semantic_eval import load_matrix, run_eval


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "evals" / "run_tl_semantic_eval.py"


def test_tl_semantic_eval_cli_run_eval_passes_matrix():
    matrix = load_matrix()
    passed, lines = run_eval(matrix)

    assert passed is True
    assert lines[0] == "PROMETEO TL SEMANTIC EVAL"
    assert "RESULT=PASS" in lines
    assert any("PASS CASE_001_FINAL_CHECK" in line for line in lines)
    assert any("PASS CASE_002_Z1_LOAD_NO_BLOCK" in line for line in lines)
    assert any("PASS CASE_003_Z1_BLOCKING_EVENT" in line for line in lines)


def test_tl_semantic_eval_cli_process_exit_code_zero():
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "PROMETEO TL SEMANTIC EVAL" in completed.stdout
    assert "RESULT=PASS" in completed.stdout
    assert completed.stderr == ""


def test_tl_semantic_eval_cli_has_no_runtime_dependency():
    source = CLI_PATH.read_text()

    forbidden_imports = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "requests",
        "openai",
        "ollama",
    ]

    for forbidden in forbidden_imports:
        assert forbidden not in source.lower()
