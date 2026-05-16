---

THIS DOCUMENT IS NOT A SEMANTIC SOURCE OF TRUTH.

Canonical domain semantics, planner constraints,
AI governance, TL operational rules,
station/process taxonomy and permanent policies
are defined exclusively in:

docs/PROMETEO_MASTER.md

This file exists only as:

* historical reference
* implementation support
* technical context
* archived material
* extracted summary

In case of conflict:
PROMETEO_MASTER.md prevails.

---

# PROMETEO — TL STRATEGY (ROBUST DOMAIN RULE)

## REGOLA MADRE
Il Team Leader costruisce la strategia produttiva del turno partendo dal **DISEGNO**.

Il disegno è la chiave logica che consente di riconoscere il comportamento produttivo del codice.

Il codice interno è un identificatore gestionale.
Il disegno rappresenta la realtà tecnica del pezzo.

---

# OBIETTIVO DEL TL

Costruire una sequenza di produzione che permetta contemporaneamente:

1. rispetto delle date di consegna cliente
2. saturazione equilibrata degli operatori
3. riduzione dei cambi setup
4. continuità del flusso produttivo
5. avanzamento costante dei complessivi
6. mantenimento della produttività media per operatore
7. prevenzione colli di bottiglia nelle postazioni critiche

indicatore tipico:
≈ 90–100 pezzi per operatore per turno
(variabile in funzione della complessità)

---

# LOGICA DECISIONALE REALE

## INPUT PRINCIPALI

### lato cliente
- codice
- quantità richiesta
- data consegna

### lato tecnico (derivato dal disegno)
- famiglia tecnica
- tipo di connettore
- tipo di guaina
- presenza O-ring
- numero fasi
- postazioni coinvolte
- attrezzature richieste
- complessità ciclo

### lato operativo
- disponibilità materiali
- operatori disponibili
- saturazione postazioni
- carico turno precedente

---

# SEQUENZA DECISIONALE TL

## 1. riconoscimento disegno
dal disegno il TL identifica immediatamente:

- comportamento produttivo
- compatibilità con altri codici
- criticità possibili
- complessità relativa

il disegno attiva esperienza pregressa.

---

## 2. classificazione codice

il TL identifica se il codice è:

### singolo
codice producibile autonomamente

oppure

### parte di complessivo
codice necessario per completamento prodotto finale

---

## 3. verifica disponibilità materiali

il codice è producibile se disponibili:

- connettori
- O-ring
- guaine
- componenti plastici
- imballi

assenza materiale → codice non pianificabile

---

## 4. selezione codice iniziale turno

il turno inizia preferibilmente con codici:

- lineari
- ad alta rotazione
- con pochi cambi tool
- con poche fasi
- con quantità adeguata

obiettivo:

stabilizzare il flusso produttivo.

---

## 5. accorpamento codici compatibili

il TL accorpa codici con comportamento produttivo simile:

- stessi componenti principali
- stessi connettori
- stessi tool ZAW
- sequenza operativa simile

obiettivo:

- ridurre cambi setup
- aumentare produttività oraria

---

## 6. inserimento codici complessità media

il TL inserisce codici mediamente complessi per mantenere ritmo stabile.

---

## 7. gestione codici TASSATIVI

ogni turno deve produrre una quota di:

parziali di complessivi

questi codici sono definiti:

**TASSATIVI**

perché necessari per completamento assemblaggi finali.

anche se meno efficienti, devono avanzare.

---

# EQUILIBRIO DEL TURNO

il TL costruisce un equilibrio tra:

- codici veloci
- codici medi
- codici tassativi

per mantenere continuità produttiva.

---

# COMPORTAMENTO PRODUTTIVO (CONCETTO CHIAVE)

due codici sono compatibili se:

richiedono sequenze simili di lavorazione.

la compatibilità è definita da:

- componenti principali condivisi
- stesse postazioni
- stessi tool ZAW
- complessità simile
- tempo ciclo simile

il disegno consente di riconoscere rapidamente questa compatibilità.

---

# POSTAZIONI CRITICHE

attenzione prioritaria a:

- ZAW
- PIDMILL
- HENN
- CP

CP è fase finale bloccante.

---

# OUTPUT ATTESO DEL TL

sequenza di codici che consenta:

- continuità operativa
- riduzione tempi morti
- avanzamento complessivi
- rispetto consegne cliente

---

# RUOLO DI PROMETEO

PROMETEO deve supportare il TL nel:

rendere visibili:

- codici con comportamento produttivo simile
- componenti condivisi critici
- impatto su ZAW
- impatto su PIDMILL
- compatibilità sequenza
- codici tassativi da avanzare

PROMETEO non sostituisce la decisione del TL.

PROMETEO riduce il tempo necessario per costruire la strategia turno.

---

# VINCOLO DI PROGETTAZIONE

qualsiasi funzione planner futura deve essere coerente con questa logica.

il sistema deve adattarsi al flusso reale del reparto.

non il contrario.
