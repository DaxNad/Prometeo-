# PROMETEO GOAL COMPLETE V1

Stato: `PROMETEO_GOAL_COMPLETE_V1_CHECK`

## Scopo

Definire il check locale unico per verificare la chiusura pratica `PROMETEO_GOAL_COMPLETE_V1` senza cambiare runtime, architettura o dati reali.

## Distinzione contrattuale dei target GOAL

`make goal-guard` e `make goal-complete-v1` hanno ruoli separati.

`make goal-guard` è un merge/PR predictor: va usato prima di push o Pull Request per verificare localmente i controlli minimi di integrabilità, inclusi diff check, Data Leak Guard, Privacy Guard, Docs Authority Guard, TL eval e backend tests.

`make goal-complete-v1` è un operational closure validator: va usato per validare localmente la chiusura pratica `PROMETEO_GOAL_COMPLETE_V1`, includendo TL Chat contract, TL eval, controlli su file sensibili tracciati, regole di session memory, Privacy Guard, Data Leak Guard e semantica di closure operativa.

I due target non sono definiti come superset obbligatori uno dell'altro. La separazione evita accoppiamento tra percorso pre-PR e validazione di chiusura operativa.

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

## Esplicitamente escluso da GOAL_COMPLETE_V1

PROMETEO DEMO PACK sintetico vendibile è escluso da GOAL_COMPLETE_V1.

Motivo:
questa fase è prematura rispetto alla chiusura operativa corrente. Prima va consolidato il GOAL tecnico-operativo già raggiunto: guard, TL eval, AI boundary, docs authority, TL practical query automation e controllo `make goal-complete-v1`.

Il DEMO PACK commerciale/sintetico potrà diventare un perimetro successivo separato, solo dopo conferma esplicita. Non deve introdurre ora:
- nuovi dataset demo;
- nuove schermate;
- nuova logica commerciale;
- nuova PWA;
- modifiche runtime;
- dati sintetici strutturati per vendita.

Per GOAL_COMPLETE_V1 il criterio resta:
chiusura operativa verificabile, non preparazione commerciale.

