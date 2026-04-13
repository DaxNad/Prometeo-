from app.station_normalizer import normalize_station


def test_station_aliases_and_phases_mapping():
    cases = {
        "ZAW1": "ZAW-1",
        "zaw-1": "ZAW-1",
        "ZAW_1": "ZAW-1",
        "Saldatura ZAW-1": "ZAW-1",
        "fase: zaw1": "ZAW-1",
        "ZAW 2": "ZAW-2",
        "Assemblaggio ZAW-2": "ZAW-2",
        "pid": "PIDMILL",
        "PID-MILL": "PIDMILL",
        "Rework pidmill": "PIDMILL",
        "henn fase": "HENN",
        None: "NON_ASSEGNATA",
        "": "NON_ASSEGNATA",
    }

    for raw, expected in cases.items():
        assert normalize_station(None if raw is None else str(raw)) == expected

