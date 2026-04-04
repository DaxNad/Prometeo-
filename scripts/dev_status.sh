#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$HOME/Documents/PROMETEO"

echo "=== HEALTH ==="
curl -sS http://127.0.0.1:8000/health && echo || true

echo "=== PID 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true

echo "=== LOG ULTIME 40 RIGHE ==="
tail -n 40 "$ROOT_DIR/prometeo.log" 2>/dev/null || true
