from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api_production import get_explain, get_sequence, get_turn_plan
from ..db.session import get_db

router = APIRouter(prefix="/planner", tags=["planner"])


def build_decision_stub(payload: dict) -> dict:
    items = payload.get("items", [])

    if not items:
        return {
            "status": "ALLOW",
            "priority": 0.3,
            "constraints": [],
            "reasons": ["no_items"],
            "explain": "nessun item presente",
            "source": "rule_v1",
        }

    first = items[0]

    open_events = first.get("open_events_total", 0)
    customer_priority = first.get("customer_priority", "")
    station = first.get("critical_station", "")

    # STATUS
    if open_events > 0:
        status = "DEFER"
        reasons = ["has_blocking_events"]
    else:
        status = "ALLOW"
        reasons = ["no_blockers"]

    # PRIORITY
    if customer_priority == "CRITICA":
        priority = 1.0
    elif customer_priority == "MEDIA":
        priority = 0.6
    else:
        priority = 0.4

    # STATION CONTEXT
    if station in ("ZAW-1", "ZAW-2"):
        reasons.append("zaw_cluster")

    return {
        "status": status,
        "priority": priority,
        "constraints": [],
        "reasons": reasons,
        "explain": f"status={status}, priority={priority}",
        "source": "rule_v1",
    }


@router.get("/sequence")
def planner_sequence(db: Session = Depends(get_db)):
    result = get_sequence(db)
    result["decision"] = build_decision_stub(result)
    return result


@router.get("/turn-plan")
def planner_turn_plan(db: Session = Depends(get_db)):
    result = get_turn_plan(db)
    result["decision"] = build_decision_stub(result)
    return result


@router.get("/explain")
def planner_explain(db: Session = Depends(get_db)):
    result = get_explain(db)
    result["decision"] = build_decision_stub(result)
    return result
