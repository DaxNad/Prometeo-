# PROMETEO_CONTEXT_ACCESS_BINDING_001

## Scopo

Definire il primo binding documentale minimo che permette a PROMETEO di sapere quali informazioni locali può consultare, con quale priorità e con quali divieti.

Questo documento non collega ancora il runtime.
Non modifica backend, frontend, planner, database, SMF o specifiche reali.

Serve come contratto preliminare per futuri moduli di retrieval governato, TL Chat, ATLAS Engine e memoria persistente file-based.

## Stato

- Tipo: documentale
- Runtime: non collegato
- Backend: non modificato
- Frontend: non modificato
- Planner: non modificato
- Database: non modificato
- SMF reale: non toccato
- specs_finitura: non toccata

## Problema che risolve

PROMETEO possiede molte informazioni locali distribuite tra documenti, memory file-based, report e contratti.
Senza un binding esplicito, il rischio è che un futuro retrieval legga fonti duplicate, obsolete, derivate o non autorevoli come se fossero tutte equivalenti.

Il binding introduce una gerarchia di accesso e autorità.

## Fonti locali rilevate

| Fonte | Stato | Ruolo | Accesso futuro | Autorità |
|---|---:|---|---|---|
| docs/PROMETEO_MASTER.md | presente | documento master storico e operativo | lettura controllata | alta, ma da interpretare con documenti più recenti |
| docs/PROMETEO_SYSTEM_MAP.md | presente | mappa sistema primaria | lettura controllata | alta |
| docs/PROMETEO_AGENT_OPERATING_MODEL.md | presente | modello operativo agenti governati | lettura controllata | alta |
| docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md | presente | canone anti-entropia e chiusura capability | lettura controllata | alta per governance sviluppo |
| docs/LLM_GOVERNANCE_PROMETEO.md | presente | regole LLM governati | lettura controllata | alta per uso LLM |
| docs/GOVERNED_RETRIEVAL_001.md | presente | base retrieval governato | lettura controllata | alta per retrieval |
| docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md | presente | contratto binding memoria/retrieval | lettura controllata | alta per memory retrieval |
| docs/MEMORY_RETRIEVAL_CONSOLIDATION_001.md | presente | consolidamento memoria/retrieval | lettura controllata | media-alta |
| docs/MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001.md | presente | contratto runtime retrieval | solo lettura documentale per ora | alta ma non attiva runtime |
| memory/ | presente | memoria persistente file-based | futura lettura filtrata | da classificare per file |
| data/local_reports/ | presente | report locali e diagnostici | lettura limitata | bassa/media, supporto non fonte primaria |

## Fonti cercate ma non presenti

| Nome atteso | Stato | Decisione |
|---|---:|---|
| docs/LLM_GOVERNANCE.md | assente | non creare alias ora; usare docs/LLM_GOVERNANCE_PROMETEO.md |
| docs/LLM_GOVERNANCE_CANON.md | assente | non creare alias ora; usare docs/LLM_GOVERNANCE_PROMETEO.md e canone closure |
| docs/PERSISTENT_MEMORY_001.md | assente | non creare alias ora; usare memory/ e contratti MEMORY_RETRIEVAL_* |

## Gerarchia di autorità informativa

### Livello A — Autorità operativa primaria

1. Specifica reale quando presente e verificata.
2. Conferma esplicita del Team Leader.
3. Metadata normalizzato con fonte e confidence.

Nota: questo documento non autorizza ancora accesso diretto automatico a specs_finitura o dati reali.

### Livello B — Architettura e governance

1. docs/PROMETEO_SYSTEM_MAP.md
2. docs/PROMETEO_AGENT_OPERATING_MODEL.md
3. docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md
4. docs/LLM_GOVERNANCE_PROMETEO.md
5. docs/GOVERNED_RETRIEVAL_001.md
6. docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md

### Livello C — Contesto master storico

1. docs/PROMETEO_MASTER.md

Il master è utile, ma può contenere stratificazioni storiche.
Quando entra in conflitto con documenti più recenti e mirati, prevale il documento più recente se coerente con gli invarianti del dominio.

