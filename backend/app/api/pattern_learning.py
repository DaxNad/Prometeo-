from fastapi import APIRouter, Query

from app.services.pattern_learning_registry import (
    find_patterns_by_code,
    find_patterns_by_station,
    list_patterns,
)

router = APIRouter(
    prefix="/pattern-learning",
    tags=["pattern-learning"],
)

@router.get("/patterns")
def get_patterns(
    station: str | None = Query(default=None),
    code: str | None = Query(default=None),
):
    if station:
        return {
            "filter": {"station": station},
            "patterns": [
                {
                    "title": p.title,
                    "status": p.status,
                    "path": p.path,
                }
                for p in find_patterns_by_station(station)
            ],
        }

    if code:
        return {
            "filter": {"code": code},
            "patterns": [
                {
                    "title": p.title,
                    "status": p.status,
                    "path": p.path,
                }
                for p in find_patterns_by_code(code)
            ],
        }

    return {
        "patterns": list_patterns()
    }
