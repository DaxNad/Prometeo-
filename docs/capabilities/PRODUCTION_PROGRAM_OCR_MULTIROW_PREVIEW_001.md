# PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001

## Scopo

Elaborare più righe OCR piatte del programma produzione preservando ordine, righe accettate, righe rifiutate e campi mancanti, senza persistenza automatica.

## Stato

CHIUSA

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

## Chiusura

### Commit di implementazione

- `6a2f02f feat(ocr): support multirow production program preview`

### Verifica eseguita

```text
48 passed in 0.55s
```

Suite pertinente:

- `backend/tests/test_production_program_snapshot_preview.py`
- `backend/tests/test_production_program_image_ocr_acquisition.py`
- `backend/tests/test_production_program_image_ocr_acquisition_endpoint.py`
- `backend/tests/test_production_program_image_ocr_multipage_acquisition.py`
- `backend/tests/test_production_program_image_ocr_multipage_acquisition_endpoint.py`

### Contratto multirow verificato

Un singolo input può contenere più righe OCR piatte.

La preview:

- preserva l'ordine originale;
- assegna `record_index` a ogni riga;
- mantiene le righe valide in `records_preview[]`;
- mantiene le righe incomplete in `rejected_rows[]`;
- associa ogni campo mancante al relativo `record_index`;
- non blocca le righe valide quando un'altra riga è incompleta.

### Caso verificato

Con tre righe, di cui due valide e una senza quantità:

- i record 1 e 3 sono presenti in `records_preview[]`;
- il record 2 è presente in `rejected_rows[]`;
- `missing_fields[]` dichiara `quantities` per `record_index: 2`;
- il motivo di rifiuto è `MISSING_QUANTITIES`;
- lo stato resta governato e richiede conferma umana.

### Confine di non persistenza verificato

La preview mantiene:

```json
{
  "requires_confirmation": true,
  "persisted": false,
  "writer_called": false,
  "planner_called": false,
  "pattern_learning_called": false
}
```

### File runtime modificati

- `backend/app/services/production_program_snapshot_preview.py`
- `backend/tests/test_production_program_snapshot_preview.py`

### File e sistemi non modificati

- frontend;
- adapter Tesseract;
- endpoint OCR;
- endpoint di conferma;
- registry persistente;
- database;
- planner;
- writer.

## Capability successiva

`PRODUCTION_PROGRAM_OCR_MULTIROW_ENDPOINT_CONTRACT_001`

Scopo minimo: verificare che l'endpoint OCR propaghi integralmente il contratto multirow governato, preservando `records_preview[]`, `rejected_rows[]`, `missing_fields[]`, `record_index`, conferma obbligatoria e assenza di persistenza.

## Next move

Aprire `PRODUCTION_PROGRAM_OCR_MULTIROW_ENDPOINT_CONTRACT_001` solo dopo il commit della presente chiusura documentale.
