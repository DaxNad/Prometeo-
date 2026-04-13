from fastapi import APIRouter

router = APIRouter()

@router.get("/mobile")
def mobile_entry():
    return {
        "ui": "prometeo-tl-mobile",
        "description": "Interfaccia Team Leader mobile",
        "recommended_views": [
            "/production/sequence",
            "/production/turn-plan",
            "/production/machine-load",
            "/agent-runtime/summary"
        ]
    }
