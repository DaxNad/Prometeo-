---
memory_id: MEMORY_CAPABILITY_STATUS_001
type: persistent_memory
status: active
authority: capability_summary
confidence: DA_VERIFICARE
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO capability status summary
---

Lifecycle: `SUPERSEDED`

Superseded by: `docs/CURRENT_STATE.md`. Le capability elencate rappresentano
uno snapshot storico e non autorizzano la prossima mossa.
# Capability Status

## FATTO

Capability dichiarate come chiuse recentemente:

- `GOVERNED_RETRIEVAL_001`;
- `TL_CHAT_EVIDENCE_MODE_001`;
- `PROMETEO_AGENT_OPERATING_MODEL_001`;
- `CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_001`.

Capability corrente:

- `PERSISTENT_MEMORY_001`: crea memoria file-based minima e non collegata al
  runtime.

Regola operativa:

- una capability alla volta;
- nessuna espansione laterale;
- nessuna nuova architettura parallela;
- nessun collegamento runtime se non autorizzato da capability dedicata.

## INFERENZA

Prossime candidate coerenti, da scegliere una alla volta:

- retrieval policy binding verso memory;
- conflict detection su evidence governata;
- operational eval loop;
- audit/override runtime solo dopo guard adeguati;
- planner end-to-end su dataset sintetico.

## DA_VERIFICARE

Lo stato "chiuso" delle capability elencate va verificato contro main, tag,
PR o documenti di release quando serve evidenza formale.

## NON_USARE_COME_FONTE

Non aprire piu capability insieme. Non usare questo file come autorizzazione a
modificare backend, frontend, planner o dati.
