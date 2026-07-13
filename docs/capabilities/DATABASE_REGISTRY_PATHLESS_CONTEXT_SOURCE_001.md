# DATABASE_REGISTRY_PATHLESS_CONTEXT_SOURCE_001

## Stato

- `CAPABILITY_STATUS`: `IMPLEMENTED`
- `IMPLEMENTATION_STATUS`: `COMPLETED`
- `RUNTIME_ACTIVATION`: `NO`
- `DATABASE_ACCESS`: `NONE`
- `DATABASE_WRITE`: `NONE`

## Contratto consolidato

Una fonte con `kind: database_registry` è una fonte logica e non una fonte file.

- la registrazione non richiede un path filesystem;
- un path esplicito sulla fonte logica viene rifiutato;
- il metadata reader espone `locator_mode: logical_registry`;
- il runtime adapter consente esclusivamente `read_metadata`;
- `read_excerpt` termina con `SOURCE_EXCERPT_UNSUPPORTED`;
- `runtime_enabled: false` resta obbligatorio;
- `access_mode: read_only` resta obbligatorio;
- nessuna connessione database viene aperta da questa capability;
- nessuna fonte viene attivata automaticamente.

## Compatibilità

Le fonti file-backed continuano a richiedere un path relativo governato sotto `docs/` o `memory/`. Traversal, path assoluti e prefissi vietati restano bloccati.

Per compatibilità con i consumer metadata esistenti, il metadata reader produce un locator virtuale sotto `memory/logical_registry/`; tale valore non viene risolto o aperto come file ed è accompagnato da `locator_mode: logical_registry`.

## Criteri di accettazione

- il source index reale non rifiuta `customer_demand_registry`;
- metadata pathless disponibile senza accesso filesystem;
- excerpt esplicitamente vietato;
- file-backed source policy invariata;
- full repository guards verdi;
- nessuna attivazione runtime o mutazione.
