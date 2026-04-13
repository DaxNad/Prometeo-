#!/usr/bin/env bash
set -euo pipefail

# Verifica “live” le chiavi attese di machine-load e sequence per una station
# Uso:
#   BASE_URL=https://... scripts/demo_snapshot.sh [STATION]
# Default: STATION=ZAW-1

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
STATION="${1:-ZAW-1}"

echo "[SNAPSHOT] BASE_URL=${BASE_URL} STATION=${STATION}"

for dep in jq curl; do
  command -v "$dep" >/dev/null 2>&1 || { echo "Missing dependency: $dep"; exit 1; }
done

ml_json="$(curl -sSf "${BASE_URL}/production/machine-load")"
seq_json="$(curl -sSf "${BASE_URL}/production/sequence")"

ml_keys_file="backend/tests/snapshots/machine_load_expected.json"
seq_keys_file="backend/tests/snapshots/sequence_expected.json"

ml_keys="$(jq -c '.expected_item_keys' "${ml_keys_file}")"
seq_keys="$(jq -c '.expected_item_keys' "${seq_keys_file}")"

echo "[SNAPSHOT] Checking machine-load keys..."
ml_item="$(echo "${ml_json}" | jq -c --arg st "${STATION}" '.items[] | select(.station==$st)')"
[ -n "${ml_item}" ] || { echo "[FAIL] machine-load: nessun item per ${STATION}"; exit 1; }
for k in $(echo "${ml_keys}" | jq -r '.[]'); do
  echo "${ml_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] machine-load missing key: ${k}"; exit 1; }
done
echo "[OK] machine-load chiavi presenti"

echo "[SNAPSHOT] Checking sequence keys..."
seq_item="$(echo "${seq_json}" | jq -c --arg st "${STATION}" '.items[] | select(.critical_station==$st)')"
[ -n "${seq_item}" ] || { echo "[FAIL] sequence: nessun item per ${STATION}"; exit 1; }
for k in $(echo "${seq_keys}" | jq -r '.[]'); do
  echo "${seq_item}" | jq -e --arg k "${k}" 'has($k)' >/dev/null || { echo "[FAIL] sequence missing key: ${k}"; exit 1; }
done
echo "[OK] sequence chiavi presenti"

echo "[SNAPSHOT] Done"

