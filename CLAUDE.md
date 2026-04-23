# PROMETEO — CLAUDE CODE OPERATING CONTEXT

## Identità del progetto

PROMETEO non è un gestionale generico e non è un MES classico.

PROMETEO è un orchestratore decisionale AI-driven per reparti produttivi manuali o semi-manuali.

Il focus non è l'automazione PLC, ma il supporto operativo al Team Leader nella gestione di:

- priorità cliente
- componenti condivisi critici
- saturazione postazioni
- colli di bottiglia
- passaggio consegne tra turni
- continuità decisionale
- eventi operativi reali di reparto

PROMETEO deve aiutare a capire:

- cosa fare adesso
- cosa blocca il flusso
- quale componente impatta più articoli
- quale postazione è critica
- quale azione TL è richiesta

---

## Regole architetturali permanenti

### 1. Non cambiare architettura senza necessità
Mantenere l'architettura attuale salvo richiesta esplicita.

Stack attuale:

- backend: FastAPI
- database: PostgreSQL
- frontend: React
- deploy: Railway
- edge runtime locale: Mac / iPhone
- bridge dati: SMF / Excel nelle fasi iniziali

### 2. Modello dominio da preservare
Il dominio da preservare è:

Order → Phase → Station → ProductionEvent

PROMETEO usa un approccio event-driven semplificato.

Non introdurre CQRS, microservizi, code distribuite o pattern enterprise superflui se non richiesti esplicitamente.

### 3. Regola anti-biforcazione
Non creare biforcazioni tra:

- smf_core
- backend
- planner
- event engine
- state engine
- frontend

Ogni modifica deve mantenere coerenza tra questi layer.

### 4. Eventi runtime
Gli eventi operativi reali devono poter influenzare:

- stato postazione
- machine load / saturazione postazioni
- sequenza produzione
- priorità operativa

### 5. Nessuna automazione fittizia
PROMETEO non deve assumere un contesto full-automation se non esplicitamente presente.

In PROMETEO:

- "machine" spesso significa "postazione"
- "event" significa spesso "segnalazione operativa"
- "severity" significa "impatto operativo"

Il linguaggio tecnico resta valido nel backend, ma la lettura operativa deve essere coerente con il reparto manuale.

---

## Vocabolario operativo da rispettare

### Linguaggio tecnico
Usare nel backend / DB / API / log:

- ProductionEvent
- Machine Load
- State
- Severity
- Rule
- Cluster
- Driver
- Planner

### Lettura operativa TL
Usare nel frontend / mobile view / dashboard:

- Segnalazione operativa
- Saturazione postazioni
- Stato operativo
- Impatto operativo
- Gruppo lavorazione
- Componente vincolante
- Suggeritore sequenza
- Logica reparto

Non eliminare il linguaggio tecnico: applicare dual-layer terminology quando utile.

---

## Vincoli operativi di sviluppo

### 1. File completi, non patch
Fornire sempre file integrali pronti da sostituire.

Evitare diff parziali salvo richiesta esplicita.

### 2. Comandi terminale completi
Quando proponi azioni terminale, dare sempre comandi completi e corretti.

### 3. Non usare nano
Non proporre nano come editor.

Usare sempre metodi tipo:

- cat <<'EOF'
- sostituzione file completa
- comandi ripetibili

### 4. Un passo alla volta
Guidare in modo sequenziale.

Non accumulare troppi task insieme se il flusso può essere guidato in step chiari.

### 5. Non chiedere all'utente di decidere il prossimo step quando il flusso è ovvio
Se il passo successivo è chiaro, proporlo direttamente.

### 6. Ridurre teoria, massimizzare operatività
Rispondere in modo pratico, concreto, orientato all'esecuzione.

---

## Contesto produttivo reale da rispettare

PROMETEO serve un reparto reale con:

- banchi assemblaggio
- ZAW-1
- ZAW-2
- PIDMILL
- HENN
- ULTRASUONI
- CP
- GUAINE
- altre postazioni manuali / semi-manuali

Le priorità reali dipendono da:

- componenti condivisi
- componenti plastici comuni
- O-ring crimpati
- componenti critici che bloccano più articoli
- date cliente
- saturazione postazione
- stato turno
- continuità operativa TL

### Regola importante
Un singolo componente condiviso può impattare più articoli contemporaneamente.

Esempio: un driver condiviso ZAW può bloccare o alterare la sequenza di più codici.

PROMETEO deve rendere visibile questa dipendenza.

---

## Obiettivi software permanenti

### 1. Vista TL mobile
La vista Team Leader mobile deve essere semplice, leggibile e azionabile da iPhone.

Deve privilegiare:

- criticità attive
- prossima azione TL
- saturazione rapida postazioni
- sequenza breve
- segnalazioni aperte

### 2. Event awareness
Un evento OPEN deve poter influenzare:

- state layer
- machine load
- sequence planner
- priorità TL

### 3. PWA / app installabile
PROMETEO deve evolvere verso una PWA installabile.

### 4. Coerenza dominio prima di espansione
Prima si consolida il dominio.
Poi si estende.

---

## Modalità di lavoro richiesta a Claude Code

Quando lavori sul codebase PROMETEO:

1. Leggi il file reale prima di modificarlo.
2. Mantieni naming e struttura attuali se non c'è un motivo forte per cambiarli.
3. Se aggiungi un nuovo campo backend, verifica subito impatto su frontend.
4. Se un endpoint cambia payload, allinea anche i componenti React che lo consumano.
5. Se un errore è causato da mismatch campo/endpoint, preferire allineamento minimo, non refactor esteso.
6. Tratta sempre i 404 frontend come possibili endpoint non implementati, non come bug casuali.
7. Quando possibile, migliorare senza allargare il perimetro.

---

## Cosa NON fare

Non fare queste cose salvo richiesta esplicita:

- non migrare architettura
- non introdurre framework nuovi
- non spezzare il progetto in troppi layer
- non sostituire FastAPI/React/Postgres
- non rinominare in massa file o cartelle
- non introdurre complessità enterprise superflua
- non inventare dominio produttivo non confermato
- non trattare PROMETEO come prodotto generico per fabbrica automatica

---

## Strategia preferita

Per PROMETEO la strategia preferita è:

- piccoli avanzamenti coerenti
- test reali
- backend e frontend sempre allineati
- sviluppo locale prima del deploy
- output leggibile per Team Leader
- mantenimento della spina dorsale architetturale

---

## Pattern di risposta preferito

Quando proponi una modifica:

1. spiega in una riga cosa stai correggendo
2. fornisci file completo
3. fornisci comando completo
4. indica test immediato da fare
5. non aggiungere teoria non richiesta

---

## Nota finale

PROMETEO non deve semplicemente mostrare dati.

Deve trasformare segnali di reparto in decisioni operative leggibili.

Obiettivo finale:

segnalazione operativa reale
→ impatto su stato postazione
→ impatto su saturazione
→ impatto su sequenza
→ azione TL chiara

Per contesto esteso: docs/PROMETEO_MASTER.md
