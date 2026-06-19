# TL_CONTEXT_RETRIEVAL_READER_ADAPTER_TEST_CONTRACT_001

Status: PROPOSED
Capability: TL_CONTEXT_RETRIEVAL_MINIMAL_001
Contract: TL_CONTEXT_RETRIEVAL_READER_ADAPTER_CONTRACT_001
Runtime impact: NONE
Planner eligible: false
Data mutation: forbidden
Source access: read-only
Requires TL confirmation: true

## Purpose

Define the minimal test contract for the TL context retrieval reader adapter before any runtime implementation.

## Required invariant

The adapter must only read from authorized sources listed in PROMETEO_CONTEXT_SOURCE_INDEX_001.

It must not write, mutate, schedule, plan, access real SMF data, or access forbidden paths.

## Test cases

### T1_AUTHORIZED_SOURCE_FOUND

Given a source identifier exists in PROMETEO_CONTEXT_SOURCE_INDEX_001
and the source is available to read-only retrieval,
the adapter must return SOURCE_FOUND.

Expected result:

- Source status is SOURCE_FOUND
- Source identifier is returned
- Retrieved excerpt is returned
- Confidence is declared
- No mutation occurs

### T2_AUTHORIZED_SOURCE_MISSING_DATA

Given a source identifier exists in PROMETEO_CONTEXT_SOURCE_INDEX_001
but no matching data is found for the query,
the adapter must return SOURCE_MISSING.

Expected result:

- Source status is SOURCE_MISSING
- Retrieved excerpt is empty
- Missing data is declared
- Confidence is DA_VERIFICARE
- No invented content is returned

### T3_AUTHORIZED_SOURCE_UNAVAILABLE

Given a source identifier exists in PROMETEO_CONTEXT_SOURCE_INDEX_001
but is not available to current retrieval,
the adapter must return SOURCE_AUTHORIZED_BUT_UNAVAILABLE.

Expected result:

- Source status is SOURCE_AUTHORIZED_BUT_UNAVAILABLE
- Retrieved excerpt is empty
- Retrieval limitation is declared
- Next safe action is source availability verification
- No mutation occurs

### T4_FORBIDDEN_SOURCE

Given a requested source identifier is not listed in PROMETEO_CONTEXT_SOURCE_INDEX_001,
the adapter must return SOURCE_FORBIDDEN.

Expected result:

- Source status is SOURCE_FORBIDDEN
- No source content is read
- No fallback to arbitrary paths occurs
- No mutation occurs

### T5_AMBIGUOUS_SOURCE

Given the requested source identifier or article/code reference is ambiguous,
the adapter must return SOURCE_AMBIGUOUS.

Expected result:

- Source status is SOURCE_AMBIGUOUS
- Ambiguity is declared
- Missing clarification is listed
- Next safe action requires TL confirmation
- No mutation occurs

### T6_FORBIDDEN_PATH_BLOCKED

Given any request attempts to access a forbidden path,
the adapter must block the request.

Expected result:

- Source status is SOURCE_FORBIDDEN
- Forbidden path content is not read
- No file content is exposed
- No mutation occurs

### T7_NO_RUNTIME_SIDE_EFFECTS

Given any adapter retrieval request,
the adapter must produce no runtime side effects.

Expected result:

- No database write
- No file write
- No planner state change
- No scheduling action
- No SMF access
- No cloud model use with sensitive data

### T8_PATH_TRAVERSAL_BLOCKED

Given any request attempts path traversal,
the adapter must block the request and declare PATH_TRAVERSAL_BLOCKED.

Expected result:

- Source status is SOURCE_FORBIDDEN
- PATH_TRAVERSAL_BLOCKED is declared
- No file content is exposed
- No fallback path is attempted
- No mutation occurs

## Completion rule

This test contract is complete when it verifies authorized source access, missing data, unavailable sources, forbidden sources, ambiguous sources, forbidden path blocking, path traversal blocking, and no runtime side effects.
