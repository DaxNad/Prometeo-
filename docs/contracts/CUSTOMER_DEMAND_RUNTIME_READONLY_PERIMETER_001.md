# CUSTOMER_DEMAND_RUNTIME_READONLY_PERIMETER_001

## Stato

- `DOCUMENT_STATUS`: `PERIMETER_DEFINED`
- `RUNTIME_STATUS`: `NOT_AUTHORIZED`
- `IMPLEMENTATION_STATUS`: `NOT_STARTED`
- `SOURCE_ID`: `customer_demand_registry`
- `SOURCE_CONTRACT`: `docs/contracts/CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001.md`
- `ACCESS_MODE_FUTURE`: `READ_ONLY`
- `HUMAN_ACCEPTANCE_REQUIRED`: `true`

Questo documento definisce esclusivamente il perimetro della futura capability runtime read-only per `customer_demand_registry`.

Non registra il source ID, non abilita accesso al database, non autorizza query, non crea reader, adapter, test o binding TL Chat e non modifica alcun componente runtime.

## 1. Obiettivo unico

Definire una futura slice verticale minima capace di leggere, mediante un reader dedicato e governato, dati selezionati dalla tabella logica `customer_demand`, senza mutazioni e senza accesso diretto alla fonte SMF.

La futura slice dovrà consentire esclusivamente il recupero verificabile di dati di domanda cliente già presenti nel registry.

Non dovrà:

- importare o aggiornare dati;
- interrogare ordini operativi;
- derivare sequenze o priorità produttive;
- interpretare `data_spedizione` come data promessa, pianificata o consuntiva;
- promuovere automaticamente il risultato a `CERTO`;
- usare fallback verso file, path esterni, importer o servizi planner.

## 2. Identità e autorità della fonte

La futura fonte logica è:

```text
source_id: customer_demand_registry
structural_origin: customer_demand
authority_class: DERIVED_CUSTOMER_DEMAND_COPY
runtime_enabled: false
```

`customer_demand_registry` rappresenta una copia strutturata della domanda cliente già importata nel database.

Non è:

- la fonte fisica originaria;
- una prova che l'importazione sia recente;
- una conferma dell'esistenza di un ordine operativo;
- una fonte planner;
- una fonte di avanzamento, residuo, disponibilità o spedizione effettiva.

Il dato recuperato deve rimanere `DA_VERIFICARE` quando freshness o autorità non sono dimostrate da evidenze future esplicite.

## 3. Input contract futuro

Il reader futuro potrà accettare esclusivamente uno dei seguenti lookup:

| Input | Tipo | Regola |
|---|---|---|
| `articolo` | stringa normalizzata | Obbligatoria quando `codice_articolo` è assente. Match esatto. |
| `codice_articolo` | stringa normalizzata | Obbligatoria quando `articolo` è assente. Match esatto. |

Vincoli:

- almeno uno dei due identificativi deve essere presente;
- nessun lookup vuoto, parziale o wildcard;
- nessuna ricerca full-table;
- nessun filtro su priorità, quantità o data come input primario;
- nessun path, nome file, SQL libero o parametro di connessione in input;
- nessun payload proveniente direttamente dalla chat può diventare SQL;
- i valori devono essere validati e passati mediante parametri bindati.

Se entrambi gli identificativi sono presenti e producono risultati incoerenti, il reader deve fermarsi con stato ambiguo e non scegliere automaticamente un record.

## 4. Output contract futuro

Il reader futuro dovrà restituire una struttura deterministica contenente solo:

```text
source_id
source_status
semantic_status
confidence
lookup
records
retrieved_at
freshness
missing_data
limitations
```

Ogni elemento di `records` potrà contenere esclusivamente:

```text
articolo
codice_articolo
quantita
data_spedizione
priorita_cliente
```

Campi vietati nell'output:

- credenziali o URI di connessione;
- path filesystem;
- contenuti o metadati del file SMF;
- SQL eseguito;
- identificativi interni non autorizzati;
- campi di `production_orders`, `board_state` o planner;
- valori derivati non presenti nella fonte.

## 5. Semantica vincolante di `data_spedizione`

`data_spedizione` deve essere esposta con la seguente semantica:

```text
customer_requested_date_recorded
```

Il valore rappresenta la copia normalizzata della colonna sorgente `Data richiesta cliente` usata dall'importer corrente.

Non equivale a:

- `due_date`;
- data pianificata;
- data promessa;
- data confermata;
- data di completamento;
- data di spedizione effettiva.

La TL Chat dovrà presentarla come "data richiesta cliente registrata". Qualsiasi domanda che richieda una semantica diversa deve produrre `MISSING_DATA` per il dato non disponibile.

## 6. Boundary database futuro

Il futuro reader dovrà essere confinato a:

