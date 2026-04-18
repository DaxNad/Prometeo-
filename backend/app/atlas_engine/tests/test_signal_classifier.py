from app.atlas_engine.signal_classifier import classify_signal
from app.atlas_engine.signal_classifier.contracts import (
    ActionHint, ClassificationLabel, SignalClassifyRequest,
)


def test_operational_message_classified_correctly():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Ordine O-4521 in lavorazione su ZAW-1. "
            "Fase di assemblaggio completata. "
            "Componenti disponibili in magazzino. "
            "Priorità operativa: ALTA. Piano di turno aggiornato."
        ),
        subject="Aggiornamento produzione ZAW-1",
    ))
    assert result.classification == ClassificationLabel.operational
    assert result.action_hint == ActionHint.handle
    assert result.signals_detected.contains_operational_keywords is True
    assert result.signals_detected.contains_phishing_indicators is False
    assert result.confidence >= 0.50
    assert len(result.reasons) >= 1


def test_generic_marketing_classified_correctly():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Newsletter mensile. Nuovi prodotti in catalogo. "
            "Scopri le nostre ultime offerte. "
            "Sconto del 20% su tutti i prodotti. "
            "Cancella iscrizione in fondo alla mail."
        ),
        subject="La nostra newsletter di aprile",
    ))
    assert result.classification == ClassificationLabel.marketing
    assert result.action_hint == ActionHint.ignore
    assert result.signals_detected.contains_unsubscribe_footer is True
    assert result.risk_score < 0.30
    assert len(result.reasons) >= 1


def test_aggressive_marketing_classified_as_grey_marketing():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Prova gratuita AI illimitata per 30 giorni senza carta di credito. "
            "Solo per oggi. Non perdere questa offerta limitata. "
            "Inizia ora! Nessun impegno, cancella quando vuoi."
        ),
        subject="ULTIMO GIORNO — La tua chance finale",
    ))
    assert result.classification == ClassificationLabel.grey_marketing
    assert result.action_hint == ActionHint.review
    assert result.signals_detected.contains_fomo_language is True
    assert result.signals_detected.contains_trial_language is True
    assert result.signals_detected.contains_operational_keywords is False
    assert 0.30 <= result.risk_score <= 0.70
    combined = " ".join(result.reasons).lower()
    assert any(w in combined for w in ["fomo", "trial", "time", "action", "limited"])


def test_phishing_classified_correctly():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Il tuo account è stato sospeso a causa di attività sospetta rilevata. "
            "Verifica il tuo account e inserisci le tue credenziali per evitare la sospensione. "
            "Accedi ora su http://bit.ly/verify-account-now"
        ),
        subject="URGENTE: verifica il tuo account",
    ))
    assert result.classification == ClassificationLabel.phishing
    assert result.action_hint == ActionHint.block
    assert result.signals_detected.contains_phishing_indicators is True
    assert result.signals_detected.contains_credential_request is True
    assert result.signals_detected.has_suspicious_url is True
    assert result.risk_score >= 0.70
    assert len(result.reasons) >= 2


def test_insufficient_input_classified_as_unknown():
    result = classify_signal(SignalClassifyRequest(text="Ciao"))
    assert result.classification == ClassificationLabel.unknown
    assert result.action_hint == ActionHint.review
    assert result.confidence <= 0.30
    assert len(result.reasons) >= 1


def test_short_text_no_domain_signal_not_operational_or_phishing():
    result = classify_signal(SignalClassifyRequest(
        text="Per favore rispondimi appena puoi grazie mille",
    ))
    assert result.classification not in {
        ClassificationLabel.operational,
        ClassificationLabel.phishing,
        ClassificationLabel.supplier,
    }


def test_phishing_reasons_name_specific_signals():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Your account has been suspended due to suspicious activity. "
            "Please enter your password immediately to restore access. "
            "Click here: http://bit.ly/restore-now"
        ),
    ))
    assert result.classification == ClassificationLabel.phishing
    combined = " ".join(result.reasons).lower()
    assert any(w in combined for w in ["phishing", "credential", "url", "suspicious", "account"])


def test_grey_marketing_reasons_name_fomo_or_trial():
    result = classify_signal(SignalClassifyRequest(
        text="Free trial for 14 days without credit card. Last chance — limited time offer. Act now!",
    ))
    assert result.classification == ClassificationLabel.grey_marketing
    combined = " ".join(result.reasons).lower()
    assert any(w in combined for w in ["fomo", "trial", "time", "action", "limited"])


def test_no_crash_on_empty_subject_and_sender():
    result = classify_signal(SignalClassifyRequest(
        text="Conferma ordine cliente numero 12345 entro domani mattina urgente",
        sender=None, subject=None,
    ))
    assert result.classification is not None
    assert 0.0 <= result.risk_score <= 1.0
    assert 0.0 <= result.confidence <= 1.0


def test_no_crash_on_very_long_text():
    result = classify_signal(SignalClassifyRequest(
        text="Ordine articolo fase produzione. " * 200,
    ))
    assert result.classification == ClassificationLabel.operational
    assert 0.0 <= result.risk_score <= 1.0


def test_no_crash_on_special_characters():
    result = classify_signal(SignalClassifyRequest(
        text="<html>!!!@@@###$$$%%%^^^&&&***((()))___+++===~~~```",
        subject="[SPECIAL]",
    ))
    assert result.classification is not None


def test_output_always_has_all_required_fields():
    for text in [
        "Ciao",
        "Free trial! Act now! Urgent!",
        "Ordine ZAW-1 assemblaggio componente",
        "Il tuo account è sospeso inserisci le credenziali http://bit.ly/x",
    ]:
        result = classify_signal(SignalClassifyRequest(text=text))
        assert result.classification in ClassificationLabel.__members__.values()
        assert result.action_hint in ActionHint.__members__.values()
        assert isinstance(result.reasons, list)
        assert isinstance(result.risk_score, float)
        assert isinstance(result.confidence, float)
        assert result.signals_detected is not None


def test_supplier_message_classified_correctly():
    result = classify_signal(SignalClassifyRequest(
        text=(
            "Conferma ordine di acquisto n. 8821. "
            "Consegna prevista per il 22/04/2026. "
            "Fornitore: Acme Components Srl. "
            "Contattare per aggiornamenti sul lead time."
        ),
        subject="Conferma OdA 8821 — Acme Components",
    ))
    assert result.classification == ClassificationLabel.supplier
    assert result.action_hint == ActionHint.handle
    assert result.signals_detected.contains_supplier_keywords is True
    assert result.risk_score <= 0.15
