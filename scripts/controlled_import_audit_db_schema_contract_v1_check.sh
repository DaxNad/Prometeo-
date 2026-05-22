#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_AUDIT_DB_SCHEMA_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_AUDIT_DB_SCHEMA_CONTRACT_V1"
  "SCOPO"
  "TABLE_NAME"
  "PRIMARY_KEY"
  "REQUIRED_COLUMNS"
  "AUDIT_EVENT_ID"
  "ACTOR_SOURCE_TIMESTAMP"
  "PREVIEW_DRY_RUN_REFERENCES"
  "CONFIRMATION_TOKEN_HASH"
  "STRONG_CONFIRMATION_STATUS"
  "RISK_WRITE_MODE"
  "ROLLBACK_RELATION"
  "BEFORE_AFTER_STATE"
  "SIDE_EFFECTS_SUMMARY"
  "PERSISTENCE_STATUS"
  "APPLY_FLAGS"
  "FAILURE_REASON"
  "IMMUTABLE_LOG_POLICY"
  "RETENTION_POLICY"
  "SENSITIVE_DATA_FORBIDDEN"
  "APPLY_RELATION"
  "ROLLBACK_RELATION_FUTURE"
  "TEST_DI_CONTRATTO"
  "NON_OBIETTIVI"
  "PROSSIMO_PASSO"
)

required_columns=(
  "audit_event_id"
  "actor"
  "source"
  "timestamp_utc"
  "preview_reference"
  "dry_run_reference"
  "confirmation_token_hash"
  "strong_confirmation_status"
  "risk_level"
  "write_mode"
  "rollback_id"
  "before_state_hash"
  "before_state_ref"
  "after_state_hash"
  "after_state_ref"
  "side_effects_summary"
  "persistence_status"
  "apply_allowed"
  "apply_executed"
  "failure_reason"
  "created_at"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_AUDIT_DB_SCHEMA_CONTRACT_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

for column in "${required_columns[@]}"; do
  if ! grep -q "$column" "$DOC"; then
    echo "MISSING COLUMN CONTRACT: $column"
    exit 1
  fi
done

for state in \
  "AUDIT_DB_SCHEMA_RUNTIME_IMPLEMENTED = FALSE" \
  "AUDIT_DB_MIGRATION_IMPLEMENTED = FALSE" \
  "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE" \
  "APPLY_RUNTIME_IMPLEMENTED = FALSE"
do
  if ! grep -q "$state" "$DOC"; then
    echo "MISSING SAFETY STATE: $state"
    exit 1
  fi
done

if ! grep -q "controlled_import_audit_events" "$DOC"; then
  echo "MISSING TABLE NAME: controlled_import_audit_events"
  exit 1
fi

if ! grep -q "^controlled-import-audit-db-schema-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-audit-db-schema-contract-v1"
  exit 1
fi

if grep -q "AUDIT_DB_MIGRATION_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: migration must not be implemented by this contract"
  exit 1
fi

echo "CONTROLLED_IMPORT_AUDIT_DB_SCHEMA_CONTRACT_V1: OK"
