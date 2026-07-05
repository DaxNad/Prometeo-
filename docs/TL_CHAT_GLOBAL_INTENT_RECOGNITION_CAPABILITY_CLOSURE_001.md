# TL_CHAT_GLOBAL_INTENT_RECOGNITION_CAPABILITY_CLOSURE_001

## Stato

`TL_CHAT_GLOBAL_INTENT_RECOGNITION_001` è **CHIUSA**.

## Problema risolto

Due formulazioni operative naturali non raggiungevano i responder globali già esistenti:

- `Quali codici sono pronti per la densificazione?`
- `Quali sono i nuovi inserimenti?`

Entrambe cadevano nel fallback terminale che richiedeva un articolo nel contesto.

## Causa tecnica

La causa era limitata ai matcher lessicali:

- `_question_asks_for_densification_candidates()` riconosceva `densificare`, ma non `densificazione`;
- `_requested_lifecycle_status_from_question()` riconosceva `nuovi`, ma la condizione preliminare non accettava `inserimenti`.

Non risultavano problemi in:

- estrazione articolo;
- ordine di dispatch;
- responder globali;
- caricamento delle fonti;
- provenance runtime.

## Correzione

Sono stati aggiunti esclusivamente i termini:

- `densificazione`;
- `inserimenti`.

Non sono stati introdotti:

- nuovi intent;
- nuovi responder;
- nuovi stati semantici;
- nuove fonti;
- modifiche a planner, frontend, database o SMF.

## Copertura

I test parametrizzati proteggono le formulazioni:

- `Quali codici sono pronti per la densificazione?`
- `Quali codici sono pronti per review TL prima della densificazione?`
- `Quali sono i nuovi inserimenti?`
- `Quali codici sono new entry?`

Le verifiche includono:

- assenza del fallback terminale;
- responder globale corretto;
- confidence invariata;
- `requires_confirmation=true`;
- provenance runtime presente;
- nessun path locale esposto.

## Evidenze

- commit runtime: `4933375`;
- PR runtime: `#432`;
- CI: 11 check completati con successo;
- suite backend locale: `819 passed, 3 deselected`;
- Data Leak Guard: `OK`;
- audit live post-merge: `PASS`.

### Audit densificazione

- `confidence=CERTO`;
- `requires_confirmation=true`;
- `source_id=codici_staging_preview`;
- `source_type=PREVIEW_PROFILE`;
- `confidence evidence=PREVIEW_ONLY`.

### Audit nuovi inserimenti

- `confidence=CERTO`;
- `requires_confirmation=true`;
- `source_id=tl_real_spec_intake`;
- `source_type=ARTICLE_METADATA`;
- `confidence evidence=PREVIEW_ONLY`.

## Decisione

La capability è formalmente chiusa.

Nessun ulteriore intervento runtime è richiesto per questo scope.

Eventuali estensioni future del riconoscimento linguistico costituiscono capability separate e non devono riaprire questa chiusura.
