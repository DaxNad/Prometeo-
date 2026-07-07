# PROMETEO_CAPABILITY_EXECUTION_WORKFLOW_001

## Status
- capability: PROMETEO_CAPABILITY_EXECUTION_WORKFLOW_001
- status: DOCUMENT_ONLY
- runtime_impact: NONE
- created_for: PROMETEO controlled capability closure

## Purpose
Definire il ciclo minimo di lavoro per chiudere una capability PROMETEO senza generare entropia.

## Workflow

### 1. Tu + ChatGPT
Definire:
- capability;
- vincoli;
- rischio;
- prossima mossa minima.

Output ammesso:
- obiettivo;
- scope;
- cosa bloccare;
- verdict iniziale.

### 2. Codex - review read-only
Codex verifica:
- diagnosi tecnica;
- file realmente coinvolti;
- rischi;
- test necessari;
- se esiste già un binding o comportamento sufficiente.

Output ammesso:
- cosa è già coperto;
- cosa manca;
- file da toccare;
- test da aggiungere o eseguire;
- verdict tecnico.

### 3. Tu + ChatGPT
Decisione esplicita:
- cosa autorizzare;
- cosa bloccare;
- se procedere con patch, solo test, solo doc, oppure CLOSE.

Se il perimetro non è chiaro, la capability resta BLOCK.

### 4. Codex - patch circoscritta
Codex modifica solo se:
- scope chiaro;
- file ammessi dichiarati;
- rischio accettabile;
- test minimi definiti.

La patch deve essere minima.
Nessun refactor laterale.
Nessuna nuova architettura.
Nessun runtime se non autorizzato.

### 5. Terminale
Regole:
- eseguire Python esclusivamente tramite `./tools/py`;
- verificare percorso corrente e stato reale prima del comando;
- non ripetere comandi falliti senza correggerne la causa;
- usare patch con guard espliciti sui marker attesi.

Eseguire:
- test mirati;
- `git status --short`;
- `git diff`;
- commit;
- PR.

Il terminale non deve introdurre modifiche non richieste.

### 6. ChatGPT
Chiudere la capability:
- stato reale;
- test eseguiti;
- file toccati;
- rischi residui;
- verdict finale;
- prossima mossa unica, solo se necessaria.

## External Timer Rule
Quando una fase richiede di attendere un intervallo temporale esplicito:

- ChatGPT non deve stimare mentalmente il tempo trascorso;
- deve creare un timer esterno reale con offset esatto;
- il timer deve essere associato all'azione da eseguire allo scadere;
- allo scadere deve verificare lo stato reale prima di procedere;
- in caso di failure, stato inatteso o scope change deve fermarsi;
- non deve dichiarare che il tempo è trascorso senza una schedulazione effettiva.

Questa regola si applica a verifiche CI, retry tecnici, attese operative e controlli differiti.

## Anti-Entropy Rule
Non aprire nuovi documenti, capability, guard, eval o runtime se la capability corrente è già chiudibile.

Verdict ammessi:
- CLOSE;
- CONTINUE;
- BLOCK.

Se una proposta non riduce direttamente la distanza dal DONE, il verdict deve essere BLOCK.

## Final Verdict
This workflow authorizes controlled capability execution only.
It does not authorize runtime behavior, planner integration, TL Chat integration, ATLAS integration, LLM generation, endpoint exposure, DB write, SMF write, or data mutation.
