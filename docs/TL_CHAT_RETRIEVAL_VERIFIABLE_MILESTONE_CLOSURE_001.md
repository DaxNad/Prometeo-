# TL Chat Retrieval Verifiable Milestone Closure 001

## 1. Stato

```text
MILESTONE_STATUS: CLOSED
VERDICT: NO_OPEN_RUNTIME_FINDINGS
```

## 2. Milestone

```text
TL Chat
→ retrieval reale
→ risposta verificabile
```

## 3. Scope chiuso

Il flusso verificato comprende:

- richiesta TL Chat;
- selezione articolo e intento;
- caricamento fonti autorizzate;
- reader adapter read-only;
- costruzione candidate;
- context resolver;
- bridge;
- `TLChatResponse`;
- serializzazione pubblica.

## 4. Proprietà verificate

- Fonti mancanti, invalide e non leggibili sono distinguibili.
- Errori reader tipizzati vengono convertiti in risposta verificabile.
- `error_code` viene preservato internamente e non serializzato.
- `DA_VERIFICARE` implica `requires_confirmation=True`.
- Nessuna fonte incerta viene promossa a `CERTO`.
- Nessuna fonte incerta diventa planner-eligible.
- Source non autorizzate non espongono contenuto.
- Reader adapter, bridge e resolver non modificano le fonti.
- Classificazioni operative specifiche, come manicotto, richiedono metadata espliciti.
- Nessun hardcoding `12201` resta nel layer API.
- Contratto pubblico `/tl/chat` invariato.

## 5. Failure path coperti

- Indice assente.
- Indice JSON invalido.
- Indice non leggibile.
- Fonte assente.
- Fonte non leggibile.
- Fonte non autorizzata.
- Candidate non disponibile.
- Resolver senza fonte valida.
- Metadata/componenti mancanti.
- Classificazione esplicita assente.
- Confidence incerta.
- Errore interno non esposto pubblicamente.

## 6. Commit di chiusura

- `579fa2c` - fix(tl-chat): anchor 12514 confirmation path and harden safe codex launch
- `2956b30` - docs(tl-chat): align 12514 confirmation persistence semantics
- `1380f8f` - fix(tl-chat): distinguish JSON source loader failures
- `bfce4ae` - refactor(tl-chat): classify manicotto from explicit metadata
- `060b116` - fix(tl-chat): require confirmation for uncertain responses
- `e0e8864` - fix(tl-chat): preserve internal context reader error codes
- `87072a5` - fix(tl-chat): handle context reader initialization errors
- `4f19260` - fix(context-reader): normalize runtime JSON and I/O errors

## 7. Evidenza di test finale

```text
97 passed in 0.60s
```

Suite mirate eseguite:

```text
backend/tests/test_tl_chat_json_loader_diagnostics.py
backend/tests/test_tl_chat_practical_query_set.py
backend/tests/test_tl_chat_context_reader_bridge_resolver_helper.py
backend/tests/test_tl_chat_context_resolver.py
backend/tests/test_tl_chat_context_reader_runtime_binding.py
backend/tests/test_context_source_reader_adapter_runtime_errors.py
backend/tests/test_context_source_reader_adapter_readonly.py
```

## 8. Vincoli preservati

- Architettura: `Order → Route → Station → ProductionEvent`.
- PROMETEO Core deterministico.
- LLM come supporto contestuale governato.
- Nessuna modifica a frontend.
- Nessuna modifica a planner.
- Nessuna modifica ad ATLAS.
- Nessuna nuova capability.
- Nessuna modifica ai dati sorgente.
- Nessuna promozione automatica a `CERTO`.

## 9. Criterio di riapertura

La milestone può essere riaperta solo con almeno una delle seguenti prove:

- test riproducibile che fallisce;
- eccezione runtime non governata;
- perdita verificata di fonte, stato o confidence;
- esposizione pubblica di dettagli interni;
- regressione sul contratto `/tl/chat`;
- nuova fonte reale da integrare nella capability già esistente.

Non riaprire per:

- refactor;
- stile;
- naming;
- nuove idee;
- frontend;
- planner;
- ATLAS;
- performance non misurate;
- osservabilità futura.

## 10. Prossimo ambito

```text
NEXT_SCOPE: TO_BE_SELECTED AFTER MILESTONE CLOSURE
```
