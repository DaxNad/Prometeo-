# PROMETEO PostgreSQL Consolidation v1

## Stato attuale
Il sistema resta operativo su SQLite come baseline stabile.

## Obiettivo di questa fase
Consolidare PostgreSQL senza rompere il CORE.

## Risultato di questa fase
- backend conosce db_backend
- backend legge DATABASE_URL
- health espone stato PostgreSQL
- probe connessione PostgreSQL disponibile
- SQLite resta sorgente primaria operativa

## Cutover non ancora eseguito
Le API events/state usano ancora SQLite.
Il passaggio completo a PostgreSQL sarà fase successiva con repository dedicato.

## Regola
Prima validazione connessione e configurazione.
Poi migrazione repository.
Poi switch operativo.
