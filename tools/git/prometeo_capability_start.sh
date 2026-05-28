#!/usr/bin/env bash
set -euo pipefail

NUMBER="${1:-}"
SLUG="${2:-}"

if [ -z "$NUMBER" ] || [ -z "$SLUG" ]; then
  echo "USO: prometeo_capability_start.sh <NUMBER> <SLUG>"
  echo "ESEMPIO: tools/git/prometeo_capability_start.sh 008 real-article-eval"
  exit 2
fi

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

CURRENT_BRANCH="$(git branch --show-current)"
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "[BLOCKED] Devi partire da main. Branch corrente: $CURRENT_BRANCH"
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "[BLOCKED] Working tree non pulito."
  git status -sb
  exit 1
fi

echo "==> Aligning main"
git pull --ff-only

echo "==> Running baseline"
make goal-complete-v1

BRANCH="capability-${NUMBER}-${SLUG}"

echo "==> Creating branch: $BRANCH"
git checkout -b "$BRANCH"

echo "==> Status"
git status -sb

echo "PROMETEO_CAPABILITY_START_PASS"
