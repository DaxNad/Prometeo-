import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_tl_eval.sh"
MAKEFILE_PATH = REPO_ROOT / "Makefile"


def test_tl_eval_script_exists_and_is_executable():
    assert SCRIPT_PATH.exists()
    assert SCRIPT_PATH.stat().st_mode & 0o111


def test_tl_eval_script_runs_successfully():
    completed = subprocess.run(
        [str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "PROMETEO TL SEMANTIC EVAL" in completed.stdout
    assert "RESULT=PASS" in completed.stdout
    assert completed.stderr == ""


def test_makefile_has_tl_eval_target():
    content = MAKEFILE_PATH.read_text()
    lines = content.splitlines()
    phony_targets = {
        token
        for line in lines
        if line.startswith(".PHONY:")
        for token in line.split(":", 1)[1].split()
    }

    assert "tl-eval" in phony_targets
    assert "tl-eval:" in content
    assert "./scripts/run_tl_eval.sh" in content


def test_tl_eval_script_has_no_runtime_dependency():
    source = SCRIPT_PATH.read_text().lower()

    forbidden_tokens = [
        "uvicorn",
        "fastapi",
        "railway",
        "vercel",
        "openai",
        "ollama",
    ]

    for forbidden in forbidden_tokens:
        assert forbidden not in source
