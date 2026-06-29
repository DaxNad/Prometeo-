from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter
from app.domain.article_tl_summary import build_article_tl_summary
from app.domain.assembly_progression import summarize_assembly_progression
from app.domain.human_checkpoint import consultation
from app.atlas_engine.governed_retrieval import build_governed_retrieval_pack
from app.semantic_registry import resolve_confidence
from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    resolve_tl_chat_context,
)
from app.services.tl_chat_confirmation_rendering import (
    TLChatConfirmationRenderingInput,
    build_confirmation_rendering,
)
from app.services.pattern_learning_registry import find_patterns_by_station
from tools.context_source_reader_adapter import ContextSourceReaderAdapter
from tools.tl_chat_context_reader_bridge import build_context_reader_candidate

router = APIRouter(prefix="/tl", tags=["tl-chat"])

ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_REGISTRY = ROOT / "data" / "local_smf" / "article_lifecycle_registry.json"
CODICI_STAGING_PREVIEW = ROOT / "data" / "local_smf" / "codici_staging_preview.json"
TL_REAL_SPEC_INTAKE = ROOT / "data" / "local_reports" / "tl_real_spec_intake" / "TL_REAL_SPEC_INTAKE_001.json"
ARTICLE_ROUTE_MATRIX_PREVIEW = ROOT / "data" / "local_smf" / "finiture" / "article_route_matrix.preview.json"
FAMILY_REGISTRY = ROOT / "data" / "backend" / "app" / "registry" / "prometeo_famiglie.json"
SPECS_ROOT = ROOT / "specs_finitura"
SPEC_INTAKE_PREVIEW_ROOT = ROOT / "data" / "local_reports" / "spec_intake_preview"


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
    evidence_pack: dict[str, Any] | None = None


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


def _resolve_tl_chat_confidence(value: Any) -> str:
    """
    Bind TL Chat confidence labels to the canonical semantic registry.

    This is intentionally read-only: it normalizes the label returned by
    existing TL Chat sources and does not grant planner or execution authority.
    """
    return resolve_confidence(value).normalized_key


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


