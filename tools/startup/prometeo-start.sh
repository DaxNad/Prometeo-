#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT="${PROMETEO_BACKEND_PORT:-8000}"
FRONTEND_PORT="${PROMETEO_FRONTEND_PORT:-5173}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}/tl-board?fresh=1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

: "${PROMETEO_API_KEY:?ERRORE: esporta PROMETEO_API_KEY prima di avviare PROMETEO}"
export DATABASE_URL="${DATABASE_URL:-postgresql://localhost/prometeo}"
export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/backend:${PYTHONPATH:-}"

if lsof -nP -iTCP:"${BACKEND_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERRORE: porta ${BACKEND_PORT} già occupata. Esegui prima: prometeo-stop"
  exit 1
fi

if lsof -nP -iTCP:"${FRONTEND_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERRORE: porta ${FRONTEND_PORT} già occupata. Esegui prima: prometeo-stop"
  exit 1
fi

cd "${REPO_ROOT}/backend"
python3 -m uvicorn app.main:app --reload > /tmp/prometeo-backend.log 2>&1 &

cd "${REPO_ROOT}/frontend"
npm run dev > /tmp/prometeo-frontend.log 2>&1 &

sleep 3

if ! curl -sf -H "X-API-Key: ${PROMETEO_API_KEY}" "http://127.0.0.1:${BACKEND_PORT}/production/sequence" >/dev/null; then
  echo "ERRORE: backend non risponde. Log:"
  echo "/tmp/prometeo-backend.log"
  exit 1
fi

if ! lsof -nP -iTCP:"${FRONTEND_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERRORE: frontend non risulta in ascolto. Log:"
  echo "/tmp/prometeo-frontend.log"
  exit 1
fi

open "${FRONTEND_URL}"

echo "PROMETEO avviato"
echo "Backend:  http://127.0.0.1:${BACKEND_PORT}"
echo "Frontend: ${FRONTEND_URL}"
