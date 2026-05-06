"""
Contratto minimo per AI locali/adapters PROMETEO.

Scopo:
- impedire che un modello locale instabile venga considerato valido;
- proteggere i vincoli TL;
- evitare che problemi di GGUF/chat-template/EOS/tokenizzazione entrino nel core dominio.

Questo test NON chiama Ollama, MiMo o servizi esterni.
È un guard rail deterministico.
"""

BANNED_INSTABILITY_PATTERNS = [
    "????",
    "<|endoftext|><|endoftext|>",
    "assistant assistant assistant",
    "user user user",
]


REQUIRED_TL_CONSTRAINTS = [
    "ZAW-1",
    "ZAW-2",
    "non sono intercambiabili",
    "CP",
    "finale",
    "validare TL",
]


def _validate_prometeo_ai_response(text: str) -> bool:
    assert isinstance(text, str)
    assert text.strip(), "Risposta AI vuota"

    lowered = text.lower()

    for pattern in BANNED_INSTABILITY_PATTERNS:
        assert pattern.lower() not in lowered, f"Pattern instabile rilevato: {pattern}"

    for token in REQUIRED_TL_CONSTRAINTS:
        assert token.lower() in lowered, f"Vincolo TL mancante: {token}"

    assert len(text) < 2500, "Risposta troppo lunga per output operativo TL"

    return True


def test_prometeo_local_ai_contract_accepts_stable_operational_response():
    response = """
    Strategia consigliata:
    ZAW-1 e ZAW-2 non sono intercambiabili. Non spostare il carico da una all'altra
    senza conferma di processo. Il CP resta fase finale di chiusura lotto.
    Suggerimento AI locale — da validare TL.
    """

    assert _validate_prometeo_ai_response(response) is True


def test_prometeo_local_ai_contract_rejects_missing_zaw_constraint():
    response = """
    Strategia consigliata:
    Spostare liberamente il lavoro tra le due postazioni ZAW.
    Il CP resta fase finale. Suggerimento AI locale — da validare TL.
    """

    try:
        _validate_prometeo_ai_response(response)
    except AssertionError as exc:
        assert "ZAW-1" in str(exc) or "non sono intercambiabili" in str(exc)
    else:
        raise AssertionError("Il contratto AI ha accettato una risposta senza vincolo ZAW")


def test_prometeo_local_ai_contract_rejects_unstable_token_output():
    response = """
    Strategia consigliata:
    ZAW-1 e ZAW-2 non sono intercambiabili. CP finale. validare TL.
    assistant assistant assistant
    """

    try:
        _validate_prometeo_ai_response(response)
    except AssertionError as exc:
        assert "Pattern instabile" in str(exc)
    else:
        raise AssertionError("Il contratto AI ha accettato output instabile")
