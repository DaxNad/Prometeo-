# ARTICLE SPECIFICATION ACQUISITION UI CLOSURE 001

Stato: `VERIFICATO`

## Scopo

Registrare la chiusura dell'esposizione UI operativa dell'acquisizione
governata delle specifiche articolo.

## UI chiusa

- route frontend dedicata `/article-specification/acquire`;
- selezione di una singola immagine dal browser;
- conversione locale dell'immagine in Base64;
- invio tramite il client API esistente a
  `POST /article-specification/acquire`;
- visualizzazione dell'esito di acquisizione e binding;
- visualizzazione dei payload candidati destinati alla revisione umana;
- visualizzazione esplicita degli errori fail-closed;
- nessuna nuova dipendenza frontend.

## Governo semantico

La UI espone il risultato del backend senza modificarne il significato.
Restano invariati:

- stato `DA_VERIFICARE`;
- `requires_review=true`;
- `writer_called=false`;
- `persisted=false`;
- nessuna promozione automatica a `CERTO`;
- nessuna persistenza autorevole;
- conferma umana obbligatoria prima di qualsiasi scrittura futura.

Il valore HTTP positivo non viene interpretato da solo come successo operativo:
la UI distingue gli esiti `BOUND` e `REJECTED` tramite il payload governato.

## Prove

- test frontend: `5 passed`;
- build TypeScript/Vite: `PASS`;
- lint mirato sui quattro file modificati: `PASS`;
- `git diff --check`: `PASS`;
- Frontend CI: `PASS`;
- SMF Backend Tests: `PASS`;
- Guards: `PASS`;
- Privacy Guard: `PASS`;
- Data Leak Guard: `PASS`;
- TL Eval Guard: `PASS`;
- PR `#466` unita con squash nel commit
  `1ec24d7375ea5585bb6e9d85aebaa3f70dfdc9e2`.

Il lint frontend globale resta non verde per errori preesistenti in file fuori
scope; nessun errore è stato rilevato nei quattro file della capability.

## Limiti invariati

La chiusura non introduce:

- workflow di conferma;
- writer o persistenza;
- modifiche al dominio;
- integrazione con TL Chat;
- uso planner;
- decisioni produttive automatiche;
- modifiche al backend o al runtime OCR.

## Stato finale

La catena operativa disponibile è:

`immagine -> UI -> endpoint -> OCR locale -> parser -> binding review-only`

L'acquisizione specifica è ora esposta tramite UI operativa. Resta separata e
aperta la conferma umana prima di qualsiasi persistenza autorevole dei dati
estratti.
