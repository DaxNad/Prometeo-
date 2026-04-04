#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$HOME/Documents/PROMETEO"
LOCAL_BASE_URL="${1:-http://127.0.0.1:8000}"
LOCAL_GATE_SCRIPT="$ROOT_DIR/scripts/agent_runtime_gate.sh"

TMP_HEALTH="$(mktemp)"
TMP_STATUS="$(mktemp)"

cleanup() {
  rm -f "$TMP_HEALTH" "$TMP_STATUS"
}
trap cleanup EXIT

echo "=== RAILWAY PREDEPLOY GATE ==="
echo "LOCAL_BASE_URL=$LOCAL_BASE_URL"

if [ ! -x "$LOCAL_GATE_SCRIPT" ]; then
  echo "ERRORE: gate locale non trovato o non eseguibile: $LOCAL_GATE_SCRIPT"
  exit 1
fi

echo
echo "=== STEP 1: LOCAL AGENT RUNTIME GATE ==="
"$LOCAL_GATE_SCRIPT" "$LOCAL_BASE_URL"

echo
echo "=== STEP 2: LOCAL HEALTH CONTRACT ==="
curl -fsS "$LOCAL_BASE_URL/health" > "$TMP_HEALTH"
python - <<'PY' "$TMP_HEALTH"
import json, sys
data = json.load(open(sys.argv[1]))
assert data["ok"] is True, "health.ok != true"
assert data["postgres_reachable"] is True, "postgres_reachable != true"
assert data["agent_runtime_enabled"] is True, "agent_runtime_enabled != true"
print("local health contract: OK")
PY

echo
echo "=== STEP 3: LOCAL AGENT STATUS CONTRACT ==="
curl -fsS "$LOCAL_BASE_URL/agent-runtime/status" > "$TMP_STATUS"
python - <<'PY' "$TMP_STATUS"
import json, sys
data = json.load(open(sys.argv[1]))
assert data["ok"] is True, "status.ok != true"
assert data["agent_runtime"] == "enabled", "agent_runtime != enabled"
assert data["repository"] == "ready", "repository != ready"
assert data["summary_available"] is True, "summary_available != true"

contract = data["summary_contract"]
assert contract["has_local_rule_count"] is True, "missing local_rule_count"
assert contract["has_local_escalation_count"] is True, "missing local_escalation_count"
assert contract["has_escalation_total_count"] is True, "missing escalation_total_count"
assert contract["has_atlas_escalation_count"] is True, "missing atlas_escalation_count"

print("local agent status contract: OK")
PY

echo
echo "=== RESULT ==="
echo "READY FOR RAILWAY DEPLOY"
