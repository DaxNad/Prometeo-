# PROMETEO_DEVELOPMENT_CLOSURE_CANON_001

## Scopo

Estrarre da AI engineering, software engineering e casi di sviluppo riusciti un set di principi pratici per guidare PROMETEO fino alla chiusura operativa.

Questo documento non serve a celebrare figure individuali o citazioni autorevoli.
Serve a distillare pattern ripetibili da persone, pratiche e sistemi che hanno superato complessità reale.

## Tesi forte

Non cercare geni della programmazione in modo romantico.
Produce citazioni, non chiusura.

Cercare invece pattern ripetibili da chi ha affrontato complessità reale:

1. chi ha capito il cambio di paradigma AI;
2. chi costruisce software piccolo e robusto;
3. chi governa agenti e tool;
4. chi misura qualità con eval;
5. chi chiude prodotto senza scope creep;
6. chi ha costruito sistemi grandi mantenendo semplicità interna.

## Canone iniziale

| Asse | Riferimento | Cosa estrarre per PROMETEO |
|---|---|---|
| AI come nuovo paradigma | Andrej Karpathy | AI potente, ma non autorità; non sostituisce dominio, test e giudizio umano |
| Sistemi piccoli/locali | Simon Willison | Tool piccoli, fonti controllate, prompt injection awareness, contesto minimo |
| Agenti governati | Anthropic Engineering | Workflow prima di agenti autonomi; tool piccoli; contesto giusto al momento giusto |
| Output controllato | OpenAI Cookbook / Docs | Structured outputs, tool calling, eval, loop di riparazione |
| Eval reali | Hamel Husain | Sembra intelligente non vale; servono casi expected vs actual |
| Test-first AI coding | Kent Beck / TDD | Con AI i test diventano ancora più importanti |
| Integrazione continua | Martin Fowler | Piccoli incrementi, build automatica, errore rilevato presto |
| Semplicità strutturale | Rich Hickey | Semplice diverso da facile; separare concetti per ridurre entropia |
| Chiusura prodotto | Shape Up / Basecamp | Cicli finiti, appetite, rischio prima, no backlog infinito |

## Applicazione diretta a PROMETEO

### 1. Karpathy — AI potente, ma non autorità

Con i modelli neurali una parte del software diventa programmata dai dati, non scritta a mano riga per riga.
Questo rafforza una regola centrale: PROMETEO non deve mettere il dominio dentro il modello.
Dominio, fonti, regole ed eval devono restare fuori e sopra il modello.

Per PROMETEO:

- LLM = assistente probabilistico;
- PROMETEO Core = struttura deterministica;
- ATLAS Engine = reasoning controllato;
- TL = autorità finale.

### 2. Willison — piccolo, locale, verificabile

PROMETEO deve privilegiare sistemi piccoli, locali, ispezionabili e difendibili.
Il rischio principale non è solo che l’AI sbagli, ma che riceva troppo contesto, fonti non autorizzate o istruzioni contaminate.

Per PROMETEO:

- niente prompt enormi;
- niente agente libero;
- retrieval piccolo e autorizzato;
- fonti tracciabili;
- log e audit.

### 3. Anthropic — workflow prima dell’agente

Prima di costruire agenti autonomi bisogna costruire workflow semplici, componibili e verificabili.
PROMETEO deve procedere per capability chiuse, tool piccoli e confini espliciti.

Per PROMETEO:

- prima retrieval governato;
- poi eval;
- poi tool piccoli;
- poi agenti limitati;
- mai agente generale libero.

### 4. OpenAI — output strutturato ed eval

TL Chat non deve produrre testo libero da fidarsi.
Deve produrre output aderenti a schema, validabili, auditabili e confrontabili con expected.

Flusso desiderato:

1. domanda TL;
2. retrieval autorizzato;
3. output strutturato;
4. validazione schema;
5. risposta breve;
6. audit;
7. eval.

### 5. Hamel — eval come motore di miglioramento

Una risposta plausibile non dimostra che il sistema funzioni.
PROMETEO deve misurarsi su casi reali expected vs actual.

Esempio:

- input: domanda su articolo 12100;
- expected:
  - ZAW1 corretto;
  - non inferire ZAW2;
  - CP finale;
  - risposta breve;
  - eventuale DA_VERIFICARE se manca fonte.

