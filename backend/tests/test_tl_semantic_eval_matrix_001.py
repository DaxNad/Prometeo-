import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "evals" / "fixtures" / "tl_semantic_eval_matrix_001.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text())


def test_tl_semantic_eval_matrix_001_boundaries():
    data = load_fixture()

    assert data["state"] == "TL_SEMANTIC_EVAL_MATRIX_READY"
    assert data["runtime_used"] is False
    assert data["frontend_used"] is False
    assert data["external_ai_used"] is False
    assert data["private_planning_file_used"] is False
    assert data["specs_used"] is False
    assert data["images_used"] is False
    assert data["real_codes_used"] is False


def test_tl_semantic_eval_matrix_001_has_four_cases():
    data = load_fixture()

    assert data["eval_matrix_id"] == "TL_SEMANTIC_EVAL_MATRIX_001"
    assert len(data["cases"]) == 4
    assert [case["case_id"] for case in data["cases"]] == [
        "CASE_001_FINAL_CHECK",
        "CASE_002_Z1_LOAD_NO_BLOCK",
        "CASE_003_Z1_BLOCKING_EVENT",
        "CASE_004_STATION_EVENT_TRIAGE",
    ]


def test_tl_semantic_eval_matrix_001_uses_only_sanitized_placeholders():
    data = load_fixture()

    for case in data["cases"]:
        context = case["context"]
        assert context["article"].startswith("ITEM_")
        assert all(station.startswith("STATION_") for station in context["stations"])
        assert all(component.startswith("COMP_") for component in context["shared_components"])


def test_tl_semantic_eval_matrix_001_required_meanings_are_deterministic():
    data = load_fixture()

    matrix = {
        case["case_id"]: set(case["required_meanings"])
        for case in data["cases"]
    }

    assert matrix["CASE_001_FINAL_CHECK"] == {
        "prioritize_final_pressure_check",
        "do_not_close_without_final_check",
    }
    assert matrix["CASE_002_Z1_LOAD_NO_BLOCK"] == {
        "verify_z1_station_load",
        "do_not_escalate_without_blocking_event",
    }
    assert matrix["CASE_003_Z1_BLOCKING_EVENT"] == {
        "verify_blocking_event_first",
        "do_not_ignore_open_block",
        "keep_final_check_required",
    }
    assert matrix["CASE_004_STATION_EVENT_TRIAGE"] == {
        "triage_open_station_event",
        "do_not_auto_escalate_open_event",
        "keep_final_check_required",
    }


def test_tl_semantic_eval_matrix_001_expected_answers_contract():
    data = load_fixture()

    by_id = {case["case_id"]: case["accepted_answer"].lower() for case in data["cases"]}

    assert "station_cp" in by_id["CASE_001_FINAL_CHECK"]
    assert "non considerare il lotto chiuso" in by_id["CASE_001_FINAL_CHECK"]

    assert "station_z1" in by_id["CASE_002_Z1_LOAD_NO_BLOCK"]
    assert "non alzare criticità" in by_id["CASE_002_Z1_LOAD_NO_BLOCK"]
    assert "evento bloccante" in by_id["CASE_002_Z1_LOAD_NO_BLOCK"]

    assert "evento bloccante" in by_id["CASE_003_Z1_BLOCKING_EVENT"]
    assert "station_z1" in by_id["CASE_003_Z1_BLOCKING_EVENT"]
    assert "station_cp" in by_id["CASE_003_Z1_BLOCKING_EVENT"]

    assert "triage" in by_id["CASE_004_STATION_EVENT_TRIAGE"]
    assert "evento aperto" in by_id["CASE_004_STATION_EVENT_TRIAGE"]
    assert "criticità automatica" in by_id["CASE_004_STATION_EVENT_TRIAGE"]
    assert "station_cp" in by_id["CASE_004_STATION_EVENT_TRIAGE"]
