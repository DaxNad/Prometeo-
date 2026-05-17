import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "evals" / "fixtures" / "tl_micro_sample.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text())


def test_tl_micro_sample_tested():
    data = load_fixture()

    assert data["state"] == "TESTED_REAL_SAMPLE"
    assert "items" in data and data["items"], "Fixture must contain items"
    assert data["tl_confirmation"]["confirmed_by"] == "TL_SANITIZED"
    assert data["tl_confirmation"]["confirmation_level"] == "SANITIZED_OPERATIONAL_CONFIRMATION"

    result = data["test_result"]
    assert result["tested_as"] == "SANITIZED_REALISTIC_TL_SAMPLE"
    assert result["result"] == "PASS"
    assert result["runtime_used"] is False
    assert result["frontend_used"] is False
    assert result["external_ai_used"] is False
    assert result["smf_used"] is False
    assert result["specs_used"] is False
    assert result["images_used"] is False


def test_tl_micro_sample_uses_only_sanitized_placeholders():
    data = load_fixture()

    assert data["work_order"] == "WO_SAMPLE_001"

    for item in data["items"]:
        assert item["article"].startswith("ITEM_")
        assert all(station.startswith("STATION_") for station in item["stations"])
        assert all(component.startswith("COMP_") for component in item["components"])
