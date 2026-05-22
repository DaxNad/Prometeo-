#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
SQL="$ROOT/backend/sql/010_controlled_import_audit_events.sql"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CREATE TABLE IF NOT EXISTS controlled_import_audit_events"
  "id BIGSERIAL PRIMARY KEY"
  "audit_event_id TEXT NOT NULL UNIQUE"
  "actor TEXT NOT NULL"
  "source TEXT NOT NULL"
  "timestamp_utc TIMESTAMPTZ NOT NULL"
  "preview_reference TEXT NOT NULL"
  "dry_run_reference TEXT NOT NULL"
  "confirmation_token_hash TEXT"
  "strong_confirmation_status TEXT NOT NULL"
  "risk_level TEXT NOT NULL"
  "write_mode TEXT NOT NULL"
  "rollback_id TEXT NOT NULL"
  "before_state_hash TEXT"
  "before_state_ref TEXT"
  "after_state_hash TEXT"
  "after_state_ref TEXT"
  "side_effects_summary JSONB NOT NULL"
  "persistence_status TEXT NOT NULL"
  "apply_allowed BOOLEAN NOT NULL DEFAULT FALSE"
  "apply_executed BOOLEAN NOT NULL DEFAULT FALSE"
  "failure_reason TEXT"
  "created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
  "CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'BLOCKED'))"
  "CHECK (write_mode IN ('PREVIEW_ONLY', 'APPLY'))"
  "CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_rollback_id"
  "CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_confirmation_token_hash"
)

if [[ ! -f "$SQL" ]]; then
  echo "MISSING: backend/sql/010_controlled_import_audit_events.sql"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -qF "$marker" "$SQL"; then
    echo "MISSING SQL MARKER: $marker"
    exit 1
  fi
done

if grep -q "confirmation_token TEXT" "$SQL"; then
  echo "FORBIDDEN COLUMN: confirmation_token in clear text"
  exit 1
fi

if grep -qE "payload|customer_data|smf_payload|bom_payload|real_data" "$SQL"; then
  echo "FORBIDDEN SENSITIVE PAYLOAD COLUMN"
  exit 1
fi

if ! grep -q "^controlled-import-audit-migration-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-audit-migration-v1"
  exit 1
fi

echo "CONTROLLED_IMPORT_AUDIT_MIGRATION_V1: OK"
