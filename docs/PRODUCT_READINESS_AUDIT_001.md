# PRODUCT_READINESS_AUDIT_001

Scope: gap audit verso `PRODUCT_LOCAL_EDGE_V1`.

Questo documento valuta il repository corrente come prodotto locale/edge
utilizzabile. Non dichiara PROMETEO prodotto completo e non introduce nuova
architettura.

## Sintesi

PROMETEO e runtime-operativo localmente, ma non ancora productizzato.

Stato complessivo: `PARTIAL`.

Punti forti:

- baseline locale `make goal-guard`;
- closure locale `make goal-complete-v1`;
- runtime smoke `tools/goal/runtime_operational_goal_check.sh`;
- backend FastAPI con `/health`;
- frontend Vite/PWA raggiungibile;
- TL Chat autenticata e contrattualizzata;
- privacy/data leak guard attivi.

Blocker prodotto:

- manca un target canonico `make setup`;
- manca un target canonico `make run`;
- manca un target canonico `make doctor`;
- startup script esistenti sono ancora legati a `$HOME/PROMETEO`;
- audit runtime esiste, ma non e ancora visibile come timeline prodotto per TL/admin;
- planner e TL Board sono presenti, ma non ancora confezionati come workflow unico
  da reparto.

## 1. Setup

STATUS: `PARTIAL`

Evidence:

- `scripts/setup_prometeo.sh`
- `README.md`
- `Makefile`

Osservazioni:

- Esiste uno script bootstrap (`scripts/setup_prometeo.sh`).
- Lo script crea struttura base, virtualenv, dipendenze Python, PostgreSQL locale
  e `.env`.
- Non e esposto da `Makefile` come target prodotto.
- Usa path hardcoded basati su `$HOME/PROMETEO`, quindi non e pienamente
  portabile per clone arbitrario.
- Non installa esplicitamente dipendenze frontend.

Minimal delta required:

- aggiungere target canonico `make setup`;
- rendere bootstrap repo-relative;
- includere controllo dipendenze frontend;
- non creare dati reali o file sensibili;
- output finale con istruzioni di avvio.

Risk:

- onboarding non ripetibile su macchina nuova;
- rischio divergenza tra ambiente sviluppatore e ambiente reparto;
- utente non tecnico bloccato prima del primo avvio.

## 2. Run

STATUS: `PARTIAL`

Evidence:

- `scripts/dev_start.sh`
- `scripts/dev_stop.sh`
- `scripts/dev_status.sh`
- `docs/RUNTIME_OPERATION_GUIDE_001.md`
- `tools/goal/runtime_operational_goal_check.sh`

Osservazioni:

- Esistono script per backend locale e status.
- Esiste guida runtime per avvio backend/frontend.
- Non esiste target `make run` che avvii backend + frontend in modo canonico.
- `scripts/dev_start.sh` avvia solo backend su 8000.
- `scripts/dev_start.sh` usa `$HOME/PROMETEO`, non root repo calcolata.
- Frontend resta avvio manuale tramite `cd frontend && npm run dev`.

Minimal delta required:

- aggiungere target `make run` o comando equivalente;
- rendere gli script repo-relative;
- distinguere backend-only, frontend-only e full-local;
- evitare kill aggressivi non documentati;
- produrre log chiari e path log non sensibili.

Risk:

- runtime prodotto dipende da memoria operativa dello sviluppatore;
- rischio istanze vecchie su porta 8000/5173;
- supporto cliente difficile.

## 3. Doctor

STATUS: `MISSING`

Evidence:

- `make goal-guard`
- `make goal-complete-v1`
- `tools/goal/runtime_operational_goal_check.sh`
- `scripts/dev_status.sh`

Osservazioni:

- Esistono guard e runtime check, ma non un comando unico `make doctor`.
- `goal-guard` predice merge/PR.
- `goal-complete-v1` valida closure operativa.
- `runtime_operational_goal_check.sh` valida backend/TL/frontend vivi.
- Questi comandi sono utili, ma non sono presentati come diagnostica prodotto
  unica per installazione cliente.

Minimal delta required:

- aggiungere `make doctor`;
- includere: repo status, Python, Node, backend health, frontend root,
  API key runtime, DB reachability, TL Chat smoke, guard privacy/leak;
- output tabellare PASS/PARTIAL/BLOCKED;
- nessuna scrittura dati.

Risk:

- troubleshooting lento;
- errori ambiente confusi con bug applicativi;
- impossibile dare a un cliente un controllo semplice post-installazione.

## 4. Backend/frontend/db reproducibility

STATUS: `PARTIAL`

Evidence:

- `backend/app/main.py`
- `backend/app/db.py`
- `backend/app/db/init_db.py`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `scripts/dev_start.sh`
- `docs/RUNTIME_OPERATION_GUIDE_001.md`

