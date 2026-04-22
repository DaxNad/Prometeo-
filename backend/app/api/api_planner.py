from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api_production import get_explain, get_sequence, get_turn_plan
from ..db.session import get_db

router = APIRouter(prefix="/planner", tags=["planner"])


def build_decision_stub(payload: dict) -> dict:
    return {
        "status": "ALLOW",
        "priority": 0.5,
        "constraints": [],
        "reasons": ["default_stub"],
        "explain": "placeholder decision",
        "source": "fallback",
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
