import json
from unittest.mock import patch

from app.services.llm_service import _validate_ai_response, run_local_llm


def test_zaw_interchangeability_returns_deterministic_response():
    response = run_local_llm(
        "Linea con 2 operatori. Verifica se ZAW-1 e ZAW-2 sono intercambiabili."
    )

    assert "ZAW-1 e ZAW-2 NON sono intercambiabili" in response
    assert "Aggiungere un terzo operatore" not in response
    assert "componente ZAW" not in response


def test_empty_prompt_returns_no_text_message():
    assert run_local_llm("   ") == "Nessun testo ricevuto."


def test_validate_ai_response_blocks_zaw_as_component():
    response = _validate_ai_response(
        "Il componente ZAW-1 deve essere sostituito."
    )

    assert response.startswith("ERRORE_LOGICO_PROMETEO")
    assert "postazioni, non componenti" in response


def test_ai_fallback_calls_ollama_for_non_deterministic_prompt(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({
                "response": "1. Strategia operativa reale\n- Verifica flusso postazioni."
            }).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=FakeResponse()) as mocked:
        response = run_local_llm("Dammi una strategia breve per una linea generica.")

    assert mocked.called
    assert "Verifica flusso postazioni" in response


def test_ai_fallback_sanitizes_thinking_output(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({
                "response": (
                    "Thinking...\\n"
                    "Thinking Process:\\n"
                    "1. Analyze request.\\n"
                    "...done thinking.\\n\\n"
                    "1. Strategia operativa reale\\n"
                    "- Non pianificare automaticamente REFERENCE_ONLY."
                )
            }).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=FakeResponse()):
        response = run_local_llm("Spiega REFERENCE_ONLY in PROMETEO.")

    assert "Thinking" not in response
    assert "Thinking Process" not in response
    assert "Non pianificare automaticamente REFERENCE_ONLY" in response


def test_reference_only_returns_deterministic_non_planning_response():
    response = run_local_llm(
        "PROMETEO TL Chat. Articolo REFERENCE_ONLY: codice articolo noto, "
        "route non strutturata, planner_eligible=false. Cosa deve fare il Team Leader?"
    )

    assert "Non produrre automaticamente" in response
    assert "ordine cliente esplicito o conferma TL" in response
    assert "produzione fuori programma" in response
    assert "Fermare la produzione" not in response
    assert "Thinking" not in response
