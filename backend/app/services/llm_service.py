import json
import urllib.request

from app.atlas_engine.tl_memory.memory_retriever import (
    format_rules_for_prompt,
    retrieve_relevant_rules,
)

MODEL = "mistral"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM_PROMPT = """Sei il Team Leader esperto reparto assemblaggio automotive (PROMETEO).

Regole operative:
- ZAW-1 e ZAW-2 NON sono intercambiabili.
- ZAW-1 e ZAW-2 sono postazioni/funzioni produttive, non componenti fisici.
- I colli di bottiglia non si risolvono automaticamente aumentando operatori.
- Considera sempre componenti condivisi come O-ring, connettori, guaine e plastiche.
- Priorità: flusso continuo, saturazione postazioni, evitare blocchi.
- CP è fase finale vincolante.

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


def run_local_llm(prompt: str) -> str:
    if not prompt.strip():
        return "Nessun testo ricevuto."

    q = prompt.lower()
    if "zaw-1" in q and "zaw-2" in q and "intercambi" in q:
        return (
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
        )

    relevant_rules = retrieve_relevant_rules(prompt)
    prompt_with_memory = (
        SYSTEM_PROMPT
        + "\n\nRegole TL rilevanti:\n"
        + format_rules_for_prompt(relevant_rules)
        + "\n\nScenario:\n"
        + prompt
    )

    payload = {
        "model": MODEL,
        "prompt": prompt_with_memory,
        "stream": False,
    }

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as res:
            data = json.loads(res.read().decode("utf-8"))

        response = data.get("response", "").strip() or "Nessuna risposta dal modello."
        return _validate_ai_response(response)

    except Exception as e:
        return f"OLLAMA_ERROR: {str(e)}"
