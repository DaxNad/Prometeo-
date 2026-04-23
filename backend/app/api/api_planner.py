from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api_production import get_explain, get_sequence, get_turn_plan
from ..db.session import get_db

router = APIRouter(prefix="/planner", tags=["planner"])


def build_decision_trace(payload: dict) -> dict:
    items = payload.get("items", [])

    stations = []
    priorities = []
    blocking = False

    for item in items:
        st = item.get("critical_station")
        if st:
            stations.append(st)

        pr = item.get("customer_priority")
        if pr:
            priorities.append(pr)

        if item.get("open_events_total", 0) > 0:
            blocking = True

    return {
        "items_count": len(items),
        "stations": list(set(stations)),
        "has_blocking_events": blocking,
        "customer_priorities": priorities,
    }



def build_decision_stub(payload: dict) -> dict:
    items = payload.get("items", [])

    if not items:
        return {
            "status": "ALLOW",
            "priority": 0.3,
            "constraints": [],
            "reasons": ["no_items"],
            "explain": "no items",
            "source": "rule_v2",
        }

    # PRIORITY MAP
    def map_priority(p):
        if p == "CRITICA":
            return 1.0
        if p == "MEDIA":
            return 0.6
        return 0.4

    priorities = []
    has_blocking = False
    stations = set()

    for item in items:
        priorities.append(map_priority(item.get("customer_priority", "")))
        if item.get("open_events_total", 0) > 0:
            has_blocking = True
        st = item.get("critical_station")
        if st:
            stations.add(st)

    # STATUS
    status = "DEFER" if has_blocking else "ALLOW"

    # PRIORITY
    priority = max(priorities) if priorities else 0.3

    # REASONS
    reasons = []
    if has_blocking:
        reasons.append("has_blocking_events")
    else:
        reasons.append("no_blockers")

    if "ZAW-1" in stations or "ZAW-2" in stations:
        reasons.append("zaw_cluster")

    if len(items) > 1:
        reasons.append("multi_item_cluster")

    return {
        "status": status,
        "priority": priority,
        "constraints": [],
        "reasons": reasons,
        "explain": f"items={len(items)}, blocking={has_blocking}, priority={priority}",
        "source": "rule_v2",
    }
@router.get("/sequence")
def planner_sequence(db: Session = Depends(get_db)):
    result = get_sequence(db)
    result["decision"] = build_decision_stub(result)
    result["decision_trace"] = build_decision_trace(result)
    return result


@router.get("/turn-plan")
def planner_turn_plan(db: Session = Depends(get_db)):
    result = get_turn_plan(db)
    result["decision"] = build_decision_stub(result)
    result["decision_trace"] = build_decision_trace(result)
    return result


@router.get("/explain")
def planner_explain(db: Session = Depends(get_db)):
    result = get_explain(db)
    result["decision"] = build_decision_stub(result)
    result["decision_trace"] = build_decision_trace(result)
    return result
