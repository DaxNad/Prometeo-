#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_SCHEMA_CONTRACT_V1.md"
MAKEFILE="$ROOT/Makefile"
TEST="$ROOT/backend/tests/test_controlled_import_schema_contract.py"

required_markers=(
  "CONTROLLED_IMPORT_SCHEMA_CONTRACT_V1"
  "SCOPO"
  "INPUT_SCHEMA"
  "OUTPUT_SCHEMA"
  "PREVIEW_SCHEMA"
  "SIDE_EFFECTS_SCHEMA"
  "REQUIRED_FIELDS"
  "RISK_LEVELS"
  "WRITE_MODE"
  "HUMAN_CONFIRMATION"
  "NO_SIDE_EFFECTS"
  "TEST_DI_CONTRATTO"
  "FAILURE_MODES"
  "PROSSIMO_PASSO"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_SCHEMA_CONTRACT_V1.md"
  exit 1
fi

if [[ ! -f "$TEST" ]]; then
  echo "MISSING: backend/tests/test_controlled_import_schema_contract.py"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

if ! grep -q "^controlled-import-schema-contract-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-schema-contract-v1"
  exit 1
fi

echo "CONTROLLED_IMPORT_SCHEMA_CONTRACT_V1: OK"
