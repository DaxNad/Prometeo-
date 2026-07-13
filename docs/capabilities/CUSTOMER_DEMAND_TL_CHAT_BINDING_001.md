# CUSTOMER_DEMAND_TL_CHAT_BINDING_001

## Stato

- `CAPABILITY_STATUS`: `IMPLEMENTED`
- `IMPLEMENTATION_STATUS`: `COMPLETED`
- `SOURCE_ID`: `customer_demand_registry`
- `TARGET_ROUTE`: `backend/app/api/tl_chat.py`
- `TARGET_DISPATCHER`: `_build_contract_response`
- `RUNTIME_BINDING_CURRENT`: `IMPLEMENTED_READ_ONLY`
- `TL_CHAT_BINDING_CURRENT`: `IMPLEMENTED`
- `DATABASE_ACCESS_MODE`: `READ_ONLY`
- `PLANNER_ELIGIBLE`: `false`
- `AUTOMATIC_PROMOTION`: `FORBIDDEN`

## Obiettivo unico

Autorizzare una futura vertical slice implementativa minima che colleghi il binding read-only `customer_demand_registry` alla route TL Chat esclusivamente per domande pertinenti alla domanda cliente, con intent gate deterministico, rendering controllato e test route dedicati.

La capability è implementata nella route TL Chat con intent gate deterministico, rendering read-only e test route dedicati.

## Prerequisiti consolidati

- source registration `customer_demand_registry` presente con `runtime_enabled: false`;
- reader read-only implementato;
- query limitata ai cinque campi autorizzati;
- Context Resolver binding implementato;
- priorità resolver registrata;
- mappatura del punto di integrazione TL Chat accettata;
- compatibilità SQLite/PostgreSQL già gestita dal reader.

## File futuri autorizzabili

La futura implementazione deve restare limitata a:

- `backend/app/api/tl_chat.py`;
- `backend/tests/test_tl_chat_contract.py` oppure un nuovo file route-test dedicato;
- `docs/capabilities/CUSTOMER_DEMAND_TL_CHAT_BINDING_001.md` per aggiornare lo stato dopo l'implementazione.

Non sono autorizzate modifiche a reader, resolver, source index o schema database salvo blocker tecnico osservato e documentato prima della patch.

## Punto di integrazione vincolante

Dentro:

```python
def _build_contract_response(payload: TLChatRequest) -> TLChatResponse:
```

nel ramo:

```python
if article:
```

Il futuro customer-demand gate deve essere collocato:

1. dopo gli handler specialistici di `local_specs_metadata` già presenti;
2. prima del fallback generico `article_summary`;
3. prima del fallback `lifecycle_registry`;
4. prima delle fonti preview;
5. prima del `ContextSourceReaderAdapter` generico;
6. prima della risposta finale `SOURCE_MISSING`.

Flusso autorizzato:

```text
local_specs_metadata handlers specialistici
    ↓
customer_demand intent gate
    ↓
article_summary
    ↓
lifecycle_registry
    ↓
spec_intake_preview
    ↓
preview_profile
    ↓
context_source_reader_adapter
    ↓
missing
```

L'ordine delle fonti non sostituisce il routing per pertinenza. Una fonte più autorevole ma non pertinente non deve impedire il recupero della domanda cliente quando l'intento è esplicito.

## Intent gate deterministico

La futura slice può introdurre una funzione privata nella route con responsabilità limitata, ad esempio:

```text
_question_asks_customer_demand(question) -> bool
```

Il nome finale deve essere verificato nella patch, ma la responsabilità è vincolante.

Il gate deve riconoscere soltanto richieste esplicite relative a:

- quantità richiesta dal cliente;
- data richiesta dal cliente;
- priorità cliente;
- presenza di domanda cliente per articolo;
- stato della richiesta cliente registrata.

Il gate non deve attivarsi per domande generiche su:

- assemblabilità;
- route;
- operazioni;
- componenti;
- planner;
- turno;
- sequenziamento;
- data confermata di spedizione;
- scadenza interna;
- promessa al cliente.

