# TL_CHAT_PRODUCTION_SPEC_SUMMARY_CLOSURE_001

## Capability

CAPABILITY: TL Chat — sintesi produzione vincolata a fonte autorizzata  
STATUS: CLOSED  
DATE: 2026-07-15

## Obiettivo verificato

Impedire alla TL Chat di generare una sintesi di produzione quando non è disponibile una specifica reale o una preview autorizzata per l’articolo richiesto.

## Evidenza runtime

- Endpoint: POST /tl/chat
- Articolo: 12069
- HTTP: 200 OK
- Risposta: SINTESI PRODUZIONE NON DISPONIBILE
- Fonte: spec_intake_preview
- Stato fonte: SOURCE_MISSING
- Stato semantico: MANCANTE
- Confidence: DA_VERIFICARE
- requires_confirmation: true

La TL Chat ha dichiarato esplicitamente che la specifica reale o preview autorizzata non è disponibile e non ha generato una sintesi da dati inferiti.

## Evidenza automatizzata

- Test: backend/tests/test_tl_chat_production_spec_summary.py
- Risultato: 7 passed
- Durata: 0.63s

## Vincoli preservati

- read-only
- local-only
- nessuna chiamata LLM
- nessuna scrittura database
- nessuna scrittura SMF
- nessuna mutazione planner
- nessuna mutazione runtime
- nessuna sintesi produzione inferita

## Limite di scope

La capability non acquisisce nuove specifiche, non abilita nuove fonti e non implementa OCR.

## Verdetto

VERDICT: CLOSED_AND_VERIFIED  
RUNTIME_TEST: PASSED  
DEDICATED_TEST_SUITE: PASSED  
NEXT_MOVE: COMMIT_CLOSURE_RECORD
