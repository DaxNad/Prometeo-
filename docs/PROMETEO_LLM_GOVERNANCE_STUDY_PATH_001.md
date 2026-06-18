# PROMETEO — LLM Governance Study Path 001

## Stato

Documento di governance e studio operativo per l’uso controllato degli LLM dentro PROMETEO.

Questo documento non abilita runtime, non collega TL Chat, non collega ATLAS Engine, non collega planner, non introduce agenti autonomi e non modifica il dominio operativo.

---

## Obiettivo

Capire come usare gli LLM in modo governato per:

* evitare fine-tuning prematuro;
* evitare agenti non controllati;
* evitare contesto eccessivo;
* migliorare TL Chat;
* rafforzare ATLAS Engine come reasoning controllato;
* introdurre retrieval locale verificabile;
* introdurre eval misurabili;
* mantenere PROMETEO coerente con l’architettura esistente.

---

## Architettura da preservare

```text
Order
  ↓
Route
  ↓
Station
  ↓
ProductionEvent
```

Ruoli corretti:

```text
PROMETEO Core  = deterministico
ATLAS Engine   = reasoning controllato
LLM            = supporto contestuale
Retrieval      = recupero fonti autorizzate
Eval           = verifica qualità
TL             = autorità finale
```

---

## Regola fondamentale

```text
Fine-tuning = ultima opzione
```

Prima del fine-tuning devono essere valutati e, dove possibile, implementati:

```text
retrieval
regole
guardrail
eval
human-in-the-loop
```

Il fine-tuning non deve essere usato per memorizzare conoscenza operativa, dati PROMETEO, specifiche, SMF, route, BOM, decisioni TL o logica di pianificazione.

---

## Percorso di studio

### 1. Andrej Karpathy

Scopo: capire cosa sono realmente gli LLM.

Studiare:

* Intro to Large Language Models
* Deep Dive into LLMs
* How I Use LLMs

Da estrarre:

```text
LLM ≠ database
LLM ≠ planner
LLM ≠ fonte autorevole
```

Definizione operativa:

```text
LLM = motore probabilistico
      + contesto
      + strumenti
```

Domanda guida:

```text
Cosa NON devo affidare al modello?
```

---

### 2. Simon Willison

Scopo: capire come costruire sistemi piccoli, robusti e verificabili.

Studiare:

* Local LLM
* Embeddings
* Prompt Injection
* RAG
* Language Models on the Command Line

Da estrarre:

```text
locale
auditabile
ripetibile
semplice
SQLite/file
fonti verificabili
```

Domanda guida:

```text
Come recupero la conoscenza senza addestrare un modello?
```

---

### 3. OpenAI Cookbook

Scopo: trasformare la teoria in implementazione controllata.

Studiare solo:

* Structured Outputs
* Tool Calling
* Retrieval
* Evals

Applicazione PROMETEO:

```text
Domanda TL
    ↓
retrieval locale autorizzato
    ↓
contesto minimo
    ↓
JSON controllato
    ↓
validazione schema
    ↓
risposta TL
    ↓
audit log
    ↓
eval
```

Da evitare:

```text
LLM libero
    ↓
risposta plausibile
    ↓
ci fidiamo
```

---

### 4. Anthropic Engineering

Scopo: capire agenti governati e context engineering.

Studiare:

* Context Engineering
* Tool Use
* Building Effective Agents
* Writing Tools for Agents

Principio chiave:

```text
L’agente non deve sapere tutto.
```

Deve sapere:

```text
quale fonte usare
quando usarla
con quali limiti
con quale output atteso
con quale audit
```

Applicazione PROMETEO:

```text
ATLAS Engine
fonti autorizzate
tool piccoli
contesto minimo
nessun agente libero
nessun accesso indiscriminato al repo
nessun accesso automatico a dati reali
```

---

### 5. Hamel Husain

Scopo: imparare a misurare.

Studiare:

* LLM Evals
* RAG Evals
* Domain Specific Evaluation Systems

Domanda guida:

```text
PROMETEO migliora davvero il lavoro operativo?
```

Non basta chiedere:

```text
La risposta sembra intelligente?
```

Serve misurare:

```text
expected vs actual
fonti usate
errori
ambiguità
verdict
regressioni
```

Verdict ammessi:

```text
PASS
FAIL
DA_VERIFICARE
```

---

## Traduzione diretta in PROMETEO

Direzione corretta:

```text
OCR
  ↓
Estrazione strutturata
  ↓
Retrieval locale
  ↓
LLM controllato
  ↓
Eval
  ↓
Human-in-the-loop
```

Direzione da evitare:

```text
OCR
  ↓
Fine-tuning
  ↓
Speriamo funzioni
```

---

## Decision Gate LLM

Prima di aprire una capability AI, verificare:

```text
1. Sto usando l’LLM come database?
2. Sto usando l’LLM come planner?
3. Sto usando l’LLM come fonte autorevole?
4. Ho già provato retrieval locale?
5. Ho già definito fonti autorizzate?
6. Ho già definito schema output?
7. Ho già definito eval?
8. Ho già previsto audit log?
9. Il TL resta autorità finale?
10. Il fine-tuning è davvero necessario?
```

Verdict:

```text
PASS
FAIL
DA_VERIFICARE
BLOCK
```

---

## Capability futura naturale

Nome possibile:

```text
PROMETEO_RAG_EVAL_001
```

Scope:

```text
input:
domanda TL

retrieval:
fonti locali autorizzate

output:
risposta controllata

eval:
expected vs actual

verdict:
PASS / FAIL / DA_VERIFICARE
```

Vincoli:

```text
nessun agente libero
nessun fine-tuning
nessuna lettura indiscriminata del repo
nessun accesso automatico a dati reali
nessun binding runtime senza contratto dedicato
nessun collegamento a planner senza guard dedicato
```

---

## Sintesi operativa

```text
Karpathy  → capire gli LLM
Willison  → costruire sistemi robusti
OpenAI    → implementare
Anthropic → governare
Hamel     → misurare
```

Per PROMETEO, il ROI iniziale più alto resta:

```text
OCR
+
estrazione strutturata
+
retrieval
+
eval
+
human-in-the-loop
```

Non:

```text
fine-tuning prematuro
agenti liberi
contesto enorme
fiducia cieca nella risposta del modello
```

---

## Verdict documento

```text
STATUS: DOCUMENTAL_GOVERNANCE_ONLY
RUNTIME_ENABLED: false
TL_CHAT_BINDING: false
ATLAS_ENGINE_BINDING: false
PLANNER_BINDING: false
FINE_TUNING_ENABLED: false
```

Questo documento serve come riferimento operativo e filtro anti-deriva per future capability LLM di PROMETEO.
