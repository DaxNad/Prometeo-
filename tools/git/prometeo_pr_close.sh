#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
  echo "USO: prometeo_pr_close.sh <PR_NUMBER>"
  exit 2
fi

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" = "main" ]; then
  echo "[OK] current branch: main"
else
  echo "[INFO] current branch: $BRANCH"
fi

echo "==> Checking PR #$PR_NUMBER"
gh pr checks "$PR_NUMBER" --watch

echo "==> Merging PR #$PR_NUMBER"
gh pr merge "$PR_NUMBER" --squash --delete-branch

echo "==> Aligning main"
git checkout main
git pull --ff-only

echo "==> Running goal-complete-v1"
make goal-complete-v1

echo "==> Running runtime operational goal check"
bash tools/goal/runtime_operational_goal_check.sh

echo "==> Final status"
git status -sb

echo "PROMETEO_PR_CLOSE_PASS"
