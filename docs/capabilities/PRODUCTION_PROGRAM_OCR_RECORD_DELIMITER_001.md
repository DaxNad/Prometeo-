# PRODUCTION_PROGRAM_OCR_RECORD_DELIMITER_001

## Scopo

Trasformare il testo OCR osservato del programma produzione in righe candidate strutturate e governate, senza persistenza automatica.

## Stato

CHIUSA

## Capability precedente

- PROMETEO_PRODUCTION_PROGRAM_IMAGE_OCR_BACKEND_AUTH_AND_PREVIEW_001

## Input minimo osservato

```text
7055845000C0 *P.12063A DIS. A 214 501 9100 A2145019100 70 400 55 55
```

## Output minimo richiesto

```json
{
  "records_preview": [
    {
      "material_code": "7055845000C0",
      "customer_material": "A2145019100",
      "quantities": [70, 400, 55, 55],
      "status": "DA_VERIFICARE"
    }
  ],
  "rejected_rows": [],
  "missing_fields": [],
  "confidence": "DA_VERIFICARE",
  "requires_confirmation": true,
  "persisted": false,
  "writer_called": false,
  "planner_called": false
}
```

## Regole minime

- `material_code` deve essere osservato direttamente nella riga.
- `customer_material` deve essere osservato direttamente nella riga.
- Le quantità devono essere estratte preservando ordine e valore.
- Nessun valore mancante può essere inventato.
- I token non riconosciuti devono restare osservabili oppure produrre una riga rifiutata.
- L'output deve mantenere stato `DA_VERIFICARE`.
- La conferma umana deve essere sempre richiesta.
- Il parser non deve chiamare writer, planner o pattern learning.
- Nessuna riga deve essere persistita durante la preview.

## Output governato

La risposta deve contenere almeno:

- `records_preview[]`;
- `rejected_rows[]`;
- `missing_fields[]`;
- `confidence`;
- `requires_confirmation`;
- `persisted`;
- `writer_called`;
- `planner_called`.

## Criterio di accettazione minimo

Data la riga:

```text
7055845000C0 *P.12063A DIS. A 214 501 9100 A2145019100 70 400 55 55
```

il backend deve estrarre almeno:

```json
{
  "material_code": "7055845000C0",
  "customer_material": "A2145019100",
  "quantities": [70, 400, 55, 55],
  "status": "DA_VERIFICARE"
}
```

e deve inoltre dichiarare:

```json
{
  "requires_confirmation": true,
  "persisted": false,
  "writer_called": false,
  "planner_called": false
}
```

## Fail-closed

La riga deve entrare in `rejected_rows[]` quando:

- manca il codice materiale;
- manca il materiale cliente;
- non sono presenti quantità riconoscibili;
- la segmentazione produce più interpretazioni incompatibili;
- il formato osservato non consente un'estrazione deterministica.

I campi mancanti devono essere dichiarati in `missing_fields[]`.

## File ammessi inizialmente

- `docs/capabilities/PRODUCTION_PROGRAM_OCR_RECORD_DELIMITER_001.md`
- servizio di preview OCR, dopo mappatura;
- eventuale parser deterministico già esistente, dopo mappatura;
- modelli di risposta strettamente pertinenti;
- test backend dedicati.

## File e azioni vietati

- registry persistente;
- endpoint di conferma;
- planner produzione;
- writer ordini;
- database e migrazioni;
- frontend, salvo successiva necessità dimostrata;
- inferenza LLM;
- euristiche non dichiarate;
- refactoring estraneo alla slice.

## Ordine di lavoro

1. Mappatura read-only del parser e del contratto preview esistenti.
2. Individuazione del primo contratto mancante.
3. Test rosso con la riga campione.
4. Parser deterministico minimo.
5. Test verde.
6. Test fail-closed per riga incompleta o ambigua.
7. Verifica esplicita della non persistenza.
8. Chiusura documentata.

## Limite di scope

La capability termina alla produzione di candidate rows governate.

Non comprende:

- conferma umana;
- correzione manuale;
- persistenza;
- pianificazione;
- apprendimento automatico del formato.

## Next move

Mappare in modalità read-only il percorso:

`observed_text → normalized_lines → snapshot_preview → parser record esistente`

senza applicare patch.

## Chiusura

### Commit di implementazione

- `09de255 feat(ocr): parse flat production program rows`

### Verifica eseguita

```text
47 passed in 0.55s
```

Suite pertinente:

- `backend/tests/test_production_program_snapshot_preview.py`
- `backend/tests/test_production_program_image_ocr_acquisition.py`
- `backend/tests/test_production_program_image_ocr_acquisition_endpoint.py`
- `backend/tests/test_production_program_image_ocr_multipage_acquisition.py`
- `backend/tests/test_production_program_image_ocr_multipage_acquisition_endpoint.py`

### Contratto positivo verificato

Data la riga OCR:

```text
7055845000C0 *P.12063A DIS. A 214 501 9100 A2145019100 70 400 55 55
```

la preview restituisce almeno:

```json
{
  "material_code": "7055845000C0",
  "customer_material": "A2145019100",
  "quantities": [70, 400, 55, 55],
  "status": "DA_VERIFICARE"
}
```

### Fail-closed verificato

Una riga riconoscibile ma priva di quantità produce:

```json
{
  "records_preview": [],
  "rejected_rows": [
    {
      "reason": "MISSING_QUANTITIES",
      "status": "BLOCCATO"
    }
  ],
  "missing_fields": ["quantities"]
}
```

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
- endpoint OCR;
- registry persistente;
- endpoint di conferma;
- database;
- planner;
- writer;
- adapter Tesseract.

## Capability successiva

`PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001`

Scopo minimo: estendere il contratto governato a più righe OCR piatte, preservando ordine, righe rifiutate, campi mancanti, conferma obbligatoria e assenza di persistenza.

## Next move

Aprire `PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001` solo dopo il commit della presente chiusura documentale.
