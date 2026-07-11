# ARTICLE SPECIFICATION TESSERACT OCR RUNTIME CLOSURE 001

Stato: `VERIFICATO`

## Scopo

Registrare la chiusura del binding runtime OCR locale per l'acquisizione
governata delle specifiche articolo.

## Runtime chiuso

- adapter concreto `TesseractArticleSpecificationOCRAdapter`;
- esecuzione locale tramite processo Tesseract;
- wiring con `POST /article-specification/acquire`;
- attivazione esclusivamente tramite opt-in esplicito;
- nessuna chiamata cloud o trasmissione esterna;
- timeout configurabile;
- file temporaneo eliminato anche in caso di errore;
- exit non-zero e timeout convertiti in risultati OCR falliti;
- nessuna nuova dipendenza Python.

## Configurazione

Il provider viene attivato solo con:

`PROMETEO_ARTICLE_SPEC_OCR_PROVIDER=tesseract`

Configurazioni opzionali:

- `PROMETEO_TESSERACT_COMMAND=tesseract`;
- `PROMETEO_TESSERACT_LANGUAGE=ita+eng`;
- `PROMETEO_TESSERACT_TIMEOUT_SECONDS=30`.

Senza opt-in, con provider sconosciuto, configurazione invalida o binario non
disponibile, il provider restituisce `None` e il flusso conserva il
comportamento fail-closed `OCR_ADAPTER_REQUIRED`.

## Governo semantico

L'OCR estrae esclusivamente testo candidato. Restano invariati:

- parsing governato;
- stato `DA_VERIFICARE`;
- `writer_called=false`;
- `persisted=false`;
- `requires_review=true`;
- conferma umana prima di qualsiasi persistenza autorevole.

## Prove

- test mirati: `27 passed`;
- backend guard: `1141 passed, 3 deselected`;
- real code registry preview: `30 passed`;
- quality gate: `PASS`;
- schema guard: `PASS`;
- PR `#464` unita con squash nel commit
  `aaf1b6c54003ab2e8104b31dbe2eae0c155c0232`.

## Limiti invariati

La chiusura non introduce:

- promozione automatica a `CERTO`;
- persistenza autorevole dei dati OCR;
- uso planner;
- decisioni produttive automatiche;
- interfaccia UI di acquisizione;
- collegamento diretto alla TL Chat come fonte autorevole.

## Stato finale

Il boundary OCR dispone ora di un adapter runtime locale concreto, opzionale e
fail-closed. Resta aperta l'esposizione UI operativa e la conferma umana prima
della persistenza autorevole.
