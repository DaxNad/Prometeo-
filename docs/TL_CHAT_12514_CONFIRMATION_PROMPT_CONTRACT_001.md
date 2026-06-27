# TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001

## Purpose

Define the exact TL confirmation questions that TL Chat may ask for article 12514.

This is a document-only prompt contract. It does not implement runtime confirmation and does not promote any field to CERTO.

## Source documents

- docs/TL_CHAT_12514_SOURCE_CONFIRMATION_REVIEW_001.md
- data/local_reports/spec_intake_preview/12514_metadata_preview.json

## Contract rule

TL answers are confirmation inputs only.

They must not automatically promote preview data to CERTO.

Any future promotion requires separate governed rules, tests, and explicit capability closure.

## Allowed answer states

| State | Meaning | Runtime effect in this contract |
|---|---|---|
| YES | TL confirms the proposed value | Candidate confirmation only |
| NO | TL rejects the proposed value | Keep DA_VERIFICARE and request corrected value |
| UNKNOWN | TL cannot confirm | Keep DA_VERIFICARE |
| CORRECTED_VALUE | TL provides replacement value | Candidate correction only |
| NOT_VISIBLE | TL states the value is not visible in current source | Keep DA_VERIFICARE or MISSING |

## Confirmation prompt format

TL Chat must ask one bounded confirmation group at a time.

Each question must include:

- field group
- current preview value
- allowed answer states
- explicit statement that confirmation does not mean CERTO
- blocked operational conclusions, when relevant

## Required TL confirmation questions

### Q1 - Article identity

Question:

Confermi per articolo 12514 questi dati: codice 7056055000A0, disegno A1675003603, rev 6, data revisione 25/09/2025?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- YES creates candidate confirmation for article identity only.
- NO or UNKNOWN keeps fields DA_VERIFICARE.
- CORRECTED_VALUE creates candidate correction only.

### Q2 - Packaging and quantities

Question:

Confermi lotto_quantita 94, imballo 50563, quantita_imballo 80?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- YES creates candidate confirmation for packaging and quantities only.
- It does not authorize production or planning.

### Q3 - Normalized route

Question:

Confermi la sequenza route normalizzata PROMETEO per articolo 12514 partendo dalle operazioni preview disponibili?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- YES creates candidate route confirmation only.
- Route remains not CERTO until governed encoding and tests exist.
- NO, UNKNOWN, or CORRECTED_VALUE keeps route_status DA_VERIFICARE.

### Q4 - ZAW station resolution

Question:

I due passaggi MACCHINA CRIMP RING ZAW sono entrambi ZAW1 oppure coinvolgono altra postazione?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Required clarification:

- If not both ZAW1, TL must provide the intended station mapping.

Outcome:

- Never infer ZAW2 only from two visible ZAW passes.
- zaw_station_resolution remains DA_VERIFICARE until governed encoding and tests exist.

### Q5 - Components

Question:

Confermi i componenti preview 468922, 468728, 468796, 468865 e 467660 per articolo 12514?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- YES creates candidate component confirmation only.
- NO or CORRECTED_VALUE requires component-level correction.

### Q6 - Tooling

Question:

Confermi le attrezzature preview CRT004, CRM004, CRT024 e CRM024?

Allowed answers:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- YES creates candidate tooling confirmation only.
- It does not resolve planner eligibility.

### Q7 - PIDMILL and CP visibility

Question:

PIDMILL e CP sono realmente assenti per articolo 12514 oppure sono solo non visibili nella specifica fornita?

Allowed answers:

- ABSENT
- NOT_VISIBLE
- UNKNOWN
- CORRECTED_VALUE

Outcome:

- ABSENT creates candidate absence confirmation only.
- NOT_VISIBLE or UNKNOWN keeps the fields MISSING or DA_VERIFICARE.
- CORRECTED_VALUE creates candidate correction only.

## Forbidden prompt behavior

TL Chat must not ask confirmation questions that imply:

- article 12514 is ready for planning
- article 12514 is ready for production
- planner_eligible can become true in this capability
- route can become CERTO automatically
- ZAW2 can be inferred from repeated ZAW operations
- SMF/DB can be written
- ATLAS runtime can be invoked

## Required response framing

Every confirmation prompt must state:

La tua risposta serve solo come input di conferma governata. Non promuove automaticamente il dato a CERTO e non abilita planner o produzione.

## Confirmation output schema

Future runtime, if implemented, must produce a structured result equivalent to:

- article: 12514
- question_id
- field_group
- proposed_value
- tl_answer_state
- corrected_value, if any
- resulting_status: CANDIDATE_CONFIRMATION, DA_VERIFICARE, MISSING, or BLOCKED
- forbidden_runtime_effects_preserved: true

## Recommended next capability

TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_TEST_001

Purpose:

- guard this prompt contract with a document-level test
- require Q1-Q7 to remain present
- require allowed answer states
- require anti-CERTO and anti-planner language
- preserve non-goals

## Explicit non-goals

- no runtime confirmation
- no automatic promotion to CERTO
- no preview JSON mutation
- no planner
- no ATLAS runtime
- no SMF/DB write
- no new source ingestion
- no TL Chat API change
- no production decision automation

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001
STATUS: DOCUMENT_CREATED
VERDICT: PENDING_TEST_AND_PR
NEXT SAFE ACTION: add, commit, push, and open PR for this confirmation prompt contract
