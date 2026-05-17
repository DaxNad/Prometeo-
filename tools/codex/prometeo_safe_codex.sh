#!/bin/zsh
set -euo pipefail

SAFE_ROOT="${PROMETEO_SAFE_CODEX_DIR:-$HOME/PROMETEO_SAFE_CODEX}"
REAL_REPO="${PROMETEO_ROOT:-$HOME/PROMETEO}"

mkdir -p "$SAFE_ROOT"

if [ -d "$SAFE_ROOT/.git" ]; then
  echo "BLOCCATO: PROMETEO_SAFE_CODEX non deve essere un repository git."
  echo "Rimuovere .git solo dopo conferma umana esplicita."
  exit 64
fi

# Riduzione leakage solo per questa sessione launcher.
unset HISTFILE 2>/dev/null || true
export HISTSIZE=0
export SAVEHIST=0
export PROMETEO_SAFE_CODEX_MODE="read_only"
export PROMETEO_AI_DECISION_AUTHORITY="none"
export PROMETEO_HUMAN_AUTHORITY="required"

cat <<MSG
PROMETEO SAFE CODEX PROFILE
mode: read-only
approval: untrusted
workspace: $SAFE_ROOT
real repo: not writable by default
forbidden: full-auto, danger-full-access, direct PROMETEO launch, deploy, ollama launch codex/codex-app
MSG

exec codex \
  --profile prometeo_safe_codex \
  --sandbox read-only \
  --ask-for-approval untrusted \
  --cd "$SAFE_ROOT"
