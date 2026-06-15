# MEMORY_RETRIEVAL_SUPERIOR_BINDING_CONTRACT_001

## Status

- capability: MEMORY_RETRIEVAL_SUPERIOR_BINDING_CONTRACT_001
- status: CONTRACT_ONLY
- runtime_impact: NONE
- created_for: PROMETEO governed memory retrieval
- no_runtime_binding: true

## Purpose

Questo contratto definisce il gate superiore sopra `ContextPack`.

Il gate superiore decide se una richiesta puo usare memoria governata gia
autorizzata. Non decide sul dominio operativo, non produce azioni, non muta
stato e non trasforma evidence candidate in decisioni.

Questo contratto non collega TL Chat, non collega planner e non modifica la
pipeline runtime esistente. Definisce solo condizioni, caller, intent, output
ammessi, stop condition e invarianti da preservare prima di ogni futura
implementazione preview-only.

## Current approved lower pipeline

La pipeline inferiore approvata e:

- `collect_memory_evidence()`
- `build_context_pack()`
- `build_memory_retrieval_preview()`
- `MemoryRetrievalRuntimeRequest`
- `MemoryRetrievalRuntimeResponse`
- `ContextPack`

La catena resta:

```text
memory/*.md autorizzati
-> EvidenceItem
-> ContextPack
-> MemoryRetrievalRuntimeResponse
```

## Authorized callers

Caller autorizzati ora:

- `runtime_preview`

Caller riservati ma non abilitati:

- `tl_chat_preview`: RESERVED_NOT_ENABLED
- `atlas_preview`: RESERVED_NOT_ENABLED

Qualunque uso da TL Chat o ATLAS richiede una capability futura dedicata,
contract dedicato e guard automatico prima dell'implementazione.

## Authorized intents

Intent autorizzati ora:

- `domain_memory_preview`
- `article_memory_preview`
- `rule_memory_preview`

Intent vietati:

- `planner_decision`
- `production_priority`
- `route_override`
- `metadata_update`
- `smf_update`
- `memory_write`
- `llm_answer_generation`
- `autonomous_decision`

Gli intent autorizzati possono produrre solo contesto preview. Non autorizzano
decisioni operative, priorita produttive, override di route o mutation.

## Request contract

Schema logico:

```text
MemorySuperiorBindingRequest:
- query: non-empty string
- intent: enum autorizzato
- caller: enum autorizzato
- memory_root: Path con nome "memory"
- dry_run: true obbligatorio
- max_items: integer, default 5
- max_chars_per_item: integer, default 500
```

La richiesta deve essere respinta se qualunque campo obbligatorio manca, e
ambiguo, non autorizzato o viola `dry_run: true`.

## Response contract

Schema logico:

```text
MemorySuperiorBindingResponse:
- ok: bool
- blocked: bool
- block_reason: string | null
- query: string
- intent: string
- caller: string
- context_pack: ContextPack | null
- allowed_next_step: enum
- audit_reason: string
```

`allowed_next_step` ammessi:

- `VIEW_ONLY`
- `ASK_HUMAN_CONFIRMATION`
- `NO_ACTION`

`allowed_next_step` vietati:

- `PLAN_PRODUCTION`
- `CHANGE_ROUTE`
- `UPDATE_METADATA`
- `WRITE_MEMORY`
- `CALL_LLM`
- `CALL_PLANNER`
- `WRITE_SMF`
- `WRITE_DATABASE`

La risposta non deve contenere comandi operativi, mutation request, planner
action o output LLM operativo.

## Gate rules

Il gate superiore deve:

- bloccare caller non autorizzato;
- bloccare intent non autorizzato;
- bloccare `dry_run` diverso da `true`;
- bloccare query vuota;
- bloccare `memory_root` non chiamata `memory`;
- bloccare `ContextPack` con `source_path` fuori `memory/`;
- bloccare `ContextPack` senza `authority`;
- bloccare `ContextPack` senza `confidence`;
- non promuovere `confidence`;
- non cambiare `authority`;
- non trasformare `ContextPack` in decisione operativa.

Il gate puo solo autorizzare preview controllata e spiegabile.

## Stop conditions

La richiesta deve essere bloccata se:

- richiesta mira a decisione produttiva;
- richiesta mira a mutazione dati;
- richiesta mira a generazione LLM operativa;
- richiesta mira a planner;
- richiesta mira a route override;
- richiesta mira a update metadata;
- richiesta mira a SMF/database;
- caller o intent sono ambigui;
- source e sensibile o non autorizzata.

In presenza di stop condition, `allowed_next_step` deve essere `NO_ACTION`.

## Explicit non-goals

Questo contratto non autorizza:

- no TL Chat binding
- no `governed_retrieval.py` binding
- no planner binding
- no LLM call
- no endpoint
- no DB write
- no SMF write
- no memory write
- no frontend
- no runtime mutation

PROMETEO resta human-in-the-loop: ATLAS Engine segnala e spiega, planner
deterministico suggerisce, TL decide.

## Security and privacy constraints

Il livello superiore deve rispettare questi vincoli:

- non leggere dati reali;
- non leggere `specs_finitura`;
- non leggere SMF reale;
- non leggere `.env`;
- non leggere immagini/PDF/Excel reali;
- usare solo memory governata gia autorizzata;
- usare fixture sintetiche per test futuri.

Nessuna fonte sensibile, privata o produttiva reale puo essere introdotta in
questo livello.

## Future implementation sequence

Sequenza futura ammessa:

1. MEMORY_RETRIEVAL_SUPERIOR_BINDING_GUARD_001
2. MEMORY_RETRIEVAL_SUPERIOR_BINDING_001 preview-only
3. MEMORY_RETRIEVAL_SUPERIOR_BINDING_EVAL_001
4. Solo dopo valutare TL Chat preview binding contract

Ogni step deve restare capability separata, con scope minimo e guard dedicato.

## Final verdict

This contract authorizes only controlled preview access to ContextPack.
It does not authorize operational use, automated decisions, planner integration,
TL Chat integration, LLM generation, or data mutation.
