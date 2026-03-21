# PROMETEO POSTGRES PHASE FREEZE v1

## Stato raggiunto
Il backend supporta ora doppio backend controllato:

- SQLite = baseline operativa
- PostgreSQL = target attivabile tramite variabili ambiente

## Componenti consolidati
- config.py con db_backend e DATABASE_URL
- db.py con probe PostgreSQL
- repository astratto EventsRepository
- SQLiteEventsRepository
- PostgresEventsRepository
- factory repository
- events/state instradati tramite repository comune
- endpoint PostgreSQL probe disponibili

## Regola attuale
Default:
- PROMETEO_DB_BACKEND=sqlite

Target:
- PROMETEO_DB_BACKEND=postgres
- DATABASE_URL valorizzato

## Cutover consentito
Il backend può passare a PostgreSQL senza refactor aggiuntivo.

## Baseline congelata
Questa fase viene considerata stabile come:
POSTGRES PREP + CUTOVER READY
