# TL_CHAT_UNIFIED_DATA_ACCESS_001

## Stato

- capability: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- titolo: Accesso governato e unificato ai dati operativi per risposte verificabili della TL Chat
- status: `AUTHORIZED`
- mode: `READ_ONLY_FIRST`

## Obiettivo

Portare PROMETEO a recuperare, unificare e utilizzare i dati operativi
autorizzati necessari per rispondere alle domande della TL Chat con risposte
verificabili, tracciabili e coerenti con la gerarchia delle fonti.

## Perimetro della prima iterazione

La prima iterazione ammessa copre esclusivamente:

1. dati articolo;
2. componenti e operazioni;
3. ordini e date di spedizione.

La fase iniziale è read-only-first. Prima di qualsiasi implementazione devono
essere verificati i contratti, i reader, i resolver, i registri delle fonti e i
test già presenti. Questa autorizzazione non estende il perimetro oltre le tre
categorie indicate.

## Vincoli

- accesso esclusivamente read-only;
- utilizzo esclusivo di fonti autorizzate;
- nessun accesso a path arbitrari;
- nessuna mutazione dei dati;
- nessuna promozione automatica a `CERTO`;
- nessuna decisione autonoma di pianificazione;
- nessuna nuova UI;
- nessun OCR;
- nessun agente autonomo;
- nessun servizio cloud per dati industriali.

## Invarianti della risposta

Ogni dato recuperato deve conservare:

- source;
- status;
- confidence.

La risposta deve dichiarare conflitti e dati mancanti. I dati `PREVIEW_ONLY`
restano da verificare e non possono essere presentati come autorevoli.

## Copertura richiesta

I test della capability devono coprire almeno:

- fonte presente;
- fonte mancante;
- fonte vietata;
- fonte ambigua;
- fonti conflittuali.

Ogni caso deve verificare l'assenza di scritture.

## Criteri di chiusura

La capability è chiusa soltanto quando:

- la TL Chat può richiedere dati da più fonti autorizzate;
- ogni dato conserva source, status e confidence;
- conflitti e dati mancanti sono dichiarati;
- `PREVIEW_ONLY` resta da verificare;
- nessuna scrittura viene effettuata;
- i test coprono fonte presente, mancante, vietata, ambigua e conflittuale.

## Stop conditions

La capability deve fermarsi se richiede fonti non autorizzate, accesso a path
arbitrari, mutazioni, promozioni automatiche a `CERTO`, decisioni autonome del
planner, nuova UI, OCR, agenti autonomi, cloud per dati industriali oppure
un'estensione simultanea oltre il perimetro della prima iterazione.
