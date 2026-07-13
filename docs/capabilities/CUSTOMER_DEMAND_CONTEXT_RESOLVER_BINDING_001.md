# CUSTOMER_DEMAND_CONTEXT_RESOLVER_BINDING_001

## Stato

- `CAPABILITY_STATUS`: `IMPLEMENTED_FOR_REVIEW`
- `SOURCE_ID`: `customer_demand_registry`
- `READER_BINDING`: `CONTEXT_RESOLVER_ONLY`
- `TL_CHAT_BINDING`: `OUT_OF_SCOPE`
- `API_BINDING`: `OUT_OF_SCOPE`
- `PLANNER_ELIGIBLE`: `false`
- `AUTOMATIC_PROMOTION`: `FORBIDDEN`

## Obiettivo unico

Collegare il reader read-only di `customer_demand_registry` al Context Resolver mediante un candidate adapter deterministico e testabile.

## File autorizzati

- `backend/app/services/customer_demand_context_resolver_binding.py`
- `backend/app/services/tl_chat_context_resolver.py`
- `backend/app/services/customer_demand_readonly_reader.py`
- `backend/tests/test_customer_demand_context_resolver_binding.py`
- `docs/capabilities/CUSTOMER_DEMAND_CONTEXT_RESOLVER_BINDING_001.md`

La correzione del reader è limitata alla compatibilità dei placeholder SQLite/PostgreSQL, necessaria perché `app.db.get_connection()` supporta entrambi i backend.

## Contratto del binding

Il binding:

- invoca esclusivamente il reader autorizzato;
- costruisce un solo `TLChatContextCandidate`;
- registra `customer_demand_registry` nella priorità del resolver;
- mantiene `confidence: DA_VERIFICARE`;
- mantiene `freshness: UNKNOWN` nel payload;
- forza `planner_eligible: false`;
- richiede conferma TL;
- impedisce `can_promote`;
- non espone endpoint o funzioni TL Chat;
- non modifica source index, database, importer o planner.

## Stati

Lettura riuscita, anche senza record:

```text
source_status: SOURCE_FOUND
```

Lookup valido senza record:

```text
records: []
missing_data: record_customer_demand_not_found
```

Errore del reader o database non disponibile:

```text
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
records: []
missing_data: customer_demand_reader_unavailable
```

Il dettaglio dell'errore database non viene esposto nel payload.

## Priorità

`customer_demand_registry` è collocata dopo le fonti autoritative `local_specs_metadata`, `article_summary`, `lifecycle_registry` e prima delle fonti preview.

La registrazione nella priorità non rende la fonte autoritativa e non consente promozione a `CERTO`.

## Prove

I test verificano:

- mapping reader → candidate → resolved context;
- nessuna promozione e nessuna eleggibilità planner;
- semantica distinta per record assente;
- mapping degli errori a `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- mancata esposizione del messaggio database;
- ordine di priorità rispetto a fonti autoritative e preview;
- adattamento locale dei placeholder SQLite.

## Fuori scope

- binding alla route TL Chat;
- modifica di `backend/app/api/tl_chat.py`;
- frontend;
- endpoint API;
- modifica del source index;
- nuovi importer;
- scritture database;
- planner, ordini, board state e viste ZAW.

## Criterio di chiusura

La capability è chiusa quando la slice resta nei cinque file autorizzati, il binding produce solo candidate read-only e Context Resolver output, e nessuna route TL Chat importa il nuovo binding.

## NEXT_MOVE

Dopo merge, eseguire una mappatura minima del punto di integrazione TL Chat senza implementarlo automaticamente.
