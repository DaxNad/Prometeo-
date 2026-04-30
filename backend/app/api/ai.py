from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import run_local_llm

router = APIRouter()

class AIRequest(BaseModel):
    text: str

@router.post("/ai/local")
def ai_local(req: AIRequest):
    return {
        "model": "mistral",
        "response": run_local_llm(req.text),
        "warning": "Suggerimento AI locale — da validare TL",
    }
