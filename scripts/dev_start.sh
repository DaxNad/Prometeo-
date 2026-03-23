#!/usr/bin/env bash
set -Eeuo pipefail

cd "$HOME/Documents/PROMETEO"
source .venv/bin/activate

kill $(lsof -ti:8000) 2>/dev/null || true

set -a
source .env
set +a

nohup uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 > prometeo.log 2>&1 &

sleep 2

echo "=== HEALTH ==="
curl -sS http://127.0.0.1:8000/health && echo

echo "=== PID 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN
