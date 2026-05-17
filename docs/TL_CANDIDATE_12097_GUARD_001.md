# TL CANDIDATE 12097 GUARD 001

Stato: `TL_CANDIDATE_12097_GUARD_001_VERIFICATO`

Questo documento registra `12097` come candidato controllato nel perimetro PROMETEO_GOAL_CLOSURE.

`12097` non viene dichiarato pilota chiuso e non viene promosso a `CERTO` globale.

## Stato candidato

- Articolo: `12097`
- Stato: candidato controllato
- Chiusura pilota: non ancora ammessa
- Promozione automatica a `CERTO`: vietata

## Evidenze già presenti

- Metadata povero con supporto produce classificazione `ASK_TL`.
- `COLLAUDO_VERTICALE` viene trattato come modalità macchina, non come stazione autonoma.
- Le modifiche operative ad alto impatto richiedono conferma forte.
- Esempio challenge: `CONFERMO MODIFICA 12097`.

## Guard operativo

`12097` resta candidato fino a quando non esiste una conferma TL/documentale sufficiente per chiudere il profilo operativo.

Regole:

- non promuovere `12097` a `CERTO` da densifier o supporto parziale;
- non usare `COLLAUDO_VERTICALE` come stazione produttiva;
- mantenere `COLLAUDO_VERTICALE` come modalità macchina CP;
- applicare preview/diff prima di qualunque modifica operativa;
- richiedere conferma forte per route, planner_eligible, confidence, operational_class, ZAW/HENN/PIDMILL/CP;
- non includere `12099` o `12101` nello stesso blocco senza copertura dedicata.

## Test di verifica

Ultima verifica locale nota:

- `test_densifier_turns_poor_metadata_with_support_into_ask_tl`
- `test_support_summary_keeps_cp_vertical_as_machine_mode_not_station`
- `test_master_contains_tl_override_confirmation_contract`

Risultato:

- 3 passed
- `make tl-eval`: `RESULT=PASS`
- Privacy Guard: OK
- Data Leak Guard: OK

## Scope rispettato

Questa registrazione non introduce:

- runtime app
- frontend
- AI esterna
- SMF reale
- immagini
- specifiche reali
- nuovi adapter
- nuova architettura
- nuovo world model

## Stato finale

`12097` è candidato controllato, non pilota chiuso.

Il prossimo avanzamento ammesso è solo verso chiusura verificata con conferma TL/documentale e test dedicati.
