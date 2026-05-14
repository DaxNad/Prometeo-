import json
import urllib.request
import urllib.error

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.factory import get_events_repository
from app.services.llm_service import get_local_llm_model, run_local_llm, run_local_llm_with_metadata
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



def _ollama_health(base_url: str = "http://127.0.0.1:11434") -> dict:
    """
    Local AI health check only.

    Contract:
    - read-only
    - no production decision authority
    - no planner mutation
    - no SMF/database write
    - no executor invocation
    """
    url = base_url.rstrip("/") + "/api/tags"

    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw)
    except Exception as exc:
        return {
            "ok": True,
            "provider": "ollama",
            "available": False,
            "base_url": base_url,
            "models": [],
            "writable": False,
            "decision_authority": False,
            "error": str(exc),
            "note": "Local AI health check only — no production decision authority",
        }

    models_payload = payload.get("models", [])
    models: list[str] = []

    if isinstance(models_payload, list):
        for item in models_payload:
            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str) and name.strip():
                    models.append(name.strip())

    return {
        "ok": True,
        "provider": "ollama",
        "available": True,
        "base_url": base_url,
        "models": models,
        "writable": False,
        "decision_authority": False,
        "note": "Local AI health check only — no production decision authority",
    }


@router.get("/ai/local/health")
def ai_local_health():
    return _ollama_health()


@router.post("/ai/local")
def ai_local(req: AIRequest):
    result = run_local_llm_with_metadata(req.text)
    return {
        "model": result.model,
        "configured_model": get_local_llm_model(),
        "fallback_used": result.fallback_used,
        "response": result.response,
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

    result = run_local_llm_with_metadata(prompt)

    return {
        "model": result.model,
        "configured_model": get_local_llm_model(),
        "fallback_used": result.fallback_used,
        "source": "sequence_planner",
        "prompt_preview": prompt,
        "response": result.response,
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
        "Non proporre modifiche runtime senza gate esplicito. "
        "Nel dominio PROMETEO, HENN, ZAW-1, ZAW-2, PIDMILL, CP e ULTRASUONI sono postazioni/processi, non operatori. "
        "Non proporre mai di spostare una postazione su un'altra. "
        "Puoi proporre solo verifiche di assegnazione operatori, saturazione postazione, sequenza fasi o vincoli da validare dal TL."
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

@router.post("/ai/mimo/validate-sequence")
def ai_mimo_validate_sequence(payload: dict):
    """
    Confronto planner vs MiMo.
    Nessun override. Solo analisi parallela.
    """
    sequence = payload.get("sequence") or {}
    events = payload.get("events") or []

    prompt = f"""
Analizza questa sequenza di produzione PROMETEO.

SEQUENZA:
{sequence}

EVENTI:
{events}

Obiettivo:
- Individua incoerenze logiche rispetto a sequenza, postazione, eventi e priorità
- Evidenzia rischi operativi in linguaggio Team Leader, non linguaggio generico IT
- NON parlare di automazioni, ridondanza, failover o azioni automatiche
- NON proporre modifiche runtime
- NON sostituire il planner
- Classifica CERTO / INFERITO / DA_VERIFICARE
- Usa solo concetti PROMETEO: postazione, saturazione, evento, priorità, sequenza, vincolo, conferma TL

Rispondi in modo sintetico e strutturato.
"""

    adapter = MiMoAdapter()

    try:
        result = adapter.ask(prompt=prompt)

        message = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return {
            "model": adapter.model,
            "enabled": True,
            "validation": message,
        }

    except MiMoAdapterError as exc:
        return {
            "model": adapter.model,
            "enabled": adapter.enabled,
            "error": str(exc),
        }

