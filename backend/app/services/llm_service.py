import json
import os
import urllib.request

from dataclasses import dataclass

from app.ai_adapters.output_sanitizer import sanitize_ai_output
from app.atlas_engine.tl_memory.memory_retriever import (
    format_rules_for_prompt,
    retrieve_relevant_rules,
)

MODEL = os.getenv("LOCAL_LLM_MODEL", "gemma4:e2b")
FALLBACK_MODEL = os.getenv("LOCAL_LLM_FALLBACK_MODEL", "mistral:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")

SYSTEM_PROMPT = """Sei il Team Leader esperto reparto assemblaggio automotive (PROMETEO).

Regole operative:
- ZAW-1 e ZAW-2 NON sono intercambiabili.
- ZAW-1 e ZAW-2 sono postazioni/funzioni produttive, non componenti fisici.
- I colli di bottiglia non si risolvono automaticamente aumentando operatori.
- Considera sempre componenti condivisi come O-ring, connettori, guaine e plastiche.
- Priorità: flusso continuo, saturazione postazioni, evitare blocchi.
- CP è fase finale vincolante.
- Non citare MES/ERP come fonte primaria: in PROMETEO usare metadata locali, SMF, specifica di finitura e conferma TL.
- Se il contesto è insufficiente, non inventare route: rispondere DA_VERIFICARE e chiedere verifica su metadata/SMF/TL.
- Non usare LaTeX, formule matematiche o notazione accademica nelle risposte TL.
- Non usare linguaggio fisico generico come modello predittivo, controllo termico, guasto componente o stabilità del sistema se non presente nei dati PROMETEO.
- Descrivere i rischi come errori operativi concreti: route errata, postazione sbagliata, sequenza sbagliata, collo di bottiglia, CP non chiuso.

Formato obbligatorio:

1. Strategia operativa reale
- azioni concrete su postazioni
- eventuale sequenza

2. Rischi reali
- cosa blocca davvero la produzione

3. Azione TL immediata
- cosa fare ORA nel turno

Non dare consigli generici.
Non proporre "aggiungi operatori" se non giustificato.
Quando una regola TL rilevante è presente, trattala come vincolo certo.
Non trasformare regole certe in ipotesi.
Se è indicato che ZAW-1 e ZAW-2 non sono intercambiabili, non scrivere mai "se sono intercambiabili".
Non chiamare mai ZAW-1 o ZAW-2 "componenti".
Rispondi come TL esperto."""


def _validate_ai_response(response: str) -> str:
    invalid_patterns = [
        "componente zaw",
        "componenti zaw",
        "zaw-1 come componente",
        "zaw-2 come componente",
    ]

    if any(pat in response.lower() for pat in invalid_patterns):
        return (
            "ERRORE_LOGICO_PROMETEO: ZAW-1 e ZAW-2 sono postazioni, non componenti. "
            "Risposta AI non valida. Ripetere analisi considerando ZAW come stazioni produttive."
        )

    return response


@dataclass(frozen=True)
class LocalLLMResult:
    response: str
    model: str
    fallback_used: bool = False


def get_local_llm_model() -> str:
    return MODEL


def get_local_llm_fallback_model() -> str:
    return FALLBACK_MODEL


def _call_ollama(model: str, prompt_with_memory: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt_with_memory,
        "stream": False,
        "options": {
            "temperature": 0,
            "top_p": 0.2,
        },
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as res:
        data = json.loads(res.read().decode("utf-8"))

    return data.get("response", "").strip() or "Nessuna risposta dal modello."


def run_local_llm_with_metadata(prompt: str) -> LocalLLMResult:
    if not prompt.strip():
        return LocalLLMResult(response="Nessun testo ricevuto.", model=MODEL)

    q = prompt.lower()
    if "zaw-1" in q and "zaw-2" in q and "intercambi" in q:
        return LocalLLMResult(response=(
            "1. Strategia operativa reale\n"
            "- ZAW-1 e ZAW-2 NON sono intercambiabili.\n"
            "- Trattale come postazioni/funzioni produttive distinte.\n"
            "- Prima di spostare lavoro o operatori, identifica quale ZAW è realmente bloccata e quale articolo/componente sta generando il collo di bottiglia.\n\n"
            "2. Rischi reali\n"
            "- Confondere ZAW-1 e ZAW-2 porta a sequenze errate, perdita di tempo e falsa saturazione della linea.\n"
            "- Aggiungere operatori senza diagnosi non risolve il vincolo reale.\n\n"
            "3. Azione TL immediata\n"
            "- Separare subito il problema: ZAW-1 o ZAW-2.\n"
            "- Verificare articolo, componente condiviso e operazione in corso.\n"
            "- Solo dopo decidere se ribilanciare operatori o sequenza."
        ), model=MODEL)

    if "reference_only" in q and (
        "planner_eligible=false" in q
        or "planner_eligible = false" in q
        or "non pianificabile automaticamente" in q
    ):
        return LocalLLMResult(response=(
            "1. Strategia operativa reale\n"
            "- Trattare l'articolo come codice noto di riferimento, non come lotto da pianificare.\n"
            "- Usare disegno, storico o nota ricambio solo per riconoscimento e verifica.\n\n"
            "2. Rischi reali\n"
            "- Inserirlo nel planner standard può generare priorità false o produzione fuori programma.\n"
            "- Route non strutturata significa: non dedurre sequenze operative automatiche.\n\n"
            "3. Azione TL immediata\n"
            "- Non produrre automaticamente.\n"
            "- Procedere solo con ordine cliente esplicito o conferma TL."
        ), model=MODEL)

    relevant_rules = retrieve_relevant_rules(prompt)
    prompt_with_memory = (
        SYSTEM_PROMPT
        + "\n\nRegole TL rilevanti:\n"
        + format_rules_for_prompt(relevant_rules)
        + "\n\nScenario:\n"
        + prompt
    )

    try:
        raw_response = _call_ollama(MODEL, prompt_with_memory)
        actual_model = MODEL
        fallback_used = False
    except Exception as primary_error:
        try:
            raw_response = _call_ollama(FALLBACK_MODEL, prompt_with_memory)
            actual_model = FALLBACK_MODEL
            fallback_used = True
        except Exception as fallback_error:
            return LocalLLMResult(
                response=(
                    f"OLLAMA_ERROR: primary={MODEL}: {str(primary_error)}; "
                    f"fallback={FALLBACK_MODEL}: {str(fallback_error)}"
                ),
                model=MODEL,
                fallback_used=False,
            )

    response = sanitize_ai_output(raw_response)
    return LocalLLMResult(
        response=_validate_ai_response(response),
        model=actual_model,
        fallback_used=fallback_used,
    )


def run_local_llm(prompt: str) -> str:
    return run_local_llm_with_metadata(prompt).response
