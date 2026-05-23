#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_URL="${PROMETEO_BASE_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${PROMETEO_FRONTEND_URL:-http://localhost:5173}"

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
  printf "%-20s %s\n" "$1" "$2"
}

json_check() {
  local body="$1"
  local mode="$2"

  BODY="$body" MODE="$mode" python3 - <<'PY'
import json
import os
import sys

body = os.environ.get("BODY", "")
mode = os.environ.get("MODE", "")

try:
    data = json.loads(body)
except Exception:
    print("INVALID_JSON")
    sys.exit(1)

answer = str(data.get("answer") or "")
confidence = str(data.get("confidence") or "")

def has_all(*tokens: str) -> bool:
    return all(token in answer for token in tokens)

if data.get("ok") is not True:
    print("FAIL_NOT_OK")
    sys.exit(1)

if mode == "12066":
    if (
        confidence == "CERTO"
        and has_all("Route:", "Vincoli:", "Azione:", "ZAW1", "CP finale")
        and "Nota:" not in answer
        and ("ZAW2 esclusa" in answer or "non usare ZAW2" in answer)
        and data.get("technical_details_hidden") is True
    ):
        print("PASS")
        sys.exit(0)
elif mode == "12100":
    if confidence == "DA_VERIFICARE":
        print("KNOWN_ABSENT")
        sys.exit(0)
    if (
        confidence == "CERTO"
        and has_all("Route:", "Vincoli:", "Azione:", "ZAW1", "CP finale")
        and "Nota:" not in answer
        and ("ZAW2 esclusa" in answer or "non usare ZAW2" in answer)
        and data.get("technical_details_hidden") is True
    ):
        print("PASS")
        sys.exit(0)
elif mode == "zaw_global":
    if (
        confidence == "CERTO"
        and "non sono intercambiabili" in answer
        and "ZAW1_2" in answer
        and data.get("requires_confirmation") is False
        and data.get("technical_details_hidden") is True
    ):
        print("PASS")
        sys.exit(0)

print("FAIL_CONTRACT")
sys.exit(1)
PY
}

post_tl_chat() {
  local question="$1"
  curl --max-time 10 -s -w $'\n%{http_code}' \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${PROMETEO_API_KEY:-}" \
    -d "{\"question\":\"$question\"}" \
    "$BASE_URL/tl/chat" || true
}

fail_count=0

echo "PROMETEO_RUNTIME_OPERATIONAL_GOAL_CHECK"
echo

health_response="$(curl --max-time 10 -s -w $'\n%{http_code}' "$BASE_URL/health" || true)"
health_code="${health_response##*$'\n'}"
health_body="${health_response%$'\n'*}"

if [ "$health_code" = "200" ] && printf "%s" "$health_body" | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
  print_line "BACKEND_HEALTH" "PASS"
else
  print_line "BACKEND_HEALTH" "FAIL_HTTP_${health_code}"
  fail_count=$((fail_count + 1))
fi

load_env_if_needed

if [ -z "${PROMETEO_API_KEY:-}" ]; then
  print_line "PROMETEO_API_KEY" "MISSING_BLOCKED"
  print_line "VERDICT" "BLOCKED_ENV"
  exit 2
fi

auth_required_response="$(curl --max-time 10 -s -w $'\n%{http_code}' \
  -H "Content-Type: application/json" \
  -d '{"question":"ZAW1 e ZAW2 sono intercambiabili?"}' \
  "$BASE_URL/tl/chat" || true)"
auth_required_code="${auth_required_response##*$'\n'}"

if [ "$auth_required_code" = "401" ]; then
  print_line "TL_AUTH_REQUIRED" "PASS"
else
  print_line "TL_AUTH_REQUIRED" "FAIL_HTTP_${auth_required_code}"
  fail_count=$((fail_count + 1))
fi

for item in \
  "TL_12066|12066|12066?" \
  "TL_12100|12100|12100?" \
  "TL_ZAW_GLOBAL|zaw_global|ZAW1 e ZAW2 sono intercambiabili?"
do
  label="${item%%|*}"
  rest="${item#*|}"
  mode="${rest%%|*}"
  question="${rest#*|}"

  response="$(post_tl_chat "$question")"
  code="${response##*$'\n'}"
  body="${response%$'\n'*}"

  if [ "$code" != "200" ]; then
    print_line "$label" "FAIL_HTTP_${code}"
    fail_count=$((fail_count + 1))
    continue
  fi

  result="$(json_check "$body" "$mode" || true)"
  print_line "$label" "$result"
  case "$result" in
    PASS|KNOWN_ABSENT) ;;
    *) fail_count=$((fail_count + 1)) ;;
  esac
done

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
if [ "$fail_count" -eq 0 ]; then
  print_line "VERDICT" "GOAL_RUNTIME_PASS"
else
  print_line "VERDICT" "GOAL_RUNTIME_PARTIAL"
  exit 1
fi
