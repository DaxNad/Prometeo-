#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_APPLY_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_APPLY_CONTRACT_V1"
  "SCOPO"
  "ORDINE_OBBLIGATORIO"
  "PREREQUISITI_APPLY"
  "STRONG_CONFIRMATION"
  "PERSISTENT_AUDIT_REQUIRED"
  "ROLLBACK_ID_REQUIRED"
  "DRY_RUN_REQUIRED"
  "RISK_POLICY"
  "WRITE_AUTHORIZATION"
  "NO_WRITE_UNTIL_TESTED"
  "FAILURE_MODES"
  "TEST_DI_CONTRATTO"
  "NON_OBIETTIVI"
  "PROSSIMO_PASSO"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_APPLY_CONTRACT_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

if ! grep -q "APPLY_RUNTIME_IMPLEMENTED = FALSE" "$DOC"; then
  echo "MISSING SAFETY STATE: APPLY_RUNTIME_IMPLEMENTED = FALSE"
  exit 1
fi

if ! grep -q "^controlled-import-apply-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-apply-contract-v1"
  exit 1
fi

if grep -q "APPLY_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: apply runtime must not be implemented by this contract"
  exit 1
fi

echo "CONTROLLED_IMPORT_APPLY_CONTRACT_V1: OK"