### Livello D — Supporto diagnostico

1. data/local_reports/
2. export, preview, cache, staging, report tecnici

Queste fonti sono supporti di analisi.
Non devono diventare fonte autorevole senza controllo incrociato.

## Invarianti che il binding deve preservare

- PROMETEO non è un MES.
- PROMETEO non è un planner autonomo.
- PROMETEO non è un agente libero.
- TL Chat è l'interfaccia primaria.
- ATLAS Engine segnala e spiega, ma non muta il dominio.
- Planner deterministico suggerisce, non decide.
- Team Leader decide e il sistema registra.
- Dominio stabile: Order -> Route -> Station -> ProductionEvent.
- LLM supporta, non decide.
- Retrieval prima di fine-tuning.
- Eval prima di fiducia.
- Output strutturato prima di testo libero.

## Regole di accesso future

Un futuro modulo PROMETEO potrà accedere alle fonti solo se rispetta queste condizioni:

1. legge solo percorsi autorizzati;
2. produce elenco fonti consultate;
3. distingue fonte primaria, fonte derivata, inferenza e supporto;
4. assegna confidence: CERTO, INFERITO o DA_VERIFICARE;
5. non usa LLM come fonte autorevole;
6. non modifica file durante la fase di retrieval;
7. non accede a dati reali sensibili senza guard dedicato;
8. non legge specs_finitura automaticamente in questa fase;
9. non usa data/local_reports come verità primaria;
10. non collega runtime senza contratto e test dedicati.

## Percorsi ammessi in questa fase

```text
docs/
memory/
data/local_reports/ solo lettura
```

## Percorsi vietati in questa fase

```text
backend/
frontend/
runtime/
planner
database
SMF reale
specs_finitura
.env
node_modules
venv
cache operative non classificate
```

## Uso previsto da parte di TL Chat

TL Chat potrà in futuro usare questo binding per sapere dove cercare contesto, ma non deve ancora farlo automaticamente.

Flusso futuro desiderato:

```text
domanda TL
-> classificazione intento
-> scelta fonti autorizzate
-> retrieval minimo
-> sintesi con fonti
-> output breve
-> confidence
-> eventuale DA_VERIFICARE
-> audit
```

## Uso previsto da parte di ATLAS Engine

ATLAS Engine potrà usare questo binding come mappa per distinguere:

- regole di dominio;
- governance;
- memoria persistente;
- report diagnostici;
- fonti derivate;
- informazioni da verificare.

ATLAS Engine non deve mutare direttamente file, metadata, planner o database.

## Uso previsto da parte del planner

Il planner non deve leggere direttamente questo documento come sorgente runtime decisionale.

Questo binding può guidare futuri adapter o resolver, ma il planner deve restare deterministico e alimentato da dati già normalizzati, validati e testati.

## Regola anti-duplicazione

Non creare nuovi documenti paralleli se un concetto è già coperto da un documento autorevole.

Se serve correggere o consolidare:

1. identificare fonte esistente;
2. verificare conflitto;
3. proporre diff mirato;
4. aggiornare documento canonico;
5. evitare duplicazione.

## Criterio PASS

Questo binding è valido se:

- esiste come documento locale;
- non modifica runtime;
- non introduce nuove fonti operative non verificate;
- chiarisce fonti ammesse e vietate;
- conserva gerarchia di autorità;
- prepara retrieval futuro senza attivarlo.

## Criterio FAIL

Il binding è fallito se:

- viene usato per collegare runtime senza test;
- autorizza accesso indiscriminato a specs_finitura o SMF reale;
- tratta report/cache/export come fonte primaria;
- confonde ATLAS Engine con Atlas Browser;
- permette all'LLM di decidere o correggere il dominio autonomamente;
- aumenta documentazione duplicata invece di ridurre entropia.

## Decisione finale

PROMETEO può iniziare ad accedere al proprio contesto solo tramite binding governato.

Prima si mappa.
Poi si classifica.
Poi si testa.
Solo dopo si collega al runtime.

Questo documento chiude la prima fase: mappa minima di accesso al contesto.
