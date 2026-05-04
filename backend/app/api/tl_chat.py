from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter

router = APIRouter(prefix="/tl", tags=["tl-chat"])


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


def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
    article = _normalize_article(payload.context.article)
    question = payload.question.strip()

    if article == "12402":
        return TLChatResponse(
            ok=True,
            answer="Il codice 12402 è da verificare prima di densificarlo o promuoverlo.",
            confidence="DA_VERIFICARE",
            risk="Lifecycle articolo non confermato: è stato citato in reparto ma non classificato come attivo, fuori produzione o new entry.",
            recommended_action="Verifica TL richiesta prima di staging.",
            requires_confirmation=True,
        )

    if article:
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} non ha ancora una risposta TL dedicata nel contratto chat v1.",
            confidence="DA_VERIFICARE",
            risk="Dato non ancora interpretato dalla memoria TL chat.",
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
