# TL_CHAT_RETRIEVAL_POST_MERGE_CHECKPOINT_001

## Status

VERIFIED.

## Date

2026-07-05.

## Verified milestone

TL Chat -> Retrieval reale -> Risposta verificabile.

## Repository state

- branch: main
- verified commit: a112c85
- origin alignment: main aligned with origin/main
- working tree before verification: clean

## Verification executed on real checkout

### TL Chat contract regression

Command: python3 -m pytest backend/tests/test_tl_chat_contract.py -q

Result:

- 52 passed
- unknown article regression included
- no failures

### Backend non-E2E regression

Command: cd backend && python3 -m pytest -q

Result:

- 794 passed
- 3 E2E tests deselected
- no failures

### E2E regression

Server: python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

Test command: python3 -m pytest tests/test_e2e_production.py -m e2e -q

Result:

- 3 passed
- health endpoint verified
- production order creation and board visibility verified
- production events endpoint verified

## Consolidated result

- 849 tests passed
- 0 failures
- no backend regression detected
- TL Chat unknown-article behavior preserved
- governed retrieval milestone verified on the real PROMETEO checkout

## Governance guarantees preserved

- read-only governed retrieval
- explicit DA_VERIFICARE behavior
- explicit missing-data behavior
- no automatic planner decision
- no automatic promotion to CERTO
- no autonomous ATLAS action
- no unintended SMF write
- no unintended database write

## Scope note

This checkpoint records regression verification only.

It does not introduce:

- new capabilities
- new source access
- planner integration
- autonomous actions
- frontend changes
- database migrations
