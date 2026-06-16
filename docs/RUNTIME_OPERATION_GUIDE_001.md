# RUNTIME OPERATION GUIDE 001

Stato: `RUNTIME_OPERATION_GUIDE_001`

Guida minima per riavviare PROMETEO dopo spegnimento, aggiornamento Mac o riavvio ambiente locale.

## Scopo

Rendere PROMETEO riavviabile senza ricostruire il flusso operativo.

Questa guida non introduce nuova architettura. Si limita a descrivere l'avvio locale già verificato in `APP_RUNTIME_CLOSURE_001`.

## Prerequisiti

- repository locale presente
- backend `.env` locale presente ma non versionato
- PostgreSQL locale disponibile
- dipendenze backend installate
- dipendenze frontend installate
- branch `main` aggiornato

## Controllo iniziale

`cd <PROMETEO_REPO> && git status --short && git branch --show-current && git pull --ff-only origin main`

Esito atteso:

- branch `main`
- working tree pulito
- repository aggiornato

## Avvio backend

Aprire un terminale dedicato al backend.

`cd <PROMETEO_REPO>/backend && load backend environment variables && export DATABASE_URL=<LOCAL_POSTGRES_URL> && python3 -m uvicorn app.main:app --reload`

Il processo deve restare attivo.

## Verifica backend

Da un secondo terminale:

`curl -sS http://127.0.0.1:8000/ping`

`curl -sS http://127.0.0.1:8000/health`

`curl -sS http://127.0.0.1:8000/db/ping`

`curl -sS http://127.0.0.1:8000/postgres/ping`

Esito atteso:

- `/ping`: OK
- `/health`: OK
- PostgreSQL raggiungibile

### Nota Swagger / OpenAPI

Swagger o OpenAPI raggiungibile non basta per dichiarare il backend sano.

La pagina /docs dimostra solo che:

- il processo FastAPI risponde;
- lo schema OpenAPI e pubblicato;
- i router risultano almeno esposti a livello documentale.

Non dimostra da sola che:

- PostgreSQL sia raggiungibile;
- il database sia inizializzato correttamente;
- SMF o servizi interni siano disponibili;
- AI locale sia raggiungibile;
- agent runtime sia sano;
- gli endpoint operativi restituiscano dati validi.

Checklist minima backend sano:

1. /ping risponde.
2. /health risponde e non segnala errori critici.
3. /db/ping risponde quando previsto.
4. /postgres/ping risponde quando il runtime usa PostgreSQL.
5. /production/board-state restituisce JSON valido quando richiesto dal flusso TL.
6. /agent-runtime/status risponde se agent runtime e abilitato.
7. /ai/local/health risponde solo se il test riguarda AI locale.

Regola operativa:

/docs aperto equivale a OpenAPI esposto, non a backend pienamente verificato.

Per dichiarare PROMETEO operativo usare sempre health endpoint, endpoint dominio e verifiche runtime coerenti con lo scenario.

## Avvio frontend

Aprire un terminale dedicato al frontend.

`cd <PROMETEO_REPO>/frontend && load backend environment variables && npm run dev`

Il processo deve restare attivo.

URL locali:

- `http://localhost:5173/`
- `http://localhost:5173/tl-board`
- `http://localhost:5173/tl-chat`

## Verifica TL Chat

Aprire:

- `http://localhost:5173/tl-chat`

Domanda minima:

- `12066?`

Esito atteso:

- risposta presente
- confidence visibile
- conferma TL visibile
- rischio visibile se presente
- azione consigliata visibile se presente

## Test minimi

Frontend:

`cd <PROMETEO_REPO>/frontend && npm run test && npm run build`

Backend minimo:

`cd <PROMETEO_REPO> && python3 -m pytest backend/tests/test_tl_chat_contract.py backend/tests/test_operational_class.py backend/tests/test_goal_closure_policy_001.py -q`

Guard:

`cd <PROMETEO_REPO> && python3 scripts/data_leak_guard.py && python3 scripts/privacy_guard_specs.py`

## Troubleshooting rapido

### TL Chat mostra `unauthorized`

Probabile causa:

- backend o frontend avviati senza environment locale corretto

Azione:

- fermare backend e frontend
- ricaricare environment locale
- riavviare backend
- riavviare frontend

### `/tl-chat` non apre la pagina React

Verificare che il proxy Vite inoltri solo `/tl/chat`, non `/tl` generico.

### `/tl/chat` restituisce 404

Verificare che il frontend locale usi API base relativa e non endpoint remoto.

### Data Leak Guard fallisce

Rimuovere o anonimizzare path locali personali, riferimenti diretti a `.env`, URL sensibili o comandi contenenti percorsi locali reali.

## Stato finale

`RUNTIME_OPERATION_GUIDE_001` è valida se backend, frontend, TL Chat, test minimi e guard risultano verdi.
