#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/CONTROLLED_IMPORT_PIPELINE_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "CONTROLLED_IMPORT_PIPELINE_V1"
  "SCOPO"
  "INPUT_AMMESSO"
  "INPUT_VIETATO"
  "VALIDAZIONE"
  "PREVIEW_ONLY"
  "RISK_CLASSIFICATION"
  "HUMAN_CONFIRMATION_REQUIRED"
  "NO_DIRECT_WRITE"
  "SANITIZATION"
  "AUDIT_LOG_MINIMO"
  "FAILURE_MODES"
  "TEST_DI_CAPABILITY"
  "PROSSIMO_PASSO_RUNTIME"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/CONTROLLED_IMPORT_PIPELINE_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

if ! grep -q "^controlled-import-pipeline-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: controlled-import-pipeline-v1"
  exit 1
fi

for forbidden in \
  "IMPORT_REALE_COMPLETATO = TRUE" \
  "DIRECT_WRITE_AUTHORIZED = TRUE" \
  "OCR_REALE_OBBLIGATORIO = TRUE" \
  "AI_RUNTIME_OBBLIGATORIA = TRUE" \
  "CLOUD_OBBLIGATORIO = TRUE"
do
  if grep -qi "$forbidden" "$DOC"; then
    echo "FORBIDDEN CLAIM: $forbidden"
    exit 1
  fi
done

echo "CONTROLLED_IMPORT_PIPELINE_V1: OK"
