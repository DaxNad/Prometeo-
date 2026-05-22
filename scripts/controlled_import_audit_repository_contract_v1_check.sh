#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_AUDIT_REPOSITORY_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_AUDIT_REPOSITORY_CONTRACT_V1"
  "SCOPO"
  "RESPONSABILITA_REPOSITORY"
  "INPUT_AMMESSO"
  "OUTPUT_ATTESO"
  "CAMPI_OBBLIGATORI"
  "CAMPI_VIETATI"
  "CONFIRMATION_TOKEN_POLICY"
  "RISK_LEVEL_VALIDATION"
  "WRITE_MODE_VALIDATION"
  "APPLY_FLAGS_VALIDATION"
  "ROLLBACK_ID_POLICY"
  "ACTOR_SOURCE_TIMESTAMP"
  "FAILURE_POLICY"
  "IDEMPOTENCY_POLICY"
  "IMMUTABILITY_POLICY"
  "NO_UPDATE_DELETE"
  "PREVIEW_ENDPOINT_RELATION"
  "DRY_RUN_RELATION"
  "APPLY_RELATION"
  "ERRORI_PREVISTI"
  "TEST_MINIMI_FUTURI"
  "TEST_DI_CONTRATTO"
  "NON_OBIETTIVI"
  "PROSSIMO_PASSO"
)

required_terms=(
  "AUDIT_REPOSITORY_RUNTIME_IMPLEMENTED = FALSE"
  "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE"
  "APPLY_RUNTIME_IMPLEMENTED = FALSE"
  "confirmation_token_hash"
  "confirmation_token"
  "audit_event_id"
  "rollback_id"
  "idempotent_replay"
  "append-only"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_AUDIT_REPOSITORY_CONTRACT_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

for term in "${required_terms[@]}"; do
  if ! grep -q "$term" "$DOC"; then
    echo "MISSING REQUIRED TERM: $term"
    exit 1
  fi
done

if ! grep -q "^controlled-import-audit-repository-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-audit-repository-contract-v1"
  exit 1
fi

if grep -q "AUDIT_REPOSITORY_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: repository runtime must not be implemented by this contract"
  exit 1
fi

echo "CONTROLLED_IMPORT_AUDIT_REPOSITORY_CONTRACT_V1: OK"
