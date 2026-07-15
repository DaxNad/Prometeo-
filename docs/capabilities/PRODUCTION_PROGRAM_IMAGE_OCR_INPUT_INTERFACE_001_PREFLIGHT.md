# PRODUCTION_PROGRAM_IMAGE_OCR_INPUT_INTERFACE_001 — PREFLIGHT

## Stato

CAPABILITY: PRODUCTION_PROGRAM_IMAGE_OCR_INPUT_INTERFACE_001  
STATUS: PREFLIGHT_ONLY  
MODE: DOCUMENTATION_ONLY  
DATE: 2026-07-15  
RUNTIME_AUTHORIZED: FALSE  
IMPLEMENTATION_AUTHORIZED: FALSE

## Decisione

Non viene aperta una nuova pipeline OCR.

PROMETEO dispone già di acquisizione PNG/JPEG, OCR locale, parsing verso snapshot preview e endpoint `POST /production-program/image-ocr/acquire`.

La capability successiva riguarda esclusivamente la futura porta di ingresso utente da smartphone o browser verso il runtime OCR esistente.

## Obiettivo futuro

Percorso minimo previsto:

1. selezione esplicita di una singola immagine PNG o JPEG;
2. invio al solo endpoint OCR esistente;
3. visualizzazione della preview governata;
4. esposizione di stato, errori, ambiguità e dati mancanti;
5. nessuna conferma o scrittura automatica.

## Fonte di verità da verificare

- `docs/PROMETEO_INPUT_INTERFACE_V1.md`
- `docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_VERTICAL_SLICE_001.md`
- `docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001.md`
- `docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001_CLOSURE.md`
- endpoint `POST /production-program/image-ocr/acquire`
- componenti frontend effettivamente presenti nel checkout locale

Ogni nome tecnico deve essere osservato nel repository prima di autorizzare implementazione.

## Perimetro autorizzato

Questo preflight autorizza soltanto:

- mappatura read-only del frontend esistente;
- individuazione del punto minimo di ingresso UI;
- verifica del contratto HTTP attuale;
- definizione di stati e campi da mostrare;
- preparazione di una vertical slice con allowlist esatta.

## Allowlist corrente

Solo questo file può cambiare:

`docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_INPUT_INTERFACE_001_PREFLIGHT.md`

## Componenti vietati

Nessuna modifica a:

- `backend/`
- `frontend/`
- `tools/ocr/`
- `scripts/`
- `tests/`
- `memory/`
- `data/`
- `.env`
- database, SMF, planner, Pattern Learning e TL Chat runtime

## Vincoli permanenti

- local-only;
- preview-first;
- conferma TL obbligatoria;
- nessuna persistenza;
- nessuna chiamata writer, planner o Pattern Learning;
- nessuna promozione automatica a `CERTO`;
- cloud OCR vietato;
- nessun secondo parser OCR;
- nessuna correzione semantica del testo OCR.

## Dati ammessi nei test futuri

Solo immagini sintetiche e fixture artificiali prive di dati industriali reali.

## Verifiche richieste prima del runtime

1. framework e componente UI attivi;
2. route o pagina corretta;
3. autenticazione API corrente;
4. schema richiesta Base64;
5. limite dimensionale backend;
6. struttura della risposta;
7. stati OCR/API da mostrare;
8. gestione preview locale;
9. annullamento, timeout e retry;
10. convenzioni dei test frontend.

## Criterio di autorizzazione futura

La vertical slice potrà essere autorizzata solo con:

- un solo percorso utente;
- una sola immagine PNG/JPEG;
- un solo endpoint esistente;
- allowlist esatta;
- test deterministici;
- nessuna persistenza;
- nessun dato industriale reale;
- condizioni di stop esplicite.

## Stop conditions

Fermarsi se occorre:

- modificare capability OCR già chiuse;
- creare un nuovo parser o provider;
- cambiare il backend senza incompatibilità osservata;
- introdurre persistenza o conferma automatica;
- integrare TL Chat, planner o Pattern Learning;
- usare dati reali;
- aprire più di una vertical slice.

## Verdetto

PREFLIGHT: COMPLETE  
NEW_RUNTIME: NOT_AUTHORIZED  
ACTIVE_SCOPE: OCR_INPUT_INTERFACE_MAPPING  
NEXT_MOVE: MAP_EXISTING_FRONTEND_ENTRYPOINT_READ_ONLY
