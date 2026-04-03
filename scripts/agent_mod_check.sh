#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [ -f ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif [ -f "../.venv/bin/python" ]; then
  PYTHON_BIN="../.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

export PYTHONPATH=.

echo "[AGENT_MOD] ROOT_DIR=$ROOT_DIR"
echo "[AGENT_MOD] BACKEND_DIR=$BACKEND_DIR"
echo "[AGENT_MOD] PYTHON_BIN=$PYTHON_BIN"
echo "[AGENT_MOD] ARGS=$*"
echo "-----"

"$PYTHON_BIN" -m app.agent_mod.cli "$@"
