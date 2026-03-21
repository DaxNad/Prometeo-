# PROMETEO PostgreSQL Cutover Phase v1

## Stato
PostgreSQL può ora gestire anche scrittura, non solo lettura.

## Quando è attivo
Se:
- PROMETEO_DB_BACKEND=postgres
- DATABASE_URL configurato e raggiungibile

allora il backend usa PostgreSQL per:

- GET /events
- GET /events/active
- POST /events/create
- GET /events/{event_id}
- PUT /events/{event_id}
- POST /events/{event_id}/close
- POST /events/close-by-line
- GET /state
- GET /state/{line}/{station}

## Regola
SQLite resta baseline di sicurezza.
Il cutover a PostgreSQL va fatto solo dopo verifica ambiente reale.

## Checklist di attivazione
1. DATABASE_URL presente
2. /health mostra postgres_reachable=true
3. POST /postgres/init eseguito
4. test create/read/close completati
5. switch backend controllato

