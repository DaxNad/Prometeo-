#!/usr/bin/env bash
set -euo pipefail

# Demo Snapshot (keys-only)
# BASE_URL=https://... scripts/demo_snapshot_min.sh [STATION]
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"

echo "[SNAPSHOT:MIN] BASE_URL=${BASE_URL} STATION=${STATION}"
for dep in jq curl; do command -v "$dep" >/dev/null 2>&1 || { echo "Missing dependency: $dep"; exit 1; }; done

ml_json="$(curl -sSf "${BASE_URL}/production/machine-load")"
seq_json="$(curl -sSf "${BASE_URL}/production/sequence")"

ml_keys='["station","orders_total","open_events_total"]'
seq_keys='["critical_station","event_impact"]'

echo "[SNAPSHOT:MIN] Checking machine-load keys..."
ml_item="$(echo "${ml_json}" | jq -c --arg st "${STATION}" '.items[] | select(.station==$st)')"
[ -n "${ml_item}" ] || { echo "[FAIL] machine-load: nessun item per ${STATION}"; exit 1; }
for k in $(echo "${ml_keys}" | jq -r '.[]'); do echo "${ml_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] machine-load missing key: ${k}"; exit 1; }; done

open_events_total="$(echo "${ml_item}" | jq -r '.open_events_total // 0')"
if [ "${open_events_total}" -ge 1 ]; then echo "[OK] machine-load: eventi OPEN rilevati (${open_events_total})"; else echo "[INFO] machine-load: nessun evento OPEN su ${STATION}"; fi

echo "[SNAPSHOT:MIN] Checking sequence keys..."
seq_item="$(echo "${seq_json}" | jq -c --arg st "${STATION}" '.items[] | select(.critical_station==$st)')"
[ -n "${seq_item}" ] || { echo "[FAIL] sequence: nessun item per ${STATION}"; exit 1; }
for k in $(echo "${seq_keys}" | jq -r '.[]'); do echo "${seq_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] sequence missing key: ${k}"; exit 1; }; done

impact="$(echo "${seq_item}" | jq -r '.event_impact')"
if [ "${impact}" = "true" ]; then echo "[OK] sequence: event_impact=true"; else echo "[INFO] sequence: event_impact non attivo"; fi

echo "[SNAPSHOT:MIN] Done"
