# TL PILOT 12066 CLOSURE 001

Stato: `TL_PILOT_12066_CLOSURE_001_VERIFICATO`

Questo documento registra la chiusura controllata del primo articolo pilota reale nel perimetro PROMETEO_GOAL_CLOSURE.

## Articolo pilota

- Articolo: `12066`
- Confidence: `CERTO`
- Primary ZAW station: `ZAW1`
- ZAW2: `false`
- HENN: `true`
- PIDMILL: `true`
- CP finale: obbligatorio
- CP mode: `VERTICALE_DUE_PIANI`

## Regola dominio confermata

Per `12066`, eventuali fonti derivate che indicano `HENN_ZAW2_PIDMILL` devono essere trattate come mismatch.

Valore operativo corretto:

- `HENN_ZAW1_PIDMILL`
- `primary_zaw_station = ZAW1`
- `has_zaw2 = false`

## Capability verificate

- TL Chat risponde da article summary prima del lifecycle registry.
- Article summary endpoint restituisce profilo coerente.
- Article process matrix legge il profilo realistico con ZAW1 confermata.
- Article TL summary produce profilo leggibile per uso operativo.
- Planner gate blocca 12066 senza ordine/lotto/richiesta attiva.
- Planner gate ammette 12066 solo con ordine attivo e nessun blocker.

## Test di verifica

Ultima verifica locale nota:

- `test_tl_chat_answers_12066_from_article_summary_before_lifecycle`
- `test_production_article_summary_endpoint_returns_12066_tl_summary`
- `test_article_matrix_reads_realistic_12066_profile_with_tl_confirmed_zaw1`
- `test_article_tl_summary_builds_readable_12066_profile`
- `test_planner_gate_blocks_12066_without_active_demand`
- `test_planner_gate_admits_12066_with_active_order_and_no_blockers`

Risultato:

- 6 passed
- `make tl-eval`: `RESULT=PASS`
- Privacy Guard: OK
- Data Leak Guard: OK

## Scope rispettato

Questa chiusura non introduce:

- runtime app
- frontend
- AI esterna
- SMF reale
- immagini
- specifiche reali
- nuovi adapter
- nuova architettura
- nuovo world model

## Stato finale

`12066` è il primo articolo pilota verificato per PROMETEO_GOAL_CLOSURE.

Il suo uso resta soggetto al planner gate: `planner_eligible=true` non produce priorità autonoma senza ordine attivo, lotto attivo o richiesta operativa esplicita.
