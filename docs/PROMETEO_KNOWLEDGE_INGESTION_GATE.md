# PROMETEO - KNOWLEDGE INGESTION GATE

## Status

ACTIVE - GOVERNANCE GATE

Questo documento traduce il Principio Fondamentale di PROMETEO in un gate operativo per valutare ogni nuova capability prima dello sviluppo.

PROMETEO esiste per trasformare conoscenza operativa reale in conoscenza strutturata, recuperabile, verificabile e riutilizzabile.

Ogni capability deve essere valutata rispetto alla sua capacita di migliorare almeno una parte del ciclo:

Conoscenza reale
-> Acquisizione
-> Classificazione
-> Collegamento
-> Memoria
-> Retrieval
-> Risposta TL

---

## 1. Domanda obbligatoria

Prima di aprire una nuova capability, rispondere:

Questa modifica aumenta la capacita di PROMETEO di acquisire, organizzare, recuperare o utilizzare conoscenza operativa reale?

Se la risposta e NO, la capability non e prioritaria e deve essere parcheggiata.

---

## 2. Scheda gate minima

Ogni capability futura deve dichiarare:

knowledge_ingestion_gate:
  capability_name:
  objective:

  contributes_to:
    acquisition: false
    classification: false
    domain_linking: false
    memory: false
    retrieval: false
    tl_response: false
    traceability: false

  evidence:
    source:
    expected_runtime_value:
    expected_tl_value:

  risk:
    adds_complexity:
    touches_runtime:
    touches_real_data:
    touches_smf:
    touches_database:

  verdict:
    priority: PRIORITY | SECONDARY | PARKED
    reason:

---

## 3. Regola di priorita

Una capability e PRIORITY solo se migliora almeno uno di questi punti:

- acquisizione di conoscenza reale;
- classificazione controllata;
- collegamento al dominio Order -> Route -> Station -> ProductionEvent;
- memoria verificabile;
- retrieval da fonti autorizzate;
- qualita della risposta TL;
- tracciabilita di fonte, confidence e motivo.

Una capability e SECONDARY se supporta indirettamente questi punti ma non li migliora da sola.

Una capability e PARKED se non contribuisce al ciclo fondamentale.

---

## 4. Regola anti-deriva

Sono segnali di deriva:

- nuova UI senza miglioramento del ciclo conoscenza -> risposta TL;
- nuova AI senza fonte, confidence, retrieval o eval;
- nuovo planner senza collegamento a conoscenza reale acquisita;
- refactor non necessario al recupero o uso della conoscenza;
- automazione che scrive dati definitivi senza preview e conferma TL;
- complessita architetturale non giustificata da valore operativo.

In presenza di deriva, la capability deve essere fermata o ridotta.

---

## 5. Vincoli permanenti

Il gate non autorizza:

- scrittura automatica su dati reali senza preview;
- modifica di SMF reale;
- modifica di .env o segreti;
- uso di specifiche reali non sanificate;
- AI come fonte autorevole;
- planner autonomo;
- bypass della conferma TL.

---

## 6. Output atteso del gate

Prima di sviluppare, ogni capability deve produrre un verdetto:

GO = prioritaria e coerente
HOLD = utile ma non ora
PARKED = fuori priorita
BLOCK = rischiosa o incoerente

Il verdetto deve essere breve, motivato e verificabile.

---

## 7. Esempio

knowledge_ingestion_gate:
  capability_name: tl-board-planner-contract-001
  objective: proteggere il contratto dati tra planner e TL Board

  contributes_to:
    acquisition: false
    classification: false
    domain_linking: true
    memory: false
    retrieval: false
    tl_response: true
    traceability: true

  evidence:
    source: /production/sequence contract
    expected_runtime_value: impedisce regressioni dei campi usati dalla TL Board
    expected_tl_value: mantiene affidabile la lettura operativa della sequenza

  risk:
    adds_complexity: low
    touches_runtime: false
    touches_real_data: false
    touches_smf: false
    touches_database: false

  verdict:
    priority: PRIORITY
    reason: protegge la forma minima della conoscenza operativa usata dalla risposta TL

---

## 8. Legge operativa

Nessuna capability futura dovrebbe partire senza questo gate compilato almeno in forma sintetica.

Il gate non sostituisce il giudizio TL. Serve a evitare dispersione, scope creep e sviluppo non collegato alla conoscenza operativa reale.
