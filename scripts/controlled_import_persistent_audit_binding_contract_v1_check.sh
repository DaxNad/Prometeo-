#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_CONTRACT_V1"
  "SCOPO"
  "BINDING_AMMESSO"
  "BINDING_VIETATO"
  "FLAG_ESPLICITO"
  "DEFAULT_DRY_RUN_NO_PERSISTENCE"
  "CONFIRMATION_TOKEN_POLICY"
  "ACTOR_SOURCE_POLICY"
  "BLOCKED_RISK_POLICY"
  "FALLBACK_REPOSITORY_DB"
  "RISPOSTA_API_ATTESA"
  "NO_PREVIEW_MUTATION"
  "NO_APPLY"
  "NO_SMF_PLANNER_WRITE"
  "FAILURE_POLICY"
  "TEST_MINIMI_FUTURI"
  "TEST_DI_CONTRATTO"
  "NON_OBIETTIVI"
  "PROSSIMO_PASSO"
)

required_terms=(
  "PERSISTENT_AUDIT_BINDING_RUNTIME_IMPLEMENTED = FALSE"
  "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE"
  "APPLY_RUNTIME_IMPLEMENTED = FALSE"
  "ControlledImportPersistentAuditService"
  "persistent_audit_requested=true"
  "confirmation_token_hash"
  "confirmation_token"
  "actor"
  "source"
  "BLOCKED"
  "PREVIEW_ONLY"
  "audit_persistence=\"NONE\""
  "apply_allowed=false"
  "apply_executed=false"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_CONTRACT_V1.md"
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

if ! grep -q "^controlled-import-persistent-audit-binding-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-persistent-audit-binding-contract-v1"
  exit 1
fi

if grep -q "PERSISTENT_AUDIT_BINDING_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: binding runtime must not be implemented by this contract"
  exit 1
fi

echo "CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_CONTRACT_V1: OK"
