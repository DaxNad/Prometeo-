# PROMETEO_HANDOFF_STATE_2026_06_26

## Repository state

main aligned with origin/main
HEAD: 2a456e1 chore(guards): improve quality gate failure detail (#381)

## Closed milestone

TL Chat → Retrieval reale → Risposta verificabile

The milestone is considered closed and protected by documentation, validation, tests, and guardrails.

## Recently closed PRs

### #379 docs(tl-chat): add real source coverage validation

- Added docs/TL_CHAT_REAL_SOURCE_COVERAGE_VALIDATION_001.md
- Added TL-facing matrix with ANSWERED / PARTIAL / MISSING / BLOCKED classifications
- Preserved document-only scope

### #380 test(tl-chat): guard real source coverage validation doc

- Added backend/tests/test_tl_chat_real_source_coverage_validation_doc.py
- Guards existence and coherence of the validation document
- Guards matrix Q001-Q010
- Guards out-of-scope boundaries
- Fixed fragile relative path using repo-root resolution

### #381 chore(guards): improve quality gate failure detail

- Improved quality_gate pytest failure detail
- Prefer explicit FAILED pytest lines
- Kept output bounded
- Preserved PASS/FAIL semantics

## Current guarantees

- TL Chat governed retrieval is available
- TL Chat answers use governed schema
- Source-aware behavior is documented and tested
- DA_VERIFICARE is preserved when certainty is missing
- No automatic promotion to CERTO
- No planner execution
- No ATLAS runtime binding
- No SMF/DB write
- Real source coverage is mapped
- Real source coverage validation exists and is test-guarded
- Quality gate failure detail is more readable

## Last successful validations

- PR #379: 54 passed in 0.76s; GitHub checks 11 successful
- PR #380: 58 passed in 0.60s; run_guards local PASS; GitHub checks 11 successful
- PR #381: run_guards local PASS; 664 passed, 3 deselected; 30 real_code_registry passed; quality_gate PASS; schema_guard PASS; GitHub checks 11 successful

## Active boundaries

Do not open without explicit approval:

- planner
- ATLAS runtime
- new source ingestion
- article densification
- TL Chat API changes
- runtime coverage automation
- production decision automation
- SMF/DB write

## Governance status

- Governance: stable
- Retrieval milestone: closed
- Coverage validation: created and guarded
- Guard readability: improved
- Runtime scope: unchanged
- Architecture: preserved

## Next capability candidate

TL_CHAT_REAL_SOURCE_COVERAGE_GAP_REVIEW_001

Purpose:

- review the validation matrix
- identify PARTIAL and MISSING cases with highest TL value
- produce a prioritized gap list
- avoid implementation during the review

Expected output:

- answered coverage
- partial coverage
- missing coverage
- blocked requests
- one next improvement candidate

## Not now

- planner
- ATLAS
- new sources
- runtime coverage
- article densification
- API changes

## Closure verdict

CAPABILITY: PROMETEO_HANDOFF_STATE_2026_06_26
STATUS: DOCUMENT_CREATED
VERDICT: PENDING_TEST_AND_PR
NEXT SAFE ACTION: add, commit, push, and open PR for this handoff document
