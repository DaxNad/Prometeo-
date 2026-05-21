#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/davidepiangiolino/PROMETEO"
DOC="$ROOT/docs/PROMETEO_PRODUCT_COMPLETE_ROADMAP_V1.md"

if [ ! -f "$DOC" ]; then
  echo "MISSING: $DOC"
  exit 1
fi

grep -q "Product Core Closure" "$DOC"
grep -q "Densificazione dominio reale" "$DOC"
grep -q "Planner assistivo" "$DOC"
grep -q "Audit e Human Override" "$DOC"
grep -q "Productization SaaS/MES leggero" "$DOC"
grep -q "PROMETEO_PRODUCT_CORE_CLOSURE_V1" "$DOC"

echo "PROMETEO_PRODUCT_COMPLETE_ROADMAP_V1: OK"
