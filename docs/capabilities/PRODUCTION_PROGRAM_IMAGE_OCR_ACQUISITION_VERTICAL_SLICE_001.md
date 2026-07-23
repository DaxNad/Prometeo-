# PRODUCTION_PROGRAM_IMAGE_OCR_ACQUISITION_VERTICAL_SLICE_001

## Scopo

Acquisire una o più immagini PNG/JPEG del programma produzione, produrre una preview OCR non autorevole, normalizzare i dati osservati in uno snapshot DA_VERIFICARE e consentire la persistenza solo dopo conferma umana autorizzata.

## Stato

CHIUSA SU MAIN

## Commit rilevanti

- 82e8a90 fix(frontend): prevent production proxy from capturing production-program route
- e70fe62 fix(frontend): proxy production program OCR requests
- 2d3e5fc feat(ocr): add deterministic production program stub

## Flusso verificato

- immagine PNG/JPEG
- upload frontend
- backend
- OCR deterministic-stub
- testo osservato
- normalizzazione righe
- snapshot preview DA_VERIFICARE
- conferma umana autorizzata
- persistenza CONFERMATO versione 1

## Guardrail

- La preview non viene persistita automaticamente.
- Una risposta HTTP 200 non equivale a successo operativo.
- Lo snapshot resta DA_VERIFICARE fino a conferma umana.
- La conferma persiste una versione CONFERMATO.
- La conferma non promuove lo snapshot a CERTO.
- Il planner non viene attivato.
- Il pattern learning non viene attivato.

## Esito test

- Backend: 25 passed
- Frontend: ProductionProgramImageOCRAcquisitionPage.test.tsx, 10 passed

## Limite di scope

Questa capability non implementa OCR reale produttivo. Usa un adapter deterministico/stub per ambiente dev/test.

## Prossima capability candidata

PRODUCTION_PROGRAM_TESSERACT_OCR_ADAPTER_001

Scopo: sostituire o affiancare lo stub con adapter OCR reale controllato, mantenendo preview non autorevole, conferma umana obbligatoria e blocco di persistenza automatica.
