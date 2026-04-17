from app.api.devos import (
    get_domain_info,
    get_event_model_info,
    get_order_model_info,
)


def test_domain_entities_stable():
    d = get_domain_info()

    assert "Order" in d["core_entities"]
    assert "ProductionEvent" in d["core_entities"]
    assert "Station" in d["core_entities"]


def test_station_enum_stable():
    d = get_domain_info()

    expected = {
        "GUAINE",
        "ULTRASUONI",
        "FORNO",
        "WINTEC",
        "PIDMILL",
        "ZAW1",
        "ZAW2",
        "HENN",
        "CP",
    }

    assert set(d["stations_supported"]) == expected


def test_order_contract_minimal_fields():
    d = get_order_model_info()

    fields = set(d["core_fields_expected"])
    assert "order_id" in fields
    assert "station" in fields
    assert "status" in fields


def test_event_contract_minimal_fields():
    d = get_event_model_info()

    fields = set(d["core_fields_expected"])

    assert "order_id" in fields
    assert "event_type" in fields
    assert "station" in fields
