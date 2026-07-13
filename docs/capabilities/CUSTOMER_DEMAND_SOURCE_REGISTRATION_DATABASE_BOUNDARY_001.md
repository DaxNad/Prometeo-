# CUSTOMER_DEMAND_SOURCE_REGISTRATION_DATABASE_BOUNDARY_001

## Stato

- `CAPABILITY_STATUS`: `AUTHORIZED_DOCUMENTAL_ONLY`
- `RUNTIME_STATUS`: `NOT_AUTHORIZED`
- `IMPLEMENTATION_STATUS`: `NOT_STARTED`
- `SOURCE_ID`: `customer_demand_registry`
- `SOURCE_CONTRACT`: `docs/contracts/CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001.md`
- `RUNTIME_PERIMETER`: `docs/contracts/CUSTOMER_DEMAND_RUNTIME_READONLY_PERIMETER_001.md`
- `SOURCE_REGISTRATION_AUTHORIZED`: `YES_DOCUMENTAL_ONLY`
- `DATABASE_BOUNDARY_AUTHORIZED`: `YES_DOCUMENTAL_ONLY`
- `READER_AUTHORIZED`: `NO`
- `QUERY_EXECUTION_AUTHORIZED`: `NO`
- `TESTS_AUTHORIZED`: `NO`
- `TL_CHAT_BINDING_AUTHORIZED`: `NO`

## 1. Obiettivo unico

Autorizzare esclusivamente la definizione e la futura implementazione separata di:

1. registrazione governata del source ID logico `customer_demand_registry`;
2. boundary applicativo read-only verso l'oggetto database `customer_demand`.

Questa capability non autorizza ancora un reader, l'esecuzione di query, test, binding con il resolver o esposizione nella TL Chat.

## 2. Autorità documentali

La capability dipende obbligatoriamente da:

- `docs/contracts/CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001.md`;
- `docs/contracts/CUSTOMER_DEMAND_RUNTIME_READONLY_PERIMETER_001.md`.

In caso di conflitto prevale la regola più restrittiva.

Questa capability non modifica la semantica della fonte e non amplia i campi ammessi.

## 3. Source ID autorizzato

L'unico source ID autorizzato è:

```text
customer_demand_registry
```

Identità vincolante:

```text
source_id: customer_demand_registry
structural_origin: customer_demand
authority_class: DERIVED_CUSTOMER_DEMAND_COPY
access_mode: READ_ONLY
runtime_enabled_initial: false
```

La registrazione futura dovrà dichiarare esplicitamente che:

- la fonte è una copia strutturata derivata;
- non è la fonte fisica originaria;
- non prova freshness, conferma ordine o stato operativo;
- non autorizza planner, sequenziamento o decisioni produttive;
- nessun dato può essere promosso automaticamente a `CERTO`.

## 4. Registrazione nel source index

La futura patch di registrazione potrà modificare esclusivamente la voce pertinente in:

```text
memory/context_source_index.json
```

La voce dovrà contenere almeno:

```text
source_id
source_type
structural_origin
authority_class
access_mode
runtime_enabled
allowed_fields
forbidden_dependencies
freshness_policy
semantic_status_policy
provenance_requirements
```

Valori minimi richiesti:

```text
source_id: customer_demand_registry
source_type: database_registry
structural_origin: customer_demand
access_mode: READ_ONLY
runtime_enabled: false
```

La registrazione non deve contenere:

- URI o credenziali di connessione;
- path filesystem locali;
- path SMF o Excel;
- SQL libero;
- riferimenti a `production_orders`, `board_state`, planner o viste ZAW;
- fallback verso importer o file esterni.

## 5. Campi autorizzati

La registrazione dovrà limitare la futura esposizione ai soli campi:

```text
articolo
codice_articolo
quantita
data_spedizione
priorita_cliente
```

Non sono autorizzati ulteriori campi business o tecnici.

In particolare restano esclusi:

- `id`;
- `note`;
- `created_at`;
- identificativi ordine;
- stato avanzamento;
- residuo;
- dati planner;
- campi di `production_orders` o `board_state`.

## 6. Semantica temporale vincolante

`data_spedizione` deve essere descritta come:

```text
customer_requested_date_recorded
```

Rappresenta la copia della data richiesta cliente registrata nella tabella `customer_demand`.

Non equivale a:

- `due_date`;
- data promessa;
- data pianificata;
- data confermata;
- data di completamento;
- data di spedizione effettiva.

La registrazione non può introdurre sinonimi che ne amplino l'autorità.

## 7. Boundary database autorizzato

Il boundary futuro deve essere confinato a:

```text
application_database_boundary: existing_authorized_application_database
allowed_object: customer_demand
operation_class: SELECT_ONLY
connection_input_from_user: forbidden
external_database_path: forbidden
schema_bootstrap: forbidden
migration_execution: forbidden
```

Il boundary dovrà impedire tecnicamente:

- connessioni arbitrarie;
- database indicati tramite input utente;
- path SQLite esterni;
- apertura di file SMF o Excel;
- inizializzazione o creazione automatica dello schema;
- accesso a oggetti diversi da `customer_demand`;
- chiamate a importer o adapter di acquisizione;
- scritture dirette o indirette.

