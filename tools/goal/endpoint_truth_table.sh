#!/usr/bin/env bash
set -u

BASE_URL="${PROMETEO_BASE_URL:-http://127.0.0.1:8000}"
RUNTIME_VALUE="${PROMETEO_RUNTIME_VALUE:-}"

if [ -z "$RUNTIME_VALUE" ]; then
  echo "PROMETEO_ENDPOINT_TRUTH_TABLE"
  echo
  printf "%-38s %-8s %-8s %-8s %s\n" "endpoint" "status" "runtime" "usable" "blocker"
  printf "%-38s %-8s %-8s %-8s %s\n" "ENV" "FAIL" "NO" "NO" "missing PROMETEO_RUNTIME_VALUE"
  exit 2
fi

header_args=(-H "X-API-Key: $RUNTIME_VALUE")

print_row() {
  printf "%-38s %-8s %-8s %-8s %s\n" "$1" "$2" "$3" "$4" "$5"
}

check_get() {
  local endpoint="$1"
  local response
  local code

  response="$(curl --max-time 10 -s -w $'\n%{http_code}' "${header_args[@]}" "$BASE_URL$endpoint" || true)"
  code="${response##*$'\n'}"

  if [ "$code" = "200" ]; then
    print_row "$endpoint" "$code" "YES" "YES" "none"
  elif [ "$code" = "000" ]; then
    print_row "$endpoint" "$code" "NO" "NO" "backend not reachable"
  else
    print_row "$endpoint" "$code" "YES" "NO" "non-200 response"
  fi
}

check_post_ai_sequence() {
  local endpoint="/ai/sequence"
  local response
  local code

  response="$(curl --max-time 20 -s -w $'\n%{http_code}' \
    "${header_args[@]}" \
    -H "Content-Type: application/json" \
    -X POST \
    "$BASE_URL$endpoint" || true)"
  code="${response##*$'\n'}"

  if [ "$code" = "200" ]; then
    print_row "$endpoint" "$code" "YES" "YES" "none"
  elif [ "$code" = "000" ]; then
    print_row "$endpoint" "TIMEOUT" "YES" "NO" "local AI call did not complete within 20s"
  else
    print_row "$endpoint" "$code" "YES" "NO" "POST non-200 response"
  fi
}

echo "PROMETEO_ENDPOINT_TRUTH_TABLE"
echo
printf "%-38s %-8s %-8s %-8s %s\n" "endpoint" "status" "runtime" "usable" "blocker"

check_get "/production/sequence"
check_get "/planner/sequence"
check_get "/production/turn-plan"
check_get "/production/sequence/explain"
check_get "/production/sequence/atlas-merge"
check_post_ai_sequence

echo
echo "VERDICT PARTIAL"
