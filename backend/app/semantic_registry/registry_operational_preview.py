from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

OperationalVerdict = Literal[
    "OK_CONSULTABILE",
    "DA_VERIFICARE_TL",
    "CONTRADDIZIONE_BLOCCANTE",
    "REFERENCE_ONLY",
    "UNKNOWN",
]


@dataclass(frozen=True)
class OperationalPilotReport:
    code: str
    sources: tuple[str, ...]
    contradictions: tuple[str, ...]
    risk: str
    explainability: str
    operational_verdict: OperationalVerdict
    read_only: bool = True
    preview_only: bool = True
    no_runtime_mutation: bool = True
    no_planner_behavior_change: bool = True
    no_smf_db_write: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_registry_operational_pilot_report(
    *,
    code: str,
    sources: tuple[str, ...] = (),
    contradictions: tuple[str, ...] = (),
    risk: str = "UNKNOWN",
    explainability: str = "",
    operational_class: str = "",
    confidence: str = "",
) -> OperationalPilotReport:
    normalized_code = str(code or "").strip()
    normalized_risk = str(risk or "UNKNOWN").strip().upper()
    normalized_class = str(operational_class or "").strip().upper()
    normalized_confidence = str(confidence or "").strip().upper()

    if not normalized_code:
        verdict: OperationalVerdict = "UNKNOWN"
    elif normalized_class in {
        "REFERENCE_ONLY",
        "CUSTOMER_REQUEST_ONLY",
        "FUORI_PRODUZIONE_STANDARD_CON_RICHIESTA_CLIENTE",
    }:
        verdict = "REFERENCE_ONLY"
    elif contradictions and normalized_risk in {"HIGH", "CRITICAL", "BLOCCANTE"}:
        verdict = "CONTRADDIZIONE_BLOCCANTE"
    elif contradictions or normalized_confidence in {"DA_VERIFICARE", "INFERITO"}:
        verdict = "DA_VERIFICARE_TL"
    elif normalized_risk in {"LOW", "BASSO"} and normalized_confidence in {"CERTO", "STANDARD"}:
        verdict = "OK_CONSULTABILE"
    else:
        verdict = "UNKNOWN"

    return OperationalPilotReport(
        code=normalized_code or "UNKNOWN",
        sources=tuple(sources),
        contradictions=tuple(contradictions),
        risk=normalized_risk,
        explainability=explainability or "preview-only operational registry pilot report",
        operational_verdict=verdict,
    )
