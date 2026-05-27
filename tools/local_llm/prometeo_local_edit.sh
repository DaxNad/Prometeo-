#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ $# -lt 1 ]]; then
  echo "usage: tools/local_llm/prometeo_local_edit.sh \"goal...\"" >&2
  exit 2
fi

goal="$*"
current_branch="$(git branch --show-current)"

if [[ "$current_branch" == "main" ]]; then
  safe_slug="$(echo "$goal" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//' | cut -c1-48)"
  if [[ -z "$safe_slug" ]]; then
    safe_slug="local-llm-edit"
  fi
  branch="local-llm/${safe_slug}-$(date +%Y%m%d-%H%M%S)"
  git switch -c "$branch"
  echo "== BRANCH CREATED =="
  echo "$branch"
else
  echo "== USING CURRENT BRANCH =="
  echo "$current_branch"
fi

echo
echo "== LOCAL LLM EDITOR =="
python3 tools/local_llm/prometeo_local_editor.py "$goal"

echo
echo "== GIT STATUS =="
git status -sb
