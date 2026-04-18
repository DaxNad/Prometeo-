from __future__ import annotations

from .contracts import (
    ActionHint, ClassificationLabel,
    SignalClassification, SignalClassifyRequest, SignalsDetected,
)
from .patterns import (
    CUSTOMER_THRESHOLD, GREY_MARKETING_THRESHOLD, MARKETING_THRESHOLD,
    MINIMUM_WORDS_FOR_CLASSIFICATION, OPERATIONAL_THRESHOLD,
    PHISHING_THRESHOLD, RISK_SCORE_RANGE, SUPPLIER_THRESHOLD,
)
from .scoring import compute_category_scores, detect_signals

_ACTION_HINT: dict[ClassificationLabel, ActionHint] = {
    ClassificationLabel.phishing: ActionHint.block,
    ClassificationLabel.grey_marketing: ActionHint.review,
    ClassificationLabel.marketing: ActionHint.ignore,
    ClassificationLabel.operational: ActionHint.handle,
    ClassificationLabel.supplier: ActionHint.handle,
    ClassificationLabel.customer: ActionHint.handle,
    ClassificationLabel.unknown: ActionHint.review,
}


def classify_signal(request: SignalClassifyRequest) -> SignalClassification:
    text, subject, sender = request.text, request.subject, request.sender

    if len(text.split()) < MINIMUM_WORDS_FOR_CLASSIFICATION:
        return SignalClassification(
            classification=ClassificationLabel.unknown,
            risk_score=0.20,
            confidence=0.20,
            action_hint=ActionHint.review,
            reasons=["text too short for reliable classification"],
            signals_detected=SignalsDetected(),
        )

    signals = detect_signals(text, subject, sender)
    scores = compute_category_scores(text, subject, signals)
    label = _determine_label(scores, signals)
    risk_score = _compute_risk_score(label, scores, signals)
    confidence = _compute_confidence(scores, signals, len(text.split()), label)
    reasons = _build_reasons(label, scores, signals)

    return SignalClassification(
        classification=label,
        risk_score=round(_clamp(risk_score), 2),
        confidence=round(_clamp(confidence), 2),
        action_hint=_ACTION_HINT[label],
        reasons=reasons,
        signals_detected=signals,
    )


def _determine_label(scores: dict[str, float], signals: SignalsDetected) -> ClassificationLabel:
    if scores["phishing"] >= PHISHING_THRESHOLD:
        return ClassificationLabel.phishing

    has_promo = signals.contains_fomo_language or signals.contains_trial_language

    if signals.contains_operational_keywords and scores["operational"] >= OPERATIONAL_THRESHOLD:
        if not has_promo or scores["operational"] > scores["grey_marketing"]:
            return ClassificationLabel.operational

    if signals.contains_supplier_keywords and scores["supplier"] >= SUPPLIER_THRESHOLD and not has_promo:
        return ClassificationLabel.supplier

    if signals.contains_customer_keywords and scores["customer"] >= CUSTOMER_THRESHOLD and not has_promo:
        return ClassificationLabel.customer

    if scores["grey_marketing"] >= GREY_MARKETING_THRESHOLD and has_promo:
        return ClassificationLabel.grey_marketing

    if scores["marketing"] >= MARKETING_THRESHOLD:
        return ClassificationLabel.marketing

    return ClassificationLabel.unknown


def _compute_risk_score(
    label: ClassificationLabel,
    scores: dict[str, float],
    signals: SignalsDetected,
) -> float:
    low, high = RISK_SCORE_RANGE[label.value]
    if label == ClassificationLabel.phishing:
        return _clamp(low + scores["phishing"] * (high - low))
    if label == ClassificationLabel.grey_marketing:
        return _clamp(low + (high - low) * 0.5 + scores["fomo"] * 0.5 * (high - low))
    return _clamp(low + (high - low) * 0.5)


def _compute_confidence(
    scores: dict[str, float],
    signals: SignalsDetected,
    word_count: int,
    label: ClassificationLabel,
) -> float:
    active = sum([
        signals.contains_urgency_language, signals.contains_trial_language,
        signals.contains_unsubscribe_footer, signals.contains_operational_keywords,
        signals.contains_supplier_keywords, signals.contains_customer_keywords,
        signals.contains_fomo_language, signals.contains_phishing_indicators,
        signals.contains_credential_request, signals.contains_cta_language,
        signals.has_suspicious_url, signals.has_sender_domain_mismatch,
    ])
    base = {4: 0.85, 3: 0.75, 2: 0.65, 1: 0.50}.get(min(active, 4), 0.30 if active == 0 else 0.85)
    if word_count < 20:
        base -= 0.15
    if signals.contains_operational_keywords and signals.contains_phishing_indicators:
        base -= 0.10
    if label == ClassificationLabel.unknown:
        base = min(base, 0.40)
    return _clamp(base)


def _build_reasons(
    label: ClassificationLabel,
    scores: dict[str, float],
    signals: SignalsDetected,
) -> list[str]:
    reasons: list[str] = []

    if label == ClassificationLabel.phishing:
        if signals.contains_phishing_indicators:
            reasons.append("phishing indicators: account suspension or identity verification language")
        if signals.contains_credential_request:
            reasons.append("explicit credential request detected")
        if signals.has_suspicious_url:
            reasons.append("suspicious URL detected (non-HTTPS or URL shortener)")
        if signals.contains_urgency_language:
            reasons.append("urgency language combined with phishing signals")

    elif label == ClassificationLabel.grey_marketing:
        if signals.contains_fomo_language:
            reasons.append("FOMO language: limited time / last chance / don't miss")
        if signals.contains_trial_language:
            reasons.append("trial or free access language with no connection to production workflow")
        if signals.contains_cta_language:
            reasons.append("aggressive call-to-action language")
        if not signals.contains_operational_keywords:
            reasons.append("no operational keyword linking this to production workflow")

    elif label == ClassificationLabel.marketing:
        if signals.contains_unsubscribe_footer:
            reasons.append("promotional email: unsubscribe footer detected")
        reasons.append("marketing keywords present without FOMO or phishing signals")

    elif label == ClassificationLabel.operational:
        reasons.append("operational keywords directly related to production workflow")
        if signals.contains_urgency_language:
            reasons.append("urgency language consistent with an operational context")

    elif label == ClassificationLabel.supplier:
        reasons.append("supplier keywords detected: delivery, purchase order, invoice, or ETA")

    elif label == ClassificationLabel.customer:
        reasons.append("customer keywords detected: order, delivery date, or client request")

    else:
        reasons.append("insufficient signals for confident classification")
        if not any([signals.contains_operational_keywords,
                    signals.contains_supplier_keywords,
                    signals.contains_customer_keywords]):
            reasons.append("no production-domain keywords detected")

    return reasons[:4]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
