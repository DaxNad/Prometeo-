# TL_CHAT_NEXT_SOURCE_READER_SCOPE_001

Status: PROPOSED
Runtime impact: NONE
Planner eligible: false
Data mutation: forbidden
Source access: read-only
Requires TL confirmation: true

## Purpose

Define the next minimal source candidate for TL Chat governed retrieval after Phase 2 runtime fallback coverage.

## Current state

TL Chat Phase 2 governed retrieval fallback is covered by runtime readiness tests.

The current governed retrieval runtime can attach an evidence_pack to /tl/chat responses and keep the response preview-only, read-only and non-promotable.

The remaining gap is that context_retrieval.py still retrieves only TL memory rules.

## Selected next source candidate

Selected source:

- spec_intake_preview

Expected source path:

- data/local_reports/spec_intake_preview/

Reason:

- It is under data/local_reports/, which is listed as read_only_support_paths in PROMETEO_CONTEXT_SOURCE_INDEX_001.
- It is already preview-oriented.
- It can provide article-specific context without accessing forbidden specs_finitura images.
- It matches the current TL confirmation model.

## Explicitly not selected

local_specs_metadata is not selected in this step because its current operational path depends on specs_finitura, which is listed under forbidden_paths in the current context source index.

## Required source behavior

The future reader source must return only:

- source_id
- source_status
- article
- excerpt or empty result
- confidence
- requires_tl_confirmation
- planner_eligible=false
- limitation

## Allowed statuses

- SOURCE_FOUND
- SOURCE_MISSING
- SOURCE_AUTHORIZED_BUT_UNAVAILABLE
- SOURCE_FORBIDDEN
- SOURCE_AMBIGUOUS
- PATH_TRAVERSAL_BLOCKED

## Mandatory constraints

The source reader must be:

- read-only
- local-only
- preview-only
- no LLM calls
- no DB writes
- no SMF writes
- no planner mutation
- no runtime mutation
- no image access
- no path traversal
- no promotion to CERTO without explicit governed rule and TL confirmation

## Completion rule

This scope is complete when PROMETEO clearly identifies spec_intake_preview as the next source candidate without enabling runtime source access yet.

The next implementation step must be a contract/test step before any runtime reader is enabled.
