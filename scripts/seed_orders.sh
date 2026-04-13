#!/usr/bin/env bash
set -euo pipefail

# Seed minimal production orders dataset (3 records on ZAW-1)
# Usage:
#   BASE_URL=https://your-app.railway.app scripts/seed_orders.sh
# Defaults to localhost if BASE_URL is not set.

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "[SEED:ORDERS] Using BASE_URL=${BASE_URL}"

post() {
  local payload="$1"
  curl -sS -X POST -H 'Content-Type: application/json' \
    --data "${payload}" \
    "${BASE_URL}/production/order" | jq '{ok, target_sheet: .target_sheet, order_id: .normalized.order_id, write_mode: .write_mode}'
}

post '{
  "order_id": "ZAW-SEED-001",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-A",
  "qta": 5,
  "postazione": "ZAW-1",
  "stato": "da fare"
}'

post '{
  "order_id": "ZAW-SEED-002",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-B",
  "qta": 3,
  "postazione": "ZAW-1",
  "stato": "da fare"
}'

post '{
  "order_id": "ZAW-SEED-003",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-C",
  "qta": 2,
  "postazione": "ZAW-1",
  "stato": "da fare"
}'

echo "[SEED:ORDERS] Done"
