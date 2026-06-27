# TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_001

## Purpose

Define the document-only rendering contract for future TL Chat responses related to
article 12514 confirmation answers.

This contract defines how TL Chat may display a non-persistent confirmation response
to the user after a TL answers one of the governed Q1-Q7 confirmation questions.

This is a rendering contract only.

It does not implement runtime behavior.
It does not persist TL answers.
It does not mutate preview JSON.
It does not promote any value to CERTO.
It does not enable planner eligibility.
It does not invoke ATLAS.
It does not write to SMF or database.
It does not change API behavior.

## Source references

This contract depends on:

* docs/TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001.md
* docs/TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001.md
* docs/TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001.md
* backend/tests/test_tl_chat_12514_confirmation_prompt_contract_doc.py
* backend/tests/test_tl_chat_12514_confirmation_runtime_boundary_doc.py
* backend/tests/test_tl_chat_12514_confirmation_non_persistent_response_model_doc.py

## Rendering principle

A TL Chat confirmation response may be displayed only as a non-persistent candidate
confirmation or correction.

The rendered answer must make the following clear:

* the article is 12514
* the answered question id is Q1-Q7
* the response is not persisted
* the response is not source of truth
* the response does not promote data to CERTO
* the response does not enable planner eligibility
* the response does not make production readiness claims
* the response does not make planning readiness claims
* the next action remains governed confirmation or source review

## Required rendered sections

Every rendered confirmation response must include these sections:

| Section | Required | Purpose |
| --- | --- | --- |
| Article | Yes | Identify article 12514 |
| Question | Yes | Identify the answered Q1-Q7 question |
| TL answer state | Yes | Display YES, NO, UNKNOWN, CORRECTED_VALUE, NOT_VISIBLE, or ABSENT |
| Resulting status | Yes | Display candidate or blocked status |
| Candidate data | Yes | Display proposed or corrected values without certainty promotion |
| Runtime effects | Yes | Explicitly state no persistence and no operational mutation |
| Confidence | Yes | Preserve DA_VERIFICARE or candidate confidence |
| Missing data | Yes | Show unresolved fields when present |
| Next safe action | Yes | Provide only one governed next action |

## Allowed rendered statuses

The rendered response may display only these statuses:

* CANDIDATE_CONFIRMATION
* CANDIDATE_CORRECTION
* DA_VERIFICARE
* MISSING
* BLOCKED

The rendered response must not display:

* CERTO
* PRODUCTION_READY
* PLANNING_READY
* PLANNER_ELIGIBLE
* SOURCE_OF_TRUTH
* SAVED
* PERSISTED

## Required runtime effects statement

Every rendered response must explicitly include the following meaning:

