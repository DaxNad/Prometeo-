---
memory_id: MEMORY_INDEX_001
type: persistent_memory
status: active
authority: governance_summary
confidence: CERTO
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO memory index
---
# Memory Index

## FATTO

| File | memory_id | Scopo | allowed_for_retrieval | authority | sensitive |
| --- | --- | --- | --- | --- | --- |
| `memory/README_MEMORY.md` | `MEMORY_README_001` | Policy della cartella memory | true | governance_summary | false |
| `memory/index.md` | `MEMORY_INDEX_001` | Indice dei file memory ammessi | true | governance_summary | false |
| `memory/active_context.md` | `MEMORY_ACTIVE_CONTEXT_001` | Contesto operativo sintetico corrente | true | operational_summary | false |
| `memory/project_state.md` | `MEMORY_PROJECT_STATE_001` | Stato progetto e limiti verso produzione completa | true | project_status_summary | false |
| `memory/domain/invariants.md` | `MEMORY_DOMAIN_INVARIANTS_001` | Invarianti dominio consolidati | true | domain_summary | false |
| `memory/capabilities/capability_status.md` | `MEMORY_CAPABILITY_STATUS_001` | Stato capability sintetico | true | capability_summary | false |
| `memory/retrieval/retrieval_policy.md` | `MEMORY_RETRIEVAL_POLICY_001` | Policy futura per retrieval da memory | true | retrieval_policy | false |

## INFERENZA

Questo indice consente ai futuri agenti di capire quali file memory sono
ammessi al retrieval governato senza esplorare cartelle non autorizzate.

## DA_VERIFICARE

Eventuali nuovi file memory dovranno essere aggiunti solo con capability
dedicata e con front matter equivalente.

## NON_USARE_COME_FONTE

Non trattare l'indice come fonte di verita dominio. L'indice descrive i file,
non sostituisce `PROMETEO_MASTER.md` o fonti operative confermate.
