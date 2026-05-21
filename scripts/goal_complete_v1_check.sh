#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SESSION_MEMORY_FILE="data/local_reports/session_memory/scadenze_2026-06-22.md"
GOAL_TMP_DIR="${PROMETEO_GOAL_TMPDIR:-$ROOT_DIR/.goal_complete_v1_tmp}"

mkdir -p "$GOAL_TMP_DIR"
export TMPDIR="$GOAL_TMP_DIR"

cleanup_tmp() {
  if [ -z "${PROMETEO_GOAL_TMPDIR:-}" ]; then
    rm -rf "$GOAL_TMP_DIR"
  fi
}
trap cleanup_tmp EXIT

log_step() {
  printf '\n==> %s\n' "$1"
}

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

log_step "PROMETEO_GOAL_COMPLETE_V1 preflight"

if [ ! -f "$SESSION_MEMORY_FILE" ]; then
  fail "session memory file missing: $SESSION_MEMORY_FILE"
fi

if git ls-files --error-unmatch "$SESSION_MEMORY_FILE" >/dev/null 2>&1; then
  fail "session memory file is tracked by git: $SESSION_MEMORY_FILE"
fi

if ! git check-ignore -q "$SESSION_MEMORY_FILE"; then
  fail "session memory file is not ignored by git: $SESSION_MEMORY_FILE"
fi

log_step "Tracked sensitive file check"

sensitive_tracked="$(
  git ls-files | while IFS= read -r path; do
    if [[ "$path" == data/local_reports/session_memory/.gitkeep ]]; then
      continue
    elif [[ "$path" == data/local_reports/session_memory/* ]]; then
      printf '%s\n' "$path"
    elif [[ "$path" == specs_finitura/*/metadata.json ]]; then
      printf '%s\n' "$path"
    elif [[ "$path" == specs_finitura/*/*.png || "$path" == specs_finitura/*/*.jpg || "$path" == specs_finitura/*/*.jpeg || "$path" == specs_finitura/*/*.pdf || "$path" == specs_finitura/*/*.heic || "$path" == specs_finitura/*/*.webp || "$path" == specs_finitura/*/*.tif || "$path" == specs_finitura/*/*.tiff || "$path" == specs_finitura/*/*.zip || "$path" == specs_finitura/*/*.7z || "$path" == specs_finitura/*/*.tar || "$path" == specs_finitura/*/*.gz || "$path" == specs_finitura/*/*.rar ]]; then
      printf '%s\n' "$path"
    elif [[ "$path" == *.env || "$path" == *.sqlite || "$path" == *.sqlite3 || "$path" == *.db || "$path" == *.dump || "$path" == *.backup || "$path" == *.bak || "$path" == *.log ]]; then
      printf '%s\n' "$path"
    fi
  done
)"

if [ -n "$sensitive_tracked" ]; then
  printf '%s\n' "$sensitive_tracked" >&2
  fail "sensitive tracked files detected"
fi

printf '[PASS] no tracked sensitive files matched local GOAL_COMPLETE patterns\n'

log_step "TL Chat contract"
python3 -m pytest backend/tests/test_tl_chat_contract.py -q -s --basetemp "$GOAL_TMP_DIR/pytest"

log_step "TL eval"
make tl-eval

log_step "Data Leak Guard"
python3 scripts/data_leak_guard.py

log_step "Privacy Guard"
python3 scripts/privacy_guard_specs.py

if [ "${PROMETEO_GOAL_CHECK_FRONTEND_BUILD:-0}" = "1" ]; then
  log_step "Frontend build (explicit opt-in)"
  (cd frontend && npm run build)
else
  log_step "Frontend build skipped"
  printf 'Set PROMETEO_GOAL_CHECK_FRONTEND_BUILD=1 to run npm build; skipped by default because it writes frontend/dist.\n'
fi

log_step "PROMETEO_GOAL_COMPLETE_V1"
printf 'RESULT=PASS\n'
