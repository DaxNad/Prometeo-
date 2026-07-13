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

`memory/context_source_index.json` resta integralmente metadata-only. La voce `customer_demand_registry` mantiene `runtime_enabled: false` e descrive soltanto registrazione, origine, campi e policy semantica.

L'autorizzazione eseguibile è separata in:

```text
memory/context_source_runtime_authorizations.json
```

Questa separazione impedisce che una fonte dedicata renda runtime l'indice documentale o il generic filesystem reader. Il grant ha policy predefinita `deny` e abilita esclusivamente `tl_chat_readonly_runtime`.

Prima di aprire una connessione, `authorize_customer_demand_runtime` verifica congiuntamente:

- schema e unicità della registrazione metadata-only;
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
- source index metadata-only e grant runtime coerenti;
- provenienza completa e deterministica;
- confidence canonica unica;
- test dedicati e guard repository verdi.
