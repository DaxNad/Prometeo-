# TL_CHAT_UNKNOWN_ARTICLE_BEHAVIOR_CONTRACT_001

## Capability

`TL_CHAT_SOURCE_NORMALIZATION_001`

## Ramo classificato

`backend/app/api/tl_chat.py::_build_contract_response`

Condizione osservabile:

- è presente un codice articolo valido;
- nessuna sorgente precedente produce una risposta utilizzabile;
- il ramo termina con il messaggio `NON DISPONIBILE NEL PROFILO ATTIVO`.

## Classificazione

- Classe risposta: `ARTICLE_OPERATIONAL_MISSING`
- Stato utente: `MANCANTE`
- Confidence pubblica corrente: `DA_VERIFICARE`
- Richiede conferma: `true`
- Planner eligible: `false`
- Promozione automatica a `CERTO`: vietata
- Natura: fallback sicuro per articolo non risolto
- Bug runtime corrente: non dimostrato

## Comportamento pubblico da preservare

La risposta deve:

1. restituire HTTP `200` e `ok=true`;
2. includere il codice articolo richiesto;
3. dichiarare che l'articolo non è disponibile nel profilo attivo;
4. usare `confidence=DA_VERIFICARE`;
5. usare `requires_confirmation=true`;
6. non inventare route, componenti, stato lifecycle o istruzioni operative;
7. non generare priorità produttive;
8. indicare come prossima azione la verifica tramite fonte autorizzata o la disponibilità di profilo/specifica;
9. non esporre dettagli tecnici interni, nomi di test o strumenti di sviluppo;
10. non promuovere il dato a `CERTO` e non autorizzare planner o esecuzione.

## Origine e stato sorgente attesi

Prima della normalizzazione completa, il ramo non dichiara ancora campi strutturati dedicati.

Target futuro della capability:

- `source = missing`
- `source_status = SOURCE_MISSING`
- `semantic_status = MANCANTE`
- `missing_data` contiene almeno l'assenza di un profilo o di una fonte operativa autorizzata;
- `next_safe_action` mantiene il comportamento pubblico corrente.

Questi campi sono un target architetturale futuro e non modificano il contratto runtime in questa fase.

## Regressione esistente

Test rilevante:

`backend/tests/test_tl_chat_contract.py::test_tl_chat_contract_unknown_article_stays_da_verificare`

Il test verifica già:

- risposta HTTP corretta;
- `ok=true`;
- `confidence=DA_VERIFICARE`;
- `requires_confirmation=true`;
- dettagli tecnici nascosti;
- presenza del messaggio `NON DISPONIBILE NEL PROFILO ATTIVO`;
- assenza di rumore tecnico relativo a Git, pytest e guard.

## Gap residuo

La regressione corrente non verifica ancora esplicitamente:

- presenza del codice articolo nella risposta;
- contenuto della prossima azione sicura;
- assenza di priorità o istruzioni operative inventate;
- futura provenienza strutturata `missing / SOURCE_MISSING / MANCANTE`.

## Fuori scope

- modifica del modello `TLChatResponse`;
- introduzione immediata di nuovi campi API;
- passaggio forzato dal Context Resolver;
- nuove sorgenti;
- modifica a UI, planner, SMF o database;
- refactoring degli altri rami TL Chat.

## Esito

`PUBLIC_BEHAVIOR_CLASSIFIED`
