#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

FILES=(
  "backend/app/api/controlled_import.py"
  "backend/app/services/controlled_import_persistent_audit.py"
  "backend/app/services/controlled_import_audit.py"
  "backend/app/repositories/controlled_import_audit_repository.py"
)

EXISTING_FILES=()
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    EXISTING_FILES+=("$file")
  fi
done

if [ "${#EXISTING_FILES[@]}" -eq 0 ]; then
  echo "CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_GUARD_V1: no controlled import files found"
  exit 1
fi

fail() {
  echo "CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_GUARD_V1: FAIL"
  echo "$1"
  exit 1
}

require_present() {
  local pattern="$1"
  local file="$2"
  if ! grep -Eq "$pattern" "$file"; then
    fail "Missing required safe marker in $file: $pattern"
  fi
}

for file in "${EXISTING_FILES[@]}"; do
  if grep -Eq 'persist_audit[[:space:]]*[:=][[:space:]]*True|persist_audit[[:space:]]*=[[:space:]]*true|persist_audit[[:space:]]*:[[:space:]]*true' "$file"; then
    fail "persist_audit default true detected in $file"
  fi

  if grep -Eq 'audit_persistence[[:space:]]*[:=][[:space:]]*["'\''](?!NONE)' "$file"; then
    fail "audit_persistence default other than NONE detected in $file"
  fi

  if grep -Eq 'confirmation_token([^_a-zA-Z0-9]|$)' "$file" && ! grep -Eq 'confirmation_token_hash' "$file"; then
    fail "plain confirmation_token accepted without hash guard in $file"
  fi

  if grep -Eq 'risk_level[[:space:]]*==[[:space:]]*["'\'']BLOCKED["'\''].*persist|persist.*risk_level[[:space:]]*==[[:space:]]*["'\'']BLOCKED["'\'']' "$file"; then
    fail "BLOCKED risk appears persistible in ordinary path in $file"
  fi

  if grep -Eq 'apply_allowed[[:space:]]*[:=][[:space:]]*True|apply_allowed[[:space:]]*=[[:space:]]*true|apply_allowed[[:space:]]*:[[:space:]]*true' "$file"; then
    fail "apply_allowed=true detected in controlled import preview path in $file"
  fi

  if grep -Eq 'apply_executed[[:space:]]*[:=][[:space:]]*True|apply_executed[[:space:]]*=[[:space:]]*true|apply_executed[[:space:]]*:[[:space:]]*true' "$file"; then
    fail "apply_executed=true detected in controlled import preview path in $file"
  fi

  if grep -Eq 'write_mode[[:space:]]*[:=][[:space:]]*["'\''](APPLY|WRITE|COMMIT|PERSIST)' "$file"; then
    fail "write_mode other than PREVIEW_ONLY detected in $file"
  fi

  if grep -Eq '/controlled-import/apply|/apply' "$file"; then
    fail "controlled import apply endpoint/path detected in $file"
  fi

  if grep -Eq 'SMFAdapter|write_extracted|append_order|update_order|get_db|SessionLocal|\.commit\(|build_turn_plan|build_global_sequence|planner_update|frontend' "$file"; then
    fail "forbidden SMF/DB/planner/frontend coupling detected in $file"
  fi
done

PREVIEW_FILE="backend/app/api/controlled_import.py"
if [ -f "$PREVIEW_FILE" ]; then
  require_present 'PREVIEW_ONLY' "$PREVIEW_FILE"
  require_present 'apply_allowed.*False|apply_allowed.*false' "$PREVIEW_FILE"
  require_present 'apply_executed.*False|apply_executed.*false' "$PREVIEW_FILE"
  require_present 'audit_dry_run' "$PREVIEW_FILE"
  require_present 'audit_persistence.*NONE' "$PREVIEW_FILE"
fi

if grep -R --line-number 'persist_audit' "${EXISTING_FILES[@]}" | grep -v 'False' | grep -v 'false' | grep -v 'actor' | grep -v 'source' | grep -v 'confirmation_token_hash' >/tmp/controlled_import_binding_guard_hits.txt 2>/dev/null; then
  cat /tmp/controlled_import_binding_guard_hits.txt
  fail "persist_audit usage lacks explicit safe gating markers"
fi

echo "CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_GUARD_V1: OK"
