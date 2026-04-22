from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api_production import get_explain, get_sequence, get_turn_plan
from ..db.session import get_db

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get("/sequence")
def planner_sequence(db: Session = Depends(get_db)):
    return get_sequence(db)


@router.get("/turn-plan")
def planner_turn_plan(db: Session = Depends(get_db)):
    return get_turn_plan(db)


@router.get("/explain")
def planner_explain(db: Session = Depends(get_db)):
    return get_explain(db)
