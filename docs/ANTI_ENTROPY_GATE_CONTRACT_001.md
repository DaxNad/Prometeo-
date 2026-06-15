# ANTI_ENTROPY_GATE_CONTRACT_001

## Status

- capability: ANTI_ENTROPY_GATE_CONTRACT_001
- status: CONTRACT_ONLY
- runtime_impact: NONE
- created_for: PROMETEO capability closure governance
- no_new_runtime: true

## Purpose

Definire il gate anti-entropia come funzione di governance per impedire scope
creep e proteggere la chiusura delle capability.

Il gate valuta se una proposta riduce davvero la distanza dal DONE verificabile
della capability corrente. Non produce lavoro aggiuntivo, non apre nuove
direzioni e non trasforma una capability chiudibile in una sequenza di NEXT.

## Scope

Il gate valuta proposte, azioni e prossimi step rispetto alla capability
corrente.

La valutazione riguarda solo:

- coerenza con la DONE definition;
- rispetto dello scope;
- rispetto del budget di entropia;
- presenza delle verifiche minime;
- assenza di aperture laterali;
- assenza di runtime, dati o integrazioni non autorizzate.

## Non-goals

Il gate non costruisce codice, non progetta architettura, non apre capability,
non decide priorita produttive, non sostituisce AGENT MOD GUARD, non
sostituisce il TL.

Il gate non propone implementazioni runtime, non collega Codex, non collega TL
Chat, non collega planner, non collega ATLAS Engine e non chiama LLM.

## Core principle

Una proposta e ammessa solo se riduce direttamente la distanza tra stato
attuale e DONE verificabile della capability corrente.

Se una proposta migliora genericamente PROMETEO ma non chiude la capability
corrente, deve essere respinta o rinviata a capability separata esplicita.

## Conceptual input schema

Input concettuale richiesto:

- capability_target
- done_definition
- current_state
- residual_gap
- proposed_action
- allowed_files
- forbidden_files
- entropy_budget
- minimal_tests
- known_blockers

Il gate deve trattare input incompleti o ambigui come motivo di BLOCK.

## Conceptual output schema

Output concettuale ammesso:

- verdict
- reason
- missing_items
- rejected_actions
- allowed_next_action

Il gate non deve produrre piano tecnico esteso, architettura, codice, test,
runtime binding o capability laterali.

## DONE definition contract

Una capability e chiudibile quando:

- il target dichiarato e stato soddisfatto;
- tutti i file richiesti nello scope sono stati creati o modificati;
- nessun file vietato e stato toccato;
- le verifiche minime richieste sono state eseguite o il blocco ambientale e
  stato dichiarato;
- il report finale include file toccati, verifiche, rischi residui e verdict;
- non rimangono gap necessari per la DONE definition corrente.

La DONE definition deve essere concreta, verificabile e limitata alla capability
corrente.

## Entropy budget

Ogni capability deve dichiarare o ereditare un budget di entropia:

- max_files
- max_tests
- max_docs
- max_runtime_changes
- max_dependencies
- allowed_directories
- forbidden_directories
- capability_lateral_ban
- refactor_ban
- data_mutation_ban

Default prudente:

- max_runtime_changes: 0 salvo capability runtime esplicita;
- max_dependencies: 0 salvo richiesta esplicita;
- capability_lateral_ban: true;
- refactor_ban: true;
- data_mutation_ban: true.

## Allowed verdicts

### CLOSE

Quando la DONE definition e soddisfatta.

Autorizza solo chiusura/report.

Vieta ulteriori miglioramenti.

Esempio PROMETEO: un documento contract-only e stato creato nello scope, il
diff e stato mostrato, il git status mostra solo quel file e non esistono
verifiche runtime richieste.

### CONTINUE

Quando manca un elemento richiesto dalla DONE definition.

Autorizza solo l'azione minima dentro scope.

Vieta refactor, nuove capability, nuove integrazioni, nuove dipendenze e
miglioramenti generici.

Esempio PROMETEO: un guard test richiesto non verifica ancora una sezione
obbligatoria del contratto; l'unica azione ammessa e completare quel controllo
nel test in scope.

### BLOCK

Quando la proposta viola scope, budget, branch, dati sensibili, runtime
boundary, o manca DONE verificabile.

Autorizza solo segnalazione del blocco.

Vieta workaround, modifiche speculative, cambio branch non autorizzato e
scrittura fuori scope.

Esempio PROMETEO: il branch corrente non e quello richiesto e la capability
vieta di cambiare branch.

## Blocking rules

BLOCK se:

- non esiste DONE verificabile
- mancano test minimi o verifiche minime
- proposta fuori scope
- file fuori budget
- nuova architettura non richiesta
- refactor laterale
- nuova dipendenza
- capability laterale
- runtime non autorizzato
- modifica dati reali
- modifica .env/segreti
- modifica SMF reale
- modifica specs_finitura
- azione migliora genericamente il sistema ma non chiude la capability

## Close rule

Se DONE definition e soddisfatta e verifiche minime passano, il verdict deve
essere CLOSE.

Se le verifiche minime non possono partire per blocco ambientale, il gate puo
comunque autorizzare CLOSE solo quando:

- il blocco e esplicito;
- non dipende da errore della patch;
- sono stati eseguiti controlli alternativi coerenti;
- non restano elementi richiesti nello scope.

## Stop rule

Quando il verdict e CLOSE, non proporre ulteriori miglioramenti o prossimi step
tecnici.

Un eventuale passo futuro deve essere richiesto come capability separata, con
branch, scope, file ammessi, file vietati e verifiche minime.

## Forbidden actions

Il gate non autorizza:

- runtime implementation
- autonomous agent behavior
- planner behavior
- architecture generation
- TL Chat binding
- planner binding
- endpoint creation
- LLM generation
- DB write
- SMF write
- metadata update
- route override
- production priority
- memory write automation
- frontend integration

## Relation with AGENT MOD GUARD

AGENT MOD GUARD definisce il perimetro operativo.

ANTI_ENTROPY_GATE valuta se una proposta riduce la distanza dal DONE.

Il gate non sostituisce il report iniziale obbligatorio, i file ammessi, i file
vietati, i test minimi o i vincoli permanenti. Opera sopra questi vincoli e
respinge azioni che aumentano il perimetro senza chiudere la capability.

## Relation with future Codex prompts

Ogni prompt Codex futuro puo includere il gate come pre-check concettuale.

Il gate non autorizza Codex a modificare file fuori scope.

Il gate deve aiutare Codex a distinguere tra:

- azione minima che chiude la capability;
- azione necessaria per continuare verso DONE;
- azione laterale da bloccare.

## Relation with TL Chat, planner and ATLAS Engine

Il gate non si collega a TL Chat, planner o ATLAS Engine in questa capability.

Eventuali binding futuri richiedono contratti separati.

Il gate non decide priorita produttive, non modifica route, non produce eventi,
non aggiorna metadata e non muta il dominio.

ATLAS Engine segnala e spiega.

Planner deterministico suggerisce.

TL decide.

## Recommended future guard

Una futura capability separata potra creare:

ANTI_ENTROPY_GATE_GUARD_001

Il guard futuro dovra verificare che questo contratto resti contract-only, non
runtime, non autonomo e limitato ai verdict:

- CLOSE
- CONTINUE
- BLOCK

## Final verdict

The Anti-Entropy Gate is defined as contract-only governance.
It authorizes no runtime behavior, no autonomous agent, no planner integration,
no TL Chat integration, no LLM generation, no endpoint exposure, and no data
mutation.
