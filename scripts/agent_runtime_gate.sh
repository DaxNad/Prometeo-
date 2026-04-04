#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

echo "=== AGENT RUNTIME GATE ==="
echo "BASE_URL=$BASE_URL"

TMP_HEALTH="$(mktemp)"
TMP_STATUS="$(mktemp)"
TMP_SUMMARY="$(mktemp)"

cleanup() {
  rm -f "$TMP_HEALTH" "$TMP_STATUS" "$TMP_SUMMARY"
}
trap cleanup EXIT

echo
echo "=== CHECK /health ==="
curl -fsS "$BASE_URL/health" > "$TMP_HEALTH"
python - <<'PY' "$TMP_HEALTH"
import json, sys
data = json.load(open(sys.argv[1]))
assert data["ok"] is True, "health.ok != true"
assert data["agent_runtime_enabled"] is True, "agent_runtime_enabled != true"
assert data["postgres_reachable"] is True, "postgres_reachable != true"
print("health: OK")
PY

echo
echo "=== CHECK /agent-runtime/status ==="
curl -fsS "$BASE_URL/agent-runtime/status" > "$TMP_STATUS"
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

totals = data["totals"]
assert "total_runs" in totals, "missing total_runs"
assert "monitor_count" in totals, "missing monitor_count"
assert "investigate_count" in totals, "missing investigate_count"
assert "escalation_total_count" in totals, "missing escalation_total_count in totals"
assert "atlas_escalation_count" in totals, "missing atlas_escalation_count in totals"

print("agent-runtime/status: OK")
print(json.dumps(totals, ensure_ascii=False, indent=2))
PY

echo
echo "=== CHECK /agent-runtime/summary ==="
curl -fsS "$BASE_URL/agent-runtime/summary" > "$TMP_SUMMARY"
python - <<'PY' "$TMP_SUMMARY"
import json, sys
data = json.load(open(sys.argv[1]))
assert data["ok"] is True, "summary.ok != true"
summary = data["summary"]

required = [
    "total_runs",
    "monitor_count",
    "investigate_count",
    "local_rule_count",
    "local_escalation_count",
    "escalation_total_count",
    "atlas_escalation_count",
    "order_domain_count",
    "machine_domain_count",
    "legacy_bootstrap_count",
    "possible_anomaly_count",
    "blocked_order_count",
    "overdue_count",
]
missing = [k for k in required if k not in summary]
assert not missing, f"summary missing keys: {missing}"

print("agent-runtime/summary: OK")
PY

echo
echo "=== GATE RESULT ==="
echo "AGENT RUNTIME GATE: OK"
