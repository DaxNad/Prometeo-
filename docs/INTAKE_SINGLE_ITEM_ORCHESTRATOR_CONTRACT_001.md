# INTAKE_SINGLE_ITEM_ORCHESTRATOR_CONTRACT_001

## Scopo

Comporre, per un singolo `IntakeItem`, la catena governata:

`classificazione → dry-run → execution bridge`

senza introdurre nuovi writer, batch, API o dispatch dinamico.

## Ingresso

- un solo `IntakeItem`;
- ruolo richiedente opzionale;
- nessuna lista o batch.

## Sequenza vincolante

1. `classify_intake_destination(item)`
2. `plan_intake_placement(...)`
3. `execute_intake_placement(plan)` solo quando il piano è:
   - `READY`;
   - `ok=True`;
   - `ready_for_persistence=True`;
   - `requires_review=False`.

## Risultato

Il risultato deve preservare separatamente:

- classificazione;
- piano dry-run;
- risultato di esecuzione, se presente;
- stato sintetico dell’orchestrazione;
- `source_id`;
- `error_code`;
- indicazione `writer_called`.

## Stati

- `EXECUTED`
- `EXECUTION_FAILED`
- `NOT_EXECUTED`
- `INVALID_INPUT`

## Regole di sicurezza

- nessun writer diretto;
- l’unico accesso alla persistenza passa da `execute_intake_placement`;
- nessuna esecuzione su piano non `READY`;
- nessun batch;
- nessun retry;
- nessun dynamic dispatch;
- nessun hardcode articolo;
- nessuna mutazione di input, classificazione o piano;
- nessuna API, frontend o integrazione TL Chat in questa capability.

## Scope autorizzato

L’unico percorso oggi eseguibile resta:

`HUMAN_CONFIRMATIONS`
→ `operational_class`
→ dry-run `READY`
→ `APPEND`
→ `confirm_article_operational_status`

Tutte le altre destinazioni devono restituire classificazione e piano senza chiamare writer.

## Test minimi

- piano `READY` eseguito una sola volta;
- piano non `READY` non eseguito;
- input non classificato preservato;
- input invalido non eseguito;
- assenza di batch, retry e dynamic dispatch;
- assenza di hardcode articolo.
