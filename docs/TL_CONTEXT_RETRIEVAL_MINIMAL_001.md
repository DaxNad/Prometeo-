# TL_CONTEXT_RETRIEVAL_MINIMAL_001

Status: PROPOSED
Runtime impact: NONE
Planner eligible: false
Data mutation: forbidden
Source access: read-only
Requires TL confirmation: true

## Goal

Enable TL Chat to answer minimal context questions using authorized PROMETEO context sources.

## In scope

- Read-only retrieval
- Source citation
- Confidence level
- Explicit missing-data response
- No production planning
- No database write
- No SMF real access

## Out of scope

- Runtime planner integration
- Automatic scheduling
- Data mutation
- Real SMF ingestion
- Autonomous agent behavior
- Cloud model use with sensitive data

## Allowed question types

- What do we know about article X?
- Which source supports this?
- Is this confirmed or to verify?
- What data is missing?

## Required output shape

- Answer
- Source
- Confidence
- Missing data
- Next safe action

## Acceptance tests

1. If source exists, answer cites it.
2. If source is missing, answer says missing.
3. If confidence is low, answer says DA_VERIFICARE.
4. If user asks to plan production, system refuses and explains scope limit.
5. No data mutation occurs.
6. If an authorized source is not available to current retrieval, answer declares SOURCE_AUTHORIZED_BUT_UNAVAILABLE.

## Completion rule

This capability is complete only when TL Chat can produce a controlled answer from authorized read-only context, with source, confidence, missing-data declaration, and no mutation.
