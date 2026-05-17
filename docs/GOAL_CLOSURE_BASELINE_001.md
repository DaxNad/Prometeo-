# GOAL CLOSURE BASELINE 001

Stato: `GOAL_CLOSURE_BASELINE_001`

Questa baseline chiude il primo blocco verificabile della fase PROMETEO_GOAL_CLOSURE.

## Commit integrati

- `#177` controlled TL semantic eval
- `#178` controlled TL semantic eval matrix
- `#179` deterministic TL semantic eval runner
- `#180` TL semantic eval CLI
- `#181` standard TL eval command
- `#182` TL Eval Guard CI
- `#183` GOAL_CLOSURE policy
- `#184` practical TL event triage case
- `#186` TL Chat operational answer shape guard
- `#188` 12066 pilot closure

## Catena chiusa

PROMETEO dispone ora di una catena eval minima:

- micro-campione sanificato
- matrice eval
- runner deterministico
- CLI
- comando standard
- CI guard
- policy GOAL_CLOSURE
- primo caso pratico di triage evento stazione
- guard forma risposta operativa breve TL Chat
- primo articolo pilota reale verificato: `12066`

## Capability chiusa

PROMETEO distingue:

- evento OPEN su stazione
- criticità automatica

PROMETEO protegge inoltre la forma risposta TL Chat:

- Route
- Vincoli
- Nota
- Azione

## Primo pilota reale verificato

`12066` è registrato come primo articolo pilota reale chiuso nel perimetro `PROMETEO_GOAL_CLOSURE`.

Vincoli operativi confermati:

- `confidence = CERTO`
- `primary_zaw_station = ZAW1`
- `has_zaw2 = false`
- HENN presente
- PIDMILL presente
- CP finale obbligatorio
- mismatch `HENN_ZAW2_PIDMILL` trattato come fonte derivata errata
- planner gate obbligatorio: nessuna priorità autonoma senza ordine/lotto/richiesta attiva

Documento dedicato:

- `docs/TL_PILOT_12066_CLOSURE_001.md`

Regola fissata:

- un evento aperto richiede triage;
- la criticità si alza solo se esiste blocco confermato.

## Verifiche baseline

Ultima verifica locale nota:

- make tl-eval: RESULT=PASS
- backend/tests/test_goal_closure_policy_001.py: 3 passed
- TL eval test suite: 24 passed
- TL Chat contract suite: 25 passed
- 12066 pilot test subset: 6 passed
- Privacy Guard: OK
- Data Leak Guard: OK

## Scope rispettato

Questa baseline non introduce:

- runtime app
- frontend
- AI esterna
- SMF reale
- specifiche reali
- immagini
- codici reali
- nuove architetture
- nuovo world model
- nuovi adapter

## Regola di avanzamento

Da questa baseline in avanti, ogni passo GOAL deve:

1. chiudere una capability esistente;
2. essere piccolo e testabile;
3. non introdurre dipendenze laterali;
4. rispettare la policy `PROMETEO_GOAL_CLOSURE`; 
5. mantenere `make tl-eval` verde.

## Stato finale

`GOAL_CLOSURE_BASELINE_001` è valida quando `make tl-eval` produce `RESULT=PASS` e il contratto TL Chat resta verde.