Osservazioni:

- Backend espone `/health` con `db_backend`, `postgres_reachable`,
  `startup_db_init_ok`.
- Frontend ha script `dev`, `build`, `test`.
- Vite proxy instrada `/production`, `/health`, `/agent-runtime`, `/tl/chat`
  verso `http://127.0.0.1:8000`.
- Runtime locale e gia stato cristallizzato da
  `tools/goal/runtime_operational_goal_check.sh`.
- Non c'e una composizione unica backend/frontend/db.
- Non risulta un `docker-compose.yml` prodotto.

Minimal delta required:

- definire modalita supportata `local-edge`;
- creare comando orchestrato o compose locale;
- standardizzare env richieste senza committare secret;
- aggiungere health finale end-to-end.

Risk:

- setup dipendente dalla macchina;
- difficile riprodurre bug cliente;
- rischio drift tra SQLite/dev, PostgreSQL locale e deploy.

## 5. TL entrypoint unico

STATUS: `PARTIAL`

Evidence:

- `frontend/src/App.tsx`
- `frontend/src/pages/TLChatPage.tsx`
- `frontend/src/pages/TLBoardPage.tsx`
- `frontend/src/pages/ProductionDashboard.tsx`

Osservazioni:

- Esistono rotte UI: `/`, `/tl-board`, `/tl-chat`.
- `App.tsx` offre navigazione base tra Dashboard, TL Board e TL Chat.
- Non esiste ancora un entrypoint unico di prodotto orientato al TL.
- La root `/` apre `ProductionDashboard`, non una schermata "turno TL" unica.

Minimal delta required:

- definire `/tl` o root prodotto come cockpit TL;
- includere accesso diretto a: domanda, priorita, blocchi, saturazione, azione;
- mantenere `TL Chat` e `TL Board` come viste interne;
- evitare schermate tecniche/debug come primo livello.

Risk:

- un TL vede piu pagine invece di un flusso operativo;
- prodotto percepito come dashboard tecnica, non strumento reparto;
- onboarding operativo piu lento.

## 6. TL Chat availability

STATUS: `DONE`

Evidence:

- `backend/app/api/tl_chat.py`
- `backend/tests/test_tl_chat_contract.py`
- `backend/tests/test_tl_chat_practical_query_set.py`
- `tools/goal/runtime_operational_goal_check.sh`
- `frontend/src/pages/TLChatPage.tsx`
- `frontend/src/lib/api/prometeo.ts`

Osservazioni:

- Endpoint `/tl/chat` presente.
- Auth via `X-API-Key` gestita dal client frontend se
  `localStorage.PROMETEO_API_KEY` e impostato.
- Contract test TL Chat presenti.
- Runtime goal check valida 12066, 12100 e regola globale ZAW1/ZAW2.
- TL Chat mostra answer, confidence, conferma TL, rischio e azione consigliata.

Minimal delta required:

- per prodotto: UX esplicita per inserire/verificare API key senza DevTools;
- messaggio guidato quando manca auth;
- collegamento piu diretto dal cockpit TL.

Risk:

- availability tecnica OK, ma primo utilizzo puo fallire se l'utente non sa
  configurare la chiave nel browser.

## 7. Planner usability

STATUS: `PARTIAL`

Evidence:

- `backend/app/services/sequence_planner.py`
- `backend/app/api_production.py`
- `backend/app/api/api_planner.py`
- `backend/tests/test_sequence_planner_minidataset.py`
- `backend/tests/test_planner_namespace_alias.py`
- `frontend/src/pages/TLBoardPage.tsx`
- `frontend/src/hooks/useTLSequence.ts`
- `tools/goal/endpoint_truth_table.sh`

Osservazioni:

- Planner espone `/production/sequence`, `/planner/sequence`,
  `/production/turn-plan`, `/production/machine-load`, explain e atlas-merge.
- Planner preserva gate di ammissione, human override e non promuove senza
  vincoli di dominio.
- TL Board consuma sequence, machine load ed explain.
- In SQLite manca vista reale: esiste fallback smoke `SQLITE_SMOKE_FALLBACK`.
- Il planner salva cache diagnostiche JSON in `backend/app/data/`.
- Non e ancora workflow prodotto completo "dammi il turno" con criterio
  operativo unico.

Minimal delta required:

- definire output TL-first per turno;
- chiarire quando il planner e reale, smoke, partial o blocked;
- evitare che fallback smoke venga percepito come piano reale;
- integrare planner nel TL cockpit con stato dati e fonte.

Risk:

- decision support percepito come ambiguo;
- possibilita di confondere fallback/dev con output operativo;
- piano utile ma non ancora abbastanza spiegato per reparto.

## 8. Privacy/guard state

STATUS: `DONE`

Evidence:

