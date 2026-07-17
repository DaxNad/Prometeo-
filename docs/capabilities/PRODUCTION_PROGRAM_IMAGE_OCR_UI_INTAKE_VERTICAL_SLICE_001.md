# PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_VERTICAL_SLICE_001

## Autorizzazione originaria

Questa sezione conserva il perimetro autorizzato prima dell'implementazione.
Le formulazioni al futuro e la route SPA qui riportata sono evidenza storica
dell'autorizzazione; lo stato runtime finale è riconciliato nella closure più
avanti.

### Stato autorizzativo originario

CAPABILITY: PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001  
SLICE: VERTICAL_SLICE_001  
AUTHORIZATION_STATUS: AUTHORIZED
MODE: LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST  
AUTHORIZATION_DATE: 2026-07-16

### Obiettivo

Implementare la più piccola porta di ingresso frontend per una singola immagine PNG o JPEG verso l'endpoint esistente:

`POST /production-program/image-ocr/acquire`

Il risultato deve essere mostrato come preview non autorevole, non persistita e soggetta a conferma esterna alla slice.

### Percorso utente autorizzato

1. apertura della route `/production-program/image-ocr/acquire`;
2. selezione di una sola immagine PNG o JPEG;
3. conversione Base64 esclusivamente nella memoria del browser;
4. invio tramite il client API esistente;
5. visualizzazione di stato, provenienza, evidenza OCR, righe normalizzate e snapshot preview;
6. nessuna conferma, persistenza o scrittura.

### Allowlist esatta

Possono cambiare esclusivamente:

- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx`
- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx`
- `frontend/src/lib/api/prometeo.ts`
- `frontend/src/App.tsx`

Nessun quinto file è autorizzato.

### Contratto client

Aggiungere in `frontend/src/lib/api/prometeo.ts`:

- tipo richiesta con `image_base64: string`;
- tipo risposta che preservi i campi backend;
- funzione `acquireProductionProgramImageOCR(...)`;
- uso esclusivo di `apiPost(...)`;
- endpoint esatto `/production-program/image-ocr/acquire`.

Campi minimi da preservare senza riscrittura semantica:

- `ok`
- `status`
- `source_id`
- `source_hash`
- `media_type`
- `provider`
- `error_code`
- `requires_confirmation`
- `semantic_status`
- `persisted`
- `writer_called`
- `planner_called`
- `pattern_learning_called`
- `observed_text`
- `normalized_lines`
- `snapshot_preview`

### Contratto UI

La pagina deve:

- accettare una sola immagine;
- comunicare esplicitamente il supporto PNG/JPEG;
- disabilitare l'invio senza file;
- mostrare caricamento, errore di trasporto e risultato;
- distinguere almeno `PREVIEW_READY`, `PREVIEW_BLOCKED`, `OCR_FAILED` e `REJECTED`;
- mostrare gli error code disponibili;
- dichiarare che HTTP 200 non equivale a successo operativo;
- dichiarare che il risultato non è autorevole e non è persistito;
- non offrire controlli di conferma, writer, planner o persistenza.

Il backend resta autorevole per firma e validità del formato.

### Integrazione App

`frontend/src/App.tsx` può soltanto:

- importare la nuova pagina;
- aggiungere una voce di navigazione;
- renderizzare la route esatta `/production-program/image-ocr/acquire`.

Sono vietati router esterni e redesign globale.

### Test obbligatori

Usare Vitest e Testing Library con fixture sintetiche.

I test devono provare:

1. rendering review-only;
2. submit disabilitato senza file;
3. PNG sintetico convertito e inviato in Base64;
4. JPEG sintetico accettato;
5. endpoint esatto;
6. rendering `PREVIEW_READY`;
7. `PREVIEW_BLOCKED` non dichiarato come successo;
8. visibilità di `OCR_FAILED`, `REJECTED` ed error code;
9. flag di governance mostrati senza alterazione;
10. errore di trasporto visibile;
11. assenza di controlli di conferma o persistenza;
12. route e navigazione operative.

### Verifiche finali

Devono passare:

- test frontend focalizzati;
- `npm test`;
- `npm run build`;
- `git diff --check`;
- verifica che siano cambiati esattamente i quattro file autorizzati.

### Scope vietato

Non sono autorizzati:

- modifiche backend;
- nuove dipendenze;
- camera API o acquisizione diretta dal dispositivo;
- drag-and-drop;
- più immagini;
- multipart, path o URL;
- formati diversi da PNG/JPEG;
- OCR o parsing lato client;
- normalizzazione o inferenza semantica;
- conferma, persistenza, writer, SMF, database;
- planner, Pattern Learning o TL Chat;
- dati industriali reali;
- cloud OCR.

### Stop conditions

Fermarsi immediatamente se occorre:

- modificare un quinto file;
- cambiare backend o contratto endpoint;
- introdurre una dipendenza;
- duplicare logica OCR o di dominio;
- aggiungere scritture o conferme;
- usare immagini reali aziendali;
- ampliare il percorso oltre una singola immagine.

### Criteri di accettazione

La slice è chiudibile solo se:

