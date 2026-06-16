# PROMETEO_CONTEXT_SOURCE_INDEX_READONLY_TEST_001

## Scopo

Definire il primo test documentale read-only per `memory/context_source_index.json`.

Questo documento non collega il runtime.
Non introduce adapter.
Non modifica backend, frontend, planner, database, SMF reale o specs_finitura.

Serve a fissare il comportamento minimo che un futuro lettore governato dell'indice dovrà rispettare.

## Stato

- Tipo: test documentale
- Runtime: non collegato
- Backend: non modificato
- Frontend: non modificato
- Planner: non modificato
- Database: non modificato
- SMF reale: non toccato
- specs_finitura: non toccata

## Artefatto testato

```text
memory/context_source_index.json
```

## Risultato audit locale

- Schema: PROMETEO_CONTEXT_SOURCE_INDEX_001
- Status: documental_index_only
- Runtime globale: False
- Fonti indicizzate: 16
- Validazione: PASS

## Condizioni verificate

Il test read-only conferma che:

1. il JSON è valido;
2. lo schema è `PROMETEO_CONTEXT_SOURCE_INDEX_001`;
3. lo stato è `documental_index_only`;
4. `runtime_enabled` globale è `false`;
5. tutte le fonti hanno `runtime_enabled=false`;
6. tutte le fonti hanno `access_mode=read_only`;
7. tutte le fonti dichiarate esistono localmente;
8. ogni fonte contiene i campi minimi richiesti;
9. i percorsi vietati restano dichiarati;
10. nessun modulo runtime viene abilitato.

## Fonti lette dal test

| ID | Path | Runtime | Accesso |
|---|---|---:|---|
| context_access_binding | docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md | false | read_only |
| system_map | docs/PROMETEO_SYSTEM_MAP.md | false | read_only |
| agent_operating_model | docs/PROMETEO_AGENT_OPERATING_MODEL.md | false | read_only |
| development_closure_canon | docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md | false | read_only |
| llm_governance | docs/LLM_GOVERNANCE_PROMETEO.md | false | read_only |
| governed_retrieval | docs/GOVERNED_RETRIEVAL_001.md | false | read_only |
| memory_retrieval_binding_contract | docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md | false | read_only |
| memory_retrieval_consolidation | docs/MEMORY_RETRIEVAL_CONSOLIDATION_001.md | false | read_only |
| memory_retrieval_runtime_contract | docs/MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001.md | false | read_only |
| memory_active_context | memory/active_context.md | false | read_only |
| memory_project_state | memory/project_state.md | false | read_only |
| memory_domain_invariants | memory/domain/invariants.md | false | read_only |
| memory_retrieval_policy | memory/retrieval/retrieval_policy.md | false | read_only |
| memory_capability_status | memory/capabilities/capability_status.md | false | read_only |
| memory_index | memory/index.md | false | read_only |
| memory_readme | memory/README_MEMORY.md | false | read_only |

## Percorsi vietati confermati

```text
backend/
frontend/
runtime/
planner
database
SMF reale
specs_finitura
.env
```

## Criterio PASS

Il test è valido se:

- il documento viene creato in `docs/`;
- nessun file fuori da `docs/` viene modificato;
- l'indice resta in `status=documental_index_only`;
- `runtime_enabled=false` resta vero globalmente e per ogni fonte;
- ogni fonte resta `read_only`;
- non viene introdotto alcun adapter.

## Criterio FAIL

Il test fallisce se:

- abilita runtime;
- apre accesso a backend, frontend, planner, database, SMF reale, specs_finitura o `.env`;
- trasforma l'indice in sorgente decisionale del planner;
- modifica dati reali;
- tratta report, cache o export come verità primaria;
- permette all'LLM di usare l'indice come autorità di dominio.

## Decisione

PROMETEO può leggere e validare l'indice delle fonti in modalità read-only documentale.

Non può ancora usarlo nel runtime.
Non può ancora usarlo in TL Chat.
Non può ancora usarlo in ATLAS Engine.
Non può ancora usarlo nel planner.

Prossimo passo ammesso solo dopo questa chiusura: definire un adapter read-only separato, con contratto e test, senza collegamento runtime operativo.