def _load_family_registry() -> dict[str, dict[str, Any]]:
    if not FAMILY_REGISTRY.exists():
        return {}

    try:
        data = json.loads(FAMILY_REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    return {
        str(k).strip().upper(): v
        for k, v in data.items()
        if isinstance(v, dict)
    }


def _extract_family_from_question(question: str) -> str:
    normalized = question.strip().upper()
    registry = _load_family_registry()

    for family in registry:
        if family in normalized:
            return family

    return ""


def _response_from_family_registry(
    family: str,
    payload: dict[str, Any],
) -> TLChatResponse:
    descrizione = _clean(payload.get("descrizione"))
    componenti = payload.get("componenti_comuni") or []
    postazioni = payload.get("postazioni_abilitate") or []

    componenti_txt = ", ".join(map(str, componenti)) or "nessuno"
    postazioni_txt = ", ".join(map(str, postazioni)) or "nessuna"

    answer = (
        f"{family}"
        + (f" — {descrizione}." if descrizione else ".")
        + f" Componenti comuni: {componenti_txt}."
        + f" Postazioni: {postazioni_txt}."
    )

    return TLChatResponse(
        ok=True,
        answer=answer,
        confidence="CERTO",
        risk=None,
        recommended_action=None,
        requires_confirmation=False,
        technical_details_hidden=True,
    )



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


def _sentence(value: str) -> str:
    text = _clean(value).rstrip(". ")
    return f"{text}." if text else ""


def _format_operational_answer(
    *,
    article: str,
    confidence: str,
    route: str,
    constraints: list[str],
    note: str,
    action: str,
) -> str:
    parts = [f"{article} — {confidence}."]

    if route:
        parts.append(_sentence(f"Route: {route}"))

    constraint_parts = [str(item).strip() for item in constraints if str(item).strip()]
    if note:
        constraint_parts.append(note)

    if constraint_parts:
        parts.append(_sentence("Vincoli: " + "; ".join(constraint_parts)))

    if action:
        parts.append(_sentence(f"Azione: {action}"))

    if confidence != "CERTO":
        confirmation = "richiesta"
        parts.append("Rischio: verificare stato operativo.")
        parts.append(_sentence(f"Conferma: {confirmation}"))

    return " ".join(parts)


def _response_from_local_specs_metadata(article: str, metadata: dict[str, Any]) -> TLChatResponse:
    confidence = _resolve_tl_chat_confidence(
        metadata.get("confidence") or metadata.get("classification") or "DA_VERIFICARE"
    )
    route_status = str(metadata.get("route_status") or "DA_VERIFICARE").upper()
    operational_class = str(metadata.get("operational_class") or "DA_VERIFICARE").upper()
    planner_eligible = bool(metadata.get("planner_eligible"))

    drawing = _clean(metadata.get("drawing"))
    rev = _clean(metadata.get("rev") or metadata.get("revision"))
    components = metadata.get("components") if isinstance(metadata.get("components"), list) else []
    packaging = metadata.get("packaging") if isinstance(metadata.get("packaging"), dict) else {}

    route_steps = metadata.get("route_steps") if isinstance(metadata.get("route_steps"), list) else []
    route_stations = []
    for step in route_steps:
        if not isinstance(step, dict):
            continue
        station = _clean(step.get("station"))
        if station:
            route_stations.append(station)

    route = " → ".join(route_stations)
    constraints_text: list[str] = []

    constraints = metadata.get("constraints") if isinstance(metadata.get("constraints"), dict) else {}

    if constraints.get("has_henn") is True:
        constraints_text.append("HENN presente")
    elif constraints.get("has_henn") is False:
        constraints_text.append("HENN assente sul singolo / HENN assente/non indicato")

    if constraints.get("has_guaina") is True:
        constraints_text.append("GUAINA presente")

    shared_components = constraints.get("shared_components") or []
    if shared_components:
        constraints_text.append("componenti condivisi " + ", ".join(str(x) for x in shared_components))

    if constraints.get("has_pidmill") is True:
        constraints_text.append("PIDMILL presente")
    elif constraints.get("has_pidmill") is False:
        constraints_text.append("PIDMILL assente")

    primary_zaw = _clean(constraints.get("primary_zaw_station"))
    zaw_passes = constraints.get("zaw_passes")
    has_zaw2 = constraints.get("has_zaw2")

    if primary_zaw:
        if isinstance(zaw_passes, int) and zaw_passes > 1:
            constraints_text.append(f"{primary_zaw} con {zaw_passes} passaggi; ZAW1_2 non è ZAW2; non dedurre ZAW2 automaticamente")
        else:
            constraints_text.append(f"{primary_zaw} obbligatorio; non usare ZAW2 come alternativa automatica")

    should_emit_zaw2_excluded = (
        has_zaw2 is False
        and (
            bool(primary_zaw)
            or constraints.get("has_zaw") is True
            or constraints.get("has_zaw1") is True
            or constraints.get("do_not_infer_zaw2") is True
        )
    )

    if should_emit_zaw2_excluded:
        constraints_text.append("ZAW2 esclusa")

    zaw_specificity = _clean(constraints.get("zaw_station_specificity")).upper()
    if zaw_specificity == "DA_VERIFICARE":
        constraints_text.append("specificità ZAW da verificare")

    if constraints.get("cp_required"):
        cp_mode = _clean(constraints.get("cp_mode"))
        cp_pieces_per_plane = constraints.get("cp_pieces_per_plane")
        if cp_mode.upper() == "VERTICALE" and cp_pieces_per_plane == 2:
            constraints_text.append("CP finale, modalità VERTICALE_DUE_PIANI")
        elif cp_mode:
            constraints_text.append(f"CP finale obbligatorio, modalità {cp_mode}")
        else:
            constraints_text.append("CP finale obbligatorio")

    if route_status != "CERTO":
        constraints_text.append(f"route {route_status}: non trattare la sequenza come definitiva senza conferma")

    note_bits = []
    if drawing:
        drawing_text = f"disegno {drawing}"
        if rev:
            drawing_text += f" rev {rev}"
        note_bits.append(drawing_text)

    note_bits.append(f"classe {operational_class}, planner_eligible={str(planner_eligible).lower()}")

    discrepancies = metadata.get("spec_discrepancies") if isinstance(metadata.get("spec_discrepancies"), list) else []
    for item in discrepancies:
        if not isinstance(item, dict):
            continue
        correct_value = _clean(item.get("correct_value"))
        status = _clean(item.get("status"))
        if correct_value:
            if status:
                note_bits.append(f"discrepanza corretta {correct_value}, stato {status}")
            else:
                note_bits.append(f"discrepanza corretta {correct_value}")
            break

    if components:
        compact_components = ", ".join(str(item) for item in components[:8])
        note_bits.append(f"componenti noti {compact_components}")

    if packaging:
        packaging_bits = []
        if packaging.get("sacchetto"):
            packaging_bits.append(f"sacchetto {packaging.get('sacchetto')}")
        if packaging.get("imballo"):
            packaging_bits.append(f"imballo {packaging.get('imballo')}")
        if packaging.get("quantita_per_imballo"):
            packaging_bits.append(f"qta/imballo {packaging.get('quantita_per_imballo')}")
        if packaging_bits:
            note_bits.append("packaging " + ", ".join(packaging_bits))

    planner_admission_status = _clean(metadata.get("planner_admission_status")).upper()
    admission_blocked = planner_admission_status in {
        "BLOCKED",
        "NOT_ADMITTED",
        "BLOCKED_PENDING_OPERATIONAL_CLASS",
        "DA_VERIFICARE",
    }

    requires_confirmation = route_status != "CERTO" or admission_blocked

    if route_status != "CERTO":
        action = "usare il metadata locale come base articolo; confermare route prima di pianificazione piena"
        risk = "Metadata locale articolo presente; route ancora da verificare."
        recommended_action = "Usare il metadata locale come base articolo; confermare route prima di pianificazione piena."
    elif admission_blocked:
        constraints_text.append(
            "admission planner bloccata: route confermata ma classe operativa non chiusa"
        )
        action = "usare route confermata solo come riferimento; confermare admission planner prima della pianificazione"
        risk = "Route confermata, ma admission planner bloccata dal metadata."
        recommended_action = "Non pianificare automaticamente; serve conferma TL su classe operativa/admission planner."
    else:
        action = "usare route confermata"
        risk = "Metadata locale articolo presente."
        recommended_action = "Usare il metadata locale come riferimento operativo confermato."

    return TLChatResponse(
        ok=True,
        answer=_format_operational_answer(
            article=article,
            confidence=confidence,
            route=route or ("non strutturata" if route_status != "CERTO" else ""),
            constraints=constraints_text,
            note="; ".join(note_bits),
            action=action,
        ),
        confidence=confidence,
        risk=risk,
        recommended_action=recommended_action,
        requires_confirmation=requires_confirmation,
        technical_details_hidden=True,
    )


def _question_asks_if_article_needs_verification(question: str) -> bool:
    normalized = question.strip().lower()
    return (
        "verificare" in normalized
        or "da verificare" in normalized
        or "verifica" in normalized
    )


def _response_for_article_operational_verification(
    article: str,
    metadata: dict[str, Any],
) -> TLChatResponse | None:
    operational_class = str(metadata.get("operational_class") or "DA_VERIFICARE").upper()
    planner_eligible = bool(metadata.get("planner_eligible"))
    route_status = str(metadata.get("route_status") or "DA_VERIFICARE").upper()
    confidence = _resolve_tl_chat_confidence(metadata.get("confidence") or route_status)

    if operational_class == "STANDARD" and planner_eligible is True:
        return None

    if operational_class == "REFERENCE_ONLY":
        operational_label = "REFERENCE_ONLY / producibile solo se esiste richiesta cliente esplicita"
    else:
        operational_label = operational_class

    return TLChatResponse(
        ok=True,
        answer=(
            f"Il codice {article} ha route {route_status}, ma classe operativa "
            f"{operational_label} e planner_eligible={str(planner_eligible).lower()}. "
            "Non va pianificato automaticamente."
        ),
        confidence=confidence,
        risk="Certezza route e ammissibilità operativa ordinaria sono due cose diverse.",
        recommended_action=(
            "Usare solo con richiesta cliente esplicita e conferma TL; "
            "non promuovere automaticamente a priorità produttiva."
        ),
        requires_confirmation=True,
        technical_details_hidden=True,
    )


CUSTOMER_REQUEST_ONLY_STATUSES = {
    "CUSTOMER_REQUEST_ONLY",
    "FUORI_PRODUZIONE_STANDARD_CON_RICHIESTA_CLIENTE",
}


def _is_customer_request_only_status(status: str) -> bool:
    return status in CUSTOMER_REQUEST_ONLY_STATUSES


def _response_from_lifecycle(article: str, payload: dict[str, Any]) -> TLChatResponse:
    status = _clean(payload.get("status")).upper() or "SCONOSCIUTO"
    note = _clean(payload.get("note"))
    source = _clean(payload.get("source"))
    checkpoint = consultation()

    if status == "NEW_ENTRY":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta NEW_ENTRY nella memoria reparto.",
            confidence="INFERITO",
            risk="Codice nuovo: va densificato con priorità ma confermato prima dello staging.",
            recommended_action="Verifica TL e poi priorità alta di densificazione.",
            requires_confirmation=checkpoint.requires_confirmation,
        )

    if status == "FUORI_PRODUZIONE":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta FUORI_PRODUZIONE nella memoria reparto.",
            confidence="INFERITO",
            risk="Codice non prioritario per densificazione operativa; evitare promozione automatica.",
            recommended_action="Non portare in staging salvo conferma TL esplicita.",
            requires_confirmation=checkpoint.requires_confirmation,
        )

    if _is_customer_request_only_status(status):
        return TLChatResponse(
            ok=True,
            answer=(
                f"Il codice {article} è fuori produzione standard ma producibile solo "
                "su richiesta cliente esplicita."
            ),
            confidence="INFERITO",
            risk="Codice non standard: non pianificare automaticamente senza ordine o richiesta cliente.",
            recommended_action="Usare solo con richiesta cliente esplicita e conferma TL.",
            requires_confirmation=checkpoint.requires_confirmation,
        )

    if status == "ATTIVO":
        return TLChatResponse(
            ok=True,
            answer=f"Il codice {article} risulta ATTIVO nella memoria reparto.",
            confidence="INFERITO",
            risk="Stato reparto presente ma da incrociare con BOM, Codici e route prima di scritture.",
            recommended_action="Procedere con preview e conferma TL prima dello staging.",
            requires_confirmation=checkpoint.requires_confirmation,
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
            requires_confirmation=checkpoint.requires_confirmation,
        )

    return TLChatResponse(
        ok=True,
        answer=f"Il codice {article} è presente nel lifecycle registry ma ha stato non riconosciuto: {status}.",
        confidence="DA_VERIFICARE",
        risk="Stato lifecycle non interpretabile.",
        recommended_action="Correggere o confermare lo stato articolo nel registry reparto.",
        requires_confirmation=checkpoint.requires_confirmation,
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



def _load_tl_real_spec_intake() -> dict[str, Any]:
    """
    Read-only TL real spec intake loader.

    Contract:
    - reads local preview-only intake if present
    - does not create files/directories
    - does not write to SMF/database/planner
    - does not call external APIs
    - missing intake preserves existing behavior
    """
    if not TL_REAL_SPEC_INTAKE.exists():
        return {}

    try:
        data = json.loads(TL_REAL_SPEC_INTAKE.read_text(encoding="utf-8"))
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

    asks_codes = (
        "codici" in normalized
        or "lista" in normalized
        or "elenco" in normalized
    )

    if not asks_codes:
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


def _new_entry_candidates_from_intake(intake: dict[str, Any]) -> list[str]:
    items = intake.get("items")
    if not isinstance(items, list):
        return []

    codes: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        article = _clean(item.get("article")).upper()
        classification = _clean(item.get("initial_classification")).upper()
        confidence = _clean(item.get("confidence")).upper()

        if (
            article
            and classification.startswith("NEW_ENTRY_CANDIDATE")
            and confidence in {"DA_VERIFICARE", "INFERITO", "CERTO"}
        ):
            codes.append(article)

    return sorted(set(codes))


def _response_for_lifecycle_status_list(
    lifecycle: dict[str, dict[str, Any]],
    requested_status: str,
) -> TLChatResponse:
    codes: list[str] = []
    customer_request_only_codes: list[str] = []

    for code, payload in sorted(lifecycle.items()):
        if not isinstance(payload, dict):
            continue

        status = _clean(payload.get("status")).upper()
        if status == requested_status:
            codes.append(code)
        elif requested_status == "FUORI_PRODUZIONE" and _is_customer_request_only_status(status):
            customer_request_only_codes.append(code)

    intake_new_entry_candidates: list[str] = []
    if requested_status == "NEW_ENTRY":
        intake_new_entry_candidates = _new_entry_candidates_from_intake(_load_tl_real_spec_intake())

    if requested_status == "DA_VERIFICARE":
        empty_answer = "Non risultano codici DA_VERIFICARE nel lifecycle registry reparto."
        risk = "Sono presenti codici con stato vita articolo non ancora confermato."
        recommended = "Verifica TL richiesta prima di densificazione o staging."
    elif requested_status == "NEW_ENTRY":
        empty_answer = "Non risultano codici NEW_ENTRY nel lifecycle registry reparto o intake locale."
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

    if not codes and not customer_request_only_codes and not intake_new_entry_candidates:
        return TLChatResponse(
            ok=True,
            answer=empty_answer,
            confidence="CERTO",
            risk=None,
            recommended_action="Nessuna azione lifecycle urgente rilevata.",
            requires_confirmation=False,
        )

    if requested_status == "NEW_ENTRY" and intake_new_entry_candidates:
        answer_parts: list[str] = []
        if codes:
            answer_parts.append(
                "Codici NEW_ENTRY nel lifecycle registry reparto: "
                + ", ".join(codes)
                + "."
            )
        answer_parts.append(
            "Candidati new entry da intake locale: "
            + ", ".join(intake_new_entry_candidates)
            + "."
        )

        return TLChatResponse(
            ok=True,
            answer=" ".join(answer_parts),
            confidence="CERTO",
            risk="Candidati da specifiche reali locali: conferma TL obbligatoria; nessuna pianificazione automatica.",
            recommended_action="Revisionare le specifiche e promuovere solo dopo conferma TL controllata.",
            requires_confirmation=True,
        )

    if requested_status == "FUORI_PRODUZIONE":
        answer_parts: list[str] = []
        if codes:
            answer_parts.append(
                "Codici FUORI_PRODUZIONE nel lifecycle registry reparto: "
                + ", ".join(codes)
                + "."
            )
        if customer_request_only_codes:
            answer_parts.append(
                "Codici fuori produzione standard producibili solo su richiesta cliente: "
                + ", ".join(customer_request_only_codes)
                + "."
            )

        return TLChatResponse(
            ok=True,
            answer=" ".join(answer_parts),
            confidence="CERTO",
            risk="Questi codici non devono essere promossi automaticamente in priorità produttiva.",
            recommended_action="Usare solo con richiesta cliente esplicita e conferma TL.",
            requires_confirmation=True,
        )

    return TLChatResponse(
        ok=True,
        answer=f"Codici {requested_status} nel lifecycle registry reparto: " + ", ".join(codes) + ".",
        confidence="CERTO",
        risk=risk,
        recommended_action=recommended,
        requires_confirmation=True,
    )



def _load_spec_intake_preview(article: str) -> dict[str, Any] | None:
    """
    Read-only spec intake preview loader.

    Contract:
    - reads local PREVIEW_ONLY spec intake metadata if present
    - does not write files
    - does not touch SMF/database/planner
    - does not promote preview data to active profile
    """
    safe_article = _normalize_article(article)
    if not safe_article:
        return None

    metadata_path = SPEC_INTAKE_PREVIEW_ROOT / f"{safe_article}_metadata_preview.json"
    if not metadata_path.exists():
        return None

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    if _clean(data.get("status")).upper() != "PREVIEW_ONLY":
        return None

    article_payload = data.get("article") if isinstance(data.get("article"), dict) else {}
    if _normalize_article(article_payload.get("articolo")) != safe_article:
        return None

    return data


def _response_from_spec_intake_preview(article: str, payload: dict[str, Any]) -> TLChatResponse:
    article_payload = payload.get("article") if isinstance(payload.get("article"), dict) else {}

    raw_confidence = _resolve_tl_chat_confidence(payload.get("confidence") or "DA_VERIFICARE")
    raw_status = _clean(payload.get("status")).upper() or "PREVIEW_ONLY"
    raw_planner_eligible = bool(payload.get("planner_eligible"))
    raw_requires_tl_confirmation = bool(payload.get("requires_tl_confirmation", True))

    resolved_context = resolve_tl_chat_context(
        article=article,
        candidates=[
            TLChatContextCandidate(
                source_name="spec_intake_preview",
                source_status=raw_status,
                confidence=raw_confidence,
                planner_eligible=raw_planner_eligible,
                requires_tl_confirmation=raw_requires_tl_confirmation,
                payload=payload,
            )
        ],
    )

    confidence = resolved_context.confidence
    status = resolved_context.source_status
    planner_eligible = resolved_context.planner_eligible
    requires_tl_confirmation = resolved_context.requires_tl_confirmation

    codice = _clean(article_payload.get("codice"))
    disegno = _clean(article_payload.get("disegno"))
    rev = _clean(article_payload.get("rev") or article_payload.get("revision"))

    details: list[str] = [
        f"Articolo {article}: dati disponibili da fonte preview spec_intake_preview.",
        f"Stato: {status}.",
        f"Confidence: {confidence}.",
        "Non è nel profilo attivo.",
        "conferma TL richiesta.",
        "Limite: contesto usato solo come supporto informativo; nessuna promozione a CERTO.",
        f"planner_eligible={str(planner_eligible).lower()}.",
        f"requires_tl_confirmation={str(requires_tl_confirmation).lower()}.",
        f"can_promote={str(resolved_context.can_promote).lower()}.",
    ]

    if codice:
        details.append(f"Codice cliente: {codice}.")

    if disegno:
        drawing_text = f"Disegno: {disegno}"
        if rev:
            drawing_text += f" rev {rev}"
        details.append(drawing_text + ".")

    return TLChatResponse(
        ok=True,
        answer=" ".join(details),
        confidence=confidence,
        risk="Spec intake preview-only: non usare per pianificazione o profilo attivo senza conferma TL.",
        recommended_action="Confermare con TL prima di promuovere il dato in un profilo operativo.",
        requires_confirmation=True,
        technical_details_hidden=True,
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

    confidence = _resolve_tl_chat_confidence(profile.get("confidence") or "DA_VERIFICARE")
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



def _pattern_hint_for_stations(stations: list[str]) -> str:
    pattern_titles: list[str] = []
    for station in stations:
        for pattern in find_patterns_by_station(station):
            if pattern.title not in pattern_titles:
                pattern_titles.append(pattern.title)

    if not pattern_titles:
        return ""

    return " PATTERN TL: ZAW1/ZAW2 non intercambiabili."


def _response_from_article_summary(article: str) -> TLChatResponse | None:
    summary = build_article_tl_summary(article)

    if not summary.get("ok"):
        return None

    signals = summary.get("signals") if isinstance(summary.get("signals"), dict) else {}
    criticalities = summary.get("criticalities") if isinstance(summary.get("criticalities"), list) else []
    planner_eligible = summary.get("planner_eligible")
    compact_non_planner = planner_eligible is False

    confidence = _resolve_tl_chat_confidence(summary.get("confidence") or "DA_VERIFICARE")
    primary_zaw = _clean(signals.get("primary_zaw_station"))
    zaw_passes = signals.get("zaw_passes")

    summary_route = summary.get("route") if isinstance(summary.get("route"), list) else []
    route_aliases = {
        "COLLAUDO_PRESSIONE": "CP",
        "COLLAUDO_PRESSSIONE": "CP",
        "COLLAUDO_VERTICALE": "CP",
        "COLLAUDO_PRESSIONE_VERTICALE": "CP",
    }
    route_parts: list[str] = []
    for item in summary_route:
        value = str(item).strip()
        if not value:
            continue
        route_parts.append(route_aliases.get(value, value))

    route_from_summary = bool(route_parts)
    constraints: list[str] = []

    if signals.get("has_henn"):
        if not route_from_summary and confidence != "CERTO":
            route_parts.append("HENN")
        constraints.append("HENN prima di ZAW")
    elif signals.get("has_henn") is False:
        constraints.append("HENN assente/non indicato")

    if primary_zaw:
        if not route_from_summary and confidence != "CERTO":
            route_parts.append(primary_zaw)
        if isinstance(zaw_passes, int) and zaw_passes > 1:
            constraints.append(f"{primary_zaw} con {zaw_passes} passaggi")
            constraints.append("ZAW1_2 non è ZAW2")
        else:
            constraints.append(f"{primary_zaw} obbligatorio")
        if not signals.get("has_zaw2"):
            constraints.append("ZAW2 non valida")

    cp_mode = _clean(signals.get("cp_machine_mode"))

    if signals.get("has_pidmill"):
        if not route_from_summary and confidence != "CERTO":
            route_parts.append("PIDMILL")
        hide_pidmill_constraint = compact_non_planner and cp_mode == "VERTICALE_DUE_PIANI" and len(route_parts) <= 4
        if not hide_pidmill_constraint:
            constraints.append("PIDMILL presente")

    hide_cp_machine_mode = compact_non_planner and bool(signals.get("has_pidmill")) and len(route_parts) <= 4
    if signals.get("cp_required"):
        if not route_from_summary and confidence != "CERTO":
            route_parts.append("CP")
        if cp_mode and not hide_cp_machine_mode:
            constraints.append(f"CP finale obbligatorio, modalità {cp_mode}")
        else:
            constraints.append("CP finale obbligatorio")

    shared = signals.get("shared_components") or []
    if shared:
        constraints.append("componenti condivisi " + ", ".join(str(x) for x in shared))

    for item in criticalities:
        value = str(item)
        if "Discrepanza" in value or "discrepanza" in value:
            if "HENN_ZAW1_PIDMILL" in value:
                constraints.append("BOM discordante")
            elif "HENN_ZAW1" in value:
                constraints.append("BOM discordante: HENN_ZAW1")
            elif "ZAW1_DOPPIO_PASSAGGIO_GUAINA_DOPPIA" in value:
                constraints.append("BOM discordante: ZAW1_DOPPIO_PASSAGGIO_GUAINA_DOPPIA")
            elif "ZAW1_DOPPIO_PASSAGGIO_PIDMILL" in value:
                constraints.append("BOM discordante: ZAW1_DOPPIO_PASSAGGIO_PIDMILL")
            else:
                constraints.append("BOM discordante")
            break

    constraints = list(dict.fromkeys(constraints))

    if summary.get("planner_eligible") is False:
        action = "usa solo con ordine attivo"
    else:
        action = "usa route confermata"

    pattern_hint = _pattern_hint_for_stations(route_parts)

    return TLChatResponse(
        ok=True,
        answer=_format_operational_answer(
            article=article,
            confidence=confidence,
            route=" → ".join(route_parts),
            constraints=constraints,
            note="",
            action=action,
        ),
        confidence=confidence,
        risk="Profilo operativo articolo disponibile. Dettagli tecnici nascosti salvo richiesta.",
        recommended_action=(str(summary.get("tl_action") or "Seguire risposta operativa sintetica.") + pattern_hint).strip(),
        requires_confirmation=False,
        technical_details_hidden=True,
    )




def _question_asks_why(question: str) -> bool:
    normalized = question.strip().lower()

    return (
        "perché" in normalized
        or "perche" in normalized
        or "motivo" in normalized
        or "come mai" in normalized
        or normalized.startswith("why ")
    )


def _response_for_article_why_question(
    article: str,
    question: str,
    metadata: dict[str, Any],
) -> TLChatResponse | None:
    normalized = question.strip().lower()

    confidence = _resolve_tl_chat_confidence(
        metadata.get("confidence") or metadata.get("classification") or "DA_VERIFICARE"
    )
    route_status = str(metadata.get("route_status") or "DA_VERIFICARE").upper()
    operational_class = str(metadata.get("operational_class") or "DA_VERIFICARE").upper()
    planner_eligible = bool(metadata.get("planner_eligible"))
    planner_admission_status = _clean(metadata.get("planner_admission_status")).upper()

    constraints = metadata.get("constraints") if isinstance(metadata.get("constraints"), dict) else {}
    primary_zaw = _clean(constraints.get("primary_zaw_station")).upper()
    has_zaw2 = constraints.get("has_zaw2")
    zaw_passes = constraints.get("zaw_passes")
    zaw_specificity = _clean(constraints.get("zaw_station_specificity")).upper()

    asks_zaw2 = "zaw2" in normalized or "zaw 2" in normalized
    asks_zaw1 = "zaw1" in normalized or "zaw 1" in normalized
    asks_planner = (
        "planner_eligible" in normalized
        or "planner eligible" in normalized
        or "planner" in normalized
        or "pianific" in normalized
    )

    if asks_zaw2 or asks_zaw1:
        if primary_zaw or has_zaw2 is False:
            reasons: list[str] = []

            if primary_zaw:
                reasons.append(f"il metadata articolo indica primary_zaw_station={primary_zaw}")

            if isinstance(zaw_passes, int) and zaw_passes > 1:
                reasons.append(
                    f"sono indicati {zaw_passes} passaggi su {primary_zaw or 'ZAW1'}; doppio passaggio non significa ZAW2"
                )

            if has_zaw2 is False:
                reasons.append("il metadata articolo indica has_zaw2=false")

            if zaw_specificity == "DA_VERIFICARE":
                reasons.append("la specificità ZAW è marcata DA_VERIFICARE, quindi non va promossa a certezza automatica")

            if not reasons:
                reasons.append("il profilo attivo non contiene evidenza sufficiente per usare ZAW2")

            return TLChatResponse(
                ok=True,
                answer=(
                    f"{article} — ZAW2 non va usata come alternativa automatica perché "
                    + "; ".join(reasons)
                    + "."
                ),
                confidence=confidence,
                risk=(
                    "ZAW1 e ZAW2 non sono intercambiabili: usare ZAW2 senza evidenza esplicita "
                    "può alterare la route reale."
                ),
                recommended_action=(
                    f"Usare {primary_zaw or 'la ZAW indicata dal profilo'}; chiedere conferma TL solo se "
                    "serve cambiare postazione o se emerge una fonte reale discordante."
                ),
                requires_confirmation=confidence != "CERTO" or zaw_specificity == "DA_VERIFICARE",
                technical_details_hidden=True,
            )

    if asks_planner:
        if planner_eligible is False:
            reason_bits = [
                f"classe operativa={operational_class}",
                f"route_status={route_status}",
            ]

            if planner_admission_status:
                reason_bits.append(f"planner_admission_status={planner_admission_status}")

            return TLChatResponse(
                ok=True,
                answer=(
                    f"{article} — planner_eligible=false perché "
                    + "; ".join(reason_bits)
                    + ". Route confermata e ammissione planner sono due cose diverse: "
                    "un articolo può essere consultabile o avere route nota senza generare priorità automatica."
                ),
                confidence=confidence,
                risk=(
                    "Non promuovere automaticamente un articolo in pianificazione solo perché la route è leggibile."
                ),
                recommended_action=(
                    "Usare il profilo come riferimento operativo; pianificare solo con ordine attivo, richiesta esplicita "
                    "o conferma TL coerente con le regole planner."
                ),
                requires_confirmation=True,
                technical_details_hidden=True,
            )

        return TLChatResponse(
            ok=True,
            answer=(
                f"{article} — planner_eligible=true perché il profilo attivo è ammesso al planner "
                f"con classe operativa={operational_class} e route_status={route_status}. "
                "Questo non significa produzione automatica: serve comunque ordine attivo o richiesta operativa."
            ),
            confidence=confidence,
            risk="Planner eligibility non equivale ad avvio automatico della produzione.",
            recommended_action="Usare solo dentro il normale flusso ordine/turno e con override TL tracciabile se necessario.",
            requires_confirmation=False,
            technical_details_hidden=True,
        )

    return None

def _question_asks_pidmill_dima(question: str) -> bool:
    normalized = question.strip().lower()

    asks_dima = (
        "dima" in normalized
        or "dime" in normalized
        or "tool" in normalized
        or "sagoma" in normalized
    )

    return asks_dima and "pidmill" in normalized


def _extract_pidmill_dime(metadata: dict[str, Any]) -> list[str]:
    values: list[str] = []

    linked_bom = metadata.get("linked_bom")
    if isinstance(linked_bom, list):
        for item in linked_bom:
            if not isinstance(item, dict):
                continue
            code = _clean(item.get("component"))
            description = _clean(item.get("description")).lower()
            if code.upper().startswith("BAT") and (
                "pidmill" in description
                or "sagoma" in description
                or "attrezzatura" in description
            ):
                values.append(code)

    route_steps = metadata.get("route_steps")
    if isinstance(route_steps, list):
        for step in route_steps:
            if not isinstance(step, dict):
                continue

            station = _clean(step.get("station")).upper()
            note = _clean(step.get("note"))

            if station != "PIDMILL":
                continue

            import re
            match = re.search(r"\bsagoma\s+(\d{1,3})\b", note, flags=re.IGNORECASE)
            if match:
                values.append(f"BAT{int(match.group(1)):03d}")

    components = metadata.get("components")
    if isinstance(components, list):
        for item in components:
            code = ""
            if isinstance(item, str):
                code = _clean(item)
            elif isinstance(item, dict):
                code = _clean(item.get("code") or item.get("component") or item.get("article"))

            if code.upper().startswith("BAT"):
                values.append(code)

    return list(dict.fromkeys(values))


def _response_for_pidmill_dima(article: str, metadata: dict[str, Any]) -> TLChatResponse:
    dime = _extract_pidmill_dime(metadata)

    if not dime:
        return TLChatResponse(
            ok=True,
            answer=(
                f"{article}\n\n"
                "DIMA PIDMILL\n\n"
                "NON DISPONIBILE NEL PROFILO ATTIVO."
            ),
            confidence="DA_VERIFICARE",
            risk=None,
            recommended_action="Verificare profilo articolo o specifica autorizzata prima di considerare disponibile la dima PIDMILL.",
            requires_confirmation=True,
            technical_details_hidden=True,
        )

    label = "DIMA PIDMILL" if len(dime) == 1 else "DIME PIDMILL"

    return TLChatResponse(
        ok=True,
        answer=(
            f"{article}\n\n"
            f"{label}:\n"
            + ", ".join(dime)
        ),
        confidence="CERTO",
        risk=None,
        recommended_action=None,
        requires_confirmation=False,
        technical_details_hidden=True,
    )



def _question_asks_components(question: str) -> bool:
    normalized = question.strip().lower()

    return (
        "component" in normalized
        or "manicotto" in normalized
        or "manicotti" in normalized
        or "distinta" in normalized
        or "bom" in normalized
        or ("lista" in normalized and "codic" in normalized)
    )



KNOWN_MANICOTTO_TUBE_CODES = frozenset({"12201"})


def _question_asks_manicotto(question: str) -> bool:
    return "manicotto" in str(question or "").strip().lower()


def _response_for_manicotto_component(article: str, values: list[str]) -> TLChatResponse | None:
    matches = [value for value in values if value in KNOWN_MANICOTTO_TUBE_CODES]

    if not matches:
        return None

    return TLChatResponse(
        ok=True,
        answer=f"{article} — manicotto: {matches[0]}.",
        confidence="CERTO",
        risk="Fonte locale metadata/components; interpretazione TL: manicotto = tubo in gomma.",
        recommended_action="Usare il codice manicotto indicato; verificare fisicamente solo in caso di discrepanza con specifica reale.",
        requires_confirmation=False,
        technical_details_hidden=True,
    )


def _response_for_components(article: str, metadata: dict[str, Any], question: str = "") -> TLChatResponse:
    components = metadata.get("components")

    if not isinstance(components, list) or not components:
        return TLChatResponse(
            ok=True,
            answer=f"{article} — componenti non disponibili nel metadata locale.",
            confidence="DA_VERIFICARE",
            risk=None,
            recommended_action="Densificare o verificare metadata/components.",
            requires_confirmation=False,
            technical_details_hidden=True,
        )

    values: list[str] = []

    excluded_prefixes = ("CRT", "CRM", "BAT")
    excluded_exact = {"SUPPORTO", "A1"}

    for item in components:
        code = None

        if isinstance(item, dict):
            code = _clean(
                item.get("code")
                or item.get("component")
                or item.get("article")
            )

        elif isinstance(item, str):
            code = _clean(item)

        if not code:
            continue

        normalized = code.upper()

        if normalized in excluded_exact:
            continue

        if normalized.startswith(excluded_prefixes):
            continue

        values.append(code)

    values = list(dict.fromkeys(values))

    if not values:
        return TLChatResponse(
            ok=True,
            answer=f"{article} — componenti presenti ma non leggibili.",
            confidence="DA_VERIFICARE",
            risk=None,
            recommended_action="Verificare struttura metadata/components.",
            requires_confirmation=False,
            technical_details_hidden=True,
        )

    if _question_asks_manicotto(question):
        manicotto_response = _response_for_manicotto_component(article, values)
        if manicotto_response is not None:
            return manicotto_response

    confidence = _resolve_tl_chat_confidence(
        metadata.get("confidence") or metadata.get("classification") or "DA_VERIFICARE"
    )
    requires_confirmation = confidence != "CERTO"

    return TLChatResponse(
        ok=True,
        answer=f"{article} — componenti: " + ", ".join(values) + ".",
        confidence=confidence,
        risk=None,
        recommended_action=None,
        requires_confirmation=requires_confirmation,
        technical_details_hidden=True,
    )



def _question_asks_zaw_interchangeability(question: str) -> bool:
    import re

    normalized = question.strip().lower()
    compact = re.sub(r"[^a-z0-9]", "", normalized)

    asks_relation = any(
        token in normalized
        for token in (
            "intercambi",
            "alternativa",
            "equivalent",
            "spostare",
        )
    )

    return "zaw1" in compact and "zaw2" in compact and asks_relation



def _question_asks_turn_fallback_without_article(question: str) -> bool:
    normalized = question.strip().lower()

    turn_tokens = (
        "turno",
        "adesso",
        "ora",
        "controllare",
        "controllo",
        "conviene",
        "priorità",
        "priorita",
        "cosa faccio",
        "cosa controllo",
    )

    return any(token in normalized for token in turn_tokens)


def _response_for_turn_fallback_without_article() -> TLChatResponse:
    return TLChatResponse(
        ok=True,
        answer=(
            "Domanda turno senza articolo o contesto operativo sufficiente. "
            "Non genero priorità automatica senza codice articolo, ordine, lotto, "
            "stato board o evento aperto confermato. "
            "NON DECIDO: contesto operativo insufficiente. "
            "MOTIVO: mancano dati minimi per una priorità affidabile. "
            "DATO MANCANTE: codice articolo, ordine, lotto, stato board o evento aperto. "
            "DOMANDA TL: quale codice articolo, ordine, lotto o evento devo valutare?"
        ),
        confidence="DA_VERIFICARE",
        risk=(
            "Domanda operativa generale: senza articolo o stato board non generare "
            "priorità automatica."
        ),
        recommended_action=(
            "Fornire codice articolo, ordine, lotto, stato board o evento aperto "
            "per una risposta operativa specifica."
        ),
        requires_confirmation=True,
        technical_details_hidden=True,
    )


def _is_generic_missing_context_response(response: TLChatResponse) -> bool:
    answer = str(response.answer or "")
    return (
        "richiede almeno un articolo nel context" in answer
        or "NON DISPONIBILE NEL PROFILO ATTIVO" in answer
    )


def _question_can_use_governed_evidence(question: str) -> bool:
    normalized = str(question or "").strip().lower()
    governed_terms = (
        "confidence",
        "certo",
        "inferito",
        "da_verificare",
        "zaw",
        "zaw1",
        "zaw2",
        "atlas",
        "planner",
        "retrieval",
        "fonte",
        "fonti",
    )
    return any(term in normalized for term in governed_terms)


def _response_from_governed_evidence_pack(
    *,
    evidence_pack: dict[str, Any],
) -> TLChatResponse | None:
    evidence = evidence_pack.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return None

    first = evidence[0]
    if not isinstance(first, dict):
        return None

    source_id = _clean(first.get("source_id"))
    source_type = _clean(first.get("source_type"))
    confidence = _clean(first.get("confidence")).upper() or "DA_VERIFICARE"
    text = _clean(first.get("text"))

    if not source_id or not text:
        return None

    confidence_notes = {
        "CERTO": "dato confermato da fonte reale, TL o struttura dominio autorevole.",
        "INFERITO": "dato dedotto da contesto governato; utile come ipotesi, non come certezza operativa.",
        "DA_VERIFICARE": "dato non sufficiente o non confermato; serve controllo TL o fonte autorizzata.",
    }

    requested_levels = [
        level
        for level in ("CERTO", "INFERITO", "DA_VERIFICARE")
        if level.lower() in text.lower() or level.lower() in source_id.lower()
    ] or [confidence]

    level_text = " ".join(
        f"{level}: {confidence_notes[level]}"
        for level in ("CERTO", "INFERITO", "DA_VERIFICARE")
        if level in requested_levels or len(requested_levels) > 1
    )

    return TLChatResponse(
        ok=True,
        answer=(
            f"Fonte governata read-only: {source_id}. "
            f"Tipo fonte: {source_type or 'governed_source'}. "
            f"Confidence fonte: {confidence}. "
            f"{level_text or text} "
            "Limite: contesto usato solo come supporto informativo; nessuna promozione a CERTO, "
            "nessuna scrittura e nessuna decisione automatica."
        ),
        confidence="DA_VERIFICARE",
        risk="Risposta basata su retrieval governato preview-only.",
        recommended_action="Usare come orientamento; conferma TL richiesta prima di decisioni operative.",
        requires_confirmation=True,
        technical_details_hidden=True,
    )



def _response_from_context_reader_bridge(article: str) -> TLChatResponse | None:
    adapter = ContextSourceReaderAdapter(
        index_path=ROOT / "memory" / "context_source_index.json",
        repo_root=ROOT,
        max_chars=500,
    )
    candidate = build_context_reader_candidate(
        source_id="context_access_binding",
        article=article,
        adapter=adapter,
        include_excerpt=True,
        max_chars=500,
    )

    resolved_context = resolve_tl_chat_context(
        article=article,
        candidates=[candidate],
    )

    if resolved_context.selected_source != "context_source_reader_adapter":
        return None

    if resolved_context.source_status != "SOURCE_FOUND":
        return TLChatResponse(
            ok=True,
            answer=(
                f"Articolo {article}: fonte governata non disponibile. "
                f"Stato fonte: {resolved_context.source_status}. "
                "Non invento contenuto e non genero decisioni operative."
            ),
            confidence="DA_VERIFICARE",
            risk="Fonte governata non disponibile o non autorizzata.",
            recommended_action="Verificare source_id o fonte ammessa prima di usare il contesto.",
            requires_confirmation=True,
            technical_details_hidden=True,
        )

    payload = resolved_context.payload
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    source_id = _clean(payload.get("source_id"))
    reader_status = _clean(payload.get("reader_status")) or "DA_VERIFICARE"
    excerpt = _clean(payload.get("excerpt"))

    if not source_id:
        return None

    missing_data = "nessun dato certo promosso; conferma TL richiesta"
    if not excerpt:
        missing_data = "excerpt non disponibile; conferma TL richiesta"

    source_summary = "fonte governata read-only disponibile"
    if excerpt:
        source_summary = "fonte governata read-only disponibile; contenuto tecnico sintetizzato e non promosso a dato operativo"

    return TLChatResponse(
        ok=True,
        answer=(
            f"Answer: Articolo {article}: {source_summary}.\n"
            f"Source: {source_id}; reader_status={reader_status}; relative_path={_clean(metadata.get('relative_path'))}.\n"
            f"Confidence: {resolved_context.confidence}; "
            f"requires_tl_confirmation={str(resolved_context.requires_tl_confirmation).lower()}; "
            f"can_promote={str(resolved_context.can_promote).lower()}; "
            f"planner_eligible={str(resolved_context.planner_eligible).lower()}.\n"
            f"Missing data: {missing_data}.\n"
            "Next safe action: usare come orientamento; non applicare decisioni operative senza conferma TL. "
            "Limite: contesto usato solo come supporto informativo; nessuna promozione a CERTO, "
            "nessuna scrittura e nessuna decisione automatica."
        ),
        confidence="DA_VERIFICARE",
        risk="Risposta basata su ContextSourceReaderAdapter read-only; conferma TL richiesta.",
        recommended_action="Usare come orientamento; non applicare decisioni operative senza conferma TL.",
        requires_confirmation=True,
        technical_details_hidden=True,
    )


def _question_asks_12514_confirmation_rendering(question: str) -> bool:
    normalized = str(question or "").strip().lower()

    asks_confirmation = (
        "conferma" in normalized
        or "confirmation" in normalized
        or "risposta tl" in normalized
        or "render" in normalized
        or "rendering" in normalized
    )
    asks_12514 = "12514" in normalized

    return asks_12514 and asks_confirmation


def _response_from_12514_confirmation_rendering(
    article: str,
    payload: dict[str, Any],
) -> TLChatResponse | None:
    if article != "12514":
        return None

    article_payload = (
        payload.get("article") if isinstance(payload.get("article"), dict) else {}
    )

    candidate_data = {
        "codice": _clean(article_payload.get("codice")),
        "disegno": _clean(article_payload.get("disegno")),
        "rev": _clean(article_payload.get("rev") or article_payload.get("revision")),
    }
    candidate_data = {key: value for key, value in candidate_data.items() if value}

    rendering = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article="12514",
            question_id="Q1",
            tl_answer_state="UNKNOWN",
            resulting_status="DA_VERIFICARE",
            candidate_data=candidate_data,
            missing_data=["conferma TL strutturata non ancora acquisita"],
            next_safe_action=(
                "presentare il rendering candidato al TL; non persistere e non "
                "promuovere a CERTO"
            ),
        )
    )

    return TLChatResponse(
        ok=True,
        answer=rendering.rendered_text,
        confidence=rendering.confidence,
        risk=(
            "Rendering candidato 12514 non persistente: non è fonte di verità, "
            "non autorizza pianificazione e non produce effetti operativi."
        ),
        recommended_action=rendering.next_safe_action,
        requires_confirmation=True,
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

    if not article and _question_asks_turn_fallback_without_article(question):
        return _response_for_turn_fallback_without_article()

    if article:
        local_specs_metadata = _load_local_specs_metadata(article)
        if local_specs_metadata:

            if _question_asks_why(question):
                why_response = _response_for_article_why_question(
                    article,
                    question,
                    local_specs_metadata,
                )
                if why_response:
                    return why_response

            if _question_asks_pidmill_dima(question):
                return _response_for_pidmill_dima(
                    article,
                    local_specs_metadata,
                )

            if _question_asks_components(question):
                return _response_for_components(
                    article,
                    local_specs_metadata,
                    question,
                )
            if _question_asks_if_article_needs_verification(question):
                operational_verification = _response_for_article_operational_verification(
                    article,
                    local_specs_metadata,
                )
                if operational_verification:
                    return operational_verification

            return _response_from_local_specs_metadata(article, local_specs_metadata)

        article_summary_response = _response_from_article_summary(article)
        if article_summary_response:
            return article_summary_response

        lifecycle_payload = lifecycle.get(article)

        if lifecycle_payload:
            return _response_from_lifecycle(article, lifecycle_payload)

        spec_intake_preview = _load_spec_intake_preview(article)
        if spec_intake_preview:
            if _question_asks_12514_confirmation_rendering(question):
                confirmation_rendering_response = (
                    _response_from_12514_confirmation_rendering(
                        article,
                        spec_intake_preview,
                    )
                )
                if confirmation_rendering_response:
                    return confirmation_rendering_response

            return _response_from_spec_intake_preview(article, spec_intake_preview)

        preview_response = _response_from_preview_profile(article)
        if preview_response:
            return preview_response

        if _question_can_use_governed_evidence(question):
            context_reader_response = _response_from_context_reader_bridge(article)
            if context_reader_response:
                return context_reader_response

        return TLChatResponse(
            ok=True,
            answer=(
                f"{article}\n\n"
                "NON DISPONIBILE NEL PROFILO ATTIVO."
            ),
            confidence="DA_VERIFICARE",
            risk=None,
            recommended_action="Verificare articolo in fonte autorizzata o fornire profilo/specifica; non trattare come attivo senza conferma TL.",
            requires_confirmation=True,
        )

    family = _extract_family_from_question(question)
    if family:
        registry = _load_family_registry()
        payload = registry.get(family)

        if payload:
            return _response_from_family_registry(
                family,
                payload,
            )

    if not article and _question_asks_zaw_interchangeability(question):
        return TLChatResponse(
            ok=True,
            answer=(
                "ZAW1 e ZAW2 non sono intercambiabili. "
                "Vincoli: ZAW1_2 indica secondo passaggio su ZAW1, non ZAW2; "
                "non spostare route o carico da ZAW1 a ZAW2 senza profilo articolo e conferma TL. "
                "Azione: usare la postazione indicata dalla route/profilo articolo."
            ),
            confidence="CERTO",
            risk=(
                "Errore di interchangeability ZAW può alterare sequenza "
                "e priorità operative."
            ),
            recommended_action="Non usare ZAW2 come alternativa automatica a ZAW1.",
            requires_confirmation=False,
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
    response = _build_contract_response(payload)
    article = _normalize_article(payload.context.article) or _extract_article_from_question(payload.question)
    evidence_pack = build_governed_retrieval_pack(
        payload.question,
        article=article or None,
        limit=5,
    )

    governed_response = None
    if (
        _is_generic_missing_context_response(response)
        and _question_can_use_governed_evidence(payload.question)
    ):
        governed_response = _response_from_governed_evidence_pack(
            evidence_pack=evidence_pack,
        )

    if governed_response is not None:
        response = governed_response

    response.evidence_pack = evidence_pack
    return response