- `scripts/data_leak_guard.py`
- `scripts/privacy_guard_specs.py`
- `scripts/docs_authority_guard.py`
- `scripts/goal_guard.sh`
- `scripts/goal_complete_v1_check.sh`
- `README.md`

Osservazioni:

- `goal-guard` esegue whitespace check, Data Leak Guard, Privacy Guard,
  Docs Authority Guard, TL Eval e backend tests.
- `goal-complete-v1` controlla session memory locale ignorata, file sensibili
  tracciati, TL Chat contract, TL eval, Data Leak Guard e Privacy Guard.
- README dichiara che dati sensibili non devono essere tracciati e che
  `data/local_reports/session_memory/` resta locale.

Minimal delta required:

- per prodotto: includere guard privacy nel futuro `make doctor`;
- produrre report leggibile per admin non sviluppatore.

Risk:

- basso lato repo;
- medio lato prodotto se i guard restano comandi da sviluppatore e non
  diagnostica installazione.

## 9. Audit visibility

STATUS: `PARTIAL`

Evidence:

- `backend/app/api/agent_runtime.py`
- `backend/app/agent_runtime/run_repository.py`
- `backend/sql/010_controlled_import_audit_events.sql`
- `backend/app/repositories/controlled_import_audit_repository.py`
- `backend/app/services/controlled_import_persistent_audit.py`
- `frontend/src/lib/api/prometeo.ts`
- `frontend/src/hooks/useProductionBoard.ts`
- `board/SYSTEM_LOG.md`

Osservazioni:

- Agent runtime espone `/agent-runtime/status`, `/agent-runtime/runs`,
  `/agent-runtime/summary`, `/agent-runtime/summary/operational`.
- `AgentRunRepository` salva e lista run runtime in tabella `agent_runs`.
- Controlled import audit ha schema, repository e servizio persistente isolato.
- Frontend consuma summary operational, ma non risulta una timeline audit
  prodotto per TL/admin.
- `board/SYSTEM_LOG.md` e storico tecnico, non audit UI operativo.

Minimal delta required:

- creare vista audit/timeline read-only per prodotto;
- mostrare: evento, fonte, azione, decision_mode, explanation, timestamp;
- distinguere agent runtime audit da controlled import audit;
- nessun apply o mutazione senza flow dedicato.

Risk:

- audit tecnicamente presente ma invisibile all'utente;
- difficile dimostrare tracciabilita a reparto/IT;
- override e responsabilita umana non ancora productizzati.

## 10. Failure/fallback clarity

STATUS: `PARTIAL`

Evidence:

- `backend/app/main.py`
- `backend/app/api_production.py`
- `backend/app/services/sequence_planner.py`
- `backend/app/api/ai.py`
- `frontend/src/pages/TLChatPage.tsx`
- `frontend/src/pages/TLBoardPage.tsx`
- `tools/goal/runtime_operational_goal_check.sh`

Osservazioni:

- `/health` espone `startup_db_init_ok`, `startup_db_init_error`,
  `db_backend`, `postgres_reachable`.
- TL Chat usa confidence `CERTO`, `INFERITO`, `DA_VERIFICARE`.
- `/ai/sequence` degrada a `ai_status=PARTIAL` se AI locale non risponde.
- Sequence explain evita traceback completo e ritorna errore sintetico.
- Planner SQLite ha fallback smoke esplicito.
- TL Chat frontend mostra messaggio se runtime non raggiungibile.
- Non esiste ancora una failure taxonomy prodotto unica.

Minimal delta required:

- definire stati prodotto: `READY`, `DEGRADED`, `AUTH_BLOCKED`,
  `DATA_PARTIAL`, `SMOKE_ONLY`, `BACKEND_DOWN`;
- mostrarli nel cockpit;
- includerli in `make doctor`;
- impedire uso operativo se fonte e solo smoke/dev.

Risk:

- gli errori sono gestiti, ma non sempre traducibili in decisione operativa;
- rischio di usare output parziale senza vedere chiaramente il livello di
  affidabilita.

## Gap finale verso PRODUCT_LOCAL_EDGE_V1

Per dichiarare `PRODUCT_LOCAL_EDGE_V1 = PASS` servono almeno:

1. `make setup` repo-relative;
2. `make run` backend + frontend;
3. `make doctor` con output prodotto;
4. cockpit TL unico;
5. stato sorgente dati visibile: real/partial/smoke/blocked;
6. audit timeline read-only visibile;
7. packaging local-edge documentato;
8. failure taxonomy mostrata in UI e doctor.

## Verdetto

`PRODUCT_LOCAL_EDGE_V1 = PARTIAL`

PROMETEO e gia un sistema locale governato e runtime-verificabile. Non e ancora
un prodotto local-edge perche mancano installazione/run/doctor canonici,
entrypoint TL unico e audit/failure state esposti come esperienza prodotto.
