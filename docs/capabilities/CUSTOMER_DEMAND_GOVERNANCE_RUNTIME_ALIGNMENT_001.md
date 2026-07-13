# CUSTOMER_DEMAND_GOVERNANCE_RUNTIME_ALIGNMENT_001

## Stato

- `CAPABILITY_STATUS`: `IMPLEMENTED`
- `SOURCE_ID`: `customer_demand_registry`
- `RUNTIME_BINDING`: `TL_CHAT_READ_ONLY`
- `DEFAULT_POLICY`: `DENY`
- `DATABASE_WRITE`: `NONE`
- `PLANNER_ELIGIBLE`: `false`
- `AUTOMATIC_PROMOTION`: `false`

## Contratto consolidato

Il registro `memory/context_source_index.json` resta l'indice strutturale delle fonti. La voce `customer_demand_registry` è allineata al binding read-only reale e dichiara `runtime_enabled: true` esclusivamente per il binding dedicato.

L'autorizzazione eseguibile è separata in:

```text
memory/context_source_runtime_authorizations.json
```

La separazione impedisce che l'attivazione della singola fonte renda runtime l'intero indice documentale. La policy predefinita è `deny`.

Prima di aprire una connessione, `authorize_customer_demand_runtime` verifica congiuntamente:

- schema e unicità della registrazione;
- `kind: database_registry`;
- `access_mode: read_only`;
- origine strutturale `customer_demand`;
- insieme esatto dei cinque campi autorizzati;
- grant unico `tl_chat_readonly_runtime` abilitato;
- nessuna eleggibilità planner;
- nessuna promozione automatica;
- conferma TL obbligatoria.

Qualunque mismatch restituisce autorizzazione negata. Il binding produce `SOURCE_AUTHORIZED_BUT_UNAVAILABLE` e non chiama il reader.

## Provenienza canonica

Il reader restituisce:

- `source_id`;
- `structural_origin`;
- `retrieved_at` UTC ISO 8601;
- `runtime_binding: TL_CHAT_READ_ONLY`;
- `freshness: UNKNOWN`;
- `source_status`;
- `semantic_status: DA_VERIFICARE`;
- `confidence: DA_VERIFICARE`;
- `missing_data`.

## Limiti

- nessuna scrittura database;
- nessun nuovo campo;
- nessun importer o SMF;
- nessun planner, ordine o board state;
- nessuna attivazione di altre fonti;
- nessun accesso tramite il generic filesystem reader;
- nessuna promozione automatica a `CERTO`.

## Criteri di accettazione

- autorizzazione verificata prima della query;
- reader non invocato in caso di deny;
- source index e grant runtime coerenti;
- provenienza completa e deterministica;
- confidence canonica unica;
- test dedicati e guard repository verdi.
