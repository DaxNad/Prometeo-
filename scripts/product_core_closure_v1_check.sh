#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DOC="$ROOT/docs/PROMETEO_PRODUCT_CORE_CLOSURE_V1.md"
MAKEFILE="$ROOT/Makefile"

required_markers=(
  "PRODUCT_CORE_CLOSURE_V1"
  "SCOPO"
  "STATO_ATTUALE"
  "CORE_GIA_CHIUSO"
  "CORE_NON_CHIUSO"
  "GAP_VENDIBILITA"
  "GAP_SAAS_MES"
  "CAPABILITY_OBBLIGATORIE"
  "GUARDRAIL_OBBLIGATORI"
  "TEST_DI_CHIUSURA"
  "CRITERI_GO_NO_GO"
  "PROSSIMO_MICRO_PASSO"
)

if [[ ! -f "$DOC" ]]; then
  echo "MISSING: docs/PROMETEO_PRODUCT_CORE_CLOSURE_V1.md"
  exit 1
fi

for marker in "${required_markers[@]}"; do
  if ! grep -q "$marker" "$DOC"; then
    echo "MISSING MARKER: $marker"
    exit 1
  fi
done

if ! grep -q "^product-core-closure-v1:" "$MAKEFILE"; then
  echo "MISSING TARGET: product-core-closure-v1"
  exit 1
fi

if grep -q "PRODUCT_CORE_CLOSURE_V1 = PASS" "$DOC"; then
  echo "INVALID STATE: gate must not declare product core PASS yet"
  exit 1
fi

echo "PROMETEO_PRODUCT_CORE_CLOSURE_V1: OK"