### 6. Kent Beck — con AI, TDD diventa più importante

Gli agenti AI possono generare codice plausibile ma regressivo.
Il test non rallenta PROMETEO: lo protegge.

Sequenza obbligatoria:

1. contratto;
2. test;
3. patch;
4. guard;
5. PR.

### 7. Fowler — integrazione continua come anti-entropia

PROMETEO non deve accumulare lavoro non verificato.
Ogni integrazione deve essere piccola, verificata e riportare main a stato pulito.

Regole:

- mai branch lunghi senza test;
- mai capability multiple insieme;
- mai considerare chiuso ciò che non passa guard e check;
- main deve restare affidabile.

### 8. Rich Hickey — semplice batte facile

La via facile può aumentare la complessità.
La semplicità richiede separazione dei concetti.

Separazioni da preservare:

- domain model separato;
- planner separato;
- ATLAS Engine separato;
- LLM separato;
- retrieval separato;
- eval separati;
- fonti separate.

### 9. Shape Up — chiusura, non backlog infinito

PROMETEO non deve crescere per accumulo di funzionalità.
Ogni ciclo deve chiedere: cosa chiudiamo, quale rischio bruciamo, quando diciamo stop.

Domande obbligatorie:

- Qual è l’appetite reale?
- Quale rischio va affrontato prima?
- Qual è il criterio di stop?
- Cosa non facciamo in questo ciclo?

## Le 12 leggi operative di PROMETEO

1. PROMETEO non deve sembrare intelligente; deve essere verificabile.
2. Il dominio resta nel codice, nei metadata, nei documenti e negli eval, non nel modello.
3. LLM supporta, non decide.
4. TL decide, il sistema registra.
5. Ogni nuova capability deve avere contratto, test, guard e criterio di chiusura.
6. Nessuna nuova architettura senza rimuovere rischio reale.
7. Retrieval prima di fine-tuning.
8. Eval prima di fiducia.
9. Tool piccoli prima di agenti.
10. Output strutturato prima di testo libero.
11. CI, PR e check verdi prima di considerare chiuso.
12. Semplicità strutturale prima di comodità momentanea.

## Anti-pattern vietati

- Cercare citazioni invece di criteri operativi.
- Aggiungere architettura senza rischio reale da rimuovere.
- Usare LLM come fonte autorevole.
- Usare agenti liberi.
- Fare fine-tuning prima di retrieval, regole, guardrail ed eval.
- Accumulare backlog senza capability chiuse.
- Aprire più capability nello stesso ciclo.
- Scrivere codice senza contratto o test minimo.
- Fondere planner, ATLAS Engine, LLM, retrieval e TL Chat in un unico blocco.
- Creare dashboard pesanti che aumentano il carico del Team Leader.

## Checklist di chiusura capability

Una capability PROMETEO è chiusa solo se:

- ha nome stabile;
- ha obiettivo esplicito;
- ha scope limitato;
- ha file ammessi dichiarati;
- ha file vietati dichiarati;
- ha test o verifica minima;
- non modifica runtime fuori scope;
- non introduce architettura laterale;
- preserva Order -> Route -> Station -> ProductionEvent;
- preserva TL come autorità finale;
- produce diff leggibile;
- passa guard locali;
- passa check CI quando applicabile;
- ha criterio PASS/FAIL chiaro;
- lascia main in stato migliore o almeno non peggiore.

## Roadmap di chiusura progetto

PROMETEO deve avanzare per blocchi chiusi, non per entusiasmo espansivo.

Sequenza guida:

1. consolidare documenti guida essenziali;
2. chiudere capability documentali che riducono entropia;
3. rafforzare guard e contratti;
4. misurare TL Chat con eval piccoli;
5. densificare dominio reale con human-in-the-loop;
6. estendere retrieval governato;
7. introdurre tool piccoli e limitati;
8. introdurre agenti solo se vincolati da contratto, scope, log, eval e rollback;
9. chiudere progressivamente il sistema operativo reale;
10. evitare ogni espansione non necessaria.

## Principio finale

PROMETEO non si chiude diventando più grande.
PROMETEO si chiude diventando più verificabile, più semplice, più governato e più utile nel turno reale.

La domanda guida non è: cosa possiamo aggiungere?
La domanda guida è: cosa possiamo chiudere adesso senza aumentare entropia?
