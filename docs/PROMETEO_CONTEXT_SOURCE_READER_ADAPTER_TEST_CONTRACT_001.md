# PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_TEST_CONTRACT_001

## Scopo

Definire il contratto dei test futuri per `ContextSourceReaderAdapter`.

Questo documento non implementa l'adapter.
Non introduce test automatici nel repository.
Non modifica backend, frontend, planner, runtime, database, SMF reale, specs_finitura o `.env`.

Serve a fissare in anticipo quali comportamenti dovrà dimostrare una futura implementazione read-only prima di poter essere accettata.

## Stato

- Tipo: contratto documentale di test
- Adapter: non implementato
- Test automatici: non introdotti
- Runtime: non collegato
- Backend: non modificato
- Frontend: non modificato
- Planner: non modificato
- Database: non modificato
- SMF reale: non toccato
- specs_finitura: non toccata
- `.env`: non toccato

## Prerequisiti chiusi

| Capability | File | Stato |
|---|---|---|
| PROMETEO_CONTEXT_ACCESS_BINDING_001 | docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md | chiuso |
| PROMETEO_CONTEXT_SOURCE_INDEX_001 | docs/PROMETEO_CONTEXT_SOURCE_INDEX_001.md + memory/context_source_index.json | chiuso |
| PROMETEO_CONTEXT_SOURCE_INDEX_READONLY_TEST_001 | docs/PROMETEO_CONTEXT_SOURCE_INDEX_READONLY_TEST_001.md | chiuso |
| PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_CONTRACT_001 | docs/PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_CONTRACT_001.md | chiuso |

## Artefatto futuro sotto test

Nome logico:

```text
ContextSourceReaderAdapter
```

File futuri non ancora autorizzati da questo contratto:

```text
nessun file codice ancora autorizzato
```

Questo contratto non decide ancora dove implementare l'adapter.
Questa scelta richiederà una capability separata con scope, file ammessi, file vietati e test reali.

## Obiettivo dei test futuri

I test futuri devono dimostrare che il reader:

1. legge solo `memory/context_source_index.json`;
2. valida schema e stato dell'indice;
3. non abilita runtime;
4. filtra fonti in modo deterministico;
5. rifiuta path vietati;
6. rifiuta path traversal;
7. non legge contenuto integrale dei documenti;
8. non scrive file;
9. non importa backend/runtime;
10. restituisce output strutturato e minimale.

## Test group A — validazione indice

### A1 — JSON valido

Input:

```text
memory/context_source_index.json presente e JSON valido
```

Expected:

```text
ok=true
schema=PROMETEO_CONTEXT_SOURCE_INDEX_001
status=documental_index_only
runtime_enabled=false
```

### A2 — JSON mancante

Input:

```text
memory/context_source_index.json assente
```

Expected:

```text
ok=false
error=INDEX_NOT_FOUND
nessuna lettura alternativa
nessun fallback a path arbitrari
```

### A3 — JSON malformato

Input:

```text
memory/context_source_index.json non parseabile
```

Expected:

```text
ok=false
error=INDEX_INVALID_JSON
nessun runtime abilitato
```

### A4 — schema errato

Input:

```text
schema diverso da PROMETEO_CONTEXT_SOURCE_INDEX_001
```

Expected:

```text
ok=false
error=INDEX_SCHEMA_UNSUPPORTED
```

### A5 — runtime globale attivo

Input:

```text
runtime_enabled=true
```

Expected:

```text
ok=false
error=RUNTIME_NOT_ALLOWED
```

## Test group B — policy fonti

### B1 — tutte le fonti read-only

Input:

```text
sources con access_mode=read_only e runtime_enabled=false
```

Expected:

```text
ok=true
tutte le fonti ammesse restano read_only
nessun contenuto completo restituito
```

### B2 — fonte con runtime_enabled=true

Input:

```text
una fonte indicizzata ha runtime_enabled=true
```

Expected:

```text
ok=false oppure fonte rifiutata
rejected.reason=SOURCE_RUNTIME_NOT_ALLOWED
```

### B3 — fonte con access_mode diverso da read_only

Input:

```text
una fonte ha access_mode=write oppure access_mode assente
```

Expected:

```text
fonte rifiutata
rejected.reason=SOURCE_NOT_READ_ONLY
```

### B4 — fonte inesistente

Input:

```text
exists=true nell'indice ma file assente su disco
```

Expected:

```text
ok=false oppure fonte rifiutata
rejected.reason=SOURCE_NOT_FOUND
```

## Test group C — filtri input

### C1 — filtro allowed_for valido

Input:

```text
allowed_for=tl_chat_context_policy
```

Expected:

```text
ritorna solo fonti che includono tl_chat_context_policy in allowed_for
output strutturato
nessun contenuto completo
```

