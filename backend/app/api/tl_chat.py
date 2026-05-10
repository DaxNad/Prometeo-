from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter
from app.domain.article_tl_summary import build_article_tl_summary
from app.domain.assembly_progression import summarize_assembly_progression

router = APIRouter(prefix="/tl", tags=["tl-chat"])

ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_REGISTRY = ROOT / "data" / "local_smf" / "article_lifecycle_registry.json"
CODICI_STAGING_PREVIEW = ROOT / "data" / "local_smf" / "codici_staging_preview.json"
ARTICLE_ROUTE_MATRIX_PREVIEW = ROOT / "data" / "local_smf" / "finiture" / "article_route_matrix.preview.json"
SPECS_ROOT = ROOT / "specs_finitura"


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


def _extract_article_from_question(question: str) -> str:
    import re

    # PROMETEO article codes can be numeric or numeric with a short alphabetic suffix.
    # Examples: 12056, 12191A.
    match = re.search(r"\b\d{5}[A-Z]{0,3}\b", str(question or "").upper())
    return match.group(0) if match else ""


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


def _load_local_specs_metadata(article: str) -> dict[str, Any] | None:
    """
    Read-only local specs metadata loader.

    Contract:
    - reads specs_finitura/<article>/metadata.json if present
    - does not write files
    - does not expose image/path internals
    - accepts only pilot schema metadata
    """
    safe_article = _normalize_article(article)
    if not safe_article:
        return None

    metadata_path = SPECS_ROOT / safe_article / "metadata.json"
    if not metadata_path.exists():
        return None

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    if data.get("schema") != "PROMETEO_REAL_DATA_PILOT_V1":
        return None

    if _normalize_article(data.get("article")) != safe_article:
        return None

    return data


def _response_from_local_specs_metadata(article: str, metadata: dict[str, Any]) -> TLChatResponse:
    confidence = str(metadata.get("confidence") or metadata.get("classification") or "DA_VERIFICARE").upper()
    route_status = str(metadata.get("route_status") or "DA_VERIFICARE").upper()
    operational_class = str(metadata.get("operational_class") or "DA_VERIFICARE").upper()
    planner_eligible = bool(metadata.get("planner_eligible"))

    drawing = _clean(metadata.get("drawing"))
    rev = _clean(metadata.get("rev") or metadata.get("revision"))
    components = metadata.get("components") if isinstance(metadata.get("components"), list) else []
    packaging = metadata.get("packaging") if isinstance(metadata.get("packaging"), dict) else {}

    parts = [f"{article} — {confidence}."]

    if drawing:
        drawing_text = f"Specifica locale presente: disegno {drawing}"
        if rev:
            drawing_text += f" rev {rev}"
        parts.append(drawing_text + ".")

    parts.append(f"Classe operativa {operational_class}; planner_eligible={str(planner_eligible).lower()}.")

    if components:
        compact_components = ", ".join(str(item) for item in components[:8])
        parts.append(f"Componenti noti: {compact_components}.")

    if packaging:
        packaging_bits = []
        if packaging.get("sacchetto"):
            packaging_bits.append(f"sacchetto {packaging.get('sacchetto')}")
        if packaging.get("imballo"):
            packaging_bits.append(f"imballo {packaging.get('imballo')}")
        if packaging.get("quantita_per_imballo"):
            packaging_bits.append(f"qta/imballo {packaging.get('quantita_per_imballo')}")
        if packaging_bits:
            parts.append("Packaging noto: " + ", ".join(packaging_bits) + ".")

    route_steps = metadata.get("route_steps") if isinstance(metadata.get("route_steps"), list) else []
    route_stations = []
    for step in route_steps:
        if not isinstance(step, dict):
            continue
        station = _clean(step.get("station"))
        if station:
            route_stations.append(station)

    if route_status != "CERTO":
        parts.append(f"Route {route_status}: non trattare la sequenza come definitiva senza conferma TL.")
    elif route_stations:
        parts.append("Route confermata: " + " → ".join(route_stations) + ".")
    else:
        parts.append("Route marcata CERTO nel metadata locale.")

    constraints = metadata.get("constraints") if isinstance(metadata.get("constraints"), dict) else {}
    if constraints.get("has_henn") is True:
        parts.append("HENN presente.")
    elif constraints.get("has_henn") is False:
        parts.append("HENN assente sul singolo.")
    if constraints.get("cp_required"):
        parts.append("CP finale obbligatorio.")

    requires_confirmation = route_status != "CERTO"

    return TLChatResponse(
        ok=True,
        answer=" ".join(parts),
        confidence=confidence,
        risk=(
            "Metadata locale articolo presente; route ancora da verificare."
            if requires_confirmation
            else "Metadata locale articolo presente."
        ),
        recommended_action=(
            "Usare il metadata locale come base articolo; confermare route prima di pianificazione piena."
            if requires_confirmation
            else "Usare il metadata locale come riferimento operativo confermato."
        ),
        requires_confirmation=requires_confirmation,
        technical_details_hidden=True,
    )


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


