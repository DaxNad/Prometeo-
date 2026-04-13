#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="$ROOT_DIR/src/pages/ProductionDashboard.tsx"

if [[ ! -f "$FILE" ]]; then
  echo "[FAIL] TL Board guard: file not found: $FILE" >&2
  exit 1
fi

require() {
  local needle="$1"
  if ! grep -q "$needle" "$FILE"; then
    echo "[FAIL] TL Board guard: missing expected text: $needle" >&2
    exit 1
  fi
}

echo "==> TL Board structural guard on $FILE"

# Headings/sections
require "TL Board"
require "attenzione immediata"
require "carico postazioni"
require "sequenza consigliata"

# Table headers
require "<th>codice</th>"
require "<th>postazione</th>"
require "<th>qta totale</th>"
require "<th>righe</th>"
require "<th>prio</th>"

echo "[PASS] TL Board guard"

