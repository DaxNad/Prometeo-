#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

usage() {
  echo "usage: tools/local_llm/prometeo_local_edit.sh [--llm|--no-llm] \"goal...\"" >&2
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 2
fi

llm_mode="--no-llm"
if [[ "${1:-}" == "--llm" ]]; then
  llm_mode=""
  shift
elif [[ "${1:-}" == "--no-llm" ]]; then
  llm_mode="--no-llm"
  shift
fi

if [[ $# -lt 1 ]]; then
  usage
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
if [[ -n "$llm_mode" ]]; then
  python3 tools/local_llm/prometeo_local_editor.py "$llm_mode" "$goal"
else
  python3 tools/local_llm/prometeo_local_editor.py "$goal"
fi

echo
echo "== GIT STATUS =="
git status -sb
