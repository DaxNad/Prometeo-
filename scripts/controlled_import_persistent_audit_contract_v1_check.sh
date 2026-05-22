#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1"
  "SCOPO"
  "WHY_PERSISTENT_AUDIT"
  "WHEN_GENERATED"
  "REQUIRED_FIELDS"
  "PREVIEW_RELATION"
  "DRY_RUN_RELATION"
  "APPLY_RELATION"
  "ROLLBACK_ID_REQUIRED"
  "STRONG_CONFIRMATION"
  "ACTOR_SOURCE_TIMESTAMP"
  "RISK_WRITE_MODE_POLICY"
  "BEFORE_AFTER_STATE"
  "PERSISTENCE_STATUS"
  "FAILURE_POLICY"
  "NO_APPLY_WITHOUT_VALID_AUDIT"
  "TEST_DI_CONTRATTO"
  "NON_OBIETTIVI"
  "PROSSIMO_PASSO"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

if ! grep -q "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE" "$DOC"; then
  echo "MISSING SAFETY STATE: PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE"
  exit 1
fi

if ! grep -q "APPLY_RUNTIME_IMPLEMENTED = FALSE" "$DOC"; then
  echo "MISSING SAFETY STATE: APPLY_RUNTIME_IMPLEMENTED = FALSE"
  exit 1
fi

if ! grep -q "^controlled-import-persistent-audit-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-persistent-audit-contract-v1"
  exit 1
fi

if grep -q "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: persistent audit runtime must not be implemented by this contract"
  exit 1
fi

if grep -q "APPLY_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: apply runtime must not be implemented by this contract"
  exit 1
fi

echo "CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1: OK"
