---
memory_id: MEMORY_RETRIEVAL_POLICY_001
type: persistent_memory
status: active
authority: retrieval_policy
confidence: CERTO
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO memory retrieval policy
---
# Memory Retrieval Policy

## FATTO

`memory/` e fonte futura per retrieval governato solo se il file dichiara:

- `allowed_for_retrieval: true`;
- `authority`;
- `confidence`;
- `sensitive: false`.

Ogni informazione recuperata da `memory/` deve conservare:

- `memory_id`;
- fonte file;
- authority;
- confidence;
- motivo di retrieval.

## INFERENZA

Il retrieval futuro dovra trattare `memory/` come fonte di contesto sintetico,
non come fonte primaria di verita operativa.

## DA_VERIFICARE

Non esiste ancora binding runtime tra `memory/`, TL Chat, LLM locali o
governed retrieval. Tale binding richiede capability separata e test dedicati.

## NON_USARE_COME_FONTE

Divieti:

- no LLM libero su tutta la cartella;
- no retrieval da file senza `allowed_for_retrieval: true`;
- no retrieval da logs, private, cache o embeddings non governati;
- no fonti sensibili;
- no dati produttivi reali;
- no promozione automatica a `CERTO`;
- no modifica runtime, planner, SMF o TL Chat da questa policy.
