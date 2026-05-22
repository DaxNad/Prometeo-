#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_AUDIT_STORAGE_DECISION_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_AUDIT_STORAGE_DECISION_V1"
  "SCOPO"
  "OPZIONI_VALUTATE"
  "OPZIONE_RACCOMANDATA"
  "OPZIONI_VIETATE_ORA"
  "POSTGRESQL_AUDIT_TABLE"
  "JSONL_LOCALE"
  "APPLICATION_LOG"
  "EXTERNAL_CLOUD_STORAGE"
  "NO_PERSISTENCE"
  "SECURITY_RATIONALE"
  "TESTABILITY_RATIONALE"
  "ROLLBACK_RELATION"
  "CONFIRMATION_RELATION"
  "APPLY_RELATION"
  "FAILURE_POLICY"
  "RETENTION_MINIMA"
  "DATI_SENSIBILI_DA_NON_SALVARE"
  "AUDIT_TECNICO_VS_DATI_PRODUTTIVI"
  "TEST_DI_DECISIONE"
  "PROSSIMO_PASSO"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_AUDIT_STORAGE_DECISION_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

for state in \
  "AUDIT_STORAGE_RUNTIME_IMPLEMENTED = FALSE" \
  "PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE" \
  "APPLY_RUNTIME_IMPLEMENTED = FALSE"
do
  if ! grep -q "$state" "$DOC"; then
    echo "MISSING SAFETY STATE: $state"
    exit 1
  fi
done

if ! grep -q "Opzione raccomandata futura: PostgreSQL audit table" "$DOC"; then
  echo "MISSING RECOMMENDATION: PostgreSQL audit table"
  exit 1
fi

if ! grep -q "^controlled-import-audit-storage-decision-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-audit-storage-decision-v1"
  exit 1
fi

if grep -q "AUDIT_STORAGE_RUNTIME_IMPLEMENTED = TRUE" "$DOC"; then
  echo "INVALID STATE: audit storage runtime must not be implemented by this decision"
  exit 1
fi

echo "CONTROLLED_IMPORT_AUDIT_STORAGE_DECISION_V1: OK"
