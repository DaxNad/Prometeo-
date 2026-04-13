#!/usr/bin/env bash
set -euo pipefail

# Seed a sample operational event into PROMETEO backend
# Usage:
#   BASE_URL=https://your-app.railway.app scripts/seed_events.sh [STATION]
# Examples:
#   scripts/seed_events.sh ZAW-1
#   BASE_URL=http://127.0.0.1:8000 scripts/seed_events.sh PIDMILL

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"

payload=$(cat << JSON
{
  "title": "Segnalazione operativa seed",
  "line": "MAIN",
  "station": "${STATION}",
  "event_type": "ALERT",
  "severity": "HIGH",
  "note": "seed via script",
  "source": "seed_script"
}
JSON
)

echo "[SEED] POST ${BASE_URL}/events/create station=${STATION}"
curl -sS -X POST -H 'Content-Type: application/json' \
  --data "${payload}" \
  "${BASE_URL}/events/create" | jq . || true

echo "[SEED] GET ${BASE_URL}/production/machine-load"
curl -sS "${BASE_URL}/production/machine-load" | jq '.items[] | {station, open_events_total} | select(.open_events_total>0)' || true