## 8. Operazioni consentite e vietate

Questa capability autorizza soltanto la definizione del boundary per future operazioni:

```text
SELECT_ONLY
```

Non autorizza l'esecuzione di alcuna query in questa slice.

Restano vietati:

- `INSERT`;
- `UPDATE`;
- `DELETE`;
- `REPLACE`;
- `UPSERT`;
- DDL;
- trigger;
- statement multipli;
- `PRAGMA` mutanti;
- transazioni con effetti di scrittura;
- join con altre tabelle o viste;
- subquery verso planner, ordini o board state;
- SQL costruito concatenando input.

## 9. Stati governati

Dopo la sola registrazione con runtime disabilitato, lo stato atteso sarà:

```text
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
runtime_enabled: false
```

Prima della registrazione lo stato resta:

```text
source_status: SOURCE_MISSING
```

La registrazione non deve produrre:

- `SOURCE_FOUND`;
- disponibilità runtime;
- dati restituiti;
- promozione a `CERTO`.

Tali esiti richiedono reader e binding separatamente autorizzati.

## 10. Freshness e provenance

La registrazione dovrà indicare che la freshness iniziale è:

```text
UNKNOWN
```

La sola registrazione non definisce una soglia temporale e non rende il dato corrente.

La provenance futura dovrà includere almeno:

```text
source_id
structural_origin
retrieved_at
freshness
source_status
semantic_status
confidence
missing_data
```

Il timestamp di lettura non può essere usato come prova di freshness della copia importata.

## 11. File allowlist della futura patch

La futura patch autorizzata da questa capability potrà modificare esclusivamente:

```text
memory/context_source_index.json
un eventuale modulo minimo di boundary database già esistente, solo se identificato e nominato esplicitamente dopo preflight
un test documentale o statico della registrazione, solo in capability successiva
```

Poiché il percorso esatto del boundary applicativo non è ancora verificato, questa capability non autorizza oggi modifiche a file runtime.

Per la presente consegna documentale è autorizzato esclusivamente:

```text
docs/capabilities/CUSTOMER_DEMAND_SOURCE_REGISTRATION_DATABASE_BOUNDARY_001.md
```

## 12. File e domini vietati

Restano fuori scope:

```text
backend/app/importers/import_customer_demand.py
backend/app/api_production.py
production_orders
board_state
viste ZAW o sequence planner
servizi planner
file SMF
real_excel
frontend
TL Chat
resolver
reader o adapter
migrazioni SQL
configurazioni con credenziali
```

## 13. Criteri per la futura patch di registrazione

Una futura capability implementativa dovrà definire prima della modifica:

1. file esatto da modificare;
2. struttura esatta della nuova voce nel source index;
3. validazione JSON o schema applicabile;
4. prova che `runtime_enabled` resti `false`;
5. prova che nessun path, credenziale o SQL venga registrato;
6. prova che non sia possibile raggiungere SMF, importer, planner o board state;
7. comportamento del resolver dopo la sola registrazione;
8. assenza di reader, query e dati restituiti;
9. rollback documentato della voce registrata.

## 14. Criterio di accettazione

La capability è accettabile se un reviewer può determinare senza ambiguità:

- quale source ID può essere registrato;
- quale origine strutturale rappresenta;
- quali campi sono autorizzati;
- quale semantica possiede `data_spedizione`;
- quale oggetto database potrà essere raggiunto;
- che il boundary è esclusivamente read-only;
- che `runtime_enabled` deve restare `false`;
- che nessun reader o query è autorizzato;
- che la sola registrazione produce `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- quali file e domini restano vietati.

## 15. Stop conditions

Il lavoro deve fermarsi se:

- il source ID differisce da `customer_demand_registry`;
- viene richiesta una fonte fisica o un path SMF;
- il boundary database non è identificabile senza accesso arbitrario;
- è necessario creare o eseguire query;
- è necessario creare un reader;
- viene richiesto `runtime_enabled: true`;
- vengono richiesti test runtime;
- viene richiesto binding con resolver o TL Chat;
- vengono coinvolti planner, ordini operativi, board state o viste ZAW;
- la patch richiede modifiche fuori allowlist;
- una fase tenta di autorizzare automaticamente la successiva.

## 16. Non autorizzazioni

Questa capability non autorizza:

- modifica immediata di `memory/context_source_index.json`;
- implementazione del boundary database;
- accesso al database;
- esecuzione di query SQL;
- creazione di reader o adapter;
- creazione o modifica di test;
- binding con resolver o TL Chat;
- modifica di frontend;
- apertura automatica della capability successiva.

## 17. Verdetto documentale

```text
VERDICT: SOURCE_REGISTRATION_DATABASE_BOUNDARY_AUTHORIZED_DOCUMENTALLY
RUNTIME_IMPACT: NONE
SOURCE_INDEX_CHANGE: NONE
DATABASE_ACCESS: NONE
QUERY_EXECUTION: NONE
READER_CREATED: NO
TESTS_CREATED: NO
TL_CHAT_BINDING: NO
```

## NEXT_MOVE

Sottoporre esclusivamente questa capability a review. Dopo accettazione umana, aprire una capability implementativa separata per la sola registrazione di `customer_demand_registry` con `runtime_enabled: false`.