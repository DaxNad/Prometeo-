# PROMETEO PostgreSQL Repository Prep v1

## Scopo
Preparare un repository PostgreSQL separato senza toccare il flusso SQLite operativo.

## Contenuto introdotto
- repository `PostgresEventsRepository`
- endpoint tecnici:
  - `/postgres/ping`
  - `/postgres/init`
  - `/postgres/events`
- schema SQL dedicato PostgreSQL

## Regola di questa fase
Gli endpoint operativi:
- `/events`
- `/state`

continuano a usare SQLite.

## Obiettivo della fase successiva
Introdurre un repository astratto comune e decidere runtime:
- SQLite repository
- PostgreSQL repository

senza rompere il CORE già validato.
