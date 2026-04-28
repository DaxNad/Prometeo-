#!/bin/zsh
set -euo pipefail

cd "$HOME/PROMETEO/backend"
python3 -m app.agent_mod.worktree_hygiene
