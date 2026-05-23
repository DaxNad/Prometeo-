#!/usr/bin/env bash
set -u

BASE_URL="${PROMETEO_BASE_URL:-http://127.0.0.1:8000}"
RUNTIME_VALUE="${PROMETEO_RUNTIME_VALUE:-}"

if [ -z "$RUNTIME_VALUE" ]; then
  echo "PROMETEO_GOAL_EXECUTION_MODE"
  echo
  printf "%-15s %s\n" "RUNTIME_VALUE" "MISSING_FAIL"
  printf "%-15s %s\n" "VERDICT" "BLOCKED_ENV_MISSING_RUNTIME_VALUE"
  exit 2
fi

header_args=()
if [ -n "$RUNTIME_VALUE" ]; then
  header_args=(-H "X-API-Key: $RUNTIME_VALUE")
fi

ok_count=0
fail_count=0
goal_articles=(12056 12057 12058)

print_line() {
  printf "%-15s %s\n" "$1" "$2"
}

fetch_endpoint() {
  local name="$1"
  local path="$2"
  local response
  local body
  local code

  response="$(curl --max-time 10 -s -w $'\n%{http_code}' "${header_args[@]}" "$BASE_URL$path" || true)"
  code="${response##*$'\n'}"
  body="${response%$'\n'*}"
  if [ "$code" = "$response" ]; then
    body=""
  fi

  if [ "$code" = "200" ]; then
    print_line "$name" "OK"
    ok_count=$((ok_count + 1))
  else
    print_line "$name" "FAIL_HTTP_$code"
    fail_count=$((fail_count + 1))
  fi

  printf -v "${name}_CODE" "%s" "$code"
  printf -v "${name}_BODY" "%s" "$body"
}

post_goal_order() {
  local order_id="$1"
  local article="$2"
  local station="$3"
  local qta="$4"
  local semaforo="$5"
  local response
  local body
  local code

  response="$(
    curl --max-time 10 -s -w $'\n%{http_code}' \
      "${header_args[@]}" \
      -H "Content-Type: application/json" \
      -X POST \
      -d "{\"order_id\":\"${order_id}\",\"cliente\":\"GOAL_DEV\",\"codice\":\"${article}\",\"qta\":${qta},\"postazione\":\"${station}\",\"stato\":\"da fare\",\"semaforo\":\"${semaforo}\",\"note\":\"GOAL runtime truth synthetic seed\"}" \
      "$BASE_URL/production/order" || true
  )"
  code="${response##*$'\n'}"
  body="${response%$'\n'*}"
  if [ "$code" = "$response" ]; then
    body=""
  fi

  if [ "$code" = "200" ] && printf "%s" "$body" | grep -q '"ok"[[:space:]]*:[[:space:]]*true' 2>/dev/null; then
    print_line "SEED_${article}" "OK"
  else
    print_line "SEED_${article}" "FAIL_HTTP_${code}"
    fail_count=$((fail_count + 1))
  fi
}

seed_goal_dataset() {
  echo "GOAL_SEED"
  post_goal_order "GOAL-12056" "12056" "ZAW-1" "5" "GIALLO"
  post_goal_order "GOAL-12057" "12057" "ZAW-1" "3" "GIALLO"
  post_goal_order "GOAL-12058" "12058" "ZAW-2" "4" "VERDE"
  echo
}

contains_any() {
  local text="$1"
  local needle="$2"
  printf "%s" "$text" | grep -q "$needle" 2>/dev/null
}

json_count_items() {
  local body="$1"
  BODY="$body" python3 -c '
import json
import os

raw = os.environ.get("BODY", "")

try:
    data = json.loads(raw)
except Exception:
    print(0)
    raise SystemExit

def find_items(obj):
    if isinstance(obj, dict):
        for key in ("items", "sequence", "rows", "data", "results", "orders"):
            value = obj.get(key)
            if isinstance(value, list):
                return value
        for value in obj.values():
            found = find_items(value)
            if found is not None:
                return found
    return None


items = find_items(data)
print(len(items) if isinstance(items, list) else 0)
'
}

echo "PROMETEO_GOAL_EXECUTION_MODE"
echo

seed_goal_dataset

fetch_endpoint "HEALTH" "/health"
fetch_endpoint "BOARD_STATE" "/production/board-state"
fetch_endpoint "MACHINE_LOAD" "/production/machine-load"
fetch_endpoint "SEQUENCE" "/production/sequence"
fetch_endpoint "PLANNER_SEQ" "/planner/sequence"

echo

items_count="$(json_count_items "$SEQUENCE_BODY")"

if [ "$items_count" -ge 3 ]; then
  print_line "ITEMS_COUNT" "${items_count}"
else
  print_line "ITEMS_COUNT" "${items_count}_FAIL"
  fail_count=$((fail_count + 1))
fi

for article in "${goal_articles[@]}"; do
  if contains_any "$BOARD_STATE_BODY" "$article"; then
    print_line "BOARD_$article" "PRESENT"
  else
    print_line "BOARD_$article" "MISSING"
    fail_count=$((fail_count + 1))
  fi
done

for article in "${goal_articles[@]}"; do
  if contains_any "$SEQUENCE_BODY" "$article" || contains_any "$PLANNER_SEQ_BODY" "$article"; then
    print_line "SEQ_$article" "PRESENT"
  elif contains_any "$SEQUENCE_BODY $PLANNER_SEQ_BODY" "SMOKE"; then
    print_line "SEQ_$article" "MISSING_SMOKE_FALLBACK"
    fail_count=$((fail_count + 1))
  else
    print_line "SEQ_$article" "MISSING_FILTER_OR_BINDING"
    fail_count=$((fail_count + 1))
  fi
done

echo

if contains_any "$SEQUENCE_BODY" "SMOKE-ZAW1" || contains_any "$PLANNER_SEQ_BODY" "SMOKE-ZAW1"; then
  print_line "SMOKE-ZAW1" "PRESENT_FAIL"
  fail_count=$((fail_count + 1))
else
  print_line "SMOKE-ZAW1" "ABSENT"
fi

if contains_any "$SEQUENCE_BODY" "SMOKE-ZAW2" || contains_any "$PLANNER_SEQ_BODY" "SMOKE-ZAW2"; then
  print_line "SMOKE-ZAW2" "PRESENT_FAIL"
  fail_count=$((fail_count + 1))
else
  print_line "SMOKE-ZAW2" "ABSENT"
fi

echo

if [ "$fail_count" -eq 0 ]; then
  print_line "VERDICT" "CLOSED"
elif [ "${SEQUENCE_CODE:-000}" = "200" ] || [ "${PLANNER_SEQ_CODE:-000}" = "200" ]; then
  print_line "VERDICT" "PARTIAL"
else
  print_line "VERDICT" "BLOCKED"
fi
