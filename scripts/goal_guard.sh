#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

GOAL_TMP_DIR="/private/tmp/prometeo_pytest"

case "$GOAL_TMP_DIR" in
  "$ROOT_DIR"/*)
    printf '[FAIL] goal guard temp dir must stay outside repo: %s\n' "$GOAL_TMP_DIR" >&2
    exit 1
    ;;
esac

mkdir -p "$GOAL_TMP_DIR"
PYTEST_BASETEMP="$(mktemp -d "$GOAL_TMP_DIR/pytest.XXXXXX")"

export TMPDIR="$GOAL_TMP_DIR"
export TEMP="$GOAL_TMP_DIR"
export TMP="$GOAL_TMP_DIR"
export PYTHONDONTWRITEBYTECODE=1

log_step() {
  printf '\n==> %s\n' "$1"
}

log_step "Diff whitespace check"
git diff --check

log_step "Data Leak Guard"
python3 scripts/data_leak_guard.py

log_step "Privacy Guard"
python3 scripts/privacy_guard_specs.py

log_step "Docs Authority Guard"
python3 scripts/docs_authority_guard.py

log_step "TL Eval Guard"
make tl-eval

log_step "Backend tests"
python3 -m pytest -p no:cacheprovider -s backend/tests -q --basetemp "$PYTEST_BASETEMP"

log_step "PROMETEO local goal guard"
printf 'RESULT=PASS\n'
