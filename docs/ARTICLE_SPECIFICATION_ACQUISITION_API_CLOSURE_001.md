# ARTICLE SPECIFICATION ACQUISITION API CLOSURE 001

Stato: `VERIFICATO`

## Scopo

Registrare la chiusura dell'esposizione governata del binding di acquisizione specifica tramite un ingresso FastAPI dedicato.

## Runtime chiuso

- endpoint `POST /article-specification/acquire` registrato in `app.main`;
- input immagine PNG/JPEG codificata Base64;
- acquisizione tramite `acquire_article_specification_image()`;
- binding tramite `bind_article_specification_acquisition()`;
- risposta con payload destinati alla revisione umana;
- stato semantico mantenuto `DA_VERIFICARE`;
- `writer_called=false`;
- `persisted=false`;
- `requires_review=true`.

## Boundary OCR

PROMETEO non configura ancora un adapter OCR runtime concreto. Il provider API restituisce `None` e il flusso fallisce chiuso con `OCR_ADAPTER_REQUIRED` finché un adapter conforme al protocollo non viene iniettato.

Non sono stati introdotti motori OCR, dipendenze OCR o servizi esterni non verificati.

## Prove

- test mirati: `20 passed`;
- backend guard: `1134 passed, 3 deselected`;
- real code registry preview: `30 passed`;
- quality gate: `PASS`;
- schema guard: `PASS`;
- PR `#462` unita con squash nel commit `24538cbfbc569fbf15d5f538ef42901634ac5734`.

## Limiti invariati

La chiusura non autorizza:

- persistenza autorevole dei dati estratti;
- promozione automatica a `CERTO`;
- uso planner;
- decisioni produttive automatiche;
- collegamento diretto alla TL Chat come fonte autorevole.

## Stato finale

L'ingresso API governato è chiuso. Resta aperta la conferma umana prima di qualsiasi persistenza autorevole dei dati estratti.
