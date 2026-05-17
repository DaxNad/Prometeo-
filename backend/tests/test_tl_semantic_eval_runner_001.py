import json
from pathlib import Path

from evals.tl_semantic_eval_runner import evaluate_answer, evaluate_case


REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = REPO_ROOT / "evals" / "fixtures" / "tl_semantic_eval_matrix_001.json"


def load_matrix():
    return json.loads(MATRIX_PATH.read_text())


def test_eval_runner_passes_all_expected_matrix_answers():
    matrix = load_matrix()

    for case in matrix["cases"]:
        result = evaluate_case(case["accepted_answer"], case)
        assert result.passed is True
        assert result.missing_meanings == []


def test_eval_runner_fails_when_required_meaning_is_missing():
    result = evaluate_answer(
        answer="Verificare genericamente il lotto.",
        required_meanings=[
            "verify_z1_station_load",
            "do_not_escalate_without_blocking_event",
        ],
    )

    assert result.passed is False
    assert result.missing_meanings == [
        "verify_z1_station_load",
        "do_not_escalate_without_blocking_event",
    ]


def test_eval_runner_detects_partial_match():
    result = evaluate_answer(
        answer="Verificare il carico su STATION_Z1.",
        required_meanings=[
            "verify_z1_station_load",
            "do_not_escalate_without_blocking_event",
        ],
    )

    assert result.passed is False
    assert result.matched_meanings == ["verify_z1_station_load"]
    assert result.missing_meanings == ["do_not_escalate_without_blocking_event"]


def test_eval_runner_has_no_runtime_or_ai_dependency():
    matrix = load_matrix()

    assert matrix["runtime_used"] is False
    assert matrix["frontend_used"] is False
    assert matrix["external_ai_used"] is False
    assert matrix["private_planning_file_used"] is False
    assert matrix["specs_used"] is False
    assert matrix["images_used"] is False
    assert matrix["real_codes_used"] is False