```text
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente,
nessuna promozione a CERTO, nessun planner, nessun ATLAS,
nessuna scrittura SMF/DB.
The wording may change in future UI implementation, but the meaning must remain present.

## Required rendering shape

Future TL Chat rendering should follow this minimal shape:

Articolo: 12514
Domanda: Qx - <field_group>
Risposta TL: <tl_answer_state>
Stato risultante: <resulting_status>
Dati candidati: <candidate data>
Confidenza: DA_VERIFICARE / candidate only
Dati mancanti: <missing data or none>
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.
Prossima azione sicura: <one governed next action>

## Q1 rendering rule

Q1 concerns article identity.

Field group:

article_identity

Allowed rendered candidate data:

* codice
* disegno
* rev
* rev_data

Required rendering constraint:

Q1 confirmation may be rendered as CANDIDATE_CONFIRMATION only.
It must not be rendered as CERTO.

## Q2 rendering rule

Q2 concerns packaging and quantities.

Field group:

packaging_and_quantities

Allowed rendered candidate data:

* lotto_quantita
* imballo
* quantita_imballo

Required rendering constraint:

Q2 confirmation may be rendered as CANDIDATE_CONFIRMATION only.
It must not be rendered as production-ready or planning-ready.

## Q3 rendering rule

Q3 concerns normalized route visibility.

Field group:

normalized_route

Allowed rendered candidate data:

* visible route steps
* missing route steps
* route ambiguity notes

Required rendering constraint:

Q3 confirmation must preserve DA_VERIFICARE where route completeness is not proven.
It must not enable planner eligibility.

## Q4 rendering rule

Q4 concerns ZAW station resolution.

Field group:

zaw_station_resolution

Allowed rendered candidate data:

* ZAW station candidate
* ambiguity note
* unresolved machine distinction

Required rendering constraint:

Q4 confirmation must not infer ZAW2 from repeated ZAW operations.
It must not resolve station ambiguity unless the source or TL answer explicitly resolves it.

## Q5 rendering rule

Q5 concerns components.

Field group:

components

Allowed rendered candidate data:

* component codes
* component labels
* missing component notes
* uncertain component notes

Required rendering constraint:

Q5 confirmation may display component candidates only.
It must not promote component completeness to CERTO.

## Q6 rendering rule

Q6 concerns tooling.

Field group:

tooling

Allowed rendered candidate data:

* tool codes
* tool labels
* missing tooling notes
* uncertain tooling notes

Required rendering constraint:

Q6 confirmation may display tooling candidates only.
It must not promote tooling completeness to CERTO.

## Q7 rendering rule

Q7 concerns PIDMILL and CP visibility.

Field group:

pidmill_and_cp_visibility

Allowed rendered candidate data:

* PIDMILL visible
* PIDMILL absent
* CP visible
* CP absent
* visibility uncertainty

Required rendering constraint:

ABSENT is renderable only for Q7.
Absence must not be rendered as CERTO unless governed source confirmation exists later.

## Rendering examples

### YES example

Articolo: 12514
Domanda: Q1 - article_identity
Risposta TL: YES
Stato risultante: CANDIDATE_CONFIRMATION
Dati candidati: codice 7056055000A0, disegno A1675003603, rev 6, rev_data 25/09/2025
Confidenza: DA_VERIFICARE
Dati mancanti: none
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.
Prossima azione sicura: mantenere la conferma come candidata fino a fonte governata.

### CORRECTED_VALUE example

Articolo: 12514
Domanda: Q2 - packaging_and_quantities
Risposta TL: CORRECTED_VALUE
Stato risultante: CANDIDATE_CORRECTION
Dati candidati: corrected_value present
Confidenza: DA_VERIFICARE
Dati mancanti: source confirmation
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.
Prossima azione sicura: richiedere conferma fonte prima di aggiornare qualsiasi dato.

### UNKNOWN example

Articolo: 12514
Domanda: Q4 - zaw_station_resolution
Risposta TL: UNKNOWN
Stato risultante: DA_VERIFICARE
Dati candidati: unresolved ZAW station
Confidenza: DA_VERIFICARE
Dati mancanti: explicit station evidence
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.
Prossima azione sicura: consultare fonte governata o chiedere conferma mirata.

### BLOCKED example

Articolo: 12514
Domanda: Q3 - normalized_route
Risposta TL: YES
Stato risultante: BLOCKED
Dati candidati: route answer cannot be used for production readiness
Confidenza: DA_VERIFICARE
Dati mancanti: governed route source
Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.
Prossima azione sicura: separare conferma candidata da decisione operativa.

## Forbidden rendering behavior

The rendered TL Chat answer must not say or imply:

* conferma salvata
* dato aggiornato
* dato certo
* CERTO
* articolo pronto per produzione
* articolo pronto per pianificazione
* planner abilitato
* ATLAS invocato
* SMF aggiornato
* database aggiornato
* sorgente modificata
* preview JSON modificato
* conferma usata come source of truth

## Safe next action policy

Every rendered confirmation response must include exactly one next safe action.

Allowed next safe actions include:

* mantenere come conferma candidata
* richiedere conferma fonte governata
* chiedere correzione mirata al TL
* consultare specifica reale
* mantenere DA_VERIFICARE
* bloccare la decisione operativa

Forbidden next safe actions include:

* pianificare produzione
* autorizzare produzione
* promuovere a CERTO
* salvare risposta TL
* aggiornare preview JSON
* aggiornare SMF
* aggiornare database
* invocare planner
* invocare ATLAS

## Acceptance criteria

This document is accepted only if a future test can verify that it includes:

* capability name
* rendering principle
* required rendered sections
* allowed rendered statuses
* forbidden rendered statuses
* required runtime effects statement
* required rendering shape
* Q1-Q7 rendering rules
* rendering examples
* forbidden rendering behavior
* one-next-safe-action policy
* explicit no persistence
* explicit no CERTO
* explicit no planner
* explicit no ATLAS
* explicit no SMF/DB
* explicit no API/runtime implementation

## Recommended next capability

TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_TEST_001

Purpose:

Guard this rendering contract with a document-level test before any runtime rendering implementation is considered.

The test must verify that the document preserves:

* required rendered sections
* allowed rendered statuses
* forbidden rendered statuses
* runtime effects statement
* Q1-Q7 rendering rules
* examples for YES, CORRECTED_VALUE, UNKNOWN, and BLOCKED
* forbidden persistence and operational claims
* exactly one safe next action policy
* no runtime implementation
* no planner
* no ATLAS
* no SMF/DB
* no API changes

## Non-goals

This capability does not implement:

* runtime rendering
* frontend changes
* TL Chat API changes
* answer persistence
* confirmation persistence
* source mutation
* preview JSON mutation
* CERTO promotion
* planner enablement
* ATLAS invocation
* SMF write
* database write
* production readiness
* planning readiness

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_RESPONSE_RENDERING_CONTRACT_001
STATUS: DOCUMENT_CREATED
VERDICT: PENDING_TEST_AND_PR
NEXT SAFE ACTION: add a document-level test guard before runtime rendering
