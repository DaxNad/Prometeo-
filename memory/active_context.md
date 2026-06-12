---
memory_id: MEMORY_ACTIVE_CONTEXT_001
type: persistent_memory
status: active
authority: operational_summary
confidence: DA_VERIFICARE
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO active context summary
---
# Active Context

## FATTO

PROMETEO e un sistema human-in-the-loop per supporto decisionale operativo in
reparti ad alta variabilita.

Architettura dominio stabile:

```text
Order -> Route -> Station -> ProductionEvent
```

Capability dichiarate come appena chiuse:

- `GOVERNED_RETRIEVAL_001`;
- `TL_CHAT_EVIDENCE_MODE_001`;
- `PROMETEO_AGENT_OPERATING_MODEL_001`;
- `CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_001`.

Ultima verifica dichiarata:

- controlled import persistent audit binding contract: OK;
- controlled import persistent audit binding guard: OK;
- controlled import audit pytest: 31 passed.

## INFERENZA

La prossima direzione coerente e stabilizzare memoria locale governata prima di
collegarla a retrieval runtime, TL Chat o LLM locali.

## DA_VERIFICARE

Lo stato "chiuso su main" delle capability elencate e riportato come contesto
operativo dichiarato e va verificato con storico Git o documenti di release se
serve usarlo come evidenza formale.

## NON_USARE_COME_FONTE

Questo file non autorizza runtime integration, retrieval automatico, LLM su
tutta la cartella, apply operativo, modifiche a backend, frontend, planner,
SMF o dati reali.
