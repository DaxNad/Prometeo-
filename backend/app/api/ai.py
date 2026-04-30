from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.factory import get_events_repository
from app.services.llm_service import run_local_llm
from app.services.sequence_planner import sequence_planner_service
from app.ai_adapters.mimo_adapter import MiMoAdapter, MiMoAdapterError

router = APIRouter()


class AIRequest(BaseModel):
    text: str


def _build_sequence_prompt(sequence_payload: dict, active_events: list[dict] | None = None) -> str:
    items = sequence_payload.get("items", [])
    decision = sequence_payload.get("decision", {})
    active_events = active_events or []

    lines = [
        "Analizza questa sequenza reale PROMETEO e produci una strategia TL breve.",
        "",
        f"Planner stage: {sequence_payload.get('planner_stage', 'UNKNOWN')}",
        f"Source view: {sequence_payload.get('source_view', 'UNKNOWN')}",
        f"Items count: {sequence_payload.get('items_count', len(items))}",
        f"Warnings: {', '.join(sequence_payload.get('warnings', [])) or 'nessuno'}",
    ]

    if active_events:
        lines.extend([
            "",
            "Eventi attivi OPEN:",
        ])
        for event in active_events[:5]:
            lines.append(
                "- "
                f"titolo={event.get('title', '')}; "
                f"linea={event.get('line', '')}; "
                f"postazione={event.get('station', '')}; "
                f"tipo={event.get('event_type', '')}; "
                f"severità={event.get('severity', '')}; "
                f"nota={event.get('note', '')}"
            )
    else:
        lines.extend(["", "Eventi attivi OPEN: nessuno"])

    lines.extend(["", "Articoli in sequenza:"])

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

    repo = get_events_repository()
    try:
        active_events = repo.list_active_events()
    except Exception:
        active_events = []

    # costruzione vincoli reali da eventi
    blocking = False
    high_risk = False
    zaw_blocked = set()

    for e in active_events:
        severity = (e.get("severity") or "").upper()
        station = (e.get("station") or "").upper()

        if severity == "CRITICAL":
            blocking = True

        if severity in ("CRITICAL", "HIGH"):
            high_risk = True

        if "ZAW" in station:
            zaw_blocked.add(station)

    prompt = _build_sequence_prompt(sequence_payload, active_events)

    # append vincoli
    prompt += "\n\nVincoli operativi reali:"
    prompt += f"\n- blocking={blocking}"
    prompt += f"\n- high_risk={high_risk}"
    prompt += f"\n- zaw_blocked={list(zaw_blocked)}"

    return {
        "model": "mistral",
        "source": "sequence_planner",
        "prompt_preview": prompt,
        "response": run_local_llm(prompt),
        "sequence": sequence_payload,
        "warning": "Suggerimento AI locale su sequenza reale — da validare TL",
    }

@router.post("/ai/mimo")
def ai_mimo(payload: dict):
    """
    Endpoint MiMo isolato.
    Protetto dal middleware PROMETEO_API_KEY.
    Non modifica dominio, planner, SMF o ProductionEvent.
    """
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        return {
            "model": "mimo",
            "enabled": False,
            "error": "prompt mancante",
        }

    system = (
        "Sei un adapter AI secondario per PROMETEO. "
        "Non prendere decisioni produttive autonome. "
        "Classifica sempre le affermazioni come CERTO, INFERITO o DA_VERIFICARE. "
        "Non proporre modifiche runtime senza gate esplicito."
    )

    adapter = MiMoAdapter()

    try:
        result = adapter.ask(prompt=prompt, system=system)
        message = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        usage = result.get("usage", {})

        return {
            "model": adapter.model,
            "enabled": True,
            "content": message,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "cost": usage.get("cost"),
            },
        }
    except MiMoAdapterError as exc:
        return {
            "model": adapter.model,
            "enabled": adapter.enabled,
            "error": str(exc),
        }

