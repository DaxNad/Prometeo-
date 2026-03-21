# PROMETEO PostgreSQL Read-Only Phase v1

## Scopo
Attivare PostgreSQL in modalità controllata, senza rompere il CORE.

## Stato di questa fase
Quando:
- PROMETEO_DB_BACKEND=postgres
- DATABASE_URL=...

il backend usa PostgreSQL per:

- GET /events
- GET /events/active
- GET /events/{event_id}
- GET /state
- GET /state/{line}/{station}

## Write operations
Le operazioni di scrittura restano bloccate con 501:

- POST /events/create
- PUT /events/{event_id}
- POST /events/{event_id}/close
- POST /events/close-by-line

## Motivazione
Prima si valida la lettura reale dei dati.
Solo dopo si attiva la scrittura PostgreSQL.
