# ADR-001 — Event Engine come modulo separato

## Stato
APPROVATO

## Data
2026-03-14

## Contesto
PROMETEO richiede una gestione strutturata degli eventi di reparto, anomalie, blocchi e stati operativi.

## Decisione
Creare un modulo Event Engine separato nel backend FastAPI con:
- model evento centralizzato
- service layer dedicato
- endpoint API propri
- futura integrazione con dashboard e ATLAS

## Motivazione
- separazione responsabilità
- scalabilità futura
- migliore manutenzione
- integrazione semplice con AI e database reale

## Conseguenze
- endpoint dedicati /events
- schema dati evento centralizzato
- service layer separato
- integrazione frontend semplificata
