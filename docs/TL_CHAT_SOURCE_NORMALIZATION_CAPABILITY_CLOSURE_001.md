# TL_CHAT_SOURCE_NORMALIZATION_CAPABILITY_CLOSURE_001

## Stato

`TL_CHAT_SOURCE_NORMALIZATION_001` è CHIUSA.

## Risultato

La TL Chat espone campi strutturati opzionali per i casi semanticamente applicabili:

- `source`
- `source_status`
- `semantic_status`
- `missing_data`

## Rami normalizzati

- articolo sconosciuto;
- fallback terminale senza articolo;
- fallback operativo turno senza contesto;
- PIDMILL senza dima disponibile;
- componenti assenti;
- componenti presenti ma non interpretabili.

## Regole preservate

- `SOURCE_*` è usato solo per sorgenti o adapter reali;
- una regola interna non finge una sorgente recuperata;
- `MANCANTE` espone sempre `missing_data`;
- preview e fonti read-only non vengono promosse a `CERTO`;
- i campi non applicabili restano assenti;
- nessuna modifica a planner, UI, SMF o database.

## Evidenze

- test mirati: 9 passed;
- suite TL Chat: 264 passed;
- suite backend: 804 passed, 3 deselected;
- audit post-merge completato in modalità `READ_ONLY_NON_BLOCKING`;
- working tree post-merge pulito e allineato a `origin/main`.

## Audit residuo

L’audit inventaria 18 ritorni in `_build_contract_response`:

- 15 ritorni tramite helper o variabile;
- 3 costruzioni dirette.

Le tre costruzioni dirette sono intenzionali e conformi:

1. articolo sconosciuto → `missing / SOURCE_MISSING / MANCANTE`;
2. regola generale ZAW → regola interna, senza fonte documentale fittizia;
3. fallback terminale → `missing / SOURCE_MISSING / MANCANTE`.

Il conteggio dell’audit non rappresenta un failure né una capability aperta.

## Decisione

Nessun ulteriore intervento runtime è richiesto per questa capability.

Qualsiasi estensione futura su family registry, lifecycle, preview, article summary o provenance completa costituisce una capability separata e non deve riaprire questa chiusura.
