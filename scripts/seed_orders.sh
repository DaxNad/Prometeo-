#!/usr/bin/env bash
set -euo pipefail

# Seed realistic demo dataset for production orders
# Requirements:
# - 3 orders on ZAW-1
# - 1 order on ZAW-2
# - 1 order with shared component pressure
# - priority mix (ALTA, MEDIA)
# - at least 1 blocked order
# Usage:
#   BASE_URL=https://your-app.railway.app scripts/seed_orders.sh
# Defaults to localhost if BASE_URL is not set.

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "[SEED:ORDERS] Using BASE_URL=${BASE_URL}"

post() {
  local payload="$1"
  curl -sS -X POST -H 'Content-Type: application/json' \
    --data "${payload}" \
    "${BASE_URL}/production/order" | jq '{ok, order_id: .order_id, rows: .rows, smf: .smf_sync.ok}'
}

post '{
  "order_id": "ZAW-SEED-001",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-A",
  "qta": 5,
  "postazione": "ZAW-1",
  "stato": "da fare",
  "priorita": "ALTA",
  "station_queue_pressure": 2
}'

post '{
  "order_id": "ZAW-SEED-002",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-B",
  "qta": 3,
  "postazione": "ZAW-1",
  "stato": "da fare",
  "priorita": "MEDIA",
  "station_queue_pressure": 1
}'

post '{
  "order_id": "ZAW-SEED-003",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-C",
  "qta": 2,
  "postazione": "ZAW-1",
  "stato": "bloccato",
  "priorita": "ALTA",
  "station_queue_pressure": 3
}'

# ZAW-2 (MEDIA)
post '{
  "order_id": "ZAW-SEED-004",
  "cliente": "SeedCustomer",
  "codice": "CODE-ZAW-D",
  "qta": 4,
  "postazione": "ZAW-2",
  "stato": "da fare",
  "priorita": "MEDIA",
  "station_queue_pressure": 1
}'

# Shared component pressure (associato a ZAW-1)
post '{
  "order_id": "ZAW-SEED-SHARED-001",
  "cliente": "SeedCustomer",
  "codice": "CODE-SHARED-X",
  "qta": 1,
  "postazione": "ZAW-1",
  "stato": "da fare",
  "priorita": "MEDIA",
  "shared_component_pressure": 1
}'

echo "[SEED:ORDERS] Done"
