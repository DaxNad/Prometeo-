#!/usr/bin/env bash
set -Eeuo pipefail

kill $(lsof -ti:8000) 2>/dev/null || true
kill $(lsof -ti:5173) 2>/dev/null || true

echo "=== PORTA 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true

echo "=== PORTA 5173 ==="
lsof -nP -iTCP:5173 -sTCP:LISTEN || true
