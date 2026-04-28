#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Backend guards"
backend/scripts/run_guards.sh

echo "==> Frontend UI structural guard"
(
  cd frontend
  ../frontend/scripts/guard_tl_board.sh
)

echo "ALL GUARDS (backend+frontend) PASS"

echo ""
echo "---- AI STACK STATUS ----"
"$HOME/PROMETEO/scripts/ai_stack_status.sh" || true
