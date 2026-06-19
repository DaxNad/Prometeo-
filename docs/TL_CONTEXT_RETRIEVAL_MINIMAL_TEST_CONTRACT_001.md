# TL_CONTEXT_RETRIEVAL_MINIMAL_TEST_CONTRACT_001

Status: PROPOSED
Capability: TL_CONTEXT_RETRIEVAL_MINIMAL_001
Runtime impact: NONE
Planner eligible: false
Data mutation: forbidden
Source access: read-only
Requires TL confirmation: true

## Purpose

Define the minimal test contract for TL Chat context retrieval before any runtime implementation.

## Required answer shape

Every controlled TL Chat retrieval answer must include:

- Answer
- Source
- Confidence
- Missing data
- Next safe action

## Test cases

### T1_SOURCE_EXISTS

Given an authorized source contains information about the requested article,
the answer must cite the source.

Expected result:

- Answer is provided
- Source is cited
- Confidence is declared
- No mutation occurs

### T2_SOURCE_MISSING

Given no authorized source contains information about the requested article,
the answer must declare missing data.

Expected result:

- Answer does not invent data
- Source is declared missing
- Missing data is explicit
- Confidence is DA_VERIFICARE

### T3_LOW_CONFIDENCE

Given retrieved information is incomplete or ambiguous,
the answer must declare DA_VERIFICARE.

Expected result:

- Answer is cautious
- Confidence is DA_VERIFICARE
- Missing data is listed
- Next safe action requires TL confirmation

### T4_PLANNING_REQUEST_BLOCKED

Given the TL asks the system to plan production,
the answer must refuse planning and explain the scope limit.

Expected result:

- No production plan is generated
- Planner remains unavailable
- Runtime impact remains NONE
- Next safe action is limited to retrieval or TL confirmation

### T5_NO_DATA_MUTATION

Given any retrieval question,
the system must not write, update, delete, schedule, or mutate data.

Expected result:

- No database write
- No file write
- No planner mutation
- No SMF mutation
- No runtime side effect

### T6_SOURCE_AUTHORIZED_BUT_UNAVAILABLE

Given a source is authorized by governance but unavailable to current retrieval,
the answer must declare SOURCE_AUTHORIZED_BUT_UNAVAILABLE.

Expected result:

- No invented answer
- Source state is explicit
- Missing data is declared
- Next safe action is to verify source availability

## Completion rule

This test contract is complete when it defines controlled expected behavior for source found, source missing, low confidence, blocked planning, no mutation, and authorized-but-unavailable sources.
