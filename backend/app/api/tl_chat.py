from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter

router = APIRouter(prefix="/tl", tags=["tl-chat"])

ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_REGISTRY = ROOT / "data" / "local_smf" / "article_lifecycle_registry.json"
CODICI_STAGING_PREVIEW = ROOT / "data" / "local_smf" / "codici_staging_preview.json"


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




def _load_codici_staging_preview() -> dict[str, Any]:
    """
    Read-only Codici staging preview loader.

    Contract:
    - reads local staging preview if present
    - does not create files/directories
    - does not write to SMF/database
    - does not call external APIs
    """
    if not CODICI_STAGING_PREVIEW.exists():
        return {}

    try:
        data = json.loads(CODICI_STAGING_PREVIEW.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def _question_asks_for_densification_candidates(question: str) -> bool:
    normalized = question.strip().lower()

    return (
        "quali" in normalized
        and "codici" in normalized
        and (
            "densificare" in normalized
            or "staging" in normalized
            or "posso portare" in normalized
            or "candidati" in normalized
        )
    )


def _response_for_densification_candidates(staging: dict[str, Any]) -> TLChatResponse:
    items = staging.get("items")
    if not isinstance(items, list):
        items = []

    codes: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        code = _clean(item.get("codice"))
        tl_decision = _clean(item.get("tl_decision")).upper()
        staging_status = _clean(item.get("staging_status")).upper()
        next_action = _clean(item.get("next_action")).upper()

        if (
            code
            and tl_decision == "PENDING"
            and staging_status == "PREVIEW_ONLY"
            and next_action in {"REVIEW_BEFORE_STAGING", "REVIEW_HIGH_PRIORITY"}
        ):
            codes.append(code)

    if not codes:
        return TLChatResponse(
            ok=True,
            answer="Non risultano codici pronti per review TL nello staging preview.",
            confidence="CERTO",
            risk=None,
            recommended_action="Rigenerare lo staging preview o verificare lifecycle/Codici/BOM.",
            requires_confirmation=False,
        )

    sample = codes[:20]
    suffix = "" if len(codes) <= 20 else f" Altri {len(codes) - 20} codici non mostrati."

    return TLChatResponse(
        ok=True,
        answer=(
            "Codici pronti per review TL prima della densificazione: "
            + ", ".join(sample)
            + "."
            + suffix
        ),
        confidence="CERTO",
        risk="I codici sono candidati da staging preview: serve conferma TL prima di qualsiasi scrittura.",
        recommended_action="Revisionare i candidati e confermare esplicitamente prima dello staging controllato.",
        requires_confirmation=True,
    )


def _requested_lifecycle_status_from_question(question: str) -> str | None:
    normalized = question.strip().lower()

    if "quali" not in normalized or "codici" not in normalized:
        return None

    if (
        "verificare" in normalized
        or "da verificare" in normalized
        or "verifica" in normalized
    ):
        return "DA_VERIFICARE"

    if "new entry" in normalized or "nuovi" in normalized or "nuovo" in normalized:
        return "NEW_ENTRY"

    if "fuori produzione" in normalized or "fuori-prod" in normalized:
        return "FUORI_PRODUZIONE"

    return None


def _response_for_lifecycle_status_list(
    lifecycle: dict[str, dict[str, Any]],
    requested_status: str,
) -> TLChatResponse:
    codes: list[str] = []

    for code, payload in sorted(lifecycle.items()):
        if not isinstance(payload, dict):
            continue

        status = _clean(payload.get("status")).upper()
        if status == requested_status:
            codes.append(code)

    if requested_status == "DA_VERIFICARE":
        empty_answer = "Non risultano codici DA_VERIFICARE nel lifecycle registry reparto."
        risk = "Sono presenti codici con stato vita articolo non ancora confermato."
        recommended = "Verifica TL richiesta prima di densificazione o staging."
    elif requested_status == "NEW_ENTRY":
        empty_answer = "Non risultano codici NEW_ENTRY nel lifecycle registry reparto."
        risk = "I codici NEW_ENTRY richiedono densificazione prioritaria e conferma TL."
        recommended = "Verificare i codici nuovi e prepararli per preview/staging controllato."
    elif requested_status == "FUORI_PRODUZIONE":
        empty_answer = "Non risultano codici FUORI_PRODUZIONE nel lifecycle registry reparto."
        risk = "I codici fuori produzione non devono essere promossi automaticamente."
        recommended = "Escludere dalla densificazione prioritaria salvo conferma TL."
    else:
        empty_answer = f"Non risultano codici {requested_status} nel lifecycle registry reparto."
        risk = "Stato lifecycle richiesto non gestito esplicitamente."
        recommended = "Verifica TL richiesta."

    if not codes:
        return TLChatResponse(
            ok=True,
            answer=empty_answer,
            confidence="CERTO",
            risk=None,
            recommended_action="Nessuna azione lifecycle urgente rilevata.",
            requires_confirmation=False,
        )

    return TLChatResponse(
        ok=True,
        answer=f"Codici {requested_status} nel lifecycle registry reparto: " + ", ".join(codes) + ".",
        confidence="CERTO",
        risk=risk,
        recommended_action=recommended,
        requires_confirmation=True,
    )


def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
    article = _normalize_article(payload.context.article)
    question = payload.question.strip()
    lifecycle = _load_lifecycle_registry()

    if not article and _question_asks_for_densification_candidates(question):
        staging = _load_codici_staging_preview()
        return _response_for_densification_candidates(staging)

    requested_status = _requested_lifecycle_status_from_question(question)
    if not article and requested_status:
        return _response_for_lifecycle_status_list(lifecycle, requested_status)

    if article:
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
