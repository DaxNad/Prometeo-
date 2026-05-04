from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter

router = APIRouter(prefix="/tl", tags=["tl-chat"])

ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_REGISTRY = ROOT / "data" / "local_smf" / "article_lifecycle_registry.json"


class TLChatContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    article: str | None = None
    station: str | None = None
    drawing: str | None = None


class TLChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    question: str = Field(min_length=1)
    context: TLChatContext = Field(default_factory=TLChatContext)


class TLChatResponse(BaseModel):
    ok: bool
    mode: str = "TL_CHAT_CONTRACT_V1"
    answer: str
    confidence: str
    risk: str | None = None
    recommended_action: str | None = None
    requires_confirmation: bool = False
    technical_details_hidden: bool = True


def _normalize_article(value: str | None) -> str:
    return str(value or "").strip().upper()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _load_lifecycle_registry() -> dict[str, dict[str, Any]]:
    """
    Read-only lifecycle registry loader.

    Contract:
    - reads local lifecycle registry if present
    - does not create files/directories
    - does not write to SMF/database
    - does not call external APIs
    """
    if not LIFECYCLE_REGISTRY.exists():
        return {}

    try:
        data = json.loads(LIFECYCLE_REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    output: dict[str, dict[str, Any]] = {}
    for code, payload in data.items():
        if isinstance(payload, dict):
            output[str(code).strip().upper()] = payload

    return output


def _response_from_lifecycle(article: str, payload: dict[str, Any]) -> TLChatResponse:
    status = _clean(payload.get("status")).upper() or "SCONOSCIUTO"
    note = _clean(payload.get("note"))
    source = _clean(payload.get("source"))

    if status == "NEW_ENTRY":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta NEW_ENTRY nella memoria reparto.",
            confidence="INFERITO",
            risk="Codice nuovo: va densificato con priorità ma confermato prima dello staging.",
            recommended_action="Verifica TL e poi priorità alta di densificazione.",
            requires_confirmation=True,
        )

    if status == "FUORI_PRODUZIONE":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta FUORI_PRODUZIONE nella memoria reparto.",
            confidence="INFERITO",
            risk="Codice non prioritario per densificazione operativa; evitare promozione automatica.",
            recommended_action="Non portare in staging salvo conferma TL esplicita.",
            requires_confirmation=True,
        )

    if status == "ATTIVO":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta ATTIVO nella memoria reparto.",
            confidence="INFERITO",
            risk="Stato reparto presente ma da incrociare con BOM, Codici e route prima di scritture.",
            recommended_action="Procedere con preview e conferma TL prima dello staging.",
            requires_confirmation=True,
        )

    if status == "DA_VERIFICARE":
        detail = f" Nota reparto: {note}" if note else ""
        source_text = f" Fonte: {source}." if source else ""
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} è da verificare prima di densificarlo o promuoverlo.{source_text}{detail}",
            confidence="DA_VERIFICARE",
            risk="Lifecycle articolo non confermato: non è ancora classificato come attivo, fuori produzione o new entry.",
            recommended_action="Verifica TL richiesta prima di staging.",
            requires_confirmation=True,
        )

    return TLChatResponse(
        ok=True,
        answer=f"Il codice {article} è presente nel lifecycle registry ma ha stato non riconosciuto: {status}.",
        confidence="DA_VERIFICARE",
        risk="Stato lifecycle non interpretabile.",
        recommended_action="Correggere o confermare lo stato articolo nel registry reparto.",
        requires_confirmation=True,
    )


def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
    article = _normalize_article(payload.context.article)

    if article:
        lifecycle = _load_lifecycle_registry()
        lifecycle_payload = lifecycle.get(article)

        if lifecycle_payload:
            return _response_from_lifecycle(article, lifecycle_payload)

        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} non è presente nel lifecycle registry della memoria reparto.",
            confidence="DA_VERIFICARE",
            risk="Stato vita articolo non noto alla TL Chat.",
            recommended_action="Verificare articolo tramite preview Codici, lifecycle registry o profilo articolo.",
            requires_confirmation=True,
        )

    return TLChatResponse(
        ok=True,
        answer="Domanda ricevuta. La TL Chat v1 richiede almeno un articolo nel context per produrre una risposta operativa specifica.",
        confidence="DA_VERIFICARE",
        risk="Contesto articolo mancante.",
        recommended_action="Ripetere la domanda indicando un codice articolo.",
        requires_confirmation=True,
    )


@router.post("/chat", response_model=TLChatResponse)
def tl_chat(payload: TLChatRequest) -> TLChatResponse:
    """
    PROMETEO TL CHAT — contract v1.

    Read-only contract:
    - no SMF write
    - no DB write
    - no planner mutation
    - no executor
    - no technical noise in response
    """
    return _build_contract_response(payload)
