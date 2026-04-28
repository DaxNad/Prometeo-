#!/bin/zsh
set -euo pipefail

echo "=============================="
echo "PROMETEO AI STACK STATUS"
echo "=============================="
echo ""

echo "---- GIT ----"
git -C "$HOME/PROMETEO" status -s || true
echo ""

echo "---- WORKTREE HYGIENE ----"
python3 -m app.agent_mod.worktree_hygiene 2>/dev/null || echo "guard non disponibile"
echo ""

echo "---- BACKEND ----"
if lsof -i :8000 >/dev/null 2>&1; then
    echo "backend attivo su :8000"
else
    echo "backend non attivo"
fi
echo ""

echo "---- CODEX ----"
if command -v codex >/dev/null 2>&1; then
    codex --version
else
    echo "codex non trovato"
fi
echo ""

echo "---- CLAUDE ----"
if command -v claude >/dev/null 2>&1; then
    claude --version || true
    echo ""
    echo "per uso dettagliato:"
    echo "  avvia: claude"
    echo "  poi:   /status"
    echo "         /stats"
else
    echo "claude non trovato"
fi
echo ""

echo "---- ENV ----"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
echo ""

echo "=============================="
echo "END STATUS"
echo "=============================="
