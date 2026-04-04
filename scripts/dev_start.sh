#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$HOME/Documents/PROMETEO"
BACKEND_DIR="$ROOT_DIR/backend"
GATE_SCRIPT="$ROOT_DIR/scripts/agent_runtime_gate.sh"

if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
elif [ -x "$BACKEND_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

PID_8000="$(lsof -tiTCP:8000 -sTCP:LISTEN || true)"
if [ -n "$PID_8000" ]; then
  kill -9 $PID_8000 2>/dev/null || true
fi

if [ -f "$BACKEND_DIR/.env" ]; then
  set -a
  source "$BACKEND_DIR/.env"
  set +a
elif [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

cd "$BACKEND_DIR"
export PYTHONPATH=.

nohup "$PYTHON_BIN" -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  > "$ROOT_DIR/prometeo.log" 2>&1 &

echo "=== WAIT HEALTH ==="
for i in {1..20}; do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "=== HEALTH ==="
curl -sS http://127.0.0.1:8000/health && echo

echo "=== PID 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true

if [ -x "$GATE_SCRIPT" ]; then
  echo
  "$GATE_SCRIPT"
else
  echo
  echo "AGENT RUNTIME GATE: SKIPPED"
  echo "script non trovato o non eseguibile: $GATE_SCRIPT"
fi
