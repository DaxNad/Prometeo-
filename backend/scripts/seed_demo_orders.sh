#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

post() {
  local body="$1"
  curl -sS -X POST "${API_BASE}/production/order" \
    -H 'Content-Type: application/json' \
    -d "${body}" | jq -r '.ok // empty' >/dev/null 2>&1 || true
}

echo "==> Seeding demo orders into ${API_BASE}"

post '{"order_id":"ORD-A-001","cliente":"Alpha","codice":"12063","qta":8,"postazione":"ZAW-1","stato":"in corso","semaforo":"GIALLO","due_date":"2026-04-20","note":"demo"}'
post '{"order_id":"ORD-B-002","cliente":"Beta","codice":"ZX-900","qta":5,"postazione":"ZAW-1","stato":"da fare","semaforo":"ROSSO","due_date":"2026-04-18","note":"demo"}'
post '{"order_id":"ORD-C-003","cliente":"Gamma","codice":"KJ-77","qta":3,"postazione":"ZAW-2","stato":"da fare","semaforo":"VERDE","due_date":"2026-04-22","note":"demo"}'
post '{"order_id":"ORD-D-004","cliente":"Delta","codice":"AB-12","qta":6,"postazione":"ZAW-2","stato":"in corso","semaforo":"GIALLO","due_date":"2026-04-21","note":"demo"}'
post '{"order_id":"ORD-E-005","cliente":"Epsilon","codice":"MN-45","qta":4,"postazione":"ZAW-1","stato":"da fare","semaforo":"ROSSO","due_date":"2026-04-19","note":"demo"}'

echo "[DONE] Seeded demo orders"

