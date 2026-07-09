# INTAKE_PLACEMENT_EXECUTION_BRIDGE_CONTRACT_001

## Scopo

L'Execution Bridge riceve un singolo `IntakePlacementDryRunResult` già prodotto
dal servizio dry-run e, solo quando il piano corrisponde esattamente al target
governato autorizzato, invoca il writer:

`confirm_article_operational_status`

Il bridge collega quindi:

`HUMAN_CONFIRMATIONS`
→ `operational_class`
→ piano dry-run `READY`
→ operazione `APPEND`
→ writer governato

## Scope autorizzato

Il bridge accetta esclusivamente piani con:

- `status=READY`;
- `ok=true`;
- `ready_for_persistence=true`;
- `requires_review=false`;
- `destination=HUMAN_CONFIRMATIONS`;
- `operation=APPEND`;
- `target_repository=article_operational_registry`;
- `target_service=confirm_article_operational_status`;
- `target_section=operational_status`.

Ogni altro piano viene rifiutato senza chiamare writer.

## Non obiettivi

Il bridge non:

- classifica input;
- costruisce o modifica il piano dry-run;
- legge il registry per decidere l'operazione;
- decide tra create, update o no-op;
- valida nuovamente le regole dominio del writer;
- introduce dispatch dinamico;
- introduce batch;
- introduce retry;
- chiama writer alternativi;
- modifica frontend, CORS, TL Chat o dati preview;
- fonde `source_evidence` con gli argomenti del writer;
- promuove semantic status o source status;
- usa LLM.

## Unico writer autorizzato

L'unico writer invocabile è:

```python
confirm_article_operational_status(
    *,
    article: str,
    operational_class: str,
    planner_eligible: bool,
    tl_confirmation_required: bool,
    authority_role: str,
    audit_note: str,
    confirmed_at: datetime | str | None = None,
    material: str | None = None,
    drawing: str | None = None,
    description: str | None = None,
    confirmation_origin: str = "HUMAN_EXPLICIT_CONFIRMATION",
)
```

L'import è statico.

Non sono ammessi:

- `getattr`;
- lookup per nome servizio;
- registry di writer;
- `import_module`;
- mappe di dispatch;
- callback esterne.

## Input

Il bridge riceve un solo:

```python
IntakePlacementDryRunResult
```

Non riceve liste, sequence o batch.

Il piano deve essere già stato prodotto dal servizio dry-run governato.

## Payload

`payload_preview` deve contenere esattamente:

```python
{
    "writer_arguments": {...},
    "source_evidence": {...},
}
```

### writer_arguments

Contiene esclusivamente argomenti ammessi dalla firma del writer.

Campi obbligatori:

- `article`;
- `operational_class`;
- `planner_eligible`;
- `tl_confirmation_required`;
- `authority_role`;
- `audit_note`.

Campi opzionali:

- `confirmed_at`;
- `material`;
- `drawing`;
- `description`;
- `confirmation_origin`.

Campi aggiuntivi non sono accettati.

### source_evidence

Resta separata dal writer.

Deve essere una mapping e il suo `source_id` deve coincidere con il
`source_id` del piano.

La source evidence viene riportata nel risultato del bridge ma non viene passata
al writer.

## Semantica APPEND

`APPEND` autorizza esclusivamente la sottoposizione della conferma al writer.

Non significa che il writer debba necessariamente aggiungere un nuovo record.

Il writer conserva la responsabilità di decidere:

- creazione;
- aggiornamento;
- no-op idempotente;
- history;
- atomicità;
- invalidazione cache;
- readback;
- errori di persistenza.

## Writer chiamato una sola volta

Per ogni esecuzione accettata il writer viene chiamato al massimo una volta.

Il bridge:

- non ritenta;
- non effettua fallback;
- non chiama nuovamente il writer dopo un errore;
- non modifica gli argomenti dopo il primo tentativo.

## Risultato

Il bridge restituisce un `IntakePlacementExecutionResult` con:

- `ok`;
- `status`;
- `writer_called`;
- `source_id`;
- `source_evidence`;
- `writer_result`;
- `persisted`;
- `created`;
- `updated`;
- `error_code`.

## Stati execution

### EXECUTED

Il writer è stato chiamato e ha restituito `ok=true`.

### WRITER_FAILED

Il writer è stato chiamato e ha restituito `ok=false`.

Il bridge non modifica l'esito originale.

In particolare:

`ok=false` con `persisted=true`

deve restare distinguibile, ad esempio nel caso:

`WRITE_SUCCEEDED_READBACK_FAILED`.

### REJECTED

Il piano non soddisfa il contratto del bridge.

Il writer non viene chiamato.

## Errori bridge

- `INVALID_EXECUTION_REQUEST`;
- `PLAN_NOT_READY`;
- `UNAUTHORIZED_DESTINATION`;
- `UNAUTHORIZED_OPERATION`;
- `UNAUTHORIZED_REPOSITORY`;
- `UNAUTHORIZED_SERVICE`;
- `UNAUTHORIZED_SECTION`;
- `INVALID_PAYLOAD`;
- `INVALID_WRITER_ARGUMENTS`;
- `INVALID_SOURCE_EVIDENCE`.

Gli errori dominio o persistenza del writer vengono riportati senza
reinterpretazione.

## Responsabilità del writer

Restano esclusivamente nel writer:

- validazione articolo;
- validazione classe operativa;
- validazione booleani;
- validazione authority role;
- validazione confirmation origin;
- audit note;
- timestamp;
- apertura e validazione registry;
- atomic write;
- preservation dei campi esistenti;
- confirmation history;
- idempotenza sostanziale;
- cache invalidation;
- readback.

## Sicurezza operativa

Il bridge non autorizza:

- pianificazione ordini;
- quantità;
- turni;
- sequenziamento;
- avvio produzione;
- promozione automatica di preview;
- scrittura su altre sezioni.

`planner_eligible=true` mantiene i limiti definiti dal contratto del writer e non
equivale ad autorizzazione di produzione.

## Criteri di accettazione

La capability è verificata quando i test dimostrano che:

1. un piano valido chiama il writer una sola volta;
2. gli argomenti passati coincidono con `writer_arguments`;
3. `source_evidence` non viene passata al writer;
4. i piani non autorizzati non chiamano il writer;
5. campi writer sconosciuti vengono rifiutati;
6. campi obbligatori mancanti vengono rifiutati;
7. source id incoerente viene rifiutato;
8. non esiste dispatch dinamico;
9. non esiste retry;
10. non esiste batch;
11. `WRITE_SUCCEEDED_READBACK_FAILED` conserva `persisted=true`;
12. nessun articolo reale è hardcoded.
