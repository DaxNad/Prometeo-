#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Backend guards"
backend/scripts/run_guards.sh

echo "==> Frontend UI guard (Vitest)"
(
  cd frontend
  npm run -s test
)

echo "ALL GUARDS (backend+frontend) PASS"

