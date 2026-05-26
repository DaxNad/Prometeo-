# PROMETEO — LOCAL LLM EDITOR CONTRACT

## STATUS

ACTIVE — SAFE LOCAL EDITING CONTRACT

## PURPOSE

Ridurre il collo di bottiglia copia/incolla usando un LLM locale tramite Ollama come editor assistito, senza concedergli autonomia operativa.

## PRIMARY OBJECTIVE

PROMETEO deve poter usare un LLM locale per proporre patch, refactor piccoli, test e trasformazioni controllate, mantenendo sempre controllo umano, diff visibile e guardrail attivi.

## ROLE OF LOCAL LLM

Il LLM locale può:

- proporre modifiche a file ammessi
- generare patch testuali
- creare test
- trasformare pattern TL in markdown o JSON
- ridurre operazioni manuali ripetitive

Il LLM locale NON può:

- fare commit
- fare push
- aprire PR
- modificare main
- modificare dati reali sensibili
- toccare .env, SMF reale, specs_finitura private, dump, log produttivi
- decidere roadmap o priorità operative

## SAFE FLOW

Obiettivo umano
→ prompt controllato
→ Ollama propone modifica
→ diff locale
→ test e guard
→ approvazione umana
→ commit manuale
→ PR
→ checks verdi
→ merge

## HARD RULES

1. Nessuna scrittura su main.
2. Nessun auto-commit.
3. Nessun auto-push.
4. Nessuna modifica dati reali senza preview.
5. Nessuna modifica fuori scope.
6. Ogni output deve produrre diff controllabile.
7. Ogni patch deve rispettare PROMETEO PATTERN LEARNING IMPERATIVE.

## FIRST TOOL TARGET

Script futuro:

tools/local_llm/prometeo_local_editor.py

Modalità iniziale:

DRY-RUN ONLY

Output atteso:

- file candidati
- proposta patch
- rischi
- test suggeriti
- nessuna scrittura automatica

## PROJECT LAW

Il Local LLM Editor serve solo ad accelerare esecuzione controllata.

Non sostituisce TL, ChatGPT orchestration, guardrail, test, PR o conferma umana.
