# PRODUCTION_PROGRAM_TESSERACT_OCR_ADAPTER_001

## Scopo

Introdurre un adapter OCR reale controllato per immagini PNG/JPEG del programma produzione, mantenendo il flusso governato già verificato dalla slice deterministic-stub.

## Stato

APERTA - PERIMETRO

## Capability precedente

- PRODUCTION_PROGRAM_IMAGE_OCR_ACQUISITION_VERTICAL_SLICE_001
- Commit chiusura: 47d1012 docs(ocr): close production program image acquisition slice

## Obiettivo verticale minimo

- Ricevere una o più immagini PNG/JPEG.
- Eseguire OCR reale tramite adapter controllato.
- Produrre testo osservato.
- Normalizzare righe programma produzione.
- Restituire snapshot preview DA_VERIFICARE.
- Richiedere conferma umana.
- Persistire solo dopo conferma autorizzata.

## Guardrail invarianti

- Nessuna persistenza automatica della preview.
- Nessuna promozione automatica a CERTO.
- Nessuna attivazione planner.
- Nessuna attivazione pattern learning.
- HTTP 200 non equivale automaticamente a successo operativo.
- Ogni campo normalizzato deve conservare provenienza osservabile.

## Limite di scope

Questa capability non deve introdurre interpretazione intelligente, pianificazione produzione, correzione automatica dei dati o apprendimento pattern. Deve limitarsi a OCR reale controllato più preview verificabile.

## Criterio di accettazione

- Test backend verdi per adapter OCR reale o fallback governato.
- Test endpoint verdi per PREVIEW_READY, OCR_FAILED e REJECTED.
- Test frontend verdi per preview, errore e conferma.
- UI manuale: immagine reale produce preview o errore governato, mai successo ambiguo.
