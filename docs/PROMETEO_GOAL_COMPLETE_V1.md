# PROMETEO GOAL COMPLETE V1

Stato: `PROMETEO_GOAL_COMPLETE_V1_CHECK`

## Scopo

Definire il check locale unico per verificare la chiusura pratica `PROMETEO_GOAL_COMPLETE_V1` senza cambiare runtime, architettura o dati reali.

## Comando

`make goal-complete-v1`

Il target esegue:

- TL Chat contract
- TL eval sanificato
- Data Leak Guard
- Privacy Guard
- controllo che `data/local_reports/session_memory/scadenze_2026-06-22.md` sia locale e ignorato da git
- controllo locale su pattern sensibili tracciati

## Guard Documentale

`python3 scripts/docs_authority_guard.py`

Il guard blocca nuove regole permanenti fuori da `docs/PROMETEO_MASTER.md` quando manca un rimando esplicito al Master.

## Frontend Build

Il frontend build non è eseguito di default perché scrive `frontend/dist`.

Per includerlo esplicitamente:

`PROMETEO_GOAL_CHECK_FRONTEND_BUILD=1 make goal-complete-v1`

## Criterio PASS

`PROMETEO_GOAL_COMPLETE_V1` passa quando il comando termina con:

`RESULT=PASS`

## Confini

Questo check non introduce:

- nuova architettura
- nuovo runtime
- nuovi adapter AI
- modifiche a dati reali
- modifiche a `specs_finitura`
- modifiche a metadata articolo
