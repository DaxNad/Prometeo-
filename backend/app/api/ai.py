from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.llm_service import run_local_llm
from app.services.sequence_planner import sequence_planner_service

router = APIRouter()


class AIRequest(BaseModel):
    text: str


def _build_sequence_prompt(sequence_payload: dict) -> str:
    items = sequence_payload.get("items", [])
    decision = sequence_payload.get("decision", {})

    lines = [
        "Analizza questa sequenza reale PROMETEO e produci una strategia TL breve.",
        "",
        f"Decisione planner: {decision.get('status', 'UNKNOWN')}",
        f"Priorità planner: {decision.get('priority', 'n/a')}",
        f"Motivi planner: {', '.join(decision.get('reasons', []))}",
        "",
        "Articoli in sequenza:",
    ]

    for item in items[:5]:
        lines.append(
            "- "
            f"articolo={item.get('article', '')}; "
            f"postazione={item.get('critical_station', '')}; "
            f"priorità={item.get('customer_priority', '')}; "
            f"quantità={item.get('quantity', '')}; "
            f"azione_TL={item.get('tl_action', '')}; "
            f"componenti_condivisi={', '.join(item.get('shared_components', []))}; "
            f"motivo={item.get('shared_component_impact_reason', '')}"
        )

    return "\n".join(lines)


@router.post("/ai/local")
def ai_local(req: AIRequest):
    return {
        "model": "mistral",
        "response": run_local_llm(req.text),
        "warning": "Suggerimento AI locale — da validare TL",
    }


@router.post("/ai/sequence")
def ai_sequence(db: Session = Depends(get_db)):
    sequence_payload = sequence_planner_service.build_global_sequence(db)
    prompt = _build_sequence_prompt(sequence_payload)

    return {
        "model": "mistral",
        "source": "sequence_planner",
        "prompt_preview": prompt,
        "response": run_local_llm(prompt),
        "sequence": sequence_payload,
        "warning": "Suggerimento AI locale su sequenza reale — da validare TL",
    }
