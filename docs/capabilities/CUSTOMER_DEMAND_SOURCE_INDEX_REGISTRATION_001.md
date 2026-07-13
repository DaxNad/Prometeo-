# CUSTOMER_DEMAND_SOURCE_INDEX_REGISTRATION_001

## Stato

- `CAPABILITY_STATUS`: `AUTHORIZED_FOR_REVIEW`
- `IMPLEMENTATION_STATUS`: `NOT_STARTED`
- `RUNTIME_STATUS`: `NOT_AUTHORIZED`
- `SOURCE_ID`: `customer_demand_registry`
- `TARGET_FILE`: `memory/context_source_index.json`
- `RUNTIME_ENABLED_REQUIRED`: `false`
- `READER_AUTHORIZED`: `NO`
- `QUERY_EXECUTION_AUTHORIZED`: `NO`
- `TEST_RUNTIME_AUTHORIZED`: `NO`
- `TL_CHAT_BINDING_AUTHORIZED`: `NO`

## 1. Obiettivo unico

Aprire una capability implementativa separata per la sola registrazione governata di:

```text
customer_demand_registry
```

in:

```text
memory/context_source_index.json
```

La futura patch dovrà mantenere:

```text
runtime_enabled: false
```

Questa capability non registra ancora la fonte. Definisce esclusivamente il perimetro implementativo da sottoporre a review prima della modifica del source index.

## 2. Autorità documentali

La capability dipende da:

- `docs/contracts/CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001.md`;
- `docs/contracts/CUSTOMER_DEMAND_RUNTIME_READONLY_PERIMETER_001.md`;
- `docs/capabilities/CUSTOMER_DEMAND_SOURCE_REGISTRATION_DATABASE_BOUNDARY_001.md`;
- `docs/PROMETEO_CONTEXT_SOURCE_INDEX_001.md`;
- `memory/context_source_index.json`.

In caso di conflitto prevale la regola più restrittiva.

## 3. Modifica autorizzabile nella futura patch

La futura implementazione potrà modificare esclusivamente:

```text
memory/context_source_index.json
```

aggiungendo una sola voce sotto `sources` con:

```text
id: customer_demand_registry
source_id: customer_demand_registry
kind: database_registry
structural_origin: customer_demand
access_mode: read_only
runtime_enabled: false
exists: true
```

La forma definitiva della voce dovrà rispettare la struttura già usata dall'indice e il relativo schema documentale.

## 4. Metadati minimi richiesti

La voce dovrà rappresentare almeno:

- identità logica della fonte;
- origine strutturale `customer_demand`;
- natura di copia derivata della domanda cliente;
- accesso futuro esclusivamente read-only;
- runtime disabilitato;
- cinque campi business autorizzati;
- semantica vincolante di `data_spedizione`;
- freshness iniziale `UNKNOWN`;
- divieto di promozione automatica a `CERTO`;
- dipendenze e domini vietati;
- allowed-for limitato a progettazione e futuro retrieval governato non attivo.

## 5. Campi business autorizzati

La registrazione dovrà limitare la futura esposizione a:

```text
articolo
codice_articolo
quantita
data_spedizione
priorita_cliente
```

Restano esclusi tutti gli altri campi, inclusi:

```text
id
note
created_at
order_id
residuo
stato avanzamento
dati planner
```

## 6. Semantica temporale

La voce dovrà dichiarare che:

```text
data_spedizione = customer_requested_date_recorded
```

Il campo non equivale a `due_date`, data pianificata, promessa, confermata, completata o spedita effettivamente.

## 7. Stato atteso dopo la futura registrazione

Dopo la sola modifica del source index, senza reader o runtime:

```text
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
runtime_enabled: false
```

La registrazione non deve produrre:

- `SOURCE_FOUND`;
- dati restituiti;
- accesso database;
- esecuzione SQL;
- binding resolver;
- esposizione TL Chat;
- promozione a `CERTO`.

## 8. Freshness e provenance

La registrazione dovrà impostare o descrivere:

```text
freshness: UNKNOWN
```

Il source index non deve contenere:

- timestamp inventati dell'ultimo import;
- URI o credenziali di connessione;
- path filesystem locali;
- path SMF o Excel;
- SQL libero;
- dati industriali reali.

## 9. Allowlist

Per la presente capability documentale è autorizzato esclusivamente:

```text
docs/capabilities/CUSTOMER_DEMAND_SOURCE_INDEX_REGISTRATION_001.md
```

Per la futura capability implementativa, dopo review esplicita, sarà autorizzabile esclusivamente:

```text
memory/context_source_index.json
```

## 10. Fuori scope

Sono vietati:

- reader o adapter;
- accesso al database;
- query SQL;
- test runtime;
- modifica di resolver o TL Chat;
- frontend;
- importer `import_customer_demand.py`;
- file SMF o `real_excel`;
- `production_orders`;
- `board_state`;
- planner e viste ZAW;
- migrazioni SQL;
- configurazioni e credenziali.

## 11. Criteri di accettazione

La capability è accettabile se il reviewer può verificare che:

1. esiste una sola futura modifica prevista;
2. il solo target è `memory/context_source_index.json`;
3. il source ID è esattamente `customer_demand_registry`;
4. `runtime_enabled` resta `false`;
5. i campi autorizzati restano cinque;
6. `data_spedizione` mantiene la semantica vincolante;
7. la freshness iniziale resta `UNKNOWN`;
8. non sono autorizzati reader, SQL, test runtime o TL Chat;
9. la sola registrazione conduce a `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
10. nessun dato sensibile o path fisico entra nell'indice.

## 12. Stop conditions

Il lavoro deve fermarsi se:

- il source ID differisce da `customer_demand_registry`;
- viene richiesto `runtime_enabled: true`;
- la modifica richiede più di `memory/context_source_index.json`;
- è necessario creare reader, query o test runtime;
- vengono introdotti path, credenziali o SQL;
- vengono coinvolti importer, SMF, planner, ordini o board state;
- la voce non rispetta la struttura dell'indice;
- una fase tenta di auto-autorizzare la patch successiva.

## 13. Non autorizzazioni

Questo documento non autorizza ancora:

- modifica di `memory/context_source_index.json`;
- registrazione effettiva della fonte;
- runtime;
- accesso database;
- query SQL;
- reader o adapter;
- test runtime;
- binding resolver o TL Chat.

## Verdetto documentale

```text
VERDICT: SOURCE_INDEX_REGISTRATION_CAPABILITY_OPENED
RUNTIME_IMPACT: NONE
SOURCE_INDEX_CHANGE: NONE
DATABASE_ACCESS: NONE
QUERY_EXECUTION: NONE
READER_CREATED: NO
TESTS_CREATED: NO
TL_CHAT_BINDING: NO
```

## NEXT_MOVE

Revisionare esclusivamente questa capability. Dopo `CAPABILITY_ACCEPTED`, aprire una patch separata che modifichi soltanto `memory/context_source_index.json` aggiungendo `customer_demand_registry` con `runtime_enabled: false`.
