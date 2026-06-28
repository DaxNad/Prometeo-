# TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001

## Purpose

Define the future API binding contract for the article 12514 TL Chat confirmation rendering service.

This contract describes how the service may later be exposed through TL Chat API behavior without violating the existing runtime boundary.

This is a documentation-only capability.

It does not implement API binding.
It does not change `backend/app/api/tl_chat.py`.
It does not change frontend behavior.
It does not persist TL answers.
It does not mutate preview JSON.
It does not promote candidate data to CERTO.
It does not enable planner eligibility.
It does not invoke ATLAS.
It does not write to SMF or database.
It does not create production readiness or planning readiness.

## Capability

`TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001`

This capability defines the contract for a future governed binding between:

- `backend/app/services/tl_chat_confirmation_rendering.py`
- future TL Chat API behavior

The future binding must remain candidate-only, read-only, non-persistent, and DA_VERIFICARE.

## Existing governed dependencies

The future API binding must preserve the constraints established by:

- `TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_001`
- `TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_001`
- `TL_CHAT_12514_CONFIRMATION_RENDERING_RUNTIME_STUB_BOUNDARY_TEST_001`
- `TL_CHAT_12514_CONFIRMATION_RENDERING_SERVICE_REGRESSION_TEST_001`

## Boundary classification

| Area | Status in this capability |
| --- | --- |
| API contract documentation | Allowed |
| Runtime change | Forbidden |
| `backend/app/api/tl_chat.py` change | Forbidden |
| Frontend change | Forbidden |
| TL answer persistence | Forbidden |
| Preview JSON mutation | Forbidden |
| CERTO promotion | Forbidden |
| Planner eligibility | Forbidden |
| ATLAS invocation | Forbidden |
| SMF write | Forbidden |
| Database write | Forbidden |
| Production readiness | Forbidden |
| Planning readiness | Forbidden |

## Future binding classification

A future API binding may be allowed only if separately scoped.

The future binding may:

- call the rendering service
- return a candidate confirmation rendering object
- preserve article 12514-only scope
- preserve Q1-Q7 scope
- preserve DA_VERIFICARE confidence
- preserve runtime effects statement
- preserve forbidden runtime effects false flags
- expose missing data explicitly
- expose next safe action explicitly

The future binding must not:

- save TL answers
- persist candidate confirmations
- update `data/local_reports/spec_intake_preview/12514_metadata_preview.json`
- promote candidate data to CERTO
- mark article 12514 as production ready
- mark article 12514 as planning ready
- enable planner eligibility
- invoke ATLAS
- write SMF
- write database rows
- change frontend behavior in the same capability

## API behavior contract

If a future TL Chat API route uses the rendering service, the response must remain:

- read-only
- non-persistent
- candidate-only
- DA_VERIFICARE
- source-limited
- planner-ineligible
- operationally non-authoritative

The response must clearly indicate that the rendered confirmation is not:

- source of truth
- persisted confirmation
- operational authorization
- planning authorization
- production authorization

## Allowed API output fields

A future API response may expose:

- `article`
- `question_id`
- `field_group`
- `tl_answer_state`
- `resulting_status`
- `candidate_data`
- `corrected_value`
- `confidence`
- `missing_data`
- `runtime_effects`
- `forbidden_runtime_effects`
- `next_safe_action`
- `rendered_text`

The API must not expose fields that imply persistence or operational authority.

## Forbidden API output fields

A future API response must not expose fields such as:

- `source_of_truth=true`
- `persisted=true`
- `saved=true`
- `planner_eligible=true`
- `route_status=CERTO`
- `production_ready=true`
- `planning_ready=true`
- `atlas_invoked=true`
- `smf_written=true`
- `database_written=true`
- `preview_json_mutated=true`

Equivalent semantic claims are also forbidden.

## Required article scope

The future API binding must remain limited to:

`article = 12514`

Any request for a different article must be rejected or routed to an unsupported/candidate-unavailable response.

The API must not silently generalize the rendering service beyond article 12514.

## Required question scope

Allowed question ids:

- Q1
- Q2
- Q3
- Q4
- Q5
- Q6
- Q7

Required field group mapping:

