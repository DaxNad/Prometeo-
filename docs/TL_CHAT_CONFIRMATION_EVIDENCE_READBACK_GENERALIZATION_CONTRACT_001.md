# TL_CHAT_CONFIRMATION_EVIDENCE_READBACK_GENERALIZATION_CONTRACT_001

## Purpose

Contract-only document for future generalization of TL Chat confirmation evidence readback beyond article 12514.

This document does not implement runtime behavior, endpoints, persistence, planner changes, SMF changes, lifecycle changes, or article generalization.

## Capability boundary

Capability: TL_CHAT_CONFIRMATION_EVIDENCE_READBACK_GENERALIZATION_CONTRACT_001

Reference implementation: article 12514 only.

This contract does not expand runtime support to other articles.

## Reference pattern

preview metadata -> TL confirmation rendering -> structured TL confirmation input -> governed local evidence persistence -> TL Chat evidence readback -> non-operational guard

## Required future invariants

A future generalized implementation must preserve:

- confidence = DA_VERIFICARE
- requires_confirmation = true
- planner_eligible = false
- promoted_to_certo = false
- requires_persistence_review = true
- confirmation evidence is governed evidence only
- confirmation evidence is not operational truth

## Allowed future behavior

A future implementation may read back confirmation evidence only when:

- the article is explicitly authorized
- the record path is controlled by source id or internal mapping
- the JSON schema is validated
- confirmation_status is governed
- confirmed_fields are exposed only as evidence
- missing evidence keeps candidate-only fallback

## Forbidden behavior

A future implementation must not:

- treat persisted confirmation evidence as CERTO
- enable planner eligibility from confirmation evidence alone
- mark an article ready for production
- mark an article ready for planning
- write to PROMETEO_MASTER
- write to lifecycle registry
- write to SMF operational files
- create or modify production routes
- accept arbitrary article/path pairs
- accept uncontrolled schema fields
- read unvalidated JSON as evidence
- overwrite existing confirmation evidence
- generalize from 12514 without dedicated tests

## Source-of-truth rule

Confirmation evidence readback has lower authority than:

- SPECIFICA REALE
- CONFERMA TL REVIEWED/PROMOTED BY DEDICATED CAPABILITY
- PROMETEO_MASTER
- STRUCTURED DOMAIN SOURCE

It has higher authority only than an unsaved volatile API response.

## Minimum future tests

A future runtime generalization must prove:

- valid governed confirmation evidence can be read back for an authorized article
- invalid schema is ignored
- wrong article is ignored
- planner_eligible=true is rejected
- promoted_to_certo=true is rejected
- requires_persistence_review=false is rejected unless reviewed by dedicated capability
- missing evidence keeps candidate-only fallback
- readback answer exposes source/status/confirmed_fields
- readback answer keeps DA_VERIFICARE
- readback risk blocks planning and production authorization
- no Master/Lifecycle/SMF file is modified
- path traversal is impossible

## Stop condition

This contract is complete when this document exists and no runtime generalization has been added.

Runtime generalization must be opened as a separate implementation capability.
