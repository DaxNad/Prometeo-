#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "PROMETEO GUARD RAILS"
echo "========================================"

echo
echo "STEP 1 — pytest"
pytest -q

echo
echo "STEP 2 — quality_gate"
python -m app.agent_mod.quality_gate

echo
echo "STEP 3 — schema_guard"
python -m app.agent_mod.schema_guard

echo
echo "STEP 4 — db_schema_guard"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL non impostata → db_schema_guard SKIPPED"
else
  python -m app.agent_mod.db_schema_guard
fi

echo
echo "========================================"
echo "ALL GUARDS COMPLETED"
echo "========================================"
