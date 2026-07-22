# PROMETEO_DEVELOPMENT_ENVIRONMENT_MIGRATION_FROM_ATLAS_001

## Stato

PIANIFICATA

## Esito iniziale

MIGRATION_PLAN_READY

La migrazione non è dichiarata completata. La chiusura richiede almeno una verticale Prometeo eseguita interamente senza dipendere da Atlas.

## Motivazione

ChatGPT Atlas è previsto cessare il funzionamento il 9 agosto 2026.

Prometeo non dipende tecnicamente da Atlas per repository, Terminale, backend, frontend, test, OCR, registry, Work, Codex, GitHub Actions o Vercel. Atlas costituisce prevalentemente una dipendenza operativa e informativa: lettura della pagina aperta, side chat, gestione delle schede, continuità tra browser e conversazione, segnalibri e cronologia.

La migrazione deve preservare il metodo robusto e deterministico di sviluppo senza sostituire una dipendenza non governata con un'altra.

## Data limite

Data esterna prevista: 9 agosto 2026.

Data interna raccomandata per completare gli smoke sostitutivi: 2 agosto 2026.

La verifica finale non deve essere rinviata all'ultimo giorno utile.

## Principio di continuità

La fonte primaria dello sviluppo Prometeo resta:

Repository GitHub  
→ Terminale locale  
→ test  
→ smoke host  
→ commit  
→ branch  
→ pull request  
→ controlli CI  
→ squash merge  
→ riallineamento locale  
→ closure documentale

Atlas non è una dipendenza tecnica di questa catena.

## Matrice delle capacità

| Capacità | Uso attuale con Atlas | Dipendenza reale | Sostituto candidato | Verifica necessaria | Stato |
|---|---|---|---|---|---|
| Git e repository | Supporto contestuale | Nessuna | Git CLI, GitHub CLI, Codex | Smoke branch/PR | PORTABILE_GIA_OGGI |
| Terminale | Affiancato al browser | Nessuna | Terminale macOS | Nessuna ulteriore | PORTABILE_GIA_OGGI |
| Backend FastAPI | Consultazione localhost | Nessuna | Browser standard, curl | Smoke `/health` | PORTABILE_GIA_OGGI |
| Frontend Vite | Lettura pagina attiva | Operativa | Chrome, ChatGPT desktop | Smoke localhost e DOM | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Test Python/frontend | Lettura output | Nessuna | Terminale, Codex | Smoke test | PORTABILE_GIA_OGGI |
| OCR Tesseract | Verifica dalla UI | Nessuna | Terminale e browser standard | Smoke PNG | PORTABILE_GIA_OGGI |
| Registry snapshot | Lettura contestuale | Nessuna | Backend, TL Chat, test | Smoke read-only | PORTABILE_GIA_OGGI |
| Work/Codex | Utilizzo tramite ChatGPT | Nessuna rispetto ad Atlas | ChatGPT web/desktop | Verifica disponibilità | PORTABILE_GIA_OGGI |
| Lettura pagina attiva | Integrata | Operativa | ChatGPT desktop o sidebar Chrome | Verifica DOM, errori e JSON | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Screenshot pagina | Integrata | Operativa | Screenshot macOS o browser agentico | Verifica acquisizione | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Gestione schede | Integrata | Operativa | Chrome o ChatGPT desktop | Verifica apertura/focus | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Caricamento file UI | Integrato | Operativa | Browser standard | Smoke PNG/JPEG | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| GitHub e check PR | Integrato | Nessuna | `gh`, GitHub web | Smoke PR completa | PORTABILE_GIA_OGGI |
| Vercel | Scheda autenticata | Operativa | Browser standard | Verifica accesso | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Segnalibri Atlas | Locale ad Atlas | Informativa | Export e import Chrome | Verifica export | PROCEDURA_MANUALE_NECESSARIA |
| Cronologia Atlas | Locale ad Atlas | Informativa | Export/inventario manuale | Verifica disponibilità | RISCHIO_DI_PERDITA |
| Conversazioni | Consultate in Atlas | Informativa | ChatGPT web/desktop | Verifica continuità account | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Accesso localhost | Interpretato da Atlas | Operativa | Chrome/desktop | Verifica porte 5173/8000 | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Mini-server e Tailscale | Consultazione browser | Nessuna rispetto ad Atlas | Terminale, SSH, browser | Smoke senza cambiare rete | SOSTITUTO_DISPONIBILE_DA_VERIFICARE |
| Dipendenza runtime da Atlas | Nessuna | Nessuna | Non necessaria | Nessuna | NON_NECESSARIA |

