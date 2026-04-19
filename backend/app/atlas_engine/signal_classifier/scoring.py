from __future__ import annotations

from .contracts import SignalsDetected
from .patterns import (
    CTA_LANGUAGE, CTA_MATCH_WEIGHT,
    CREDENTIAL_REQUESTS, CREDENTIAL_REQUEST_WEIGHT,
    FOMO_MATCH_WEIGHT, FOMO_PHRASES,
    MARKETING_KEYWORDS, MARKETING_MATCH_WEIGHT,
    OPERATIONAL_KEYWORDS, OPERATIONAL_MATCH_WEIGHT,
    PHISHING_INDICATOR_WEIGHT, PHISHING_INDICATORS,
    SENDER_DOMAIN_MISMATCH_WEIGHT,
    SUPPLIER_KEYWORDS, SUPPLIER_MATCH_WEIGHT,
    CUSTOMER_KEYWORDS, CUSTOMER_MATCH_WEIGHT,
    SUSPICIOUS_URL_RE, SUSPICIOUS_URL_WEIGHT,
    SUSPICIOUS_SENDER_RE,
    TRIAL_LANGUAGE, TRIAL_MATCH_WEIGHT,
    UNSUBSCRIBE_MARKERS, UNSUBSCRIBE_MATCH_WEIGHT,
    URGENCY_LANGUAGE,
)


def detect_signals(
    text: str,
    subject: str | None,
    sender: str | None,
) -> SignalsDetected:
    combined = _combine(text, subject)
    return SignalsDetected(
        contains_urgency_language=_any(combined, URGENCY_LANGUAGE),
        contains_trial_language=_any(combined, TRIAL_LANGUAGE),
        contains_unsubscribe_footer=_any(combined, UNSUBSCRIBE_MARKERS),
        contains_operational_keywords=_any(combined, OPERATIONAL_KEYWORDS),
        contains_supplier_keywords=_any(combined, SUPPLIER_KEYWORDS),
        contains_customer_keywords=_any(combined, CUSTOMER_KEYWORDS),
        contains_fomo_language=_any(combined, FOMO_PHRASES),
        contains_phishing_indicators=_any(combined, PHISHING_INDICATORS),
        contains_credential_request=_any(combined, CREDENTIAL_REQUESTS),
        contains_cta_language=_any(combined, CTA_LANGUAGE),
        has_suspicious_url=bool(SUSPICIOUS_URL_RE.search(combined)),
        has_sender_domain_mismatch=_suspicious_sender(sender),
    )


def compute_category_scores(
    text: str,
    subject: str | None,
    signals: SignalsDetected,
) -> dict[str, float]:
    combined = _combine(text, subject)

    phishing_score = _clamp(
        _count(combined, PHISHING_INDICATORS) * PHISHING_INDICATOR_WEIGHT
        + _count(combined, CREDENTIAL_REQUESTS) * CREDENTIAL_REQUEST_WEIGHT
        + (SUSPICIOUS_URL_WEIGHT if signals.has_suspicious_url else 0.0)
        + (SENDER_DOMAIN_MISMATCH_WEIGHT if signals.has_sender_domain_mismatch else 0.0)
    )
    operational_score = _clamp(_count(combined, OPERATIONAL_KEYWORDS) * OPERATIONAL_MATCH_WEIGHT)
    supplier_score = _clamp(_count(combined, SUPPLIER_KEYWORDS) * SUPPLIER_MATCH_WEIGHT)
    customer_score = _clamp(_count(combined, CUSTOMER_KEYWORDS) * CUSTOMER_MATCH_WEIGHT)
    marketing_score = _clamp(
        _count(combined, MARKETING_KEYWORDS) * MARKETING_MATCH_WEIGHT
        + _count(combined, UNSUBSCRIBE_MARKERS) * UNSUBSCRIBE_MATCH_WEIGHT
    )
    fomo_score = _clamp(
        _count(combined, FOMO_PHRASES) * FOMO_MATCH_WEIGHT
        + _count(combined, TRIAL_LANGUAGE) * TRIAL_MATCH_WEIGHT
        + _count(combined, CTA_LANGUAGE) * CTA_MATCH_WEIGHT
    )
    grey_marketing_score = _clamp(marketing_score + fomo_score)

    return {
        "phishing": phishing_score,
        "operational": operational_score,
        "supplier": supplier_score,
        "customer": customer_score,
        "marketing": marketing_score,
        "fomo": fomo_score,
        "grey_marketing": grey_marketing_score,
    }


def _combine(text: str, subject: str | None) -> str:
    parts = [subject, text] if subject else [text]
    return " ".join(parts).lower()


def _any(text: str, patterns: frozenset[str]) -> bool:
    return any(p in text for p in patterns)


def _count(text: str, patterns: frozenset[str]) -> int:
    return sum(1 for p in patterns if p in text)


def _suspicious_sender(sender: str | None) -> bool:
    if not sender:
        return False
    return bool(SUSPICIOUS_SENDER_RE.search(sender))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
