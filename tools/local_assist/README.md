# LOCAL_ASSIST_BRIDGE_001

Bridge locale proposal-only per ridurre copia-incolla operativo in PROMETEO.

Scopo:
- classificare output terminale/check/log
- proporre il prossimo comando sicuro
- mantenere conferma umana obbligatoria

Modalità:
- read-only
- proposal-only
- fail-closed
- deterministic fallback prima di Ollama per casi noti
- Ollama solo come supporto locale per casi non codificati

Vietato:
- modificare file
- eseguire comandi
- commit
- push
- merge PR
- leggere .env
- leggere segreti
- leggere dati reali/spec private
- bypassare guard, privacy, Data Leak Guard, PR o check

Uso:
tools/local_assist/local_assist.py --task "classifica questo output PR checks" --input-file /tmp/prometeo_output.txt

Output contract:
verdict: PASS | FAIL | DA_VERIFICARE
risk: LOW | MEDIUM | HIGH
summary: string
suggested_next_command: string | null
requires_human_confirmation: true

Known limitations:
- LLM output non è fonte affidabile.
- Il fallback deterministico ha priorità sui casi noti.
- Ogni comando suggerito richiede conferma umana.
- Il bridge non esegue azioni: propone soltanto.
