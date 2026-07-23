# PROMETEO_LOCAL_DEPLOYMENT_PILOT_001

## Stato

- `STATUS`: `OPEN_PREFLIGHT_COMPLETE`
- `MODE`: `LOCAL_PILOT`
- `TARGET`: `CURRENT_MAC`
- `RUNTIME_CHANGE_AUTHORIZED`: `false`
- `SYSTEM_SERVICE_AUTHORIZED`: `false`
- `REAL_DATA_AUTHORIZED`: `false`

## Obiettivo

Creare una prima installazione pilota Prometeo separata dal checkout di sviluppo sul Mac attuale, usando solo dati sintetici e senza servizi permanenti, per verificare che il deployment sia riproducibile prima di scegliere o acquistare un mini-server.

## Baseline osservata

### Host

Il Mac locale dispone già di:

- Git;
- Python 3;
- Node.js e npm;
- Tesseract;
- SQLite;
- curl;
- backend attivo su `127.0.0.1:8000`;
- frontend Vite attivo su `127.0.0.1:5173`;
- `GET /health` con risposta `HTTP 200`.

### Repository

- branch osservato: `main`;
- baseline: `c09e005e4883d42d8718a99d640ea276b883db7d`;
- working tree osservato pulito;
- checkout di sviluppo: `~/PROMETEO`.

### Verticale applicativa già verificata

```text
immagine sintetica
→ OCR locale
→ preview DA_VERIFICARE
→ conferma umana esplicita
→ registry CONFERMATO
→ read-back
→ TL Chat
```

Fonte: `PRODUCTION_PROGRAM_OCR_CONFIRMED_READ_FLOW_CLOSURE_001`.

## Mappatura dei comandi reali

### Backend

Il comando corrente osservato in `scripts/dev_start.sh` è:

```bash
cd ~/PROMETEO
export PYTHONPATH=backend
./tools/py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Lo script corrente:

- sceglie `.venv/bin/python`, `backend/.venv/bin/python` o `python3`;
- carica `backend/.env` oppure `.env` se presenti;
- termina forzatamente un processo già in ascolto sulla porta `8000`;
- avvia Uvicorn in background;
- verifica `/health`.

Per il pilot separato non è autorizzato usare lo script mentre il checkout di sviluppo mantiene già la porta `8000`, perché terminerebbe il backend esistente.

### Frontend

Il comando osservato è:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Per il pilot deve essere usata una porta diversa da quella dello sviluppo.

### Setup

`make setup` richiama `scripts/setup_prometeo.sh`, che:

- crea directory;
- crea un virtualenv;
- installa dipendenze Python e Node;
- tenta di avviare PostgreSQL con Homebrew;
- tenta di creare il database `prometeo`;
- può creare `.env`.

`make setup` non è autorizzato nella prima slice perché modifica l'host e introduce PostgreSQL prima che sia dimostrato necessario al pilot OCR.

## Persistenza esplicita

Il registry OCR usa:

```text
PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_PATH
```

Se la variabile non è valorizzata, il default è:

```text
data/production_program_snapshots/registry.json
```

Nel pilot deve essere impostato un path separato dal checkout di sviluppo, per esempio:

```text
~/PROMETEO_LOCAL_PILOT_DATA/production_program_snapshots/registry.json
```

Il path deve contenere solo dati sintetici.

## Slice verticale autorizzata

```text
checkout separato
→ verifica commit
→ riuso controllato delle dipendenze già presenti o creazione venv locale al checkout
→ backend su porta non confliggente
→ frontend su porta non confliggente
→ registry in directory pilota esplicita
→ health 200
→ smoke sintetico OCR/conferma/read-back
→ arresto e riavvio backend
→ verifica persistenza dello snapshot
```

## Porte pilota

Per evitare interferenze con lo sviluppo:

```text
backend pilot: 127.0.0.1:8100
frontend pilot: 127.0.0.1:5273
```

Non sono autorizzate aperture su `0.0.0.0` in questa slice.

## Directory pilota

```text
~/PROMETEO_LOCAL_PILOT          checkout separato
~/PROMETEO_LOCAL_PILOT_DATA     dati persistenti sintetici
~/PROMETEO_LOCAL_PILOT_LOGS     log pilota
```

## Allowlist

Sono autorizzati:

- `git clone` o `git worktree` verso una directory separata;
- creazione di directory pilota sotto `$HOME`;
- creazione di un virtualenv dentro il checkout pilota;
- installazione delle sole dipendenze dichiarate in `backend/requirements.txt` nel virtualenv pilota, se necessaria;
- `npm ci` o `npm install` nel solo checkout pilota, se necessaria;
- avvio di processi utente su `127.0.0.1:8100` e `127.0.0.1:5273`;
- uso di dati sintetici;
- eliminazione finale delle sole directory pilota, dopo esplicita autorizzazione.

## Denylist

Non sono autorizzati:

- `make setup`;
- avvio o modifica di PostgreSQL;
- modifiche al checkout `~/PROMETEO`;
- kill dei processi sulle porte `8000` e `5173`;
- servizi `launchd` o demoni permanenti;
- ascolto su `0.0.0.0`;
- modifiche a firewall, router, SSH o Tailscale;
- dati reali;
- copia di `.env` contenenti segreti;
- acquisto hardware;
- modifica del runtime Prometeo.

## Stop conditions

Fermarsi immediatamente se:

- il checkout di sviluppo risulta modificato;
- una porta pilota è già occupata;
- una dipendenza richiede privilegi amministrativi;
- il backend richiede segreti non disponibili;
- lo smoke tenta di usare dati reali;
- il registry scrive fuori dalla directory pilota;
- il riavvio perde lo snapshot persistito;
- emerge la necessità di una patch runtime.

## Criterio di accettazione

La capability è pronta per closure quando sono osservate tutte le evidenze seguenti:

1. checkout pilota separato e allineato a `origin/main`;
2. checkout di sviluppo invariato;
3. backend pilota avviabile su `127.0.0.1:8100`;
4. frontend pilota avviabile su `127.0.0.1:5273`;
5. `GET /health` restituisce `HTTP 200`;
6. registry scritto esclusivamente nel path pilota;
7. smoke sintetico produce uno snapshot `CONFERMATO`;
8. TL Chat rilegge lo snapshot sintetico confermato;
9. backend arrestato e riavviato senza perdita del registry;
10. nessun planner, writer o Pattern Learning viene attivato;
11. Privacy Guard e Data Leak Guard verdi;
12. nessuna modifica runtime o infrastrutturale.

## Limiti

Questa capability non dimostra ancora:

- installazione su una macchina pulita;
- installazione Linux;
- accesso multi-dispositivo;
- uso in rete locale o Tailscale;
- servizi persistenti dopo reboot;
- backup automatici;
- recovery;
- uso con dati reali;
- requisiti hardware definitivi.

## Prima esecuzione autorizzata

La prima esecuzione deve limitarsi a:

```text
creazione directory pilota
→ checkout separato
→ verifica dipendenze e porte
→ nessun avvio ancora
```

Solo dopo l'esito di questa verifica sarà autorizzato l'avvio del backend e del frontend pilota.

## Prossima mossa unica

Eseguire sul Mac una fase zero che crei il checkout separato e verifichi commit, working tree, porte `8100` e `5273`, senza installare dipendenze e senza avviare processi.