```text
database object: customer_demand
operation class: SELECT_ONLY
connection source: existing authorized application database boundary
```

Il boundary dovrà impedire:

- connessioni arbitrarie fornite dall'utente;
- accesso a database o file SQLite indicati tramite path esterno;
- apertura diretta di file SMF o Excel;
- bootstrap, migrazioni o creazione automatica di tabelle;
- chiamate a importer o adapter di acquisizione;
- query su oggetti diversi da `customer_demand`.

La modalità di connessione dovrà essere autorizzata da una capability runtime separata prima dell'implementazione.

## 7. Boundary SQL futuro

Saranno ammesse esclusivamente query `SELECT` parametrizzate con:

- proiezione limitata ai cinque campi business autorizzati;
- clausola `WHERE` su `articolo` e/o `codice_articolo`;
- match esatto;
- limite massimo esplicito sui record restituiti;
- ordinamento deterministico solo se necessario per stabilizzare l'output.

Sono vietati:

- `INSERT`;
- `UPDATE`;
- `DELETE`;
- `REPLACE`;
- `UPSERT`;
- DDL;
- `PRAGMA` mutanti;
- trigger;
- transazioni con effetti di scrittura;
- statement multipli;
- SQL costruito tramite concatenazione di input;
- join con altre tabelle o viste;
- subquery verso planner, ordini o board state.

Il reader non potrà invocare funzioni che eseguono scritture indirette o inizializzazione dello schema.

## 8. Freshness policy futura

La freshness deve essere distinta dal timestamp di lettura.

```text
retrieved_at: quando il reader ha letto il registry
freshness: quanto è recente e verificabile la copia importata
```

Stati minimi richiesti:

| Stato freshness | Significato | Trattamento |
|---|---|---|
| `UNKNOWN` | Nessuna evidenza affidabile sull'ultimo import. | Restituire il dato come `DA_VERIFICARE`. |
| `MISSING` | Il riferimento di freshness richiesto non esiste. | Inserire il gap in `missing_data`; non presentare il dato come corrente. |
| `STALE` | La copia supera una soglia futura autorizzata. | Segnalare non corrente; vietato uso operativo. |
| `VERIFIED` | Esiste un riferimento verificabile conforme a una policy futura. | Conservare evidenza e criterio; nessuna promozione automatica a `CERTO`. |

Questo documento non definisce una soglia temporale numerica perché il registry corrente non dispone ancora di una policy di import freshness autorizzata. La soglia dovrà essere definita e approvata prima dell'attivazione runtime.

## 9. Source status futuro

Il comportamento dovrà rispettare almeno i seguenti stati:

| Condizione | `source_status` | Esito utente |
|---|---|---|
| Source ID non registrato | `SOURCE_MISSING` | `MISSING_DATA` |
| Source ID autorizzato ma reader/runtime disabilitato | `SOURCE_AUTHORIZED_BUT_UNAVAILABLE` | `MISSING_DATA` con indisponibilità dichiarata |
| Connessione autorizzata non disponibile | `SOURCE_AUTHORIZED_BUT_UNAVAILABLE` | Nessun fallback |
| Lookup valido senza record | `SOURCE_FOUND` (o stato canonico equivalente di fonte disponibile) con `records: []` e `missing_data: record_customer_demand_not_found` | `MISSING_DATA` |
| Risultati incoerenti per identificativi forniti | `SOURCE_AMBIGUOUS` | Nessun record scelto automaticamente |
| Dato presente con freshness sconosciuta | stato di fonte disponibile + `semantic_status: DA_VERIFICARE` | Dato con limite esplicito |
| Richiesta fuori semantica o fuori campi autorizzati | stato di stop governato | `MISSING_DATA` per il dato richiesto |

I nomi definitivi dovranno riutilizzare gli stati già governati dal resolver. La futura patch non potrà introdurre sinonimi se esiste già uno stato canonico.

## 10. Confidence e semantic status

La confidence dovrà descrivere la qualità del recupero, non l'autorità operativa del dato.

Regole:

- match esatto e record leggibile non implicano `CERTO`;
- freshness `UNKNOWN`, `MISSING` o `STALE` impedisce qualunque classificazione equivalente a certezza operativa;
- dati presenti ma non verificati devono essere `DA_VERIFICARE`;
- nessun dato può essere inferito da altri campi;
- record multipli o incoerenti devono abbassare la confidence o produrre stop;
- la TL Chat deve mostrare limiti e dati mancanti.

## 11. Strategia di prova della non mutazione

La futura capability dovrà includere prove verificabili che il reader non muta il database.

Piano minimo richiesto:

