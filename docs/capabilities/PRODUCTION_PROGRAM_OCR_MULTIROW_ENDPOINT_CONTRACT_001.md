# PRODUCTION_PROGRAM_OCR_MULTIROW_ENDPOINT_CONTRACT_001

## Scopo

Verificare che l'endpoint OCR del programma produzione propaghi integralmente la preview multirow governata prodotta dal dominio, senza trasformazioni distruttive e senza persistenza automatica.

## Stato

CHIUSA

## Capability precedente

- `PRODUCTION_PROGRAM_OCR_MULTIROW_PREVIEW_001`
- Commit di integrazione:
  `0a960a1 feat(ocr): support multirow production program preview (#551)`

## Percorso verticale minimo

```text
immagini OCR
→ adapter OCR
→ observed_text multirow
→ snapshot_preview
→ endpoint HTTP
→ risposta JSON governata
```

## Contratto minimo da propagare

L'endpoint deve preservare integralmente:

- `records_preview[]`;
- `rejected_rows[]`;
- `missing_fields[]`;
- `record_index`;
- `confidence`;
- `semantic_status`;
- `requires_confirmation`;
- `persisted`;
- `writer_called`;
- `planner_called`;
- `pattern_learning_called`.

## Input minimo

Il provider OCR controllato deve restituire un testo equivalente a:

```text
7055845000C0 *P.12063A DIS. A 214 501 9100 A2145019100 70 400 55 55
7055845000C1 *P.12064A DIS. A2145019200
7055845000C2 *P.12065A DIS. A 214 501 9300 A2145019300 20 30
```

## Output minimo atteso

```json
{
  "status": "PREVIEW_READY",
  "snapshot_preview": {
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
}
```

## Regole deterministiche

- L'endpoint non deve ricostruire il contratto multirow.
- L'endpoint deve propagare il risultato prodotto dal servizio dominio.
- L'ordine di `records_preview[]` e `rejected_rows[]` deve essere preservato.
- `record_index` non deve essere ricalcolato o rimosso.
- `missing_fields[]` deve conservare l'associazione al record.
- Nessun campo governato può essere omesso silenziosamente.
- Una riga rifiutata non deve trasformare una preview parziale valida in errore di trasporto.
- La risposta deve mantenere `requires_confirmation=true`.
- La risposta deve mantenere `persisted=false`.
- Writer, planner e pattern learning devono restare disabilitati.
- Nessuna chiamata endpoint deve modificare registry o database.

## Criterio di accettazione minimo

Un test endpoint deve dimostrare che:

1. un adapter OCR controllato restituisce tre righe;
2. due righe sono propagate in `records_preview[]`;
3. una riga è propagata in `rejected_rows[]`;
4. `record_index` vale rispettivamente `1`, `2`, `3`;
5. `missing_fields[]` dichiara `quantities` per il record 2;
6. lo stato HTTP è `200`;
7. la risposta resta una preview governata;
8. `requires_confirmation` è `true`;
9. `persisted`, `writer_called`, `planner_called` e
   `pattern_learning_called` sono `false`;
10. il registry resta invariato.

## Fail-closed

L'endpoint deve:

- restituire `422` per payload Base64 invalido;
- conservare i codici OCR fail-closed già esistenti;
- non presentare una risposta incompleta come confermata;
- non inventare `records_preview[]` quando il dominio non li produce;
- non eseguire fallback verso writer, planner o persistenza.

## File ammessi inizialmente

- `docs/capabilities/PRODUCTION_PROGRAM_OCR_MULTIROW_ENDPOINT_CONTRACT_001.md`;
- `backend/tests/test_production_program_image_ocr_acquisition_endpoint.py`;
- endpoint OCR solo se il test dimostra una perdita reale del contratto;
- servizio preview solo se emerge una regressione strettamente pertinente.

## File e azioni vietati

- frontend;
- adapter Tesseract reale;
- endpoint di conferma;
- registry persistente;
- database e migrazioni;
- planner;
- writer;
- inferenza LLM;
- refactoring non necessario;
- modifica del contratto single-row.

## Ordine di lavoro

1. Mappatura read-only dell'endpoint e dei test endpoint esistenti.
2. Verifica del payload restituito dal servizio di acquisizione.
3. Primo test rosso sul contratto multirow endpoint.
4. Patch minima solo se il test dimostra una perdita reale.
5. Test verde dedicato.
6. Regressione OCR backend pertinente.
7. Verifica esplicita della non persistenza.
8. Chiusura documentata.

## Limite di scope

La capability termina alla propagazione HTTP della preview multirow.

Non comprende:

- visualizzazione frontend;
- conferma;
- persistenza;
- correzione manuale;
- deduplicazione;
- aggregazione quantità;
- pianificazione;
- associazione con registri ordini esistenti.

## Next move

Mappare in modalità read-only:

```text
adapter OCR
→ servizio acquisizione
→ snapshot_preview
→ serializer endpoint
→ risposta JSON
```

e i test endpoint esistenti, producendo un output compatto e senza patch.

## Chiusura

### Commit di verifica

- `5b6039f test(ocr): preserve multirow endpoint contract`

### Verifica eseguita

```text
49 passed in 0.54s
```

### Esito contrattuale

```text
CONTRACT_ALREADY_PRESERVED=YES
RUNTIME_PATCH_REQUIRED=NO
```

L'endpoint OCR preserva integralmente il contratto multirow prodotto dal servizio dominio.

Sono stati verificati:

- `records_preview[]`;
- `rejected_rows[]`;
- `missing_fields[]`;
- `record_index`;
- ordine dei record;
- `confidence`;
- `semantic_status`;
- `requires_confirmation=true`;
- `persisted=false`;
- `writer_called=false`;
- `planner_called=false`;
- `pattern_learning_called=false`.

### Decisione

Non è stata applicata alcuna patch runtime.

La capability è stata chiusa mediante test di caratterizzazione endpoint, poiché la propagazione di `snapshot_preview` risultava già corretta e non distruttiva.

### File modificato

- `backend/tests/test_production_program_image_ocr_acquisition_endpoint.py`

### Sistemi non modificati

- servizio runtime OCR;
- servizio snapshot preview;
- frontend;
- adapter Tesseract;
- endpoint multipage;
- endpoint di conferma;
- registry persistente;
- database e migrazioni;
- writer;
- planner;
- pattern learning;
- inferenza LLM.

### Limite confermato

La capability termina alla verifica della propagazione HTTP del contratto multirow.

Non introduce:

- conferma;
- persistenza;
- correzione manuale;
- aggregazione;
- deduplicazione;
- pianificazione;
- scrittura su registry.

## Next move

Aprire una capability successiva solo dopo aver definito il prossimo confine verticale minimo verificabile.
