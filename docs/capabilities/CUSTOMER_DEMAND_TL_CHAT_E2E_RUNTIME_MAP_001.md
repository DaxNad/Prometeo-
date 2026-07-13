# CUSTOMER_DEMAND_TL_CHAT_E2E_RUNTIME_MAP_001

## Stato

- `MAP_STATUS`: `COMPLETED_READ_ONLY`
- `RUNTIME_CHANGE`: `NONE`
- `DATABASE_WRITE`: `NONE`
- `SOURCE_ID`: `customer_demand_registry`
- `TARGET_ROUTE`: `/tl/chat`
- `CURRENT_BINDING`: `ACTIVE_READ_ONLY`
- `GOVERNANCE_ALIGNMENT`: `INCOMPLETE`

## Obiettivo

Ricostruire il percorso reale, osservato su `main`, dal messaggio TL Chat fino alla query read-only su `customer_demand`, distinguendo comportamento implementato, garanzie presenti e lacune residue.

## Percorso end-to-end osservato

```text
POST /tl/chat
    ↓
TLChatRequest.question + TLChatRequest.context.article
    ↓
_build_contract_response(payload)
    ↓
article = context.article normalizzato oppure estratto dalla domanda
    ↓
handler specialistici local_specs_metadata
    ↓
_question_asks_customer_demand(question)
    ↓ true
_response_from_customer_demand_context(article)
    ↓
resolve_customer_demand_context(articolo=article)
    ↓
build_customer_demand_candidate(...)
    ↓
read_customer_demand(articolo=article, limit=50)
    ↓
get_connection()
    ↓
SELECT articolo, codice_articolo, quantita, data_spedizione, priorita_cliente
FROM customer_demand
WHERE articolo = parametro
ORDER BY data_spedizione, codice_articolo
LIMIT parametro
    ↓
_normalize(row)
    ↓
TLChatContextCandidate
    ↓
resolve_tl_chat_context(...)
    ↓
TLChatResolvedContext
    ↓
TLChatResponse
```

## 1. Ingresso e selezione articolo

La route usa:

```python
article = _normalize_article(payload.context.article) or _extract_article_from_question(question)
```

Ordine deterministico:

1. articolo esplicito nel contesto;
2. fallback di estrazione dalla domanda;
3. nessuna invocazione customer-demand se l'articolo non è disponibile.

## 2. Intent gate

Il gate `_question_asks_customer_demand` riconosce termini espliciti relativi a:

- quantità cliente o quantità richiesta;
- data richiesta dal cliente;
- priorità cliente;
- domanda o richiesta cliente.

Il gate è collocato dopo gli handler specialistici di `local_specs_metadata` e prima di `article_summary` e `lifecycle_registry`, evitando i return anticipati generici.

### Limite osservato

Il blocco `forbidden_only_terms` non modifica realmente il risultato: la funzione restituisce comunque `False` quando nessun termine esplicito è presente. È ridondante ma non altera il comportamento.

## 3. Binding route → resolver

La route invoca direttamente:

```python
resolve_customer_demand_context(articolo=article)
```

Il binding:

1. costruisce un solo candidate `customer_demand_registry`;
2. chiama il reader con `articolo`, `codice_articolo=None`, `limit=50`;
3. cattura qualsiasi eccezione;
4. converte l'errore in `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
5. mantiene `planner_eligible=False` e conferma TL obbligatoria.

Il tipo tecnico dell'eccezione resta nel payload interno ma non viene esposto dal rendering TL Chat.

## 4. Reader SQL read-only

Il reader autorizza esattamente un lookup:

- `articolo`; oppure
- `codice_articolo`.

La route usa soltanto `articolo`.

Garanzie osservate:

- query SQL costante;
- parametri separati dal testo SQL;
- massimo 100 record, 50 nella route;
- cinque campi autorizzati;
- compatibilità placeholder PostgreSQL/SQLite;
- sessione read-only quando `set_session` è disponibile;
- nessun `commit`;
- `rollback` e chiusura delle risorse nel `finally`.

## 5. Normalizzazione e semantica

Ogni record espone soltanto:

```text
articolo
codice_articolo
quantita
data_spedizione
priorita_cliente
```

Date e datetime sono convertiti in ISO 8601.

Il payload reader dichiara:

```text
source_status: SOURCE_FOUND
freshness: UNKNOWN
semantic_status: DA_VERIFICARE
confidence: LOW_UNTIL_FRESHNESS_VERIFIED
```

