# TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001

## Purpose

Define the non-operational response model for TL Chat confirmation behavior for article 12514.

This model covers the TL-facing confirmation rendering. The runtime endpoint may persist a governed local confirmation evidence record, but that evidence is not operational truth: it does not mutate preview JSON, promote any field to CERTO, enable planner, invoke ATLAS, or write to SMF/database.

## Source documents

* docs/TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001.md
* docs/TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001.md
* backend/tests/test_tl_chat_12514_confirmation_prompt_contract_doc.py
* backend/tests/test_tl_chat_12514_confirmation_runtime_boundary_doc.py

## Model principle

A TL answer to Q1-Q7 may be represented as a candidate confirmation response and, through the structured endpoint, as a governed local evidence record.

The response model is allowed to summarize what the TL answered, but neither the response nor the persisted evidence may become source of truth or modify operational state.

## Required fields

| Field                               |    Required | Meaning                                              |
| ----------------------------------- | ----------: | ---------------------------------------------------- |
| article                             |         Yes | Article identifier. For this capability: 12514       |
| question_id                         |         Yes | One of Q1, Q2, Q3, Q4, Q5, Q6, Q7                    |
| field_group                         |         Yes | Governed confirmation group                          |
| proposed_value                      |         Yes | Current preview value shown to TL                    |
| tl_answer_state                     |         Yes | TL answer state from the allowed set                 |
| corrected_value                     | Conditional | Present only when tl_answer_state is CORRECTED_VALUE |
| resulting_status                    |         Yes | Non-persisted candidate result                       |
| forbidden_runtime_effects_preserved |         Yes | Must be true                                         |

## Allowed question_id values

* Q1
* Q2
* Q3
* Q4
* Q5
* Q6
* Q7

## Allowed tl_answer_state values

* YES
* NO
* UNKNOWN
* CORRECTED_VALUE
* NOT_VISIBLE
* ABSENT

## Allowed resulting_status values

| resulting_status       | Meaning                                               |
| ---------------------- | ----------------------------------------------------- |
| CANDIDATE_CONFIRMATION | TL answer appears to confirm proposed value           |
| CANDIDATE_CORRECTION   | TL provides corrected value                           |
| DA_VERIFICARE          | Value remains uncertain                               |
| MISSING                | Required value is unavailable, absent, or not visible |
| BLOCKED                | Request exceeds governed confirmation scope           |

## Field group mapping

| question_id | field_group               |
| ----------- | ------------------------- |
| Q1          | article_identity          |
| Q2          | packaging_and_quantities  |
| Q3          | normalized_route          |
| Q4          | zaw_station_resolution    |
| Q5          | components                |
| Q6          | tooling                   |
| Q7          | pidmill_and_cp_visibility |

## State transition rules

### YES

YES may produce:

* CANDIDATE_CONFIRMATION

YES must not produce:

* CERTO
* planner_eligible=true
* route_status=CERTO
* production readiness
* planning readiness

### NO

NO may produce:

* DA_VERIFICARE
* BLOCKED, if the user asks for an effect outside scope

NO must not persist rejection.

### UNKNOWN

UNKNOWN must produce:

* DA_VERIFICARE

UNKNOWN must not infer missing values.

### CORRECTED_VALUE

CORRECTED_VALUE may produce:

* CANDIDATE_CORRECTION

CORRECTED_VALUE requires corrected_value to be present.

CORRECTED_VALUE must not mutate source data or become CERTO.

### NOT_VISIBLE

NOT_VISIBLE may produce:

* DA_VERIFICARE
* MISSING

NOT_VISIBLE must not infer absence.

### ABSENT

ABSENT is allowed only for Q7 PIDMILL and CP visibility.

ABSENT may produce:

* CANDIDATE_CONFIRMATION
* MISSING

ABSENT must not promote absence to CERTO.

## Required invariant

Every response object must include forbidden_runtime_effects_preserved=true.

This means:

* local TL confirmation evidence persistence is allowed only as governed evidence
* no preview JSON mutation
* no automatic promotion to CERTO
* no planner enablement
* no ATLAS invocation
* no SMF write
* no database write
* no TL Chat API contract change
* no production or planning readiness decision

## Example response object

```json
{
  "article": "12514",
  "question_id": "Q1",
  "field_group": "article_identity",
  "proposed_value": {
    "codice": "7056055000A0",
    "disegno": "A1675003603",
    "rev": "6",
    "rev_data": "25/09/2025"
  },
  "tl_answer_state": "YES",
  "corrected_value": null,
  "resulting_status": "CANDIDATE_CONFIRMATION",
  "forbidden_runtime_effects_preserved": true
}
```

## Forbidden model behavior

The model must not include fields that imply operational promotion, including:

* source_of_truth
* certo
* planner_eligible
* route_status
* production_ready
* planning_ready
* atlas_invoked
* smf_written
* database_written
* preview_json_mutated

## Stop conditions

The response model must return BLOCKED or refuse when the requested confirmation asks to:

* update source JSON
* promote any value to CERTO
* set planner_eligible=true
* confirm article 12514 ready for planning
* confirm article 12514 ready for production
* infer ZAW2 from repeated ZAW operations
* write to SMF or database
* invoke ATLAS or planner

## Future implementation preconditions

Runtime tests must verify:

* all required fields are present
* only allowed question_id values are accepted
* only allowed tl_answer_state values are accepted
* CORRECTED_VALUE requires corrected_value
* ABSENT is allowed only for Q7
* forbidden runtime effects remain preserved
* evidence persistence does not mutate source data
* no CERTO, planner, ATLAS, SMF, DB, or API effects occur

## Recommended next capability

TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_TEST_001

Purpose:

* guard this non-operational response model with a document-level test
* require required fields
* require allowed values
* require forbidden field names
* require anti-promotion, anti-CERTO, anti-planner, anti-ATLAS, anti-SMF/DB behavior

## Explicit non-goals

* no operational promotion
* no unreviewed promotion from persisted evidence
* no preview JSON mutation
* no automatic promotion to CERTO
* no planner
* no ATLAS runtime
* no SMF/DB write
* no API changes
* no production decision automation

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_NON_PERSISTENT_RESPONSE_MODEL_001
STATUS: DOCUMENT_CREATED
VERDICT: PENDING_TEST_AND_PR
NEXT SAFE ACTION: add a document-level test guard before runtime implementation
