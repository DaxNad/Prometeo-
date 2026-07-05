# TL_CHAT_RUNTIME_PROVENANCE_COMPLETENESS_001

## Stato

PROPOSED CONTRACT.

## Problema verificato

Alcuni responder TL Chat producono risposte corrette da fonti locali già
autorizzate e lette dal runtime, ma il relativo `evidence_pack.evidence`
resta vuoto.

Il pack viene costruito separatamente dopo `_build_contract_response()` e
non conosce la fonte effettivamente consumata dal responder.

## Obiettivo

Garantire che una risposta derivata da una fonte locale presente esponga
almeno una evidence strutturata, senza modificare il significato della
risposta pubblica.

## Responder nello scope

- risposta da metadata locale articolo;
- risposta da article summary;
- risposta da route matrix preview;
- lista candidati da staging preview;
- lista lifecycle;
- lista new-entry derivata da intake locale.

## Classificazione governata

| Fonte runtime | Candidate source type |
|---|---|
| local specs metadata | ARTICLE_METADATA |
| article TL summary | ARTICLE_SUMMARY |
| lifecycle registry | LIFECYCLE_REGISTRY |
| article route matrix preview | PREVIEW_PROFILE |
| codici staging preview | PREVIEW_PROFILE |
| TL real spec intake | ARTICLE_METADATA |

Questa capability non introduce nuovi reader o nuove fonti fisiche.

## Evidence contract

Ogni evidence mantiene lo schema esistente:

- source_id;
- source_type;
- authority_rank;
- confidence;
- text;
- reason.

Non vengono aggiunti path assoluti o contenuti sensibili.

## Disegno runtime ammesso

`TLChatResponse` può trasportare evidence interna tramite attributo privato
non serializzato.

Il responder che ha letto la fonte assegna direttamente la provenance.

L'endpoint finale fonde deterministicamente tale provenance dentro
`evidence_pack.evidence`.

È vietato dedurre la fonte dal testo della risposta.

## Regole confidence

- metadata o summary confermati possono mantenere la confidence governata
  già prodotta dal responder;
- route matrix, staging e intake preview restano `PREVIEW_ONLY`;
- nessuna evidence preview può promuovere la risposta a `CERTO`;
- confidence della fonte e confidence della risposta restano semanticamente
  distinte.

## Test anti-regressione

Un test parametrizzato deve verificare almeno:

- articolo certo da summary/metadata;
- articolo inferito da route preview;
- candidati densificazione da staging preview;
- fuori produzione da lifecycle registry;
- new-entry da intake locale.

Per ciascun caso:

- `evidence_pack` presente;
- `evidence` non vuoto;
- campi evidence completi;
- source type atteso;
- nessun path assoluto;
- vincoli read-only preservati;
- risposta, confidence e recommended action pubbliche invariate.

## Eccezioni ammesse

L'evidence può restare vuoto per:

- articolo o fonte mancanti;
- risposta di guardrail puro;
- domanda generica senza fonte locale consumata;
- fallback governato privo di contenuto;
- errore di lettura tipizzato.

## Fuori scope

- nuovi reader;
- nuove sorgenti fisiche;
- frontend;
- planner;
- ATLAS runtime;
- SMF o database;
- promozione a CERTO;
- modifica dei testi TL-facing;
- riapertura di TL_CHAT_SOURCE_NORMALIZATION_001.

## Criterio di chiusura

La capability è chiusa quando i responder nello scope espongono provenance
completa e il guard parametrizzato impedisce il ritorno del limite osservato.