### C2 — source_ids validi

Input:

```text
source_ids=[system_map, llm_governance]
```

Expected:

```text
ritorna solo le fonti richieste se ammesse
mantiene ordine deterministico
```

### C3 — source_id sconosciuto

Input:

```text
source_ids=[fonte_inesistente]
```

Expected:

```text
ok=false oppure rejected
rejected.reason=SOURCE_ID_UNKNOWN
```

### C4 — max_sources

Input:

```text
max_sources=3
```

Expected:

```text
massimo 3 fonti restituite
ordine deterministico
warning se fonti filtrate oltre limite
```

### C5 — input generico

Input:

```text
intent vuoto oppure input assente
```

Expected:

```text
ok=false
error=INTENT_REQUIRED
nessuna lettura ampia
```

## Test group D — sicurezza path

### D1 — path arbitrario

Input:

```text
path=<repo>/backend/app/main.py
```

Expected:

```text
ok=false
error=ARBITRARY_PATH_NOT_ALLOWED
```

### D2 — path traversal

Input:

```text
source_ids o path contenente ../
```

Expected:

```text
ok=false
error=PATH_TRAVERSAL_BLOCKED
```

### D3 — path vietato indicizzato per errore

Input:

```text
una fonte nell'indice punta a backend/ oppure .env
```

Expected:

```text
fonte rifiutata
rejected.reason=FORBIDDEN_PATH
```

### D4 — glob libero

Input:

```text
path=docs/*.md oppure **/*
```

Expected:

```text
ok=false
error=GLOB_NOT_ALLOWED
```

## Test group E — output

### E1 — output schema stabile

Expected minimo:

```text
ok
schema
runtime_enabled
status
sources
rejected
warnings
```

### E2 — niente contenuto integrale

Expected:

```text
nessun campo content
nessun campo full_text
nessun corpo markdown completo
solo metadati
```

### E3 — niente decisioni operative

Expected:

```text
nessun campo planner_decision
nessun campo priority
nessun campo production_action
nessuna modifica a dominio
```

## Test group F — isolamento runtime

### F1 — nessun import backend

Expected:

```text
adapter non importa FastAPI
adapter non importa router backend
adapter non importa planner runtime
```

### F2 — nessuna rete

Expected:

```text
nessuna chiamata HTTP
nessuna chiamata esterna
nessun accesso provider AI
```

### F3 — nessuna scrittura file

Expected:

```text
nessun write_text
nessun open in modalità write/append
nessun aggiornamento JSON
nessun audit scritto in questa fase
```

### F4 — nessun accesso .env

Expected:

```text
nessuna lettura .env
nessuna variabile segreta richiesta
```

## Test group G — anti prompt injection

### G1 — contenuto documentale non eseguito

Premessa:

```text
in futuro il reader potrà eventualmente leggere contenuti solo con capability successiva
```

Expected per questo adapter:

```text
non legge contenuto completo
non esegue istruzioni presenti nei documenti
non tratta testo letto come comando
```

## Matrice PASS minima per futura implementazione

| Gruppo | Obbligatorio |
|---|---:|
| A - validazione indice | sì |
| B - policy fonti | sì |
| C - filtri input | sì |
| D - sicurezza path | sì |
| E - output | sì |
| F - isolamento runtime | sì |
| G - anti prompt injection | sì |

## Criterio PASS di questo contratto

Questo contratto è valido se:

- resta documentale;
- non introduce test automatici;
- non introduce codice adapter;
- non modifica `memory/context_source_index.json`;
- definisce casi positivi e negativi;
- include rifiuto path arbitrari;
- include rifiuto path traversal;
- include divieto contenuto integrale;
- include isolamento da runtime/backend/planner;
- conferma che TL Chat, ATLAS Engine e planner non sono ancora collegati.

## Criterio FAIL

Questo contratto fallisce se:

- autorizza implementazione nello stesso ciclo;
- abilita runtime;
- autorizza backend o FastAPI;
- autorizza planner a leggere il reader;
- consente lettura specs_finitura o SMF reale;
- consente lettura `.env`;
- consente path arbitrari;
- tratta documenti come istruzioni eseguibili;
- introduce test automatici senza scope separato.

## Decisione

PROMETEO può definire i test futuri del `ContextSourceReaderAdapter`, ma non può ancora implementarlo.

Sequenza corretta:

```text
binding documentale
-> indice sorgenti
-> test read-only documentale
-> contratto adapter read-only
-> contratto test adapter read-only
-> solo dopo eventuale implementazione adapter in capability separata
```

Stato finale di questa capability:

```text
nessun adapter operativo
nessun test automatico
nessun runtime binding
nessun backend
nessun frontend
nessun planner
nessun accesso TL Chat
nessun accesso ATLAS Engine
```
