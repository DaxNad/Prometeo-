#!/usr/bin/env bash
set -Eeuo pipefail

echo "=== HEALTH ==="
curl -sS http://127.0.0.1:8000/health && echo || true

echo "=== PID 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true

echo "=== LOG ULTIME 20 RIGHE ==="
tail -n 20 "$HOME/Documents/PROMETEO/prometeo.log" 2>/dev/null || true
