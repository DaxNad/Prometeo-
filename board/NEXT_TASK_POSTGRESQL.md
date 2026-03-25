# PROMETEO — NEXT TASK

## task attivo
Consolidare PostgreSQL reale end-to-end.

## obiettivo
Rendere stabile la persistenza backend su database reale, sia in locale sia su Railway.

## perimetro
- configurazione DATABASE_URL
- connessione SQLAlchemy o layer DB attuale
- endpoint /health con stato db
- endpoint /db/ping
- verifica deploy Railway con variabili ambiente corrette

## criterio di completamento
Il task è completo quando:

1. il backend parte in locale con PostgreSQL attivo
2. /health restituisce stato ok + database raggiungibile
3. /db/ping risponde correttamente
4. Railway vede DATABASE_URL al runtime
5. il deploy remoto risponde senza 502

## vincoli
- non cambiare architettura
- non introdurre nuovi moduli inutili
- non toccare frontend in questo task