def _load_article_route_matrix_preview() -> dict[str, Any]:
    """
    Read-only preview matrix loader.

    Contract:
    - reads local preview matrix only
    - does not write to SMF/database
    - does not call external APIs
    - preview is secondary fallback after active article_tl_summary
    """
    if not ARTICLE_ROUTE_MATRIX_PREVIEW.exists():
        return {}

    try:
        data = json.loads(ARTICLE_ROUTE_MATRIX_PREVIEW.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def _response_from_preview_profile(article: str) -> TLChatResponse | None:
    matrix = _load_article_route_matrix_preview()
    profiles = matrix.get("profiles")

    if not isinstance(profiles, dict):
        return None

    profile = profiles.get(article)
    if not isinstance(profile, dict):
        return None

    confidence = str(profile.get("confidence") or "DA_VERIFICARE").upper()
    signals = profile.get("signals") if isinstance(profile.get("signals"), dict) else {}
    review_reasons = profile.get("review_reasons") if isinstance(profile.get("review_reasons"), list) else []
    discrepancies = profile.get("discrepancies") if isinstance(profile.get("discrepancies"), list) else []

    primary_zaw = signals.get("primary_zaw_station")
    zaw_passes = signals.get("zaw_passes")
    cp_mode = signals.get("cp_machine_mode")
    shared = signals.get("shared_components") or []

    pieces: list[str] = [f"{article} — {confidence}."]

    if confidence == "DA_VERIFICARE":
        pieces.append("Profilo non operativo: serve conferma TL prima di usarlo per strategia turno.")
    elif confidence == "INFERITO":
        pieces.append("Profilo inferito: usare con cautela, non come dato certo.")

    if primary_zaw and isinstance(zaw_passes, int) and zaw_passes > 1:
        pieces.append(f"Segnale ZAW: {primary_zaw} con {zaw_passes} passaggi; non dedurre ZAW2 automaticamente.")
    elif primary_zaw:
        pieces.append(f"Segnale ZAW: {primary_zaw}; non dedurre ZAW2 automaticamente.")

    if signals.get("has_henn"):
        pieces.append("HENN presente.")
    elif signals.get("has_henn") is False:
        pieces.append("HENN non indicato.")

    if signals.get("has_pidmill"):
        pieces.append("PIDMILL presente.")

    if signals.get("cp_required"):
        if cp_mode:
            pieces.append(f"CP finale obbligatorio, modalità {cp_mode}.")
        else:
            pieces.append("CP finale obbligatorio.")

    if shared:
        pieces.append("Componenti condivisi da monitorare: " + ", ".join(str(x) for x in shared) + ".")

    progression_lines = summarize_assembly_progression(profile)
    if progression_lines:
        pieces.append("Progressione assemblaggio: " + " | ".join(progression_lines[:3]) + ".")

    if review_reasons:
        pieces.append("Motivi verifica: " + ", ".join(str(x) for x in review_reasons) + ".")

    for item in discrepancies:
        if not isinstance(item, dict):
            continue
        if item.get("status") == "DA_VERIFICARE":
            code = item.get("code") or "discrepanza"
            wrong = item.get("wrong_source") or ""
            pieces.append(f"Discrepanza da verificare: {code}. {wrong}".strip())
            break

    return TLChatResponse(
        ok=True,
        answer=" ".join(pieces),
        confidence=confidence,
        risk=(
            "Profilo preview da verificare: non usarlo per decisione operativa senza conferma TL."
            if confidence == "DA_VERIFICARE"
            else "Profilo preview inferito: usare con cautela."
            if confidence == "INFERITO"
            else "Profilo preview disponibile."
        ),
        recommended_action=(
            "Conferma TL richiesta prima di usare questo articolo in strategia turno."
            if confidence == "DA_VERIFICARE"
            else "Usare come supporto provvisorio, poi consolidare con specifica/metadata."
            if confidence == "INFERITO"
            else "Seguire risposta operativa sintetica."
        ),
        requires_confirmation=confidence != "CERTO",
        technical_details_hidden=True,
    )


def _response_from_article_summary(article: str) -> TLChatResponse | None:
    summary = build_article_tl_summary(article)

    if not summary.get("ok"):
        return None

    signals = summary.get("signals") if isinstance(summary.get("signals"), dict) else {}
    criticalities = summary.get("criticalities") if isinstance(summary.get("criticalities"), list) else []

    compact: list[str] = []
    compact.append(f"{article} — {summary.get('confidence', 'DA_VERIFICARE')}.")

    primary_zaw = signals.get("primary_zaw_station")
    zaw_passes = signals.get("zaw_passes")

    if primary_zaw and isinstance(zaw_passes, int) and zaw_passes > 1:
        compact.append(
            f"Usa {primary_zaw} con {zaw_passes} passaggi; ZAW1_2 non è ZAW2."
        )
    elif primary_zaw:
        compact.append(f"Usa {primary_zaw}; non trattare ZAW2 come alternativa automatica.")

    if signals.get("has_henn"):
        compact.append("HENN prima di innesto rapido/ZAW.")
    elif signals.get("has_henn") is False:
        compact.append("Nessun HENN indicato nel profilo operativo.")

    if signals.get("has_pidmill"):
        compact.append("PIDMILL presente.")

    cp_mode = signals.get("cp_machine_mode")
    if signals.get("cp_required") and cp_mode:
        compact.append(f"CP finale obbligatorio, modalità {cp_mode}.")
    elif signals.get("cp_required"):
        compact.append("CP finale obbligatorio.")

    shared = signals.get("shared_components") or []
    if shared:
        compact.append("Componenti condivisi da monitorare: " + ", ".join(str(x) for x in shared) + ".")

    for item in criticalities:
        text = str(item)
        if "Discrepanza" in text or "discrepanza" in text:
            compact.append(text)
            break

    return TLChatResponse(
        ok=True,
        answer=" ".join(compact),
        confidence=str(summary.get("confidence") or "DA_VERIFICARE"),
        risk="Profilo operativo articolo disponibile. Dettagli tecnici nascosti salvo richiesta.",
        recommended_action=str(summary.get("tl_action") or "Seguire risposta operativa sintetica."),
        requires_confirmation=False,
        technical_details_hidden=True,
    )


def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
    question = payload.question.strip()
    article = _normalize_article(payload.context.article) or _extract_article_from_question(question)
    lifecycle = _load_lifecycle_registry()

    if not article and _question_asks_for_densification_candidates(question):
        staging = _load_codici_staging_preview()
        return _response_for_densification_candidates(staging)

    requested_status = _requested_lifecycle_status_from_question(question)
    if not article and requested_status:
        return _response_for_lifecycle_status_list(lifecycle, requested_status)

    if article:
        article_summary_response = _response_from_article_summary(article)
        if article_summary_response:
            return article_summary_response

        local_specs_metadata = _load_local_specs_metadata(article)
        if local_specs_metadata:
            return _response_from_local_specs_metadata(article, local_specs_metadata)

        lifecycle_payload = lifecycle.get(article)

        if lifecycle_payload:
            return _response_from_lifecycle(article, lifecycle_payload)

        preview_response = _response_from_preview_profile(article)
        if preview_response:
            return preview_response

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
