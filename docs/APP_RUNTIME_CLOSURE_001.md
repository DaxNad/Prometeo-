# APP RUNTIME CLOSURE 001

Stato: `APP_RUNTIME_CLOSURE_001_VERIFICATO`

Questo documento registra la prima chiusura runtime reale della PWA/gestionale PROMETEO nel perimetro `PROMETEO_GOAL_CLOSURE`.

## Scopo

Verificare che l'applicazione esistente sia avviabile e usabile localmente senza introdurre nuova architettura.

## Runtime verificato

- Backend FastAPI locale avviato con `uvicorn app.main:app --reload`.
- PostgreSQL locale raggiungibile.
- Frontend Vite locale avviato con `npm run dev`.
- Dashboard/TL Board visibile da browser.
- TL Chat visibile da browser.
- TL Chat collegata correttamente al backend locale.

- Dashboard principale collegata correttamente al backend locale.
- TL Board collegata correttamente al backend locale.

## Endpoint verificati

- `/ping`: OK
- `/health`: OK
- `/db/ping`: OK
- `/postgres/ping`: OK
- `/tl/chat`: OK con API key locale

## Fix runtime integrato

PR collegata:

- `#194` fix(frontend): route local TL Chat through Vite proxy
- `#197` fix(frontend): use local API base for production dashboard

Problema risolto:

- `/tl-chat` veniva intercettato dal proxy Vite come se fosse API backend.
- La TL Chat locale usava `VITE_PROMETEO_API_BASE` remoto invece del proxy locale.

Comportamento corretto:

- `/tl-chat` resta pagina React.
- `/tl/chat` viene inoltrato al backend locale via Vite proxy.
- `/production/*` viene inoltrato al backend locale via Vite proxy.
- frontend locale usa API base relativa per TL Chat, TL Board e Dashboard.
- frontend non locale usa `VITE_PROMETEO_API_BASE`.

## Verifica UI

TL Chat locale verificata da browser:

- pagina caricata
- invio domanda funzionante
- risposta articolo ricevuta
- confidence visibile
- conferma TL visibile
- rischio visibile
- azione consigliata visibile

Esempi verificati:

- `12066?` restituisce risposta `CERTO`
- `12070` restituisce risposta `INFERITO` con conferma TL richiesta

- Dashboard `/` caricata correttamente dopo fix API base locale
- TL Board caricata correttamente dopo fix API base locale
- TL Chat caricata correttamente dopo fix API base locale

## Verifiche tecniche

Ultima verifica locale nota:

- frontend test: 2 passed
- frontend build: OK
- backend minimal tests: 43 passed
- Privacy Guard: OK
- Data Leak Guard: OK

## Comandi runtime locali

Backend:

`cd <PROMETEO_REPO>/backend && load backend environment variables && export DATABASE_URL=<LOCAL_POSTGRES_URL> && python3 -m uvicorn app.main:app --reload`

Frontend:

`cd <PROMETEO_REPO>/frontend && load backend environment variables && npm run dev`

URL locali:

- `http://localhost:5173/`
- `http://localhost:5173/tl-board`
- `http://localhost:5173/tl-chat`

## Scope rispettato

Questa chiusura non introduce:

- nuova architettura
- nuovo world model
- nuovo adapter AI
- nuovo planner
- nuovo frontend complesso
- SMF reale
- immagini
- specifiche reali

## Stato finale

`APP_RUNTIME_CLOSURE_001` dimostra che PROMETEO è avviabile localmente e che la TL Chat è utilizzabile da interfaccia PWA contro backend locale.
