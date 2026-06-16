# PROMETEO_CONTEXT_SOURCE_INDEX_001

## Scopo

Definire un indice locale machine-readable delle fonti autorizzate che PROMETEO potrà usare in futuro tramite retrieval governato.

Questo documento accompagna `memory/context_source_index.json`.

## Stato

- Tipo: indice documentale e JSON
- Runtime: non collegato
- Backend: non modificato
- Frontend: non modificato
- Planner: non modificato
- Database: non modificato
- specs_finitura: non toccata
- SMF reale: non toccato

## File prodotti

| File | Ruolo |
|---|---|
| docs/PROMETEO_CONTEXT_SOURCE_INDEX_001.md | spiegazione umana dell'indice |
| memory/context_source_index.json | indice strutturato futuro per retrieval governato |

## Regola centrale

Questo indice non autorizza ancora nessun collegamento runtime.

Serve solo a trasformare il binding documentale in una struttura leggibile da macchina, verificabile e revisionabile.

## Fonti indicizzate

| ID | Percorso | Tier | Autorità | Runtime |
|---|---|---:|---|---:|
| context_access_binding | docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md | B | high | false |
| system_map | docs/PROMETEO_SYSTEM_MAP.md | B | high | false |
| agent_operating_model | docs/PROMETEO_AGENT_OPERATING_MODEL.md | B | high | false |
| development_closure_canon | docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md | B | high | false |
| llm_governance | docs/LLM_GOVERNANCE_PROMETEO.md | B | high | false |
| governed_retrieval | docs/GOVERNED_RETRIEVAL_001.md | B | high | false |
| memory_retrieval_binding_contract | docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md | B | high | false |
| memory_retrieval_consolidation | docs/MEMORY_RETRIEVAL_CONSOLIDATION_001.md | B | medium_high | false |
| memory_retrieval_runtime_contract | docs/MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001.md | B | high_but_runtime_inactive | false |
| memory_active_context | memory/active_context.md | B | medium_high | false |
| memory_project_state | memory/project_state.md | B | medium_high | false |
| memory_domain_invariants | memory/domain/invariants.md | A_support | high_if_consistent_with_spec_and_tl | false |
| memory_retrieval_policy | memory/retrieval/retrieval_policy.md | B | high | false |
| memory_capability_status | memory/capabilities/capability_status.md | C | medium | false |
| memory_index | memory/index.md | B | medium_high | false |
| memory_readme | memory/README_MEMORY.md | B | medium_high | false |

## Percorsi ammessi

- docs/
- memory/
- data/local_reports/ solo come supporto read-only

## Percorsi vietati

- backend/
- frontend/
- runtime/
- planner
- database
- SMF reale
- specs_finitura
- .env
- node_modules
- venv
- cache operative non classificate

## Regole di autorità

1. Specifica reale e conferma esplicita del Team Leader restano autorità primaria operativa.
2. LLM non è fonte autorevole.
3. ATLAS Engine segnala e spiega, ma non muta il dominio.
4. Il planner resta deterministico e non legge questo indice come sorgente runtime decisionale.
5. Report, preview, export e cache sono supporti, non verità primaria.

## Criterio PASS

- JSON valido.
- Tutte le fonti indicizzate esistono.
- Ogni fonte ha id, path, tier, authority, access_mode, runtime_enabled.
- runtime_enabled è false per tutte le fonti.
- Nessun file fuori da docs/ e memory/ viene creato o modificato.

## Criterio FAIL

- Il JSON abilita runtime.
- Il JSON autorizza specs_finitura o SMF reale.
- Il planner viene collegato direttamente all'indice.
- L'indice tratta report/cache/export come fonte primaria.
- L'indice sostituisce specifica reale o conferma TL.

## Decisione

PROMETEO ora può avere un indice sorgenti locale, ma solo come artefatto documentale.

Prima indice.
Poi test di lettura.
Poi adapter read-only.
Solo dopo eventuale binding runtime controllato.
