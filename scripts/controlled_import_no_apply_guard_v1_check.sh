#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"

runtime_files=(
  "$ROOT/backend/app/api/controlled_import.py"
  "$ROOT/backend/app/services/controlled_import_preview.py"
  "$ROOT/backend/app/services/controlled_import_audit.py"
)

missing=0
for file in "${runtime_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "MISSING RUNTIME FILE: ${file#$ROOT/}"
    missing=1
  fi
done
if [[ "$missing" -ne 0 ]]; then
  exit 1
fi

violations=0

check_pattern() {
  local name="$1"
  local pattern="$2"
  local file

  for file in "${runtime_files[@]}"; do
    if grep -nE "$pattern" "$file" >/dev/null; then
      if [[ "$violations" -eq 0 ]]; then
        echo "CONTROLLED_IMPORT_NO_APPLY_GUARD_V1: FAIL"
      fi
      violations=1
      while IFS= read -r line; do
        echo "${file#$ROOT/}: ${name}: ${line}"
      done < <(grep -nE "$pattern" "$file")
    fi
  done
}

check_pattern "controlled_import_apply_endpoint" "['\"]/(controlled-import/)?apply['\"]"
check_pattern "controlled_import_apply_function" "\\b(apply_controlled_import|controlled_import_apply)\\b"
check_pattern "write_mode_apply" "write_mode[[:space:]]*[:=][[:space:]]*['\"]APPLY['\"]"
check_pattern "apply_allowed_true" "apply_allowed[[:space:]]*[:=][[:space:]]*True\\b|['\"]apply_allowed['\"][[:space:]]*:[[:space:]]*true\\b"
check_pattern "db_session_write_path" "\\b(get_db|SessionLocal)\\b|\\.commit[[:space:]]*\\("
check_pattern "smf_write_path" "\\b(SMFAdapter|write_extracted)\\b|\\b(append_order|update_order)[[:space:]]*\\("
check_pattern "planner_mutation_path" "\\b(build_turn_plan|build_global_sequence)\\b|planner_update[[:space:]]*[:=][[:space:]]*True\\b"

if [[ "$violations" -ne 0 ]]; then
  exit 1
fi

echo "CONTROLLED_IMPORT_NO_APPLY_GUARD_V1: OK"
