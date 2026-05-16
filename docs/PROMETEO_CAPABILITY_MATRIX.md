# PROMETEO Capability Matrix

Scopo: rendere visibile il gap tra lavoro svolto e meta, collegando capacita, fonte, modulo, test e prossimo passo.

## Stati

- `NOT_STARTED`: non esiste ancora struttura utile.
- `STRUCTURAL_READY`: struttura o registry esiste, ma non basta come prova operativa.
- `TESTED_SYNTHETIC`: coperto da casi sintetici non sensibili.
- `TESTED_REAL_SAMPLE`: verificato su campione reale sanificato o conferma TL documentata.
- `PILOT_READY`: usabile in pilota controllato read-only.
- `PRODUCTION_READY`: stabile, monitorato, spiegabile, con guard attivi.

## Matrice

| Capacita | Stato | Fonte verita | Modulo | Test / Eval | Rischio | Prossimo passo |
| --- | --- | --- | --- | --- | --- | --- |
| Semantic confidence canonica | `TESTED_SYNTHETIC` | `PROMETEO_MASTER` | `semantic_registry` | `backend/tests/test_semantic_registry.py` | Drift tra moduli | Usare accessor solo in diagnostica prima di enforcement |
| Planner admission gate | `TESTED_SYNTHETIC` | `PROMETEO_MASTER`, Manifesto | `domain/operational_class.py` | `backend/tests/test_operational_class.py` | Promozione indebita a planner | Aggiungere casi eval di non-ammissione |
| TL Chat confidence binding | `TESTED_SYNTHETIC` | semantic registry | `api/tl_chat.py` | `backend/tests/test_tl_chat_contract.py` | Cambi risposta pubblica | Mantenere compatibilita output |
| ATLAS merge confidence awareness | `TESTED_SYNTHETIC` | semantic registry | `atlas_engine/decision_merge_engine.py` | `backend/app/atlas_engine/tests/test_decision_merge_engine.py` | Cambio scoring involontario | Tenere metadata fuori dallo scoring |
| Data Boundary Guard | `STRUCTURAL_READY` | security policy | `security/*`, `ai_router/*` | `backend/tests/test_data_boundary_guard.py` | Oversharing verso AI esterna | Collegare agli adapter solo dopo policy review |
| Local session memory | `STRUCTURAL_READY` | policy locale utente | `scripts/context_pack.py` | comando manuale + guard | Accumulo contenuti sensibili | Tenere `.md/.jsonl` ignorati e sanificati |
| ZAW saturation reasoning | `TESTED_SYNTHETIC` | dominio stazioni | planner, ATLAS | `evals/prometeo_pilot_cases/case_001_station_saturation.json`, `case_006_zaw_shared_component_risk_contract.json` | Inferenze opache | Collegare a test runtime read-only solo dopo review |
| CP final block reasoning | `TESTED_SYNTHETIC` | dominio stazioni | planner, ATLAS | `evals/prometeo_pilot_cases/case_002_final_check_block.json`, `case_006_zaw_shared_component_risk_contract.json` | Mancata propagazione blocker | Misurare explainability minima in output runtime |
| Shared component conflict | `TESTED_SYNTHETIC` | componente condiviso | ATLAS, planner | `evals/prometeo_pilot_cases/case_003_shared_component_conflict.json`, `case_006_zaw_shared_component_risk_contract.json` | Priorita non motivata | Collegare a campione sanificato prima di pilota |
| TL authority boundary | `TESTED_SYNTHETIC` | TL authority | semantic registry, guards | semantic/accessor tests | Autonomia eccessiva | Inserire forbidden outputs negli eval |

## Regola Operativa

Ogni nuova feature deve aggiornare almeno una riga della matrice o motivare perche non cambia capability.
