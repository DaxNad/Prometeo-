import json
from pathlib import Path
from fastapi import APIRouter, Query

router = APIRouter(prefix="/search", tags=["Search"])

DATA_DIR = Path("data")


def load_data():
    records = []

    if not DATA_DIR.exists():
        return records

    for file in DATA_DIR.glob("*.json"):

        try:
            with open(file, "r", encoding="utf-8") as f:

                content = json.load(f)

                if isinstance(content, list):
                    records.extend(content)

                elif isinstance(content, dict):
                    records.append(content)

        except Exception as e:
            print(f"Errore lettura {file}: {e}")

    return records


def search_data(query: str, limit: int = 50):

    query = query.lower()
    results = []

    data = load_data()

    for item in data:

        try:
            text = json.dumps(item).lower()

            if query in text:
                results.append(item)

        except:
            continue

        if len(results) >= limit:
            break

    return results


@router.get("/")
def search_endpoint(
    q: str = Query(..., description="Search query"),
    limit: int = 50,
):

    results = search_data(q, limit)

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
