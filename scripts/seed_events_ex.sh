#!/usr/bin/env bash
set -euo pipefail

# Extended event seed (env-driven template)
# Usage:
#   BASE_URL=https://... scripts/seed_events_ex.sh [STATION]
# Env: TITLE, LINE, EVENT_TYPE, SEVERITY, NOTE, SOURCE

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"
TITLE="${TITLE:-Segnalazione operativa seed}"
LINE="${LINE:-MAIN}"
EVENT_TYPE="${EVENT_TYPE:-ALERT}"
SEVERITY="${SEVERITY:-HIGH}"
NOTE="${NOTE:-seed via script}"
SOURCE="${SOURCE:-seed_script}"

payload=$(cat << JSON
{
  "title": "${TITLE}",
  "line": "${LINE}",
  "station": "${STATION}",
  "event_type": "${EVENT_TYPE}",
  "severity": "${SEVERITY}",
  "note": "${NOTE}",
  "source": "${SOURCE}"
}
JSON
)

echo "[SEED:EX] POST ${BASE_URL}/events/create station=${STATION}"
curl -sS -X POST -H 'Content-Type: application/json' \
  --data "${payload}" \
  "${BASE_URL}/events/create" | jq . || true

# idempotent-friendly check
curl -sS "${BASE_URL}/production/machine-load" | jq '.items[] | select(.station=="'"${STATION}"'") | {station, open_events_total, event_titles}' || true
