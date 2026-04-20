import json

import app.domain.drawing_registry_service as service


def test_get_drawing_behavior_reads_primary_registry(monkeypatch, tmp_path):
    registry_file = tmp_path / "drawing_behavior_registry.json"
    registry_file.write_text(
        json.dumps(
            {
                "drawing_behavior": {
                    "DWG-100": {"stations": ["HENN"], "rotation": "bassa"},
                }
            }
        )
    )

    monkeypatch.setattr(service, "BASE_PATH", tmp_path)
    monkeypatch.setattr(service, "REGISTRY_FILE", registry_file)

    result = service.get_drawing_behavior(" DWG -100 ")
    assert result == {"stations": ["HENN"], "rotation": "bassa"}


def test_get_drawing_behavior_falls_back_to_registry_entry_files(monkeypatch, tmp_path):
    registry_file = tmp_path / "drawing_behavior_registry.json"
    registry_file.write_text(json.dumps({"drawing_behavior": {}}))
    (tmp_path / "registry_entry_12062.json").write_text(
        json.dumps(
            {
                "A2145019000": {
                    "stations": ["ZAW", "CP"],
                    "rotation": "bassa",
                }
            }
        )
    )

    monkeypatch.setattr(service, "BASE_PATH", tmp_path)
    monkeypatch.setattr(service, "REGISTRY_FILE", registry_file)

    result = service.get_drawing_behavior("A2145019000")
    assert result == {"stations": ["ZAW", "CP"], "rotation": "bassa"}