1. cambiano esattamente i quattro file allowlisted;
2. nessun backend cambia;
3. il flusso usa un solo endpoint;
4. la risposta è renderizzata senza mutazioni semantiche;
5. nessuna azione operativa è disponibile;
6. test e build sono verdi;
7. il repository resta privo di dati sensibili.

### Verdetto autorizzativo originario

AUTHORIZATION: GRANTED  
RUNTIME_SCOPE: FRONTEND_ONLY  
BACKEND_CHANGE: FORBIDDEN  
NEXT_MOVE_AT_AUTHORIZATION: IMPLEMENT_EXACT_FOUR_FILE_SLICE

## Closure della vertical slice

La closure distingue l'implementazione attribuibile alla slice UI dalla merge
cumulativa che l'ha portata su `main`. Il codice e i test presenti su `main`
prevalgono sulle formulazioni autorizzative storiche.

### Implementazione osservata

Il commit logico `14f9d26` ha modificato esclusivamente i quattro file
autorizzati:

- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx`;
- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx`;
- `frontend/src/lib/api/prometeo.ts`;
- `frontend/src/App.tsx`.

La slice ha introdotto la pagina di acquisizione, il relativo test focalizzato,
il client `acquireProductionProgramImageOCR(...)` e l'integrazione nella App.
La parte attribuibile al commit logico UI non ha modificato il backend e usa
l'endpoint esistente:

```text
POST /production-program/image-ocr/acquire
```

### Correzione routing

La route SPA inizialmente autorizzata e implementata,
`/production-program/image-ocr/acquire`, collideva con il namespace `/production`
riservato dal proxy Vite. Il commit logico `9d50cda` ha separato i due confini:

```text
BACKEND_API_ENDPOINT: /production-program/image-ocr/acquire
FRONTEND_SPA_ROUTE: /app/production-program/image-ocr/acquire
```

La correzione è confluita nella merge cumulativa `de2fcd0` della PR `#528`.
Quella PR comprende dodici file e altre modifiche non attribuibili alla sola
slice UI; la closure non li riclassifica come parte dell'allowlist originaria.

### Guard di regressione

La PR `#529`, merge `6aa8198`, ha aggiunto
`frontend/src/spaRouteNamespaceGuard.test.ts`. Il guard verifica che le route SPA
non usino prefissi riservati dal proxy Vite e accetta esplicitamente la route
`/app/production-program/image-ocr/acquire`. Questo hardening è successivo
all'implementazione e non faceva parte dell'autorizzazione originaria.

### Evidenze Git

- `14f9d26`: commit logico della slice UI nei quattro file autorizzati;
- `9d50cda`: commit logico della correzione route SPA;
- `de2fcd0` / PR `#528`: squash merge cumulativa che ha introdotto su `main`
  pagina, test, client e route già corretta;
- `6aa8198` / PR `#529`: guard di regressione dei namespace SPA/proxy;
- `2520d57` / PR `#530`: classificazione catalogo del documento come
  `EVIDENCE / ARCHIVED`.

I commit logici `14f9d26` e `9d50cda` sono elencati nel commit della squash merge
ma non risultano antenati diretti di `main`. I blob della pagina, del test e del
client su `main` coincidono con quelli del commit logico UI; `App.tsx` differisce
per la sola correzione della route SPA.

### Evidenze test disponibili

È verificabile nel repository la presenza del test focalizzato
`frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx`, basato su
fixture PNG/JPEG sintetiche. Il test copre in modo osservabile:

- rendering review-only e submit disabilitato senza file;
- conversione Base64 e invio del payload sintetico;
- PNG e JPEG;
- `PREVIEW_READY`, `PREVIEW_BLOCKED`, `OCR_FAILED` e `REJECTED`;
- provenienza, stato semantico e flag di non persistenza;
- errore di trasporto e assenza di controlli di conferma o persistenza.

È inoltre verificabile la presenza del guard SPA aggiunto dalla PR `#529`.
Nessun test o build è stato rieseguito durante questa fase esclusivamente
documentale.

### Limiti delle prove

Non sono stati recuperati:

- i log grezzi originali di `npm test` per la PR `#528`;
- i log originali di `npm run build` per la PR `#528`;
- il check rollup completo della PR `#528`;
- la prova storica completa della suite frontend al momento del merge.

La presenza dei test e del codice su `main` prova implementazione e copertura
definita, ma non autorizza il marker assoluto `TESTED` in assenza dei log storici.

### Stato finale

STATUS: CLOSED / MERGED
VERIFICATION_STATUS: IMPLEMENTATION_VERIFIED / HISTORICAL_TEST_LOGS_NOT_FULLY_RECOVERED
LIFECYCLE: ARCHIVED
CATEGORY: EVIDENCE

### Verdetto

CAPABILITY_CLOSURE: JUSTIFIED_WITH_EVIDENCE_LIMITS
RUNTIME_SCOPE: FRONTEND_ONLY
BACKEND_CHANGE_ATTRIBUTABLE_TO_SLICE: NONE
FINAL_FRONTEND_ROUTE: /app/production-program/image-ocr/acquire
BACKEND_ENDPOINT: /production-program/image-ocr/acquire
NEXT_MOVE: REVIEW_DOCUMENTATION_DIFF
