#!/usr/bin/env bash
set -euo pipefail

# Seed a sample operational event into PROMETEO backend
# Usage:
#   BASE_URL=https://your-app.railway.app scripts/seed_events.sh [STATION]
# Env vars:
#   TITLE, LINE, EVENT_TYPE (or TYPE), SEVERITY, STATUS, NOTE, SOURCE
# Examples:
#   scripts/seed_events.sh ZAW-1
#   BASE_URL=http://127.0.0.1:8000 TITLE="Fermo macchina" SEVERITY=CRITICAL STATUS=OPEN scripts/seed_events.sh PIDMILL

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"
TITLE="${TITLE:-Segnalazione operativa seed}"
LINE="${LINE:-MAIN}"
EVENT_TYPE="${EVENT_TYPE:-${TYPE:-ALERT}}"
SEVERITY="${SEVERITY:-HIGH}"
STATUS="${STATUS:-OPEN}"
NOTE="${NOTE:-seed via script}"
SOURCE="${SOURCE:-seed_script}"

payload=$(cat << JSON
{
  "title": "${TITLE}",
  "line": "${LINE}",
  "station": "${STATION}",
  "event_type": "${EVENT_TYPE}",
  "severity": "${SEVERITY}",
  "status": "${STATUS}",
  "note": "${NOTE}",
  "source": "${SOURCE}"
}
JSON
)

echo "[SEED] POST ${BASE_URL}/events/create station=${STATION}"
curl -sS -X POST -H 'Content-Type: application/json' \
  --data "${payload}" \
  "${BASE_URL}/events/create" | jq . || true

echo "[SEED] GET ${BASE_URL}/production/machine-load (ZAW-1 excerpt)"
curl -sS "${BASE_URL}/production/machine-load" | jq '.items[] | select(.station=="'"${STATION}"'") | {station, open_events_total, event_titles}' || true
