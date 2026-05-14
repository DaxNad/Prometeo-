from __future__ import annotations


def _route_stations(metadata: dict) -> list[str]:
    route_steps = metadata.get("route_steps") or []
    stations: list[str] = []
    if isinstance(route_steps, list):
        for step in route_steps:
            if not isinstance(step, dict):
                continue
            station = str(step.get("station") or "").strip().upper()
            if station:
                stations.append(station)
    return stations


def _has_zaw_token(station: str) -> bool:
    return "ZAW" in station


def _validate_metadata_contract(metadata: dict) -> list[str]:
    errors: list[str] = []

    confidence = str(metadata.get("confidence") or "").strip().upper()
    route_status = str(metadata.get("route_status") or "").strip().upper()
    route_steps = metadata.get("route_steps")
    route = _route_stations(metadata)

    constraints = metadata.get("constraints")
    if not isinstance(constraints, dict):
        constraints = {}

    if confidence == "CERTO" and route_status == "CERTO":
        if not isinstance(route_steps, list) or len(route_steps) == 0:
            errors.append("CERTO/CERTO requires non-empty route_steps")

    route_has_zaw = any(_has_zaw_token(s) for s in route)
    if route_has_zaw:
        required = {
            "has_zaw",
            "has_zaw1",
            "has_zaw2",
            "primary_zaw_station",
            "zaw_passes",
            "zaw_station_specificity",
        }
        missing = sorted(k for k in required if k not in constraints)
        if missing:
            errors.append(f"missing ZAW constraints: {', '.join(missing)}")

        zaw1_count = sum(1 for s in route if s == "ZAW1")
        route_has_zaw2 = any(s == "ZAW2" for s in route)
        if zaw1_count == 1 and not route_has_zaw2:
            if constraints.get("zaw_passes") != 1:
                errors.append("single ZAW1 and no ZAW2 requires zaw_passes == 1")

        if constraints.get("has_zaw2") is True:
            notes = str(metadata.get("notes") or "")
            source = str(metadata.get("route_source") or "")
            joined = f"{notes} {source}".upper()
            if "ZAW2" not in joined:
                errors.append("has_zaw2=True requires explicit note/source confirming real ZAW2 usage")

    planner_eligible = metadata.get("planner_eligible")
    operational_class = str(metadata.get("operational_class") or "").strip().upper()
    planner_block_reason = str(metadata.get("planner_block_reason") or "").strip()
    if planner_eligible is False and operational_class == "STANDARD" and not planner_block_reason:
        errors.append(
            "planner_eligible=False with operational_class=STANDARD requires planner_block_reason "
            "or non-standard operational_class"
        )

    return errors


def test_specs_metadata_contract_accepts_valid_synthetic_metadata():
    metadata = {
        "confidence": "CERTO",
        "route_status": "CERTO",
        "planner_eligible": True,
        "operational_class": "STANDARD",
        "route_source": "TL confirms ZAW2 real usage",
        "notes": "Specifica finitura + TL confermano ZAW2 reale.",
        "route_steps": [
            {"seq": 1, "station": "LAVAGGIO"},
            {"seq": 2, "station": "ZAW1"},
            {"seq": 3, "station": "ZAW2"},
            {"seq": 4, "station": "CP"},
        ],
        "constraints": {
            "has_zaw": True,
            "has_zaw1": True,
            "has_zaw2": True,
            "primary_zaw_station": "ZAW1",
            "zaw_passes": 2,
            "zaw_station_specificity": "CERTO",
        },
    }
    assert _validate_metadata_contract(metadata) == []


def test_specs_metadata_contract_flags_missing_route_steps_for_certo():
    metadata = {
        "confidence": "CERTO",
        "route_status": "CERTO",
        "constraints": {},
    }
    errors = _validate_metadata_contract(metadata)
    assert any("route_steps" in e for e in errors)


def test_specs_metadata_contract_flags_missing_zaw_constraints():
    metadata = {
        "confidence": "CERTO",
        "route_status": "CERTO",
        "route_steps": [{"seq": 1, "station": "ZAW1"}],
        "constraints": {"has_zaw1": True},
    }
    errors = _validate_metadata_contract(metadata)
    assert any("missing ZAW constraints" in e for e in errors)


def test_specs_metadata_contract_flags_single_zaw1_wrong_pass_count():
    metadata = {
        "confidence": "CERTO",
        "route_status": "CERTO",
        "route_steps": [{"seq": 1, "station": "ZAW1"}],
        "constraints": {
            "has_zaw": True,
            "has_zaw1": True,
            "has_zaw2": False,
            "primary_zaw_station": "ZAW1",
            "zaw_passes": 2,
            "zaw_station_specificity": "CERTO",
        },
    }
    errors = _validate_metadata_contract(metadata)
    assert any("zaw_passes == 1" in e for e in errors)


def test_specs_metadata_contract_flags_standard_not_eligible_without_reason():
    metadata = {
        "confidence": "INFERITO",
        "route_status": "DA_VERIFICARE",
        "planner_eligible": False,
        "operational_class": "STANDARD",
        "route_steps": [],
        "constraints": {},
    }
    errors = _validate_metadata_contract(metadata)
    assert any("planner_block_reason" in e for e in errors)


def test_specs_metadata_contract_flags_zaw2_without_explicit_evidence():
    metadata = {
        "confidence": "CERTO",
        "route_status": "CERTO",
        "route_steps": [{"seq": 1, "station": "ZAW2"}],
        "route_source": "TL",
        "notes": "no station detail",
        "constraints": {
            "has_zaw": True,
            "has_zaw1": False,
            "has_zaw2": True,
            "primary_zaw_station": "ZAW2",
            "zaw_passes": 1,
            "zaw_station_specificity": "CERTO",
        },
    }
    errors = _validate_metadata_contract(metadata)
    assert any("has_zaw2=True requires explicit note/source" in e for e in errors)
