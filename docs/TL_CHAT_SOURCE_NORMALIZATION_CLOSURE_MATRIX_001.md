# TL_CHAT_SOURCE_NORMALIZATION_CLOSURE_MATRIX_001

## Stato

Binding di chiusura per `TL_CHAT_SOURCE_NORMALIZATION_001`.

## Contratto comune

Campi pubblici opzionali:

- `source`
- `source_status`
- `semantic_status`
- `missing_data`

I campi devono essere presenti solo quando semanticamente applicabili. `SOURCE_*` è riservato a sorgenti o adapter reali; una regola interna non deve fingere una sorgente recuperata.

## Classi

| Ramo | Classe | source | source_status | semantic_status | missing_data |
|---|---|---|---|---|---|
| articolo sconosciuto | dato mancante | missing | SOURCE_MISSING | MANCANTE | profilo o fonte operativa |
| fallback terminale senza articolo | contesto mancante | missing | SOURCE_MISSING | MANCANTE | codice articolo |
| fallback operativo turno | contesto operativo mancante | missing | SOURCE_MISSING | MANCANTE | articolo, ordine, lotto, board o evento |
| PIDMILL senza dima | dato specifico mancante | local_specs_metadata | SOURCE_FOUND | MANCANTE | dima PIDMILL |
| componenti assenti | dato specifico mancante | local_specs_metadata | SOURCE_FOUND | MANCANTE | components |
| componenti illeggibili | dato non interpretabile | local_specs_metadata | SOURCE_FOUND | DA_VERIFICARE | struttura components leggibile |
| family registry | fonte presente | family_registry | SOURCE_FOUND | CERTO | assente |
| local specs metadata | fonte presente | local_specs_metadata | SOURCE_FOUND | uguale a `confidence` della risposta | assente |
| lifecycle registry | fonte presente | lifecycle_registry | SOURCE_FOUND | uguale a `confidence` della risposta | assente |
| staging preview | fonte preview | codici_staging_preview | PREVIEW_ONLY | PREVIEW_ONLY | assente |
| spec intake preview | fonte preview | spec_intake_preview | stato restituito dal resolver, normalmente PREVIEW_ONLY | PREVIEW_ONLY | assente |
| article summary | fonte composta | article_summary | SOURCE_FOUND | uguale a `confidence` della risposta | assente |
| context reader trovato | fonte governata | context_source_reader_adapter | SOURCE_FOUND | DA_VERIFICARE | eventuali dati non promossi |
| context reader non disponibile | fonte indisponibile | context_source_reader_adapter | stato reader tipizzato | DA_VERIFICARE | dato richiesto |
| regola ZAW generale | regola interna | non applicabile | non applicabile | CERTO | assente |
| spiegazioni profilo/ZAW/planner | derivazione da profilo | local_specs_metadata | SOURCE_FOUND | uguale a `confidence` del profilo | assente |

## Criteri di chiusura

La capability è chiusa solo quando:

1. ogni ramo runtime appartiene a una classe della matrice;
2. i rami `MANCANTE` espongono `missing_data`;
3. preview e fonti read-only non vengono promosse a `CERTO`;
4. risposte di regola non dichiarano fonti documentali inesistenti;
5. risposte non applicabili non espongono campi null;
6. test positivi e negativi coprono ogni classe;
7. audit, suite TL Chat e guard completi sono verdi.