## Dipendenze tecniche

Non risultano dipendenze tecniche di Prometeo da Atlas.

Restano indipendenti:

- repository GitHub;
- Git e GitHub CLI;
- backend FastAPI;
- frontend Vite;
- test;
- Tesseract locale;
- registry snapshot;
- Work e Codex;
- GitHub Actions;
- Vercel;
- mini-server;
- Tailscale e SSH.

## Dipendenze operative

Richiedono una procedura sostitutiva verificata:

- lettura della pagina Prometeo aperta;
- interpretazione diretta dello stato UI;
- lettura di errori e preview JSON;
- side chat associata alla pagina;
- gestione contestuale delle schede;
- passaggio rapido tra browser, ChatGPT e Terminale;
- consultazione di localhost;
- caricamento file negli smoke UI.

## Dipendenze informative

Devono essere esportate, inventariate o riportate nel repository quando appropriate:

- segnalibri;
- pagine GitHub, Vercel e Prometeo utilizzate;
- prompt canonici;
- comandi canonici;
- roadmap;
- capability e closure;
- procedure oggi presenti solo nelle conversazioni;
- riferimenti a percorsi locali;
- eventuali screenshot operativi non sensibili.

Non devono essere trasferiti nel repository:

- password;
- cookie;
- token;
- API key;
- chiavi private;
- sessioni autenticate;
- dati aziendali sensibili.

## Strumenti sostitutivi da verificare

### ChatGPT desktop

Verificare navigazione browser, più schede, lettura pagine, download e allegati, accesso agli account, utilizzo con localhost e continuità delle conversazioni.

### ChatGPT web

Verificare conversazioni Prometeo, Work, Codex, progetti, file, allegati e continuità del contesto operativo.

### Chrome con sidebar o estensione ChatGPT

Verificare lettura della pagina attiva, side chat, accesso a localhost, autenticazione, caricamento file e gestione delle schede.

### Codex

Usare per lettura repository, mapping, test, patch, GitHub, CI e browser autonomo quando disponibile.

Non assumere che Codex sostituisca automaticamente la lettura della UI locale senza uno smoke esplicito.

### Terminale

Resta il controllo deterministico per backend, frontend, test, curl, Git, GitHub CLI, Tesseract, porte, processi e diagnostica SSH/Tailscale.

## Comandi canonici Prometeo

### Backend

