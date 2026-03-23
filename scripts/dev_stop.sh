#!/usr/bin/env bash
set -Eeuo pipefail

kill $(lsof -ti:8000) 2>/dev/null || true

echo "=== PORTA 8000 ==="
lsof -nP -iTCP:8000 -sTCP:LISTEN || true
