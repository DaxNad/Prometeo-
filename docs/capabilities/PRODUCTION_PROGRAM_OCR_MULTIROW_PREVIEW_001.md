# PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001

## Scopo

Elaborare più righe OCR piatte del programma produzione preservando ordine, righe accettate, righe rifiutate e campi mancanti, senza persistenza automatica.

## Stato

APERTA - PERIMETRO

## Capability precedente

- `PRODUCTION_PROGRAM_OCR_RECORD_DELIMITER_001`
- Commit di integrazione: `8b0a1c9 feat(ocr): parse flat production program rows (#550)`

## Input verticale minimo

Il parser deve ricevere più righe OCR nello stesso testo, ad esempio:

```text
7055845000C0 *P.12063A DIS. A 214 501 9100 A2145019100 70 400 55 55
7055845000C1 *P.12064A DIS. A2145019200
7055845000C2 *P.12065A DIS. A 214 501 9300 A2145019300 20 30
```

## Output minimo richiesto

```json
{
  "records_preview": [
    {
      "record_index": 1,
      "material_code": "7055845000C0",
      "customer_material": "A2145019100",
      "quantities": [70, 400, 55, 55],
      "status": "DA_VERIFICARE"
    },
    {
      "record_index": 3,
      "material_code": "7055845000C2",
      "customer_material": "A2145019300",
      "quantities": [20, 30],
      "status": "DA_VERIFICARE"
    }
  ],
  "rejected_rows": [
    {
      "record_index": 2,
      "source_line": "7055845000C1 *P.12064A DIS. A2145019200",
      "reason": "MISSING_QUANTITIES",
      "status": "BLOCCATO"
    }
  ],
  "missing_fields": [
    {
      "record_index": 2,
      "field": "quantities"
    }
  ],
  "confidence": "DA_VERIFICARE",
  "requires_confirmation": true,
  "persisted": false,
  "writer_called": false,
  "planner_called": false,
  "pattern_learning_called": false
}
```

## Regole deterministiche

- Ogni riga non vuota rappresenta una candidata indipendente.
- L'ordine delle righe deve essere preservato tramite `record_index`.
- Una riga valida non deve essere scartata perché un'altra riga è invalida.
- Una riga incompleta deve entrare in `rejected_rows[]`.
- Ogni campo mancante deve essere dichiarato con il relativo `record_index`.
- Nessun valore può essere inventato, completato o corretto implicitamente.
- Il parser non deve riordinare quantità o record.
- Il risultato complessivo resta `DA_VERIFICARE`.
- `requires_confirmation` deve restare `true`.
- Nessuna preview può chiamare writer, planner o pattern learning.
- Nessuna preview può modificare registry o database.

## Criterio di accettazione minimo

Dato un input di tre righe, di cui due valide e una priva di quantità:

1. `records_preview[]` contiene due record nell'ordine originale;
2. `rejected_rows[]` contiene la seconda riga;
3. ogni elemento espone il corretto `record_index`;
4. `missing_fields[]` dichiara `quantities` per il record 2;
5. `requires_confirmation` è `true`;
6. `persisted`, `writer_called`, `planner_called` e `pattern_learning_called` sono `false`;
7. le regressioni della preview OCR restano verdi.

## Fail-closed

L'intero input deve essere bloccato solo quando:

- non contiene righe non vuote;
- nessuna riga può essere classificata deterministicamente;
- il formato rende impossibile preservare il confine tra le righe.

Le righe individualmente incomplete non devono impedire la preview delle altre righe valide.

## File ammessi inizialmente

- `docs/capabilities/PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001.md`
- `backend/app/services/production_program_snapshot_preview.py`, dopo mappatura;
- `backend/tests/test_production_program_snapshot_preview.py`;
- test endpoint OCR solo se la necessità è dimostrata.

## File e azioni vietati

- frontend;
- adapter Tesseract;
- endpoint di conferma;
- registry persistente;
- database e migrazioni;
- planner;
- writer;
- inferenza LLM;
- apprendimento del formato;
- refactoring non necessario.

## Ordine di lavoro

1. Mappatura read-only del ramo flat OCR introdotto da `8b0a1c9`.
2. Definizione del contratto multirow senza cambiare quello single-row.
3. Primo test rosso con due righe valide e una rifiutata.
4. Implementazione deterministica minima.
5. Test verde dedicato.
6. Regressione completa preview e acquisizione OCR.
7. Verifica esplicita della non persistenza.
8. Chiusura documentata.

## Limite di scope

La capability termina alla preview governata di più righe OCR piatte.

Non comprende:

- correzione manuale;
- conferma;
- persistenza;
- deduplicazione;
- aggregazione delle quantità;
- pianificazione;
- associazione a ordini già registrati.

## Next move

Mappare in modalità read-only il ramo flat OCR corrente e i test introdotti da `8b0a1c9`, producendo un output compatto e senza applicare patch.
