# TL_CHAT_UNIFIED_DATA_ACCESS_001

## Stato

- capability: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- titolo: Accesso governato e unificato ai dati operativi per risposte verificabili della TL Chat
- status: `CLOSED` / `TESTED` / `MERGED`
- mode: `READ_ONLY_FIRST`
- closure date: `2026-07-13`
- final PR: `#497`
- final merge SHA: `a397b1df92886f23b70561379fca89eef242d562`

## Obiettivo

Portare PROMETEO a recuperare, unificare e utilizzare i dati operativi
autorizzati necessari per rispondere alle domande della TL Chat con risposte
verificabili, tracciabili e coerenti con la gerarchia delle fonti.

## Perimetro chiuso

La capability copre:

1. dati articolo;
2. componenti e operazioni;
3. ordini e date di spedizione;
4. lettura coordinata da più fonti autorizzate;
5. dichiarazione strutturata di conflitti e dati mancanti.

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

Ogni dato recuperato conserva:

- source;
- status;
- confidence.

La risposta dichiara conflitti e dati mancanti. I dati `PREVIEW_ONLY` restano
da verificare e non possono essere presentati come autorevoli.

## Copertura consegnata

I test coprono:

- fonte presente;
- fonte mancante;
- fonte vietata;
- fonte ambigua;
- fonti conflittuali;
- valori equivalenti senza falso conflitto;
- assenza di scritture.

## Slice consegnate

- `VERTICAL_SLICE_001`: articolo, componenti e operazioni;
- `VERTICAL_SLICE_002`: ordini e date customer-demand read-only;
- `VERTICAL_SLICE_003`: rilevazione deterministica dei conflitti;
- `VERTICAL_SLICE_004`: percorso `/tl/chat` multi-fonte con readback strutturato.

## Criteri di chiusura

Tutti i criteri risultano soddisfatti:

- la TL Chat può richiedere dati da più fonti autorizzate;
- ogni dato conserva source, status e confidence;
- conflitti e dati mancanti sono dichiarati;
- `PREVIEW_ONLY` resta da verificare;
- nessuna scrittura viene effettuata;
- i test coprono fonte presente, mancante, vietata, ambigua e conflittuale.

`VERDICT`: `CAPABILITY_CLOSED`.

## Evidenze finali

- runtime multi-fonte: PR `#497`;
- merge SHA: `a397b1df92886f23b70561379fca89eef242d562`;
- validazione locale mirata: `9 passed`;
- repository CI: sei workflow PASS;
- resolver e priorità delle fonti invariati nella slice finale;
- nessun accesso in scrittura introdotto.

## Chiusura

Questa chiusura non autorizza automaticamente una nuova slice o capability.