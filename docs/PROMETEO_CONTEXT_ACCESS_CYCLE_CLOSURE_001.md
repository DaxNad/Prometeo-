# PROMETEO_CONTEXT_ACCESS_CYCLE_CLOSURE_001

## Scopo

Questo documento chiude il ciclo governato `Context Access` dopo la sequenza:

- context source binding;
- context source index;
- context source reader adapter read-only minimale;
- verification harness metadata-only;
- binding policy contract anti-drift.

La chiusura non abilita alcun collegamento runtime.

## Stato del ciclo

```text
CONTEXT ACCESS CYCLE: CLOSED
ADAPTER: READ_ONLY
OUTPUT: METADATA_ONLY
RUNTIME_BINDING: FORBIDDEN
TL_CHAT_BINDING: FORBIDDEN
ATLAS_ENGINE_BINDING: FORBIDDEN
PLANNER_BINDING: FORBIDDEN
FULL_CONTENT_READING: FORBIDDEN
```

## Valore ottenuto

PROMETEO ora dispone di un perimetro governato per rappresentare fonti di contesto indicizzate senza trasformarle in input runtime libero.

Il valore principale non è l'accesso ai contenuti, ma la separazione controllata tra:

- fonti documentate;
- indice macchina;
- adapter read-only;
- test anti-deriva;
- divieto esplicito di binding prematuro.

## Cosa è chiuso

- Esiste un indice delle fonti di contesto.
- Esiste un adapter minimale read-only.
- Esistono test sul contratto metadata-only.
- Esiste un controllo anti-binding verso runtime, TL Chat, ATLAS Engine e planner.
- Il ciclo è verificabile tramite guard locali e CI.

## Cosa non è abilitato

- Nessuna lettura integrale del contenuto delle fonti.
- Nessun collegamento a TL Chat.
- Nessun collegamento ad ATLAS Engine.
- Nessun collegamento al planner deterministico.
- Nessun endpoint FastAPI.
- Nessun retrieval runtime.
- Nessun agente libero.
- Nessuna scrittura su fonti, SMF, database o repository.

## Vincoli permanenti da preservare

- `Order -> Route -> Station -> ProductionEvent` resta il dominio centrale.
- ATLAS Engine ragiona e segnala, non muta direttamente il dominio.
- Il planner suggerisce, il Team Leader decide.
- Le fonti reali e la conferma TL prevalgono su cache, export, preview e inferenze.
- Ogni dato operativo deve avere fonte, confidence e motivo.
- Nessun dato reale privato deve essere esposto o versionato.
- Nessuna capability nuova deve essere aperta prima della chiusura della capability attiva.

## Prossimo gate consentito

La prossima capability può essere aperta solo se resta nel perimetro read-only e introduce una verifica controllata senza collegare l'adapter al runtime.

Esempi ammessi:

- test aggiuntivo di coerenza metadata;
- contratto documentale per futura lettura selettiva;
- policy di lifecycle/retention/superseding dell'indice;
- verifica anti-obsolescenza delle fonti indicizzate.

Esempi non ammessi in questa fase:

- binding TL Chat;
- binding ATLAS Engine;
- binding planner;
- endpoint FastAPI;
- retrieval runtime;
- lettura contenuto completo delle fonti;
- agenti autonomi su documenti locali.

## Regola di chiusura

Il ciclo `Context Access` è considerato chiuso solo come infrastruttura governata metadata-only.

Ogni futuro avanzamento dovrà dichiarare esplicitamente:

1. capability attiva;
2. file ammessi;
3. file vietati;
4. test minimi;
5. assenza di binding runtime;
6. assenza di lettura contenuto completo;
7. assenza di dati reali privati.

## Verdetto

```text
VERDETTO: CLOSED_METADATA_ONLY
NEXT_ALLOWED_MOVE: ONE_READONLY_POLICY_OR_TEST_CAPABILITY
DO_NOT_OPEN_RUNTIME_BINDING: TRUE
```

