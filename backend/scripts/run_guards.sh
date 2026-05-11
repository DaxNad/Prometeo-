#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"

echo "========================================"
echo "PROMETEO GUARD RAILS"
echo "========================================"

echo
echo "STEP 1 — pytest (backend config)"
pytest -q -c backend/pytest.ini

echo
echo "STEP 2 — quality_gate"
"$PYTHON_BIN" -m app.agent_mod.quality_gate

echo
echo "STEP 3 — schema_guard"
"$PYTHON_BIN" -m app.agent_mod.schema_guard

echo
echo "STEP 4 — db_schema_guard"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL non impostata → db_schema_guard SKIPPED"
else
  "$PYTHON_BIN" -m app.agent_mod.db_schema_guard
fi

echo
echo "========================================"
echo "ALL GUARDS COMPLETED"
echo "========================================"
