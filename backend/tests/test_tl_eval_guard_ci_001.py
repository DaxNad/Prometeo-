from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "tl-eval.yml"


def test_tl_eval_guard_workflow_exists():
    assert WORKFLOW_PATH.exists()


def test_tl_eval_guard_runs_make_tl_eval():
    content = WORKFLOW_PATH.read_text()

    assert "name: TL Eval Guard" in content
    assert "make tl-eval" in content
    assert "pull_request:" in content
    assert "push:" in content


def test_tl_eval_guard_has_no_runtime_or_external_ai_dependency():
    content = WORKFLOW_PATH.read_text().lower()

    forbidden_tokens = [
        "uvicorn",
        "fastapi",
        "railway",
        "vercel",
        "openai",
        "ollama",
        "database_url",
        "smf",
    ]

    for forbidden in forbidden_tokens:
        assert forbidden not in content