1. creare un database di test isolato con schema e record noti;
2. acquisire hash o snapshot logico prima della lettura;
3. eseguire il reader tramite il solo entry point autorizzato;
4. acquisire hash o snapshot logico dopo la lettura;
5. verificare uguaglianza completa di schema e contenuti;
6. verificare che nessun importer o funzione mutante sia stato chiamato;
7. verificare che la query appartenga alla classe `SELECT_ONLY`;
8. verificare che input malevoli non producano statement aggiuntivi;
9. verificare assenza di accesso a file SMF e path esterni;
10. verificare che errori e fonte indisponibile non attivino fallback mutanti.

Una prova basata soltanto sull'assenza di eccezioni non è sufficiente.

## 12. File allowlist della futura patch

La futura implementazione potrà modificare esclusivamente file esplicitamente nominati nella capability runtime autorizzativa.

Allowlist documentale proposta, da confermare prima della patch:

```text
un nuovo reader dedicato sotto backend/app/ o tools/
un nuovo test target dedicato
memory/context_source_index.json, solo se autorizzato nella stessa capability
eventuale binding TL Chat minimo, solo in una slice successiva separata
```

Il percorso esatto del reader e dei test non è autorizzato da questo documento e dovrà essere verificato sul repository prima dell'apertura della capability.

File e domini vietati nella futura prima patch reader:

```text
backend/app/importers/import_customer_demand.py
file SMF o real_excel
production_orders
board_state
viste ZAW o sequence planner
servizi planner
migrazioni SQL esistenti
configurazioni con credenziali
frontend o interfaccia TL Chat
```

La registrazione del source ID, il reader e il binding TL Chat non devono essere accorpati automaticamente. L'ordine delle slice dovrà essere autorizzato esplicitamente.

## 13. Ordine futuro delle capability

Ordine minimo raccomandato:

1. autorizzazione umana di questo perimetro;
2. capability per registrazione governata del source ID e boundary database;
3. capability per reader read-only con test di non mutazione;
4. capability per binding minimo al resolver;
5. capability separata per esposizione TL Chat e test end-to-end.

Ogni passaggio richiede una nuova autorizzazione. Il completamento di una fase non autorizza automaticamente la successiva.

## 14. Criterio di accettazione del perimetro

Il perimetro è accettabile solo se un reviewer può determinare senza ambiguità:

- quale input è ammesso;
- quali campi possono essere letti;
- quale semantica possiede `data_spedizione`;
- quale oggetto database è accessibile;
- quali query sono ammesse e vietate;
- come sono rappresentati source status, semantic status e confidence;
- come vengono trattate freshness sconosciuta, assente o scaduta;
- come sarà provata la non mutazione;
- quali file e domini restano fuori scope;
- che nessun runtime è autorizzato da questo documento.

## 15. Stop conditions

Il lavoro futuro deve fermarsi se:

- il source ID non è stato autorizzato;
- il boundary di connessione non è esplicito;
- è necessario accedere al file SMF;
- è necessario invocare l'importer;
- la query richiede tabelle o viste diverse da `customer_demand`;
- non è possibile garantire `SELECT_ONLY`;
- il reader può inizializzare o modificare lo schema;
- freshness e timestamp di lettura vengono confusi;
- `data_spedizione` viene reinterpretata come `due_date`;
- viene richiesta una decisione di pianificazione;
- la patch supera l'allowlist autorizzata;
- manca una prova di non mutazione;
- viene tentato un fallback verso path, file o fonti non governate;
- una fase tenta di auto-autorizzare la successiva.

## 16. Non autorizzazioni

Questo documento non autorizza:

- modifica di `memory/context_source_index.json`;
- accesso al database;
- esecuzione di query SQL;
- creazione di reader o adapter;
- modifica o creazione di test;
- binding con resolver o TL Chat;
- accesso a SMF, importer, planner, ordini o board state;
- modifiche runtime;
- apertura automatica della capability successiva.

## 17. Gate umano

Il perimetro diventa utilizzabile come base per la capability successiva solo dopo un'accettazione umana esplicita.

Esiti ammessi della review:

```text
PERIMETER_ACCEPTED
ONE_REQUIRED_CHANGE
STOP
```

Senza `PERIMETER_ACCEPTED`, lo stato rimane:

```text
RUNTIME_STATUS: NOT_AUTHORIZED
NEXT_RUNTIME_ACTION: NONE
```

## Verdetto documentale

```text
VERDICT: RUNTIME_READONLY_PERIMETER_DEFINED
RUNTIME_IMPACT: NONE
SOURCE_INDEX_CHANGE: NONE
DATABASE_ACCESS: NONE
READER_CREATED: NO
TESTS_CREATED: NO
TL_CHAT_BINDING: NO
```

## NEXT_MOVE

Sottoporre esclusivamente questo perimetro ad accettazione umana. Non aprire o implementare la capability runtime finché l'esito non è `PERIMETER_ACCEPTED`.