Un lookup valido senza record mantiene `SOURCE_FOUND` e aggiunge:

```text
record_customer_demand_not_found
```

## 6. Resolver

`resolve_tl_chat_context` riceve un solo candidate. La priorità numerica `35` è quindi formalmente presente ma non determina una competizione tra fonti in questo binding dedicato.

Il resolver impedisce la promozione perché:

- il candidate richiede conferma TL;
- la confidence è `DA_VERIFICARE` nel candidate;
- `planner_eligible` resta `false`;
- `can_promote` resta `false`.

## 7. Rendering TL Chat

### Record presenti

La risposta mostra esclusivamente i cinque campi autorizzati e chiarisce che `data_spedizione` è:

```text
data richiesta dal cliente registrata nella fonte
```

Non è descritta come data confermata, promessa al cliente, scadenza interna o piano di produzione.

### Record assente

```text
source_status: SOURCE_FOUND
missing_data: record_customer_demand_not_found
```

### Fonte indisponibile

```text
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
missing_data: customer_demand_reader_unavailable
```

La risposta non espone dettagli tecnici del database.

## Lacune deterministiche ricostruite

### GAP-01 — Source index non allineato al runtime reale

`memory/context_source_index.json` dichiara ancora:

```text
runtime_enabled: false
allowed_for: future_governed_retrieval, source_registration_only
expected_source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
nessun reader, query o binding runtime autorizzato
```

Il runtime reale, invece, invoca il reader dalla route TL Chat. Il source index non viene consultato prima della query.

**Classificazione:** `GOVERNANCE_CONTRADICTION`.

**Impatto:** il comportamento applicativo è read-only e testato, ma la fonte di governance descrive ancora lo stato precedente all'attivazione del binding.

### GAP-02 — `runtime_binding` del reader non rappresenta lo stato corrente

Il payload di `read_customer_demand` restituisce:

```text
runtime_binding: UNBOUND
```

La route TL Chat è ora realmente collegata al reader.

**Classificazione:** `STALE_PROVENANCE_METADATA`.

### GAP-03 — Provenienza richiesta ma non prodotta integralmente

Il source index richiede:

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

Il reader non produce `structural_origin` né `retrieved_at`.

**Classificazione:** `PROVENANCE_INCOMPLETE`.

### GAP-04 — Gate di autorizzazione non centralizzato

La route importa e chiama direttamente il binding dedicato. Non esiste un controllo runtime che verifichi, prima della query:

- presenza della fonte nel source index;
- `access_mode=read_only`;
- autorizzazione esplicita del binding;
- stato di attivazione coerente.

**Classificazione:** `AUTHORIZATION_GATE_MISSING`.

### GAP-05 — Stato e confidence duplicati tra livelli

Il reader produce `LOW_UNTIL_FRESHNESS_VERIFIED`; il candidate sovrascrive la confidence a `DA_VERIFICARE`; il rendering usa ancora `DA_VERIFICARE` hardcoded.

La semantica finale è prudente e corretta, ma la catena non conserva una singola confidence canonica.

**Classificazione:** `SEMANTIC_DUPLICATION`.

## Decisione della mappatura

```text
END_TO_END_PATH: FUNCTIONAL
READ_ONLY_ENFORCEMENT: PRESENT
ROUTE_TEST_COVERAGE: PRESENT
RUNTIME_MUTATION: NONE
GOVERNANCE_ALIGNMENT: NOT_COMPLETE
```

La capability customer-demand è funzionale e protetta contro scritture, ma non è ancora chiusa come percorso governato completo finché source index, metadata di provenienza e gate di autorizzazione non descrivono e controllano lo stesso stato reale.

## Perimetro della futura correzione

La futura vertical slice deve essere unica e limitata a:

1. definire uno stato canonico di attivazione read-only per `customer_demand_registry`;
2. rendere source index e reader coerenti con il binding realmente implementato;
3. aggiungere `structural_origin` e `retrieved_at` al payload;
4. introdurre un gate deterministico prima della query;
5. preservare query, cinque campi, intent gate e rendering esistenti;
6. non aggiungere scritture, planner, ordini, SMF o nuove fonti.

## Stop conditions

Fermarsi se la correzione richiede:

- scritture database;
- nuovi campi customer-demand;
- attivazione di altre fonti;
- planner o decisioni operative;
- modifica dell'importer;
- uso di file reali o SMF;
- promozione automatica a `CERTO`.
