#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$HOME/Documents/PROMETEO"
GATE_SCRIPT="$ROOT_DIR/scripts/agent_runtime_gate.sh"

echo "=== HEALTH ==="
curl -sS http://127.0.0.1:8000/health && echo || true

echo "=== PID 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true

echo "=== AGENT RUNTIME STATUS ==="
curl -sS http://127.0.0.1:8000/agent-runtime/status && echo || true

if [ -x "$GATE_SCRIPT" ]; then
  echo
  "$GATE_SCRIPT" || true
else
  echo "AGENT RUNTIME GATE: SKIPPED"
  echo "script non trovato o non eseguibile: $GATE_SCRIPT"
fi

echo "=== LOG ULTIME 40 RIGHE ==="
tail -n 40 "$ROOT_DIR/prometeo.log" 2>/dev/null || true
