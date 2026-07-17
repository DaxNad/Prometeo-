# PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_VERTICAL_SLICE_001

## Stato

CAPABILITY: PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001  
SLICE: VERTICAL_SLICE_001  
STATUS: AUTHORIZED  
MODE: LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST  
DATE: 2026-07-16

## Obiettivo

Implementare la più piccola porta di ingresso frontend per una singola immagine PNG o JPEG verso l'endpoint esistente:

`POST /production-program/image-ocr/acquire`

Il risultato deve essere mostrato come preview non autorevole, non persistita e soggetta a conferma esterna alla slice.

## Percorso utente autorizzato

1. apertura della route `/production-program/image-ocr/acquire`;
2. selezione di una sola immagine PNG o JPEG;
3. conversione Base64 esclusivamente nella memoria del browser;
4. invio tramite il client API esistente;
5. visualizzazione di stato, provenienza, evidenza OCR, righe normalizzate e snapshot preview;
6. nessuna conferma, persistenza o scrittura.

## Allowlist esatta

Possono cambiare esclusivamente:

- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx`
- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx`
- `frontend/src/lib/api/prometeo.ts`
- `frontend/src/App.tsx`

Nessun quinto file è autorizzato.

## Contratto client

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

## Contratto UI

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

## Integrazione App

`frontend/src/App.tsx` può soltanto:

- importare la nuova pagina;
- aggiungere una voce di navigazione;
- renderizzare la route esatta `/production-program/image-ocr/acquire`.

Sono vietati router esterni e redesign globale.

## Test obbligatori

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

## Verifiche finali

Devono passare:

- test frontend focalizzati;
- `npm test`;
- `npm run build`;
- `git diff --check`;
- verifica che siano cambiati esattamente i quattro file autorizzati.

## Scope vietato

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

## Stop conditions

Fermarsi immediatamente se occorre:

- modificare un quinto file;
- cambiare backend o contratto endpoint;
- introdurre una dipendenza;
- duplicare logica OCR o di dominio;
- aggiungere scritture o conferme;
- usare immagini reali aziendali;
- ampliare il percorso oltre una singola immagine.

## Criteri di accettazione

La slice è chiudibile solo se:

1. cambiano esattamente i quattro file allowlisted;
2. nessun backend cambia;
3. il flusso usa un solo endpoint;
4. la risposta è renderizzata senza mutazioni semantiche;
5. nessuna azione operativa è disponibile;
6. test e build sono verdi;
7. il repository resta privo di dati sensibili.

## Verdetto

AUTHORIZATION: GRANTED  
RUNTIME_SCOPE: FRONTEND_ONLY  
BACKEND_CHANGE: FORBIDDEN  
NEXT_MOVE: IMPLEMENT_EXACT_FOUR_FILE_SLICE
