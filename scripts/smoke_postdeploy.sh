#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "SMOKE TEST → $BASE_URL"
echo

fail() {
  echo "SMOKE FAILED → $1"
  exit 1
}

check_health() {
  echo "1. health"
  
  body=$(curl -fsS "$BASE_URL/health") \
    || fail "/health not reachable"

  echo "response:"
  echo "$body"
  echo

  python3 - <<PY || fail "/health not valid"
import json,sys

body = """$body""".strip()

if body.lower() == "ok":
    sys.exit(0)

try:
    j = json.loads(body)
    assert (
        j.get("ok") is True
        or j.get("status") == "ok"
        or j.get("healthy") is True
    )
except Exception:
    raise

PY

  echo "OK → /health"
}

check_endpoint() {
  local path="$1"

  curl -fsS "$BASE_URL$path" >/dev/null \
    || fail "$path not responding"

  echo "OK → $path"
}

check_health

echo
echo "2. machine-load"
check_endpoint "/production/machine-load"

echo
echo "3. sequence"
check_endpoint "/production/sequence"

echo
echo "SMOKE OK"
