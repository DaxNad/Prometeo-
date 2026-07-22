# PROMETEO_END_TO_END_MINI_SERVER_READINESS_PREFLIGHT_001

## Stato

- `STATUS`: `OPEN_READ_ONLY_PREFLIGHT`
- `MODE`: `READ_ONLY`
- `BASELINE`: `main` at `e68bc891810336bb2f4b8289a68166d43c1bfd0e`
- `RUNTIME_AUTHORIZED`: `false`
- `INFRASTRUCTURE_CHANGES_AUTHORIZED`: `false`
- `INSTALLATION_AUTHORIZED`: `false`

## Scopo

Determinare se la verticale Prometeo già verificata nel repository può essere eseguita end-to-end su mini-server e identificare il primo anello realmente mancante, senza modificare runtime, rete, SSH, Tailscale, porte o configurazioni.

## Fonte di verità

Ordine di autorità:

1. repository GitHub Prometeo;
2. closure e test versionati;
3. output osservabili del checkout locale;
4. output osservabili del mini-server, solo quando verrà autorizzata una verifica read-only;
5. memoria e ricostruzioni manuali solo come fonti non verificate.

## Evidenza già disponibile

La closure `PRODUCTION_PROGRAM_OCR_CONFIRMED_READ_FLOW_CLOSURE_001` dichiara chiusa e verificata la verticale:

```text
PNG/JPEG
→ OCR Tesseract locale
→ preview DA_VERIFICARE non persistita
→ parsing deterministico
→ conferma umana autorizzata
→ registry versionato CONFERMATO
→ read-back governato
→ TL Chat per periodo confermato
```

Contratti osservati nel repository:

- `POST /production-program/image-ocr/acquire`;
- `POST /production-program/image-ocr/acquire-multipage`;
- `POST /production-program-snapshot/confirm`;
- `POST /tl/chat`;
- pagina `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx`;
- provider OCR locale `backend/app/services/production_program_tesseract_ocr.py`;
- registry `backend/app/domain/production_program_snapshot_registry.py`;
- test end-to-end `backend/tests/test_production_program_verified_snapshot_e2e.py`.

## Matrice readiness iniziale

| Anello | Stato iniziale | Evidenza | Decisione |
|---|---|---|---|
| Pagina acquisizione OCR | `READY_IN_REPOSITORY` | pagina e test frontend presenti | non modificare |
| Endpoint acquisizione singola | `READY_IN_REPOSITORY` | route e test HTTP presenti | non modificare |
| Endpoint multipagina | `READY_IN_REPOSITORY` | route e test HTTP presenti | non modificare |
| OCR Tesseract locale | `READY_IN_REPOSITORY` | servizio e test fail-closed presenti | verificare dipendenza host sul mini-server |
| Preview governata | `READY_IN_REPOSITORY` | closure e test presenti | non modificare |
| Conferma esplicita | `READY_IN_REPOSITORY` | endpoint, servizio e test presenti | verificare configurazione runtime sul mini-server |
| Registry confermato | `READY_IN_REPOSITORY` | dominio, persistenza e read-back testati | verificare path persistente e permessi host |
| Lettura TL Chat | `READY_IN_REPOSITORY` | binding e test end-to-end presenti | verificare avvio integrato |
| Avvio backend sul mini-server | `UNVERIFIED` | nessuna evidenza end-to-end sul target | mappare comando canonico e dipendenze |
| Avvio frontend sul mini-server | `UNVERIFIED` | nessuna evidenza end-to-end sul target | mappare build/serve e proxy |
| Persistenza dopo riavvio | `UNVERIFIED` | non osservata sul target | verificare senza dati reali |
| Accesso client al servizio | `UNVERIFIED` | rete e porte non autorizzate in questa capability | solo inventario read-only |
| Riavvio automatico servizi | `UNVERIFIED` | nessuna evidenza target | rinviare a capability installativa |
| Backup e diagnostica | `OUT_OF_SCOPE` | capability futura separata | non aprire ora |

## Primo divario reale

Il primo anello non provato non è la logica OCR o TL Chat. È il contratto di esecuzione sul mini-server:

```text
checkout/versione
→ dipendenze host
→ configurazione non sensibile
→ avvio backend
→ avvio frontend
→ persistenza locale
→ smoke sintetico end-to-end
```

## Mappatura read-only autorizzata

La prossima verifica può leggere esclusivamente:

- versione del sistema operativo e architettura CPU;
- disponibilità di Python, Node, npm e Tesseract;
- comandi canonici già presenti nel repository;
- file di dipendenze e build;
- variabili ambiente richieste per nome, mai per valore;
- processi e porte in ascolto, senza modificarli;
- directory di persistenza per struttura e permessi, senza leggere dati sensibili;
- health check esistenti;
- spazio disco e memoria disponibili;
- commit Prometeo installato, se esiste.

## File e componenti ammessi nella prossima mappatura

- `AGENTS.md`;
- file di dipendenze backend e frontend;
- script di avvio e diagnostica esistenti;
- configurazione Vite e route API;
- endpoint health esistenti;
- documentazione OCR già chiusa;
- output read-only del mini-server.

## Esclusioni permanenti per questo preflight

Non sono autorizzati:

- installazione o aggiornamento di pacchetti;
- modifica di file `.env`;
- lettura o copia di valori segreti;
- apertura o chiusura di porte;
- modifica firewall;
- modifica SSH o Tailscale;
- creazione di servizi `systemd`, container o reverse proxy;
- modifica backend o frontend;
- acquisizione di immagini o dati aziendali reali;
- scrittura nel registry reale;
- dichiarazione di installazione completata.

## Stop conditions

Fermarsi immediatamente se:

- il checkout locale o remoto contiene modifiche non correlate;
- servono credenziali o valori segreti;
- il mini-server non è identificabile con certezza;
- una verifica richiede mutazioni;
- il percorso di persistenza contiene dati aziendali reali;
- emerge un conflitto tra documentazione e runtime;
- il primo anello mancante richiede una capability diversa.

## Criterio di accettazione

Il preflight è completo quando produce:

1. stato `READY`, `PARTIAL`, `MISSING` o `BLOCKED` per ogni anello sul mini-server;
2. comandi e file osservati, senza assunzioni;
3. elenco delle sole dipendenze mancanti;
4. primo anello mancante chiaramente identificato;
5. una sola slice successiva;
6. nessuna modifica al target o al runtime;
7. guard privacy e data leak verdi prima del merge.

## Slice verticale successiva autorizzabile

Solo dopo la mappatura read-only potrà essere proposta una capability installativa minima. La slice candidata dovrà limitarsi al primo anello mancante e includere uno smoke sintetico, senza coinvolgere dati reali, rete aziendale o automazioni non necessarie.

## Impatto architetturale

- Modello `Order -> ProductionEvent -> Station/Phase`: invariato.
- OCR e conferma: invariati.
- Registry: invariato.
- TL Chat: invariata.
- Planner, writer e Pattern Learning: non coinvolti.

## Esito documentale

`MINI_SERVER_READINESS_PREFLIGHT_CONTRACT_READY`

## Prossima mossa

Eseguire una sola sessione read-only sul mini-server e compilare la matrice readiness con evidenze osservate. Non installare né modificare nulla durante la sessione.