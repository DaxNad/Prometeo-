# TL_CONTEXT_RETRIEVAL_READER_ADAPTER_CONTRACT_001

Status: PROPOSED
Capability: TL_CONTEXT_RETRIEVAL_MINIMAL_001
Runtime impact: NONE
Planner eligible: false
Data mutation: forbidden
Source access: read-only
Requires TL confirmation: true

## Purpose

Define the minimal read-only reader adapter contract required before any TL Chat runtime retrieval implementation.

## Adapter responsibility

The reader adapter may only expose authorized PROMETEO context sources to TL Chat retrieval in a controlled read-only shape.

It must not plan, mutate, schedule, infer production actions, or access real SMF data.

## Required input

The adapter contract accepts only:

- Query text
- Requested article or code, when provided
- Authorized source identifier
- Retrieval mode: read-only

## Required output

The adapter contract returns only:

- Source status
- Source identifier
- Retrieved excerpt or empty result
- Confidence
- Missing data
- Retrieval limitation

## Authorized source boundary

The adapter may only accept source identifiers already listed as authorized read-only sources in PROMETEO_CONTEXT_SOURCE_INDEX_001.

If a requested source identifier is not present in the authorized source index, the adapter must return SOURCE_FORBIDDEN.

## Source statuses

Allowed source statuses:

- SOURCE_FOUND
- SOURCE_MISSING
- SOURCE_AUTHORIZED_BUT_UNAVAILABLE
- SOURCE_FORBIDDEN
- SOURCE_AMBIGUOUS

## Forbidden behavior

The adapter must not:

- Write files
- Update database records
- Mutate planner state
- Access real SMF data
- Access forbidden paths
- Use cloud models with sensitive data
- Generate production plans
- Create autonomous actions
- Hide missing data
- Invent unavailable source content

## Required safeguards

The adapter must enforce:

- Read-only access
- Authorized source list only
- Explicit missing-data response
- Explicit confidence declaration
- Explicit source status
- No runtime side effects
- No planner eligibility

## Completion rule

This contract is complete only when it defines a safe read-only boundary between TL Chat retrieval and authorized PROMETEO context sources, without enabling runtime mutation or production planning.
