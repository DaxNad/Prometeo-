import json
from pathlib import Path


def test_tl_micro_sample_sanitized():
    data = json.loads(Path("evals/fixtures/tl_micro_sample.json").read_text())
    assert data["state"] == "SANITIZED_SAMPLE_READY"
    assert "items" in data and data["items"], "Fixture must contain items"
