# TL_CHAT_RETRIEVAL_VERIFIABLE_ANSWER_MINIMAL_CLOSURE_001

## Stato

CLOSE.

Il blocco `TL Chat → Retrieval reale → Risposta verificabile` è stabilizzato per tracciabilità minima verificabile.

## Scope chiuso

Questa closure riguarda solo:

- TL Chat;
- domanda reale;
- retrieval governato;
- evidence pack reale;
- fonte primaria;
- excerpt;
- risposta renderizzata;
- coerenza source → evidence → excerpt → answer.

## Capability incluse

- PR #415 — `TL_CHAT_REAL_QUESTION_RENDERING_IMPROVEMENT_001`
- PR #416 — `TL_CHAT_REAL_QUESTION_TRACEABILITY_REGRESSION_001`
- PR #417 — `TL_CHAT_REAL_QUESTION_END_TO_END_TRACEABILITY_GUARD_001`

## Garanzia raggiunta

La TL Chat deve produrre risposte verificabili dove:

- la fonte dichiarata resta coerente con l'evidenza usata;
- l'excerpt mostrato deriva dalla fonte selezionata;
- la risposta non sostituisce contenuto della fonte primaria con evidenze secondarie;
- una domanda reale come `Spiegami planner confidence` mantiene tracciabilità end-to-end;
- contenuti `semantic_registry_confidence:*` non contaminano una risposta attribuita a `docs/prometeo_system_map.md`.

## Stato confidence

Le risposte coinvolte restano correttamente:

- `DA_VERIFICARE`;
- `PREVIEW_ONLY` quando applicabile;
- non promosse a `CERTO`;
- non operative;
- non planner-eligible.

## Fuori scope

Questa closure non apre e non autorizza:

- planner;
- ATLAS runtime;
- SMF/DB;
- frontend;
- nuove fonti;
- densificazione articoli;
- refactor;
- decisioni automatiche di produzione.

## Verdetto

Il blocco è chiudibile come primo nucleo tecnico verificabile della TL Chat.

PROMETEO ora protegge il principio minimo:

`rispondere solo con fonte, evidenza, excerpt e answer coerenti tra loro`.

## Prossima area possibile

Solo dopo questa closure, la prossima area può essere valutazione prodotto/UX TL.

Non è una nuova capability tecnica automatica.
