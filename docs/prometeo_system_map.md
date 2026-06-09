# PROMETEO_SYSTEM_MAP

## 1. Visione

PROMETEO e un sistema human-in-the-loop di supporto decisionale operativo per Team Leader in ambiente produttivo ad alta variabilita.

PROMETEO non e un MES, non e una dashboard enterprise pesante, non e un agente autonomo, non e un planner libero.

PROMETEO deve aiutare il TL a interrogare il sistema, riconoscere vincoli, conflitti, rischi e priorita operative, lasciando la decisione finale al Team Leader.

## 2. Obiettivo finale

Domanda TL -> recupero fonti autorizzate -> interpretazione dominio -> segnalazione vincoli/rischi/conflitti -> risposta breve e verificabile -> decisione umana tracciabile.

Interfaccia primaria: TL Chat.

## 3. Architettura stabile

Architettura dominio stabile: Order -> Route -> Station -> ProductionEvent.

Architettura operativa: Specifiche / SMF / Conoscenza TL / Eventi -> Retrieval governato -> Domain Model -> ATLAS Engine -> Planner deterministico -> TL Chat -> Audit / Eval / Guardrail.

ATLAS Engine segnala, confronta e spiega. Planner suggerisce. TL decide.

## 4. Modello dominio

Entita centrali: Order, Article, Drawing, Route, Station, Phase, ProductionEvent, Component, Constraint, Family, Rule, Source, TLConfirmation.

Dato operativo = fonte + confidence + motivo.

Confidence ammessa: CERTO, INFERITO, DA_VERIFICARE.

## 5. Moduli runtime

Moduli osservati: backend/app/api, backend/app/domain, backend/app/services, backend/app/repositories, backend/app/smf, backend/app/executor, backend/app/ingest, api_production, api_smf, api/tl_chat.

Responsabilita: API espongono funzioni operative; Domain interpreta articoli, route, stati e vincoli; Services orchestrano logiche applicative; Repositories gestiscono accesso dati; SMF collega dati produzione; Executor resta controllato e non decisionale; Ingest/OCR acquisisce dati in modo controllato.

## 6. Moduli AI

Moduli osservati: backend/app/atlas_engine, backend/app/ai_router, backend/app/ai_adapters, backend/app/semantic_registry, backend/app/agent_mod, backend/app/agent_runtime.

Regola: AI = supporto contestuale e spiegazione. AI != fonte autorevole. AI != planner autonomo. AI != decisore operativo.

## 7. Moduli dati

Fonti dati principali: specifiche reali, metadata normalizzati, SMF, registry locali, eventi produzione, test/eval, documentazione dominio.

Gerarchia fonti: Specifica reale + conferma TL > metadata normalizzato > SMF > registry locali > BOM/cache/export/preview > inferenza modello.

## 8. Flussi principali

TL Chat: domanda TL -> estrazione articolo/stazione/famiglia -> lettura fonti locali autorizzate -> normalizzazione confidence -> risposta breve.

Planner: ordini/eventi/componenti/stazioni -> vincoli -> priorita suggerita -> azione consigliata. Il planner non decide automaticamente.

ATLAS Engine: contesto -> segnali -> rischi -> conflitti -> spiegazione. ATLAS Engine resta separato dal planner deterministico.

## 9. Autorita delle fonti

Fonte autorevole primaria: specifica di finitura reale + conferma TL.

Fonti derivate: BOM, preview, cache, export, registry temporanei, dati inferiti.

Regola: una fonte derivata non puo prevalere su specifica reale o conferma TL.

## 10. Stato capability

Dominio produttivo: avanzato. Backend FastAPI: operativo. TL Chat: operativa ma da rafforzare. Planner: operativo ma da alimentare meglio. Retrieval: incompleto. Conflict Detection: debole. Eval operativo: iniziale. Documentazione sistema: da consolidare. Knowledge Graph logico: non ancora implementato come capability dedicata.

## 11. Gap aperti

Gap principali: mappa sistema non stabilizzata; retrieval governato non centralizzato; conflict detection non primaria; eval operativo non continuo; knowledge graph logico non formalizzato; distinzione runtime/legacy/preview da rafforzare; autorita delle fonti da rendere visibile in TL Chat.

## 12. Roadmap completamento

Sequenza corretta: MAPPARE -> UNIFICARE -> RETRIEVAL -> CONFLICT DETECTION -> EVAL -> KNOWLEDGE GRAPH CODE.

Capability immediate: PROMETEO_SYSTEM_MAP_001, GOVERNED_RETRIEVAL_001, CONFLICT_DETECTION_001, TL_CHAT_EVIDENCE_MODE_001, OPERATIONAL_EVAL_LOOP_001, KNOWLEDGE_GRAPH_LOGICAL_001.

## 13. Regole invarianti

ZAW1 e ZAW2 non sono intercambiabili. ZAW1_2 non e ZAW2. ZAW2 non va inferito da doppio passaggio ZAW. CP finale obbligatorio quando cp_required=true. COLLAUDO_VERTICALE e modalita macchina CP, non postazione separata. HENN non va inferito senza fonte confermata. Specifica reale + TL prevalgono su fonti incomplete. Non inventare route, componenti, stati o comportamenti. Planner suggerisce, TL decide. ATLAS Engine segnala e spiega, non muta il dominio direttamente.

## 14. Regole anti-regressione

Vietato: push diretto su main; modificare dati reali senza preview/diff/conferma; esporre .env o segreti; versionare immagini o specifiche private; introdurre database/UI/AI nuova senza capability chiara; confondere ATLAS Engine con Atlas Browser; trasformare TL Chat in dashboard pesante; trattare AI come fonte autorevole; espandere scope durante hardening; introdurre Knowledge Graph implementativo prima di completare la mappa logica.

## 15. Come usare questa mappa

Questo file e la prima lettura obbligatoria per ChatGPT, Codex, Claude, MiMo, Agent Mod e futuri agenti PROMETEO.

Uso previsto: leggere questa mappa -> capire architettura e vincoli -> identificare capability target -> limitare scope -> proporre patch/test solo se coerenti.

Criterio di successo: un agente nuovo deve capire PROMETEO in meno di 30 minuti senza ricostruire tutto da zero.
