#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

GUARD_TMP_ROOT="${PROMETEO_GUARD_TMPDIR:-${TMPDIR:-/tmp}/prometeo_run_guards}"
mkdir -p "$GUARD_TMP_ROOT"
export TMPDIR="$GUARD_TMP_ROOT"
export TEMP="$GUARD_TMP_ROOT"
export TMP="$GUARD_TMP_ROOT"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"
export PYTHONPATH="$ROOT_DIR/backend:${PYTHONPATH:-}"
PYTEST_BASETEMP="$(mktemp -d "$GUARD_TMP_ROOT/pytest.XXXXXX")"
trap 'rm -rf "$PYTEST_BASETEMP"' EXIT

echo "========================================"
echo "PROMETEO GUARD RAILS"
echo "========================================"

echo
echo "STEP 1 — pytest (backend config)"
"$PYTHON_BIN" -m pytest -q -c backend/pytest.ini backend/tests backend/app/atlas_engine/tests --basetemp "$PYTEST_BASETEMP/backend"

echo
echo "STEP 1B — real_code_registry preview tests"
"$PYTHON_BIN" -m pytest -q tests/real_code_registry --basetemp "$PYTEST_BASETEMP/real_code_registry"

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
