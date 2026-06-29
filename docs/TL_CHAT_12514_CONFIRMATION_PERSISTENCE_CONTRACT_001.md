# TL_CHAT_12514_CONFIRMATION_PERSISTENCE_CONTRACT_001

## Purpose

Define the future persistence contract for structured TL confirmation of article `12514`.

This document is contract-only.

It does not implement persistence, does not write runtime data, does not promote the article to `CERTO`, and does not enable planner or SMF execution.

## Capability boundary

Capability:

```text
TL_CHAT_12514_CONFIRMATION_PERSISTENCE_CONTRACT_001
```

Previous closed capability:

```text
TL_CHAT_12514_CONFIRMATION_STRUCTURED_INPUT_001
```

Current confirmed input endpoint:

```text
POST /tl/12514/confirmation
```

The current endpoint accepts and validates a structured TL confirmation payload, then returns a governed response.

The future persistence step may only persist the confirmation as controlled evidence. It must not convert the preview into an operationally certain source.

## Allowed future persistence target

A future implementation may persist a local, governed confirmation record for article `12514`.

Allowed conceptual target:

```text
data/local_reports/spec_intake_confirmation/12514_confirmation.json
```

The exact path may change only through a later implementation capability.

The persisted record must remain local, auditable, and non-operational by default.

## Allowed persisted fields

A future persisted record may contain only:

```json
{
  "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
  "article": "12514",
  "source_capability": "TL_CHAT_12514_CONFIRMATION_STRUCTURED_INPUT_001",
  "confirmation_status": "TL_CONFIRMED_PREVIEW",
  "confidence": "DA_VERIFICARE",
  "planner_eligible": false,
  "promoted_to_certo": false,
  "requires_persistence_review": true,
  "confirmed_fields": [],
  "confirmed_by_role": "TL",
  "notes": "",
  "created_at": ""
}
```

## Required semantic state

The persisted confirmation must keep:

```text
confidence = DA_VERIFICARE
planner_eligible = false
promoted_to_certo = false
requires_persistence_review = true
```

The persisted record may be used as evidence that a TL confirmed a preview.

It must not be treated as final production truth.

## Forbidden behavior

A future implementation must not:

```text
promote 12514 to CERTO automatically
write to PROMETEO_MASTER
write to lifecycle registry
write to SMF operational files
enable planner eligibility
create or modify production routes
generalize to other articles
accept arbitrary file paths
accept uncontrolled schema fields
overwrite existing confirmed records without review
```

## Source-of-truth rule

The persisted confirmation has lower authority than:

```text
SPECIFICA REALE
CONFERMA TL REVIEWED/PROMOTED BY DEDICATED CAPABILITY
PROMETEO_MASTER
STRUCTURED DOMAIN SOURCE
```

It has higher authority only than a volatile API response that was not saved.

## Future test contract

A future implementation must add tests proving:

```text
valid 12514 confirmation can be persisted as governed evidence
persisted confidence remains DA_VERIFICARE
planner_eligible remains false
promoted_to_certo remains false
non-12514 article is rejected
unsupported confirmation_action is rejected
extra schema fields are rejected
path traversal is impossible
existing record overwrite is blocked or explicitly governed
no lifecycle/master/SMF file is modified
```

## Stop condition

This contract is complete when the repository contains this document and no runtime persistence behavior has been added.

Runtime persistence must be opened as a separate implementation capability.
