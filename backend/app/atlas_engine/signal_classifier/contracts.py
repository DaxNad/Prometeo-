from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClassificationLabel(str, Enum):
    operational = "operational"
    supplier = "supplier"
    customer = "customer"
    marketing = "marketing"
    grey_marketing = "grey_marketing"
    phishing = "phishing"
    unknown = "unknown"


class ActionHint(str, Enum):
    handle = "handle"
    review = "review"
    ignore = "ignore"
    block = "block"


class SignalsDetected(BaseModel):
    contains_urgency_language: bool = False
    contains_trial_language: bool = False
    contains_unsubscribe_footer: bool = False
    contains_operational_keywords: bool = False
    contains_supplier_keywords: bool = False
    contains_customer_keywords: bool = False
    contains_fomo_language: bool = False
    contains_phishing_indicators: bool = False
    contains_credential_request: bool = False
    contains_cta_language: bool = False
    has_suspicious_url: bool = False
    has_sender_domain_mismatch: bool = False  # V1: basic heuristic; extend in V2 with reputation lookup


class SignalClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1)
    sender: Optional[str] = Field(default=None)
    subject: Optional[str] = Field(default=None)
    source_type: str = Field(default="email")


class SignalClassification(BaseModel):
    """
    Output of the signal classifier pipeline.

    Future integration:
        This model is intended to be embedded as an optional field inside SignalEvent,
        produced by the event engine without introducing runtime coupling.

        Embedding pattern (event engine side):
            classification: Optional[SignalClassification] = None

        The event engine imports only this contracts module — never classifier.py,
        scoring.py, or patterns.py. Classification is applied externally and
        injected into the event; the event engine never calls classify_signal().

        One-way dependency:
            event_engine → signal_classifier.contracts   (safe, no circular risk)
            event_engine -/-> signal_classifier.classifier  (never imported)
    """

    model_config = ConfigDict(extra="ignore")

    classification: ClassificationLabel
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    action_hint: ActionHint
    reasons: List[str]
    signals_detected: SignalsDetected
