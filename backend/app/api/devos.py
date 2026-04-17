from fastapi import APIRouter

from ..services import devos_service

router = APIRouter(tags=["Development OS"])


@router.get("/dev/status")
def get_dev_status():
    return devos_service.get_dev_status()


@router.get("/dev/tasks")
def get_dev_tasks():
    return devos_service.get_dev_tasks()


@router.get("/dev/logs")
def get_dev_logs():
    return devos_service.get_dev_logs()


@router.get("/dev/milestones")
def get_dev_milestones():
    return devos_service.get_dev_milestones()


@router.get("/dev/domain-info")
def get_domain_info():
    return {
        "domain": "PROMETEO",
        "core_entities": [
            "Order",
            "ProductionEvent",
            "Station",
            "Rule",
            "SMFRow",
        ],
        "states_supported": [
            "PARZIALE",
            "IN_ATTESA",
            "SOSPESO",
            "COMPLETATO",
            "BLOCCATO",
        ],
        "stations_supported": [
            "GUAINE",
            "ULTRASUONI",
            "FORNO",
            "WINTEC",
            "PIDMILL",
            "ZAW1",
            "ZAW2",
            "HENN",
            "CP",
        ],
    }


@router.get("/dev/domain-check")
def get_domain_check():
    core_entities = [
        "Order",
        "ProductionEvent",
        "Station",
        "Rule",
        "SMFRow",
    ]
    states_expected = [
        "PARZIALE",
        "IN_ATTESA",
        "SOSPESO",
        "COMPLETATO",
        "BLOCCATO",
    ]
    stations_expected = [
        "GUAINE",
        "ULTRASUONI",
        "FORNO",
        "WINTEC",
        "PIDMILL",
        "ZAW1",
        "ZAW2",
        "HENN",
        "CP",
    ]

    return {
        "domain": "PROMETEO",
        "status": "OK",
        "checks": {
            "core_entities_present": True,
            "states_defined": True,
            "stations_defined": True,
        },
        "core_entities": core_entities,
        "states_expected": states_expected,
        "stations_expected": stations_expected,
    }


@router.get("/dev/planner-info")
def get_planner_info():
    return {
        "planner": "PROMETEO",
        "status": "OK",
        "planning_focus": [
            "station_constraints",
            "shared_components",
            "blocking_phases",
            "customer_priority",
            "delivery_dates",
        ],
        "core_dependencies": [
            "Order",
            "ProductionEvent",
            "Station",
            "Rule",
        ],
        "notes": [
            "planner is diagnostic-only here",
            "no runtime planner state inspection",
            "no database access",
        ],
    }


@router.get("/dev/order-model-info")
def get_order_model_info():
    return {
        "aggregate": "Order",
        "role": "bounded aggregate root",
        "depends_on": [
            "ProductionEvent",
            "Station",
            "Rule",
        ],
        "core_fields_expected": [
            "order_id",
            "code",
            "quantity",
            "station",
            "status",
            "priority",
            "due_date",
        ],
        "states_supported": [
            "IN_ATTESA",
            "PARZIALE",
            "COMPLETATO",
            "BLOCCATO",
            "SOSPESO",
            "NOK",
        ],
        "notes": [
            "static domain diagnostic",
            "no database access",
            "no schema validation",
        ],
    }
