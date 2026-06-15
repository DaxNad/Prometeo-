#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT="${PROMETEO_BACKEND_PORT:-8000}"
FRONTEND_PORT="${PROMETEO_FRONTEND_PORT:-5173}"

pkill -f "uvicorn.*app.main:app" || true
pkill -f "vite" || true

for port in "${BACKEND_PORT}" "${FRONTEND_PORT}"; do
  for _ in {1..20}; do
    if ! lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
      break
    fi
    sleep 0.25
  done

  if lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "ERRORE: porta ${port} ancora occupata dopo prometeo-stop"
    lsof -nP -iTCP:"${port}" -sTCP:LISTEN
    exit 1
  fi
done

echo "PROMETEO spento"