| Question | Field group |
| --- | --- |
| Q1 | article_identity |
| Q2 | packaging_and_quantities |
| Q3 | normalized_route |
| Q4 | zaw_station_resolution |
| Q5 | components |
| Q6 | tooling |
| Q7 | pidmill_and_cp_visibility |

The future API binding must reject unknown question ids.

## Required answer state scope

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

## Required resulting status scope

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

Any future API-bound rendered response must preserve the meaning of:

`Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, nessuna promozione a CERTO, nessun planner, nessun ATLAS, nessuna scrittura SMF/DB.`

This statement must remain visible or machine-readable in the API response.

It prevents the candidate rendering from being interpreted as operational execution.

## Required forbidden runtime effects flags

Any future API-bound response must preserve false values for:

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

No flag may become true in the future API binding capability.

## Source policy

The future API binding may not claim real source confirmation unless a governed source has provided it.

For article 12514, the confirmation rendering remains candidate-only unless separately promoted by a governed source-of-truth process.

The API must distinguish between:

- candidate confirmation
- candidate correction
- missing data
- DA_VERIFICARE
- blocked operational decision

The API must not collapse these states into CERTO.

## Planner policy

The future API binding must not enable planner behavior.

The API must not set:

- `planner_eligible=true`
- `route_status=CERTO`
- `production_ready=true`
- `planning_ready=true`

The API must not call planner services.

## ATLAS policy

The future API binding must not invoke ATLAS.

The confirmation rendering service is a formatting and validation boundary, not a reasoning engine invocation.

Any ATLAS-related behavior requires a separate governed capability.

## Persistence policy

The future API binding must not persist:

- TL answer
- candidate confirmation
- candidate correction
- rendered response
- preview JSON mutation
- derived source-of-truth value

Any persistence requires a separate governed capability and explicit source-of-truth policy.

## Frontend policy

This contract does not authorize frontend changes.

Any future UI rendering of the confirmation response requires a separate governed frontend capability.

The future API binding must be testable without frontend changes.

## Error handling policy

The future API binding must reject or safely return unsupported states for:

- non-12514 article
- unknown question_id
- unsupported answer state
- unsupported resulting status
- CORRECTED_VALUE without corrected_value
- ABSENT outside Q7
- empty next safe action

Error handling must not mutate state.

Error handling must not persist anything.

## Required tests before future API binding

Before API binding is implemented, a separate test contract must verify:

- this API binding contract exists
- runtime changes are forbidden in this capability
- `backend/app/api/tl_chat.py` is not changed in this capability
- frontend is not changed in this capability
- allowed API output fields
- forbidden API output fields
- article 12514-only scope
- Q1-Q7 scope
- answer state scope
- resulting status scope
- runtime effects statement
- forbidden runtime effects false flags
- no persistence
- no preview JSON mutation
- no CERTO promotion
- no planner
- no ATLAS
- no SMF/DB
- no production or planning readiness

## Stop conditions

The future API binding must stop if implementation attempts to:

- persist TL answer
- mutate preview JSON
- promote to CERTO
- enable planner
- invoke ATLAS
- write SMF or database
- change frontend in the same capability
- generalize beyond article 12514
- claim operational readiness
- claim planning readiness
- treat candidate response as source of truth

## Recommended next capability

`TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_TEST_001`

Purpose:

Guard this API binding contract before implementing any actual TL Chat API binding.

The test must verify:

- contract title
- existing governed dependencies
- boundary classification
- future binding classification
- allowed API output fields
- forbidden API output fields
- article 12514-only scope
- Q1-Q7 field group mapping
- allowed answer states
- allowed resulting statuses
- forbidden resulting statuses
- runtime effects statement
- forbidden runtime effects false flags
- source policy
- planner policy
- ATLAS policy
- persistence policy
- frontend policy
- error handling policy
- stop conditions

## Non-goals

This capability does not implement:

- API binding
- TL Chat endpoint change
- frontend rendering
- persistence
- preview JSON mutation
- source-of-truth promotion
- CERTO promotion
- planner enablement
- ATLAS invocation
- SMF write
- database write
- production readiness
- planning readiness
- multi-article generalization

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_RENDERING_API_BINDING_CONTRACT_001

STATUS: DOCUMENT_CREATED

VERDICT: PENDING_TEST_AND_PR

NEXT SAFE ACTION: add API binding contract document-level test