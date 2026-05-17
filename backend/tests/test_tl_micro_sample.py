import json
from pathlib import Path


def test_tl_micro_sample_confirmed():
    data = json.loads(Path("evals/fixtures/tl_micro_sample.json").read_text())

    assert data["state"] == "TL_CONFIRMED_SAMPLE_READY"
    assert "items" in data and data["items"], "Fixture must contain items"
    assert data["tl_confirmation"]["confirmed_by"] == "TL_SANITIZED"
    assert data["tl_confirmation"]["confirmation_level"] == "SANITIZED_OPERATIONAL_CONFIRMATION"


def test_tl_micro_sample_contains_no_real_sources():
    data = json.loads(Path("evals/fixtures/tl_micro_sample.json").read_text())
    serialized = json.dumps(data)

    forbidden_tokens = [
        "SMF",
        "specifica",
        "specifiche",
        "immagine",
        "png",
        "jpg",
        "jpeg",
    ]

    for token in forbidden_tokens:
        assert token.lower() not in serialized.lower()