La prima slice usa esclusivamente:

```text
resolve_customer_demand_context(articolo=article)
```

Il lookup tramite `codice_articolo` resta fuori scope finché non esiste una distinzione esplicita e testata del tipo di identificatore.

## Rendering TL Chat

La futura implementazione deve trasformare `TLChatResolvedContext` in `TLChatResponse` preservando:

- `selected_source` come `source`;
- `source_status`;
- `confidence`;
- `payload.semantic_status` come `semantic_status`;
- `payload.missing_data` come `missing_data`;
- `requires_tl_confirmation` come `requires_confirmation`;
- `planner_eligible: false`;
- `can_promote: false`.

Il rendering deve esporre esclusivamente:

- `articolo`;
- `codice_articolo`;
- `quantita`;
- `data_spedizione`;
- `priorita_cliente`.

`data_spedizione` deve essere presentata come:

```text
data richiesta dal cliente registrata nella fonte
```

Non deve essere descritta come data confermata, promessa, scadenza interna o piano di produzione.

## Stati obbligatori

### Record presenti

```text
source: customer_demand_registry
source_status: SOURCE_FOUND
confidence: DA_VERIFICARE
semantic_status: DA_VERIFICARE
requires_confirmation: true
planner_eligible: false
can_promote: false
```

### Lookup valido senza record

```text
source: customer_demand_registry
source_status: SOURCE_FOUND
records: []
missing_data: record_customer_demand_not_found
```

Non deve essere convertito in `SOURCE_MISSING`.

### Reader o database indisponibile

```text
source: customer_demand_registry
source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE
missing_data: customer_demand_reader_unavailable
```

Nessun dettaglio tecnico del database deve comparire nella risposta TL.

## Test route minimi obbligatori

La futura slice deve verificare almeno:

- domanda sulla quantità cliente con articolo → usa `customer_demand_registry`;
- domanda sulla data richiesta cliente → chiarisce la semantica non confermata;
- domanda sulla priorità cliente → usa il binding dedicato;
- domanda non customer-demand → il reader non viene invocato;
- handler specialistico `local_specs_metadata` pertinente → non viene scavalcato;
- presenza di article summary o lifecycle → non blocca un intento customer-demand esplicito;
- record assente → `SOURCE_FOUND` con missing data specifico;
- reader indisponibile → `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- nessuna promozione a `CERTO`;
- nessuna eleggibilità planner;
- nessun dettaglio database nella risposta;
- nessun accesso a campi oltre i cinque autorizzati.

## Fuori scope

- nuovi endpoint;
- frontend;
- modifica del source index;
- modifica del reader;
- modifica del resolver;
- nuove query o nuove colonne;
- lookup automatico tramite `codice_articolo`;
- importer o SMF;
- scritture database;
- planner, ordini, board state o viste ZAW;
- promozione automatica a `CERTO`;
- uso della fonte per decisioni automatiche.

## Stop conditions

La futura implementazione deve fermarsi se:

- richiede campi oltre i cinque autorizzati;
- richiede scritture database;
- richiede interpretazione di `data_spedizione` come data confermata;
- richiede invocazione del reader per tutte le domande articolo;
- richiede modifica del planner o degli ordini;
- richiede promozione automatica;
- richiede spostare il gate dopo fallback con return anticipato;
- richiede esporre errori tecnici del database.

## Criterio di accettazione

La capability è accettata quando autorizza una sola futura slice TL Chat, mantiene il runtime invariato nella presente PR, definisce intent gate, insertion point, rendering, stati e test minimi senza espandere reader, resolver o database.

## Chiusura

- `IMPLEMENTATION_ACCEPTED`: `VERIFIED_FOR_MERGE`
- `DATABASE_WRITE`: `NONE`
- `PLANNER_ELIGIBLE`: `false`
- `AUTOMATIC_PROMOTION`: `FORBIDDEN`
- `NEXT_MOVE`: unire la PR dopo il completamento dei controlli obbligatori, senza aprire ulteriori capability.