```bash
cd ~/PROMETEO

API_KEY="$(grep '^PROMETEO_API_KEY=' backend/.env | cut -d= -f2-)"

PYTHONPATH="$PWD:$PWD/backend" \
PROMETEO_API_KEY="$API_KEY" \
PROMETEO_PRODUCTION_PROGRAM_OCR_PROVIDER=tesseract \
./tools/py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Non usare:

- `python3 -m uvicorn backend.app.main:app`;
- `cd backend && ../tools/py -m uvicorn app.main:app`;
- `./tools/py -m uvicorn app.main:app` senza `PYTHONPATH`.

### Frontend

```bash
cd ~/PROMETEO
npm --prefix frontend run dev
```

Prima di avviare una nuova istanza verificare che la porta 5173 non sia già occupata. Non rilanciare Vite quando il frontend è già attivo.

## Workflow portabile

1. preflight;
2. mappatura minima;
3. test rosso;
4. patch minima;
5. regressioni;
6. smoke host;
7. commit;
8. branch;
9. push;
10. pull request;
11. check CI;
12. squash merge;
13. riallineamento locale a `origin/main`;
14. closure documentale;
15. aggiornamento catalogo tramite `make docs-catalog`.

Nessuno di questi passaggi richiede Atlas come dipendenza tecnica.

## Piano di migrazione

1. inventariare dati e funzionalità Atlas;
2. esportare segnalibri e dati disponibili;
3. salvare procedure e prompt canonici nel repository;
4. installare o verificare gli strumenti sostitutivi;
5. provare localhost e UI Prometeo fuori da Atlas;
6. eseguire gli smoke definiti;
7. usare Atlas e ambiente sostitutivo in parallelo;
8. completare una verticale Prometeo senza Atlas;
9. verificare il piano di recupero;
10. chiudere formalmente la migrazione.

## Smoke test

### SMOKE 1 — Repository

Verificare `git status`, creare un branch temporaneo, eseguire test e non modificare direttamente `main`.

### SMOKE 2 — Backend

Avviare con il comando canonico, verificare `GET /health` e una richiesta TL Chat.

### SMOKE 3 — Frontend

Avviare Vite, aprire Prometeo e verificare caricamento e routing.

### SMOKE 4 — Lettura pagina

Lo strumento sostitutivo deve leggere correttamente file selezionato, stato backend, errore, preview JSON ed esito conferma.

### SMOKE 5 — OCR

Caricare un PNG sintetico, acquisire preview, verificare Tesseract e non persistere senza conferma.

### SMOKE 6 — Conferma

Confermare uno snapshot sintetico e verificare registry, planner, writer e Pattern Learning.

### SMOKE 7 — TL Chat

Domanda:

`Mostrami il programma produzione confermato 2026-W30`

Verificare lettura dal registry confermato.

### SMOKE 8 — GitHub

Branch, push, PR, check, squash merge e reset locale su `origin/main`.

### SMOKE 9 — Conversazioni e file

Aprire una conversazione Prometeo, recuperare un documento, allegare un file e verificare continuità operativa.

### SMOKE 10 — Mini-server e Tailscale

Senza modificare porte o configurazioni, verificare raggiungibilità, SSH, health backend, UI e fallback locale.

## Criteri di accettazione

La capability potrà essere chiusa solo quando:

- dati Atlas importanti sono esportati o inventariati;
- workflow GitHub è verificato;
- Work e Codex sono disponibili;
- backend è avviabile;
- frontend è avviabile;
- localhost è consultabile;
- pagina Prometeo è interpretabile;
- file è caricabile;
- OCR è verificabile;
- conferma snapshot è verificabile;
- TL Chat è verificabile;
- non rimangono dipendenze critiche solo in Atlas;
- procedure canoniche sono documentate;
- nessun segreto è stato copiato nella documentazione;
- almeno una verticale completa è stata eseguita senza Atlas.

## Rischi

- perdita di segnalibri;
- perdita di cronologia utile;
- differenze nella lettura della pagina attiva;
- differenze nell'accesso a localhost;
- differenze nell'autenticazione;
- disponibilità incompleta delle capacità agentiche;
- procedure presenti solo nelle conversazioni;
- processi backend/frontend duplicati;
- backend stale dopo una patch;
- perdita di contesto tra browser e Terminale;
- esportazioni contenenti dati sensibili;
- migrazione eseguita troppo vicino alla data limite.

## Contromisure

- repository come fonte primaria;
- capability e closure versionate;
- comandi canonici;
- smoke ripetibili;
- file sintetici;
- Chrome come ambiente di continuità;
- ChatGPT desktop da verificare;
- Codex per repository e automazione;
- Terminale come controllo deterministico;
- esportazione anticipata;
- periodo di uso parallelo;
- checklist finale verificata.

## Limiti

Questa capability non autorizza modifiche al runtime Prometeo, migrazione automatica di password o cookie, modifiche a porte o rete, modifiche Tailscale, modifiche mini-server, installazione di software, eliminazione di Atlas, equivalenze non verificate o dichiarazione di migrazione completata senza smoke.

## Esito

MIGRATION_PLAN_READY

## Prossima mossa

PROMETEO_ATLAS_DATA_EXPORT_AND_INVENTORY_001

Scopo:

- inventariare ed esportare i dati Atlas importanti;
- escludere segreti e credenziali dal repository;
- produrre una checklist verificabile;
- iniziare la migrazione mentre Atlas è ancora disponibile.

Questa attività non è aperta né implementata dalla presente capability.
