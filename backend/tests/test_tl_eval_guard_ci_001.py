from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github' / 'workflows' / 'tl-eval.yml'


def test_tl_eval_guard_ci_workflow_exists():
    assert WORKFLOW.exists()


def test_tl_eval_guard_ci_scope_is_eval_only():
    data = yaml.safe_load(WORKFLOW.read_text(encoding='utf-8'))

    assert data['name'] == 'TL Eval Guard'
    assert 'pull_request' in data[True]
    assert data[True]['push']['branches'] == ['main']

    job = data['jobs']['tl-eval']
    assert job['runs-on'] == 'ubuntu-latest'

    steps = job['steps']
    assert any(step.get('uses') == 'actions/checkout@v4' for step in steps)
    assert any(
        step.get('uses') == 'actions/setup-python@v5'
        and step.get('with', {}).get('python-version') == '3.11'
        for step in steps
    )
    assert any(step.get('run') == 'make tl-eval' for step in steps)

    lowered = WORKFLOW.read_text(encoding='utf-8').lower()
    forbidden_terms = [
        'uvicorn', 'npm', 'vite', 'vercel', 'railway',
        'openai', 'ollama', 'database', 'postgres', 'smf'
    ]
    for term in forbidden_terms:
        assert term not in lowered
