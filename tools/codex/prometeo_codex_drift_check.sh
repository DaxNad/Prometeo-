#!/bin/zsh
set -euo pipefail

SAFE_ROOT="${PROMETEO_SAFE_CODEX_DIR:-$HOME/PROMETEO_SAFE_CODEX}"
PROMETEO_ROOT="${PROMETEO_ROOT:-$HOME/PROMETEO}"
CONFIG="${CODEX_CONFIG:-$HOME/.codex/config.toml}"
REPORT_DIR="$PROMETEO_ROOT/data/local_reports/codex_drift_checks"

mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/drift_check_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "PROMETEO CODEX/OLLAMA DRIFT CHECK"
  echo "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mode=READ_ONLY_NO_LAUNCH_NO_PATCH"
  echo

  echo "===== SAFE_CODEX_GIT_CHECK ====="
  if [ -d "$SAFE_ROOT/.git" ]; then
    echo "FAIL: SAFE_CODEX contains .git"
  else
    echo "PASS: SAFE_CODEX is not a git repo"
  fi
  echo

  echo "===== CODEX_VERSION ====="
  command -v codex >/dev/null 2>&1 && codex --version || echo "codex_not_found"
  echo

  echo "===== OLLAMA_VERSION ====="
  command -v ollama >/dev/null 2>&1 && ollama --version || echo "ollama_not_found"
  echo

  echo "===== CODEX_CONFIG_POLICY_CHECK ====="
  if [ -f "$CONFIG" ]; then
    grep -n 'projects\|trust_level\|profiles.prometeo_safe_codex\|approval_policy\|sandbox_mode' "$CONFIG" || true
  else
    echo "config_missing"
  fi
  echo

  echo "===== SHELL_GUARD_CHECK ====="
  grep -n 'PROMETEO SAFE CODEX GUARD\|PROMETEO OLLAMA CODEX GUARD\|codex()\|ollama()\|prometeo-codex' ${ZSHRC_PATH:-$HOME/.zshrc} || true
  echo

  echo "===== LAUNCHER_CHECK ====="
  grep -n 'sandbox read-only\|ask-for-approval untrusted\|HISTFILE\|PROMETEO_AI_DECISION_AUTHORITY\|SAFE_CODEX non deve essere un repository git' "$PROMETEO_ROOT/tools/codex/prometeo_safe_codex.sh" || true
} > "$REPORT"

cat "$REPORT"
echo
echo "REPORT=$REPORT"
