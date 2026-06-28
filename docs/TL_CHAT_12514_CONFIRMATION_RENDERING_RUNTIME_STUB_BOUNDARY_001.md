# TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001

## Purpose

Define the runtime boundary for the article 12514 TL Chat confirmation rendering stub.

This document describes the allowed and forbidden behavior of:

- `backend/app/services/tl_chat_confirmation_rendering.py`
- `backend/tests/test_tl_chat_confirmation_rendering.py`

This is a boundary document only.

It does not add runtime behavior.
It does not bind the service to TL Chat API routes.
It does not change frontend behavior.
It does not persist TL answers.
It does not mutate preview JSON.
It does not promote any value to CERTO.
It does not enable planner eligibility.
It does not invoke ATLAS.
It does not write to SMF or database.
It does not make production readiness or planning readiness decisions.

## Capability

`TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_001`

The capability introduced an isolated service-level runtime stub that can build a renderable candidate response for article 12514 confirmation answers.

The stub is intentionally not connected to the operational TL Chat runtime.

## Boundary classification

| Area | Status |
| --- | --- |
| Service module | Allowed |
| Service-level tests | Allowed |
| TL Chat API binding | Forbidden |
| Frontend rendering | Forbidden |
| TL answer persistence | Forbidden |
| Preview JSON mutation | Forbidden |
| CERTO promotion | Forbidden |
| Planner eligibility | Forbidden |
| ATLAS invocation | Forbidden |
| SMF write | Forbidden |
| Database write | Forbidden |
| Production readiness | Forbidden |
| Planning readiness | Forbidden |

## Allowed behavior

The rendering stub may:

- accept article 12514 confirmation rendering input
- validate question_id Q1-Q7
- validate TL answer state
- validate resulting status
- map Q1-Q7 to governed field groups
- preserve DA_VERIFICARE confidence
- construct candidate rendered text
- expose runtime effects as explicit no-op statements
- return forbidden runtime effects as false flags
- reject unsupported or unsafe input
- be tested through service-level tests only

## Forbidden behavior

The rendering stub must not:

- save TL answers
- update source files
- mutate `data/local_reports/spec_intake_preview/12514_metadata_preview.json`
- promote candidate values to CERTO
- set `planner_eligible=true`
- set `route_status=CERTO`
- call planner code
- call ATLAS code
- write SMF files
- write database rows
- change `backend/app/api/tl_chat.py`
- change frontend code
- create production readiness claims
- create planning readiness claims
- treat TL answers as source of truth

## Service-only rule

The service may be imported by tests.

The service must not be bound to:

- FastAPI routes
- TL Chat endpoint handlers
- frontend components
- persistence adapters
- planner services
- ATLAS Engine
- SMF writers
- database sessions

Any future binding requires a separate governed capability.

## Article scope

The stub is limited to:

`article = 12514`

Any other article must be rejected.

This prevents the stub from becoming a generic confirmation engine before the article 12514 flow is proven and guarded.

## Question scope

Allowed question ids:

- Q1
- Q2
- Q3
- Q4
- Q5
- Q6
- Q7

The field group mapping must remain:

| Question | Field group |
| --- | --- |
| Q1 | article_identity |
| Q2 | packaging_and_quantities |
| Q3 | normalized_route |
| Q4 | zaw_station_resolution |
| Q5 | components |
| Q6 | tooling |
| Q7 | pidmill_and_cp_visibility |

## Answer state scope

Allowed TL answer states:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE
- NOT_VISIBLE
- ABSENT

Rules:

- CORRECTED_VALUE requires corrected_value.
- ABSENT is allowed only for Q7.
- UNKNOWN must preserve DA_VERIFICARE.
- YES must not promote data to CERTO.
- NO must not persist rejection.
- NOT_VISIBLE must not infer absence.

## Resulting status scope

Allowed resulting statuses:

- CANDIDATE_CONFIRMATION
- CANDIDATE_CORRECTION
- DA_VERIFICARE
- MISSING
- BLOCKED

Forbidden resulting statuses:

- CERTO
- PRODUCTION_READY
- PLANNING_READY
- PLANNER_ELIGIBLE
- SOURCE_OF_TRUTH
- SAVED
- PERSISTED

## Required runtime effects statement

The rendered output must preserve the meaning of:

`Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.`

This statement is not decorative.

It is a boundary marker that prevents the candidate rendering from being mistaken for operational execution.

## Required forbidden runtime effects flags

The service must preserve false values for:

- tl_answer_persistence
- preview_json_mutation
- certo_promotion
- planner_enablement
- atlas_invocation
- smf_write
- database_write
- api_contract_change
- production_readiness
- planning_readiness

No flag may become true in this capability.

## Required output nature

The output is a renderable candidate only.

It may include:

- article
- question_id
- field_group
- tl_answer_state
- resulting_status
- candidate_data
- corrected_value
- confidence
- missing_data
- runtime_effects
- forbidden_runtime_effects
- next_safe_action
- rendered_text

The output is not:

- source of truth
- persisted confirmation
- operational authorization
- planning authorization
- production authorization

## Stop conditions

The capability must be stopped if a future change attempts to:

- bind the service to TL Chat API
- expose the service to frontend
- persist TL answers
- mutate preview JSON
- promote candidate data to CERTO
- enable planner
- invoke ATLAS
- write SMF or database
- claim article 12514 is ready for production
- claim article 12514 is ready for planning
- generalize the service beyond article 12514 without a new capability

## Acceptance criteria

This boundary is accepted only if a future test can verify:

- capability name
- service-only boundary
- allowed behavior
- forbidden behavior
- article 12514 scope
- Q1-Q7 scope
- allowed answer states
- allowed resulting statuses
- forbidden resulting statuses
- required runtime effects statement
- required forbidden runtime effects false flags
- output is candidate only
- stop conditions
- no API binding
- no frontend
- no persistence
- no preview JSON mutation
- no CERTO
- no planner
- no ATLAS
- no SMF/DB
- no production or planning readiness

## Recommended next capability

`TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_TEST_001`

Purpose:

Guard this boundary document with a document-level test before any future TL Chat API binding is considered.

The test must verify that the boundary preserves:

- service-only scope
- article 12514 limit
- Q1-Q7 field group mapping
- allowed answer states
- allowed resulting statuses
- forbidden operational statuses
- required runtime effects statement
- forbidden runtime effects false flags
- no persistence
- no preview JSON mutation
- no CERTO promotion
- no planner
- no ATLAS
- no SMF/DB
- no API binding
- no frontend binding
- no production or planning readiness

## Non-goals

This capability does not implement:

- API binding
- frontend rendering
- TL Chat integration
- answer persistence
- confirmation persistence
- source mutation
- preview JSON mutation
- CERTO promotion
- planner enablement
- ATLAS invocation
- SMF write
- database write
- production readiness
- planning readiness
- multi-article generalization

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_DOC_001

STATUS: DOCUMENT_CREATED

VERDICT: PENDING_TEST_AND_PR

NEXT SAFE ACTION: add a document-level boundary test