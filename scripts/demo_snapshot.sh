#!/usr/bin/env bash
set -euo pipefail

# Confronta le chiavi attese con le risposte live di machine-load e sequence.
# Uso:
#   BASE_URL=https://... scripts/demo_snapshot.sh [STATION]
# Default STATION=ZAW-1

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"

echo "[SNAPSHOT] BASE_URL=${BASE_URL} STATION=${STATION}"

require() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }
require jq
require curl

ml_json="$(curl -sSf "${BASE_URL}/production/machine-load")"
seq_json="$(curl -sSf "${BASE_URL}/production/sequence")"

echo "[SNAPSHOT] Loaded endpoints"

ml_keys_file="backend/tests/snapshots/machine_load_expected_keys.json"
seq_keys_file="backend/tests/snapshots/sequence_expected_keys.json"

ml_keys="$(jq -c '.expected_item_keys' "${ml_keys_file}")"
seq_keys="$(jq -c '.expected_item_keys' "${seq_keys_file}")"

# Verifica che per la station vi sia almeno un item e che item contenga le chiavi attese.
echo "[SNAPSHOT] Checking machine-load keys and event pressure..."
ml_item="$(echo "${ml_json}" | jq -c --arg st "${STATION}" '.items[] | select(.station==$st)')"
[ -n "${ml_item}" ] || { echo "[FAIL] machine-load: nessun item per ${STATION}"; exit 1; }

for k in $(echo "${ml_keys}" | jq -r '.[]'); do
  echo "${ml_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] machine-load missing key: ${k}"; exit 1; }
done

open_events_total="$(echo "${ml_item}" | jq -r '.open_events_total // 0')"
[ "${open_events_total}" -ge 1 ] || { echo "[FAIL] machine-load: open_events_total < 1"; exit 1; }
echo "[OK] machine-load shape + pressione eventi"

echo "[SNAPSHOT] Checking sequence keys and event impact..."
seq_item="$(echo "${seq_json}" | jq -c --arg st "${STATION}" '.items[] | select(.critical_station==$st)')"
[ -n "${seq_item}" ] || { echo "[FAIL] sequence: nessun item per ${STATION}"; exit 1; }

for k in $(echo "${seq_keys}" | jq -r '.[]'); do
  echo "${seq_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] sequence missing key: ${k}"; exit 1; }
done

impact="$(echo "${seq_item}" | jq -r '.event_impact')"
[ "${impact}" = "true" ] || { echo "[FAIL] sequence: event_impact != true"; exit 1; }
echo "[OK] sequence shape + event impact"

echo "[SNAPSHOT] Done"
