#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="${PROMETEO_BASE_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${PROMETEO_FRONTEND_URL:-http://localhost:5173}"

fail_count=0
auth_missing=0

load_env_if_needed() {
  if [ -n "${PROMETEO_API_KEY:-}" ]; then
    return
  fi

  set -a
  [ -f "$ROOT/backend/.env" ] && . "$ROOT/backend/.env" || true
  [ -f "$ROOT/.env" ] && . "$ROOT/.env" || true
  set +a
}

print_line() {
  printf "%-24s %s\n" "$1" "$2"
}

require_command() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    print_line "CMD_${name}" "PASS"
  else
    print_line "CMD_${name}" "MISSING"
    fail_count=$((fail_count + 1))
  fi
}

echo "PROMETEO_PRODUCT_DOCTOR"
echo

print_line "REPO_ROOT" "$ROOT"
require_command python3
require_command node
require_command npm
require_command curl
load_env_if_needed

echo
echo "== Runtime smoke =="

health_response="$(curl --max-time 10 -s -w $'\n%{http_code}' "$BASE_URL/health" || true)"
health_code="${health_response##*$'\n'}"
health_body="${health_response%$'\n'*}"

if [ "$health_code" = "200" ] && printf "%s" "$health_body" | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
  print_line "BACKEND_HEALTH" "PASS"
else
  print_line "BACKEND_HEALTH" "FAIL_HTTP_${health_code}"
  fail_count=$((fail_count + 1))
fi

frontend_head="$(curl --max-time 10 -s -I "$FRONTEND_URL/" || true)"
frontend_html="$(curl --max-time 10 -s "$FRONTEND_URL/" | head -40 || true)"

if printf "%s" "$frontend_head" | grep -q "200 OK" \
  && printf "%s" "$frontend_html" | grep -q '<div id="root"></div>' \
  && ! printf "%s" "$frontend_html" | grep -Eq '/Users|specs_finitura|local_smf'; then
  print_line "FRONTEND_ROOT" "PASS"
else
  print_line "FRONTEND_ROOT" "FAIL"
  fail_count=$((fail_count + 1))
fi

echo
echo "== TL Chat smoke =="

if [ -z "${PROMETEO_API_KEY:-}" ]; then
  auth_required_response="$(curl --max-time 10 -s -w $'\n%{http_code}' \
    -H "Content-Type: application/json" \
    -d '{"question":"ZAW1 e ZAW2 sono intercambiabili?"}' \
    "$BASE_URL/tl/chat" || true)"
  auth_required_code="${auth_required_response##*$'\n'}"

  if [ "$auth_required_code" = "401" ]; then
    print_line "TL_AUTH_REQUIRED" "PASS"
    print_line "TL_CHAT_SMOKE" "SKIPPED_AUTH_MISSING"
    auth_missing=1
  else
    print_line "TL_AUTH_REQUIRED" "FAIL_HTTP_${auth_required_code}"
    print_line "TL_CHAT_SMOKE" "SKIPPED_AUTH_MISSING"
    fail_count=$((fail_count + 1))
    auth_missing=1
  fi
elif bash "$ROOT/tools/goal/runtime_operational_goal_check.sh"; then
  print_line "TL_CHAT_SMOKE" "PASS"
else
  print_line "TL_CHAT_SMOKE" "FAIL"
  fail_count=$((fail_count + 1))
fi

echo
if [ "$fail_count" -eq 0 ]; then
  if [ "$auth_missing" -eq 1 ]; then
    print_line "VERDICT" "PRODUCT_DOCTOR_AUTH_MISSING"
    exit 2
  fi
  print_line "VERDICT" "PRODUCT_DOCTOR_PASS"
else
  print_line "VERDICT" "PRODUCT_DOCTOR_PARTIAL"
  exit 1
fi
