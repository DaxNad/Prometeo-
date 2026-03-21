from fastapi import APIRouter
from .search import search_data

router = APIRouter()

@router.get("/search")
def search_endpoint(q: str):

    results = search_data(q)

    return {
        "query": q,
        "count": len(results),
        "results": results
    }
