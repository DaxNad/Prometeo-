#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY=${PYTHON:-python}

fail_count=0

run_check() {
  local name="$1"; shift
  echo "==> ${name}"
  set +e
  "$@"
  local rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "[PASS] ${name}"; echo
  else
    echo "[FAIL] ${name} (rc=$rc)"; echo
    fail_count=$((fail_count+1))
  fi
}

# Quality Gate (includes pytest baseline, excludes e2e by default via pytest.ini)
run_check "Quality Gate" "$PY" -m app.agent_mod.quality_gate

# API Schema Guard (structural)
run_check "Schema Guard" "$PY" -m app.agent_mod.schema_guard

# DB Schema Guard (requires PostgreSQL DATABASE_URL)
run_check "DB Schema Guard" "$PY" -m app.agent_mod.db_schema_guard

if [[ $fail_count -eq 0 ]]; then
  echo "ALL GUARDS PASS"
  exit 0
else
  echo "${fail_count} GUARD(S) FAILED"
  exit 1
fi

