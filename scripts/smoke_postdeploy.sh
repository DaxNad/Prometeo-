#!/usr/bin/env bash
set -euo pipefail

# Simple post-deploy smoke test for PROMETEO backend
# Usage:
#   BASE_URL=https://your-app.railway.app scripts/smoke_postdeploy.sh
# or
#   scripts/smoke_postdeploy.sh https://your-app.railway.app

BASE_URL="${1:-${BASE_URL:-}}"
if [[ -z "${BASE_URL}" ]]; then
  BASE_URL="${RAILWAY_STATIC_URL:-}"
fi
if [[ -z "${BASE_URL}" ]]; then
  BASE_URL="http://127.0.0.1:8000"
fi

echo "[SMOKE] Using BASE_URL=${BASE_URL}"

fail() { echo "[SMOKE][FAIL] $1" >&2; exit 1; }

http_get() {
  local path="$1"
  local url="${BASE_URL}${path}"
  # -s silent, -S show errors, -f fail on >=400, --max-time 10s
  curl -sSf --max-time 10 "$url" -o /dev/null || fail "GET ${path} failed"
  echo "[SMOKE][OK] GET ${path}"
}

# Core health
http_get "/ping"
http_get "/health"

# Production views (sequence may be heavy but should respond)
http_get "/production/machine-load"
http_get "/production/sequence"
http_get "/production/events"

# Optional: Postgres probe (do not fail if 4xx)
curl -sS --max-time 10 "${BASE_URL}/postgres/ping" -o /dev/null && \
  echo "[SMOKE][OK] GET /postgres/ping (optional)" || \
  echo "[SMOKE][WARN] /postgres/ping not available (optional)"

echo "[SMOKE] All checks passed"

