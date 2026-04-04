#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE_BASE_URL="${1:-https://prometeo-railway-bootstrap-production.up.railway.app}"

TMP_HEALTH="$(mktemp)"
TMP_STATUS="$(mktemp)"

cleanup() {
  rm -f "$TMP_HEALTH" "$TMP_STATUS"
}
trap cleanup EXIT

echo "=== RAILWAY POSTDEPLOY GATE ==="
echo "REMOTE_BASE_URL=$REMOTE_BASE_URL"

echo
echo "=== STEP 1: REMOTE /health ==="
curl -fsS "$REMOTE_BASE_URL/health" > "$TMP_HEALTH"
python - <<'PY' "$TMP_HEALTH"
import json, sys
data = json.load(open(sys.argv[1]))
assert data["ok"] is True, "health.ok != true"
assert data["agent_runtime_enabled"] is True, "agent_runtime_enabled != true"
assert data["postgres_reachable"] is True, "postgres_reachable != true"
print("remote health: OK")
print({
    "service": data.get("service"),
    "version": data.get("version"),
    "db_backend": data.get("db_backend"),
    "postgres_reachable": data.get("postgres_reachable"),
})
PY

echo
echo "=== STEP 2: REMOTE /agent-runtime/status ==="
curl -fsS "$REMOTE_BASE_URL/agent-runtime/status" > "$TMP_STATUS"
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

print("remote agent-runtime/status: OK")
print(json.dumps(data["totals"], ensure_ascii=False, indent=2))
PY

echo
echo "=== RESULT ==="
echo "RAILWAY POSTDEPLOY GATE: OK"
