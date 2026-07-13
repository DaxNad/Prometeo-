# CUSTOMER_DEMAND_TL_CHAT_INTEGRATION_MAP_001

## Stato

- `DOCUMENT_STATUS`: `MAPPED_FOR_REVIEW`
- `IMPLEMENTATION_STATUS`: `NOT_STARTED`
- `RUNTIME_BINDING`: `NOT_AUTHORIZED`
- `SOURCE_ID`: `customer_demand_registry`
- `TARGET_ROUTE`: `backend/app/api/tl_chat.py`
- `TARGET_DISPATCHER`: `_build_contract_response`

## Obiettivo unico

Mappare il punto esatto in cui una futura capability potrà collegare il binding read-only `customer_demand_registry` alla route TL Chat, senza introdurre in questa slice alcun import, chiamata runtime, risposta o test eseguibile.

## Fonti osservate

- `backend/app/api/tl_chat.py`
- `backend/app/services/customer_demand_context_resolver_binding.py`
- `backend/app/services/tl_chat_context_resolver.py`
- `backend/app/services/customer_demand_readonly_reader.py`
- `backend/tests/test_tl_chat_contract.py`

## Punto esatto di integrazione

Il punto di integrazione futuro è dentro:

```python
def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
```

nel ramo:

```python
if article:
```

La chiamata futura deve essere collocata:

1. dopo il tentativo `article_summary_response = _response_from_article_summary(article)`;
2. dopo il controllo `lifecycle_payload = lifecycle.get(article)` e il relativo return;
3. prima di `_load_spec_intake_preview(article)`;
4. prima di `_response_from_preview_profile(article)`;
5. prima del fallback `ContextSourceReaderAdapter` generico;
6. prima della risposta finale `SOURCE_MISSING`.

Posizione schematica:

```text
local_specs_metadata
    ↓
article_summary
    ↓
lifecycle_registry
    ↓
[FUTURE customer_demand_registry intent gate + resolver binding]
    ↓
spec_intake_preview
    ↓
preview_profile
    ↓
context_source_reader_adapter
    ↓
missing
```

Questa posizione è coerente con `SOURCE_PRIORITY`, dove `customer_demand_registry` segue le fonti autoritative e precede le fonti preview.

## Import futuro previsto

Una capability successiva potrà autorizzare esclusivamente un import dalla service già consolidata:

```python
from app.services.customer_demand_context_resolver_binding import (
    resolve_customer_demand_context,
)
```

Questo documento non aggiunge l'import.

## Gate di intent necessario

Il reader non deve essere invocato per ogni domanda contenente un articolo. Prima della chiamata serve un gate deterministico dedicato alle domande sulla domanda cliente, ad esempio una funzione privata nella route con responsabilità limitata:

```text
_question_asks_customer_demand(question) -> bool
```

Il nome è proposto, non ancora autorizzato come simbolo runtime.

Il gate futuro dovrà riconoscere esclusivamente richieste compatibili con i campi autorizzati:

- quantità richiesta;
- data richiesta dal cliente;
- priorità cliente;
- presenza di domanda cliente per articolo o codice articolo.

Non dovrà interpretare `data_spedizione` come:

- scadenza interna;
- data confermata di spedizione;
- promessa al cliente;
- piano o sequenza di produzione.

## Input futuro

La route dispone già di:

```text
article = normalize(context.article) oppure estrazione dalla domanda
```

Per il primo vertical slice futuro, il lookup autorizzabile è:

```text
resolve_customer_demand_context(articolo=article)
```

L'uso di `codice_articolo` richiede una distinzione esplicita dell'intento o del tipo di identificatore; non deve essere dedotto automaticamente nella prima slice.

## Mapping dell'output

Il binding restituisce `TLChatResolvedContext`. Una futura funzione di rendering dedicata dovrà trasformarlo in `TLChatResponse` senza perdere:

- `selected_source` → `source`;
- `source_status`;
- `confidence`;
- `payload.semantic_status` → `semantic_status`;
- `payload.missing_data` → `missing_data`;
- `requires_tl_confirmation` → `requires_confirmation`;
- `planner_eligible: false`;
- `can_promote: false`.

Il rendering dovrà esporre soltanto i cinque campi autorizzati presenti in `records`:

- `articolo`;
- `codice_articolo`;
- `quantita`;
- `data_spedizione`;
- `priorita_cliente`.

## Comportamenti richiesti alla capability futura

### Record trovati

```text
source: customer_demand_registry
source_status: SOURCE_FOUND
confidence: DA_VERIFICARE
semantic_status: DA_VERIFICARE
requires_confirmation: true
```

La risposta deve definire `data_spedizione` come data richiesta dal cliente registrata nella fonte.

### Lookup valido senza record

```text
source_status: SOURCE_FOUND
records: []
missing_data: record_customer_demand_not_found
```

Non deve diventare `SOURCE_MISSING`.

### Reader o database non disponibile

```text
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
missing_data: customer_demand_reader_unavailable
```

Il dettaglio tecnico dell'errore non deve essere esposto nella risposta TL.

## File futuri minimi

Una futura slice implementativa dovrebbe essere limitata a:

- `backend/app/api/tl_chat.py`;
- `backend/tests/test_tl_chat_contract.py` oppure un nuovo test route strettamente dedicato;
- un documento capability di implementazione.

Non è necessario modificare reader, resolver, source index o schema database salvo blocker verificabile.

## Test futuri minimi

- domanda quantità cliente con articolo → usa `customer_demand_registry`;
- domanda data cliente → chiarisce la semantica non confermata;
- domanda non relativa alla domanda cliente → reader non invocato;
- record assente → `SOURCE_FOUND` con `missing_data` specifico;
- reader indisponibile → `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- fonte autoritativa già risolutiva → non viene scavalcata;
- nessuna promozione a `CERTO`;
- nessuna eleggibilità planner;
- nessun dettaglio database nella risposta.

## Stop conditions

La capability futura deve fermarsi se:

- richiede accesso a campi oltre i cinque autorizzati;
- richiede interpretazione di `data_spedizione` come data confermata;
- richiede scritture o aggiornamenti database;
- richiede modifiche planner, ordini o board state;
- richiede invocazione del reader per tutte le domande articolo senza intent gate;
- richiede promozione automatica a `CERTO`.

## Esclusioni della presente slice

- nessuna modifica a `backend/app/api/tl_chat.py`;
- nessun import runtime;
- nessuna chiamata al reader o al resolver;
- nessun test runtime;
- nessun endpoint;
- nessuna modifica frontend;
- nessuna modifica source index;
- nessuna query o accesso database;
- nessuna modifica planner, ordini o board state.

## Criterio di accettazione

La mappatura è accettata se identifica un solo insertion point, preserva l'ordine di autorità già esistente, richiede un intent gate deterministico e non introduce alcun effetto runtime.

## NEXT_MOVE

Revisionare questa mappatura ed emettere uno dei seguenti esiti:

```text
MAP_ACCEPTED
ONE_REQUIRED_CHANGE
STOP
```
