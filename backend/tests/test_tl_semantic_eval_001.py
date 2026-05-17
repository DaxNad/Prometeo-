import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "evals" / "fixtures" / "tl_semantic_eval_001.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text())


def test_tl_semantic_eval_001_boundaries():
    data = load_fixture()

    assert data["state"] == "TL_SEMANTIC_EVAL_READY"
    assert data["runtime_used"] is False
    assert data["frontend_used"] is False
    assert data["external_ai_used"] is False
    assert data["private_planning_file_used"] is False
    assert data["specs_used"] is False
    assert data["images_used"] is False
    assert data["real_codes_used"] is False


def test_tl_semantic_eval_001_uses_only_sanitized_placeholders():
    data = load_fixture()
    context = data["context"]

    assert context["article"].startswith("ITEM_")
    assert all(station.startswith("STATION_") for station in context["stations"])
    assert all(component.startswith("COMP_") for component in context["shared_components"])


def test_tl_semantic_eval_001_required_meanings():
    data = load_fixture()
    meanings = set(data["expected_semantic_answer"]["required_meanings"])

    assert "prioritize_final_pressure_check" in meanings
    assert "verify_z1_station_load" in meanings
    assert "do_not_escalate_without_blocking_event" in meanings


def test_tl_semantic_eval_001_expected_answer_contract():
    data = load_fixture()
    answer = data["expected_semantic_answer"]["accepted_answer"].lower()

    assert "station_cp" in answer
    assert "station_z1" in answer
    assert "evento bloccante" in answer
    assert "non alzare criticità" in answer